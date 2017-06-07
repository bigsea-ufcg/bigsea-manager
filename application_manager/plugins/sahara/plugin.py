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
import time

from application_manager import exceptions as ex
from application_manager.openstack import connector as os_connector
from application_manager.openstack import utils as os_utils
from application_manager.plugins import base
from application_manager.service import api
from application_manager.utils import monitor
from application_manager.utils import optimizer
from application_manager.utils import scaler
from application_manager.utils import spark
from application_manager.utils.logger import Log

from saharaclient.api.base import APIException as SaharaAPIException

LOG = Log("SaharaPlugin", "sahara_plugin.log")


class SaharaProvider(base.PluginInterface):

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
        user = api.user
        password = api.password
        project_id = api.project_id
        auth_ip = api.auth_ip
        domain = api.domain
        public_key = api.public_key

        net_id = data['net_id']
        master_ng = data['master_ng']
        slave_ng = data['slave_ng']

        plugin = data['openstack_plugin']
        job_type = data['job_type']
        version = data['version']
        # cluster_id = data['cluster_id']
        opportunistic = data['opportunistic']
        req_cluster_size = data['cluster_size']
        args = data['args']
        main_class = data['main_class']
        job_template_name = data['job_template_name']
        job_binary_name = data['job_binary_name']
        job_binary_url = data['job_binary_url']
        # input_ds_id = data['input_datasource_id']
        # output_ds_id = data['output_datasource_id']
        plugin_app = data['plugin']
        expected_time = data['expected_time']
        collect_period = data['collect_period']
        image_id = data['image_id']

        #### SCALER PARAMETERS ###
        scaler_plugin = data['scaler_plugin']
        actuator = data['actuator']
        metric_source = data['metric_source']
        # workers = data['workers']
        check_interval = data['check_interval']
        trigger_down = data['trigger_down']
        trigger_up = data['trigger_up']
        min_cap = data['min_cap']
        max_cap = data['max_cap']
        actuation_size = data['actuation_size']
        metric_rounding = data['metric_rounding']

        connector = os_connector.OpenStackConnector(LOG)

        sahara = connector.get_sahara_client(user, password, project_id,
                                             auth_ip, domain)

        # Cluster Creation
        tmp_flavor = 'large.m1'
        # monitor.get_host_cpu_utilization()
        cluster_size = optimizer.get_initial_size(api.optimizer_url,
                                                  plugin_app,
                                                  tmp_flavor,
                                                  req_cluster_size)

        # cluster_size = int(req_cluster_size)
        # cluster_size = _get_new_cluster_size(hosts)ah
        cluster_id = connector.get_existing_cluster_by_size(sahara,
                                                            cluster_size)

        if not cluster_id:

            cluster_id = self._create_cluster(sahara, connector,  opportunistic,
                                              cluster_size, public_key, net_id,
                                              image_id, plugin, version,
                                              master_ng, slave_ng)

        if cluster_id:
            master = connector.get_master_instance(sahara,
                                                   cluster_id)['internal_ip']
            LOG.log("%s | Master is: %s" % (time.strftime("%H:%M:%S"), master))

            configs = os_utils.get_job_config(connector, plugin, cluster_size,
                                              user, password, args, main_class)

            workers = connector.get_worker_instances(sahara, cluster_id)
            workers_id = []
            for worker in workers:
                workers_id.append(worker['instance_id'])

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

            # Running job
            job = connector.create_job_execution(sahara, job_template_id,
                                                 cluster_id, configs=configs)

            spark_app_id = spark.get_running_app(master)
            job_exec_id = job.id
            job_status = connector.get_job_status(sahara, job_exec_id)

            LOG.log("%s | Sahara job status: %s" %
                    (time.strftime("%H:%M:%S"), job_status))

            info_plugin = {"spark_submisson_url": "http://" + master,
                           "expected_time": expected_time}

            monitor.start_monitor(api.monitor_url, spark_app_id, plugin_app,
                                  info_plugin, collect_period)
            # scaler.start_scaler(api.controller_url, spark_app_id,
            #                     scaler_plugin, actuator, metric_source,
            #                     workers_id, check_interval, trigger_down,
            #                     trigger_up, min_cap, max_cap,
            #                     actuation_size, metric_rounding)

            job_status = self._wait_on_job_finish(sahara, connector,
                                                  job_exec_id)
        else:
            raise ex.ClusterNotCreatedException()

        return job_status

    def _get_job_binary_id(self, sahara, connector, job_binary_name,
                           job_binary_url, user, password):
        extra = dict(user=user, password=password)
        job_binary_id = connector.get_job_binary(sahara, job_binary_url)

        if not job_binary_id:
            job_binary_id = connector.create_job_binary(sahara, job_binary_name,
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

    def _wait_on_job_finish(self, sahara, connector, job_exec_id):
        completed = failed = False
        start_time = datetime.datetime.now()
        while not (completed or failed):
            job_status = connector.get_job_status(sahara, job_exec_id)
            LOG.log("%s | Sahara current job status: %s" %
                    (time.strftime("%H:%M:%S"), job_status))
            if job_status == 'RUNNING':
                time.sleep(10)

            current_time = datetime.datetime.now()
            current_job_time = (current_time - start_time).total_seconds()
            if current_job_time > 3600:
                LOG.log("Job execution killed due to inactivity")
                job_status = 'TIMEOUT'

            completed = connector.is_job_completed(job_status)
            failed = connector.is_job_failed(job_status)

        end_time = datetime.datetime.now()
        total_time = end_time - start_time
        LOG.log("%s | Sahara job took %s seconds to execute" %
                (time.strftime("%H:%M:%S"), str(total_time.total_seconds())))

        return job_status

    def _create_cluster(self, sahara, connector,  opportunistic, cluster_size,
                        public_key, net_id, image_id, plugin, version,
                        master_ng, slave_ng):

        if opportunistic:
            LOG.log('Runnning job with opportunistic cluster')
            try:
                cluster_id = connector.create_cluster(sahara, cluster_size,
                                                      public_key, net_id,
                                                      image_id, plugin,
                                                      version, master_ng,
                                                      slave_ng)
            except SaharaAPIException:
                raise SaharaAPIException('Could not create clusters')

        else:
            try:

                LOG.log('Runnning job with non opportunistic cluster')
                cluster_id = connector.create_cluster(sahara, cluster_size,
                                                      public_key, net_id, image_id,
                                                      plugin, version, master_ng,
                                                      slave_ng)
            except Exception as e:
                print e.message

        return cluster_id

