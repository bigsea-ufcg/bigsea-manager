# Copyright (c) 2017 UFCG-LSD.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import os
import subprocess
import time
import threading
import uuid

from application_manager import exceptions as ex
from application_manager.openstack import connector as os_connector
from application_manager.openstack import utils as os_utils
from application_manager.plugins import base
from application_manager.service import api
from application_manager.utils import hdfs
from application_manager.utils import monitor
from application_manager.utils import optimizer
from application_manager.utils import remote
from application_manager.utils import scaler
from application_manager.utils import spark
from application_manager.utils.logger import Log, configure_logging

from saharaclient.api.base import APIException as SaharaAPIException
from application_manager.utils.ids import ID_Generator
from application_manager.plugins.base import GenericApplicationExecutor

plugin_log = Log("Sahara_Plugin", "logs/sahara_plugin.log")
application_time_log = Log("Application_Time", "logs/application_time.log")
instances_log = Log("Instances", "logs/instances.log")

configure_logging()

class OpenStackSparkApplicationExecutor(GenericApplicationExecutor):

    def __init__(self):
        self.application_state = "None"
        self.state_lock = threading.RLock()
        self.application_time = -1
        self.start_time = -1

    def get_application_state(self):
        with self.state_lock:
            state = self.application_state
        return state

    def update_application_state(self, state):
        print state
        with self.state_lock:
            self.application_state = state

    def get_application_execution_time(self):
        return self.application_time

    def get_application_start_time(self):
        return self.start_time

    def start_application(self, data, spark_applications_ids, app_id):
        try:
            self.update_application_state("Running")

            # Broker Parameters
            user = api.user
            password = api.password
            project_id = api.project_id
            auth_ip = api.auth_ip
            domain = api.domain
            public_key = api.public_key
            key_path = api.key_path
            log_path = api.log_path
            container = api.container
            hosts = api.hosts
            remote_hdfs = api.remote_hdfs

            # User Request Parameters
            net_id = data['net_id']
            master_ng = data['master_ng']
            slave_ng = data['slave_ng']
            op_slave_ng = data['opportunistic_slave_ng']
            plugin = data['openstack_plugin']
            percentage = data['percentage']
            job_type = data['job_type']
            version = data['version']
            req_cluster_size = data['cluster_size']
            cluster_size = data['cluster_size']
            args = data['args']
            main_class = data['main_class']
            dependencies = data['dependencies']
            job_template_name = data['job_template_name']
            job_binary_name = data['job_binary_name']
            job_binary_url = data['job_binary_url']
            image_id = data['image_id']
            plugin_app = data['plugin']
            expected_time = data['expected_time']
            collect_period = data['collect_period']
            image_id = data['image_id']
            starting_cap = data['starting_cap']

            # Openstack Components
            connector = os_connector.OpenStackConnector(plugin_log)

            sahara = connector.get_sahara_client(user, password, project_id,
                                                 auth_ip, domain)

            swift = connector.get_swift_client(user, password, project_id,
                                               auth_ip, domain)

            # Check Oportunism

            plugin_log.log(
                "%s | Checking if opportunistic instances are available" %
                (time.strftime("%H:%M:%S")))
            pred_cluster_size = optimizer.get_cluster_size(api.optimizer_url,
                                                           hosts,
                                                           percentage)

            if pred_cluster_size > req_cluster_size:
                cluster_size = pred_cluster_size
            else:
                cluster_size = req_cluster_size

            plugin_log.log(
                "%s | Cluster size: %s" % (time.strftime("%H:%M:%S"),
                                           str(cluster_size)))

            # Cluster Operations
            cluster_id = connector.get_existing_cluster_by_size(sahara,
                                                                cluster_size)

            if not cluster_id:
                plugin_log.log(
                    "%s | Cluster does not exist. Creating cluster..." %
                    (time.strftime("%H:%M:%S")))

                cluster_id = self._create_cluster(sahara, connector,
                                                  req_cluster_size,
                                                  pred_cluster_size,
                                                  public_key, net_id, image_id,
                                                  plugin, version, master_ng,
                                                  slave_ng, op_slave_ng)

            plugin_log.log("%s | Cluster id: %s" % (time.strftime("%H:%M:%S"),
                                                    cluster_id))

            swift_path = self._is_swift_path(args)

            if cluster_id:
                master = connector.get_master_instance(
                     sahara, cluster_id)['internal_ip']

                plugin_log.log("%s | Master is: %s" % (time.strftime("%H:%M:%S"),
                                                       master))

                workers = connector.get_worker_instances(sahara, cluster_id)
                workers_id = []

                for worker in workers:
                    workers_id.append(worker['instance_id'])

                scaler.setup_environment(api.controller_url, workers_id,
                                         starting_cap, data)

                if swift_path:
                    job_status = self._swift_spark_execution(
                        master, key_path, sahara, connector, job_binary_name,
                        job_binary_url, user, password, job_template_name,
                        job_type, plugin, cluster_size, args, main_class,
                        cluster_id, spark_applications_ids, workers_id, app_id,
                        expected_time, plugin_app, collect_period, log_path, swift,
                        container, data)
                else:
                    job_status = self._hdfs_spark_execution(
                        master, remote_hdfs, key_path, args, job_binary_url,
                        main_class, dependencies)

#               # Delete cluster
#               plugin_log.log("%s | Delete cluster: %s" % (time.strftime("%H:%M:%S"),
#                                                           cluster_id))
#               connector.delete_cluster(sahara, cluster_id)

            else:
                # FIXME: exception type
                self.update_application_state("Error")
                raise ex.ClusterNotCreatedException()

            return job_status

        except Exception as e:
            self.update_application_state("Error")
            plugin_log.log(str(e))

    def get_application_time(self):
        return self.application_time

    def _get_job_binary_id(self, sahara, connector, job_binary_name,
                           job_binary_url, user, password):
        extra = dict(user=user, password=password)
        job_binary_id = connector.get_job_binary(sahara, job_binary_url)

        if not job_binary_id:
            job_binary_id = connector.create_job_binary(sahara,
                                                        job_binary_name,
                                                        job_binary_url, extra)

        return job_binary_id

    def _get_job_template_id(self, sahara, connector, mains, job_template_name,
                             job_type):
        job_template_id = connector.get_job_template(sahara, mains)
        if not job_template_id:
            job_template_id = connector.create_job_template(sahara,
                                                            job_template_name,
                                                            job_type, mains)
        return job_template_id

    def _wait_on_job_finish(self, sahara, connector, job_exec_id,
                            spark_app_id):
        completed = failed = False
        start_time = datetime.datetime.now()
        self.start_time = time.mktime(start_time.timetuple())
        while not (completed or failed):
            job_status = connector.get_job_status(sahara, job_exec_id)
            plugin_log.log("%s | Sahara current job status: %s" %
                    (time.strftime("%H:%M:%S"), job_status))
            if job_status == 'RUNNING':
                time.sleep(2)

            current_time = datetime.datetime.now()
            current_job_time = (current_time - start_time).total_seconds()
            if current_job_time > 3600:
                plugin_log.log("Job execution killed due to inactivity")
                job_status = 'TIMEOUT'

            completed = connector.is_job_completed(job_status)
            failed = connector.is_job_failed(job_status)

        end_time = datetime.datetime.now()
        total_time = end_time - start_time
        application_time_log.log(
            "%s|%.0f|%.0f" % (spark_app_id,
                              float(time.mktime(start_time.timetuple())),
                              float(total_time.total_seconds())))
        self.application_time = total_time.total_seconds()
        plugin_log.log("%s | Sahara job took %s seconds to execute" %
                (time.strftime("%H:%M:%S"), str(total_time.total_seconds())))

        return job_status

    def _create_cluster(self, sahara, connector, req_cluster_size,
                        pred_cluster_size, public_key, net_id, image_id,
                        plugin, version, master_ng, slave_ng, op_slave_ng):
        plugin_log.log('Creating cluster')
        try:
            cluster_id = connector.create_cluster(sahara, req_cluster_size,
                                                  pred_cluster_size,
                                                  public_key, net_id,
                                                  image_id, plugin,
                                                  version, master_ng,
                                                  slave_ng, op_slave_ng)
        except SaharaAPIException:
            raise SaharaAPIException('Could not create clusters')

        return cluster_id

    def _is_swift_path(self, args):
        for arg in args:
            if arg.startswith('hdfs://') or arg.startswith('swift://'):
                if arg.startswith('swift://'):
                    return True
                else:
                    return False
                  
    def _swift_spark_execution(self, master, key_path, sahara, connector,
                               job_binary_name, job_binary_url, user, password,
                               job_template_name, job_type, plugin,
                               cluster_size, args, main_class, cluster_id,
                               spark_applications_ids, workers_id, app_id,
                               expected_time, plugin_app, collect_period,
                               log_path, swift, container, data):

        # Preparing job
        job_binary_id = self._get_job_binary_id(sahara, connector,
                                                job_binary_name,
                                                job_binary_url, user,
                                                password)

        mains = [job_binary_id]
        job_template_id = self._get_job_template_id(sahara, connector,
                                                    mains,
                                                    job_template_name,
                                                    job_type)

        plugin_log.log("%s | Starting job..." % (time.strftime("%H:%M:%S")))

        # Running job
        configs = os_utils.get_job_config(connector, plugin,
                                          cluster_size, user, password,
                                          args, main_class)

        job = connector.create_job_execution(sahara, job_template_id,
                                             cluster_id,
                                             configs=configs)

        plugin_log.log("%s | Created job" % (time.strftime("%H:%M:%S")))

        spark_app_id = spark.get_running_app(master,
                                             spark_applications_ids)
        spark_applications_ids.append(spark_app_id)

        plugin_log.log("%s | Spark app id" % (time.strftime("%H:%M:%S")))

        job_exec_id = job.id

        for worker_id in workers_id:
            instances_log.log("%s|%s" % (app_id, worker_id))

        job_status = connector.get_job_status(sahara, job_exec_id)

        plugin_log.log("%s | Sahara job status: %s" %
                (time.strftime("%H:%M:%S"), job_status))

        info_plugin = {"spark_submisson_url": "http://" + master,
                       "expected_time": expected_time}

        plugin_log.log("%s | Starting monitor" % (time.strftime("%H:%M:%S")))
        monitor.start_monitor(api.monitor_url, spark_app_id,
                              plugin_app, info_plugin, collect_period)
        plugin_log.log("%s | Starting scaler" % (time.strftime("%H:%M:%S")))
        scaler.start_scaler(api.controller_url, spark_app_id, 
                            workers_id, data)

        job_status = self._wait_on_job_finish(sahara, connector,
                                              job_exec_id, app_id)

        plugin_log.log("%s | Stopping monitor" % (time.strftime("%H:%M:%S")))
        monitor.stop_monitor(api.monitor_url, spark_app_id)
        plugin_log.log("%s | Stopping scaler" % (time.strftime("%H:%M:%S")))
        scaler.stop_scaler(api.controller_url, spark_app_id)

        spark_applications_ids.remove(spark_app_id)

        plugin_log.log("Finished application execution")

        if connector.is_job_completed(job_status):
            self.update_application_state("OK")

        if connector.is_job_failed(job_status):
            self.update_application_state("Error")

        return job_status

    def _hdfs_spark_execution(self, master, remote_hdfs, key_path, args,
                              job_bin_url, main_class, dependencies):
        job_exec_id = str(uuid.uuid4())[0:7]
        plugin_log.log("%s | Job execution ID: %s" %
                (time.strftime("%H:%M:%S"), job_exec_id))

        # Defining params
        local_path = '/tmp/spark-jobs/' + job_exec_id + '/'
        remote_path = 'ubuntu@' + master + ':' + local_path

        job_input_paths, job_output_path, job_params = (
            hdfs.get_job_params(key_path, remote_hdfs, args))

        job_binary_path = hdfs.get_path(job_bin_url)
        
        # Create temporary job directories
        plugin_log.log("%s | Create temporary job directories" %
                (time.strftime("%H:%M:%S")))
        self._mkdir(local_path)

        # Create cluster directories
        plugin_log.log("%s | Creating cluster directories" %
                (time.strftime("%H:%M:%S")))
        remote.execute_command(master, key_path,
                               'mkdir -p %s' % local_path)

        # Get job binary from hdfs
        plugin_log.log("%s | Get job binary from %s" %
                (time.strftime("%H:%M:%S"), job_binary_path))
        remote.copy_from_hdfs(master, key_path, remote_hdfs,
                              job_binary_path, local_path)

        # Submit job
        plugin_log.log("%s | Submit job" % (time.strftime("%H:%M:%S")))
        local_binary_file = (local_path +
                             remote.list_directory(key_path, master, local_path))

        self._submit_job(master, key_path, main_class, dependencies,
                         local_binary_file, args)

        plugin_log.log("Finished application execution")
        self.update_application_state("OK")

        return 'OK'

    def _submit_job(self, remote_instance, key_path, main_class,
                    dependencies, job_binary_file, args):
        args_line = ''
        for arg in args:
            args_line += arg + ' '

        spark_submit = ('/opt/spark/bin/spark-submit '
                        '--packages %(dependencies)s '
                        '--class %(main_class)s '
                        '%(job_binary_file)s %(args)s ' %
                        {'dependencies': dependencies,
                         'main_class': main_class,
                         'job_binary_file': 'file://'+job_binary_file,
                         'args': args_line})

        if main_class == '':
            spark_submit = spark_submit.replace('--class', '')

        if dependencies == '':
            spark_submit = spark_submit.replace('--packages', '')

        remote.execute_command(remote_instance, key_path, spark_submit)

    def _mkdir(self, path):
        subprocess.call('mkdir -p %s' % path, shell=True)


class SaharaProvider(base.PluginInterface):

    def __init__(self):
        self.spark_applications_ids = []
        self.id_generator = ID_Generator()

    def get_title(self):
        return 'OpenStack Sahara'

    def get_description(self):
        return 'Plugin that allows utilization of Sahara to run jobs'

    def to_dict(self):
        return {
            'name': self.name,
            'title': self.get_title(),
            'description': self.get_description(),
        }

    def execute(self, data):
        executor = OpenStackSparkApplicationExecutor()
        app_id = "osspark" + self.id_generator.get_ID()
        handling_thread = threading.Thread(target=executor.start_application,
                                           args=(data,
                                                 self.spark_applications_ids,
                                                 app_id))
        handling_thread.start()
        return (app_id, executor)
