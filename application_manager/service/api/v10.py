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

from datetime import datetime
import json
import requests
import time

from application_manager import exceptions as ex
from application_manager.openstack import connector as os_connector
from application_manager.openstack import utils as os_utils
from application_manager.service import api
from application_manager.service.horizontal_scale import r_predictor
from application_manager.utils import spark
from application_manager.utils.logger import Log

from saharaclient.api.base import APIException as SaharaAPIException


LOG = Log("Servicev10", "serviceAPIv10.log")
predictor = r_predictor.RPredictor()


def execute(data):
    project_id = api.project_id
    auth_ip = api.auth_ip
    user = api.user
    password = api.password
    domain = api.domain
    public_key = api.public_key
    net_id = api.net_id
    image_id = api.image_id
    hosts = api.hosts
    monitor_url = api.monitor_url
    controller_url = api.controller_url
    master_ng = api.master_ng
    slave_ng = api.slave_ng

    plugin = data['plugin']
    job_type = data['job_type']
    version = data['version']
    cluster_id = data['cluster_id']
    opportunistic = data['opportunistic']
    req_cluster_size = data['cluster_size']
    args = data['args']
    main_class = data['main_class']
    job_template_name = data['job_template_name']
    job_binary_name = data['job_binary_name']
    job_binary_url = data['job_binary_url']
    input_ds_id = data['input_datasource_id']
    output_ds_id = data['output_datasource_id']
    plugin_app = data['plugin_app']
    expected_time = data['expected_time']
    collect_period = data['collect_period']

    ### SCALER PARAMETERS ###
    scaler_plugin = data['scaler_plugin']
    actuator = data['actuator']
    print "Debug caliente"
    metric_source = data['metric_source']
    # workers = data['workers']
    check_interval = data['check_interval']
    trigger_down = data['trigger_down']
    trigger_up = data['trigger_up']
    min_cap = data['min_cap']
    max_cap = data['max_cap']
    actuation_size = data['actuation_size']
    metric_rounding = data['metric_rounding']

    # args = [input_ds_id, output_ds_id]

    connector = os_connector.OpenStackConnector(LOG)

    sahara = connector.get_sahara_client(user, password, project_id, auth_ip,
                                         domain)

    # monitor.get_host_cpu_utilization()

    cluster_size = int(req_cluster_size)
    #cluster_size = _get_new_cluster_size(hosts)

    cluster_id = connector.get_existing_cluster_by_size(sahara, cluster_size)

    if not cluster_id:
        if opportunistic:
            LOG.log('Runnning job with opportunistic cluster')
            cluster_delete = True
            #cluster_size = connector.get_new_cluster_size(hosts)
            try:
                cluster_id = connector.create_cluster(sahara, cluster_size,
                                                      public_key, net_id,
                                                      image_id, plugin,
                                                      version, master_ng,
                                                      slave_ng)
            except SaharaAPIException as e:
                raise SaharaAPIException('Could not create clusters')

        else:
            LOG.log('Runnning job with non opportunistic cluster')
            cluster_id = connector.create_cluster(sahara, cluster_size,
                                                  public_key, net_id, image_id,
                                                  plugin, version, master_ng,
                                                  slave_ng)
    if cluster_id:
        master = connector.get_master_instance(sahara,
                                               cluster_id)['internal_ip']
        LOG.log("%s | Master is: %s" % (time.strftime("%H:%M:%S"), master))

        is_monitoring = False

        configs = os_utils.get_job_config(connector, plugin, cluster_size,
                                          user, password, args, main_class)

        workers = connector.get_worker_instances(sahara, cluster_id)
        workers_id = []
        #
        for worker in workers:
            workers_id.append(worker['instance_id'])
            # host_ips[worker_id] = connector.get_worker_host_ip(worker_id)

        extra = dict(user=user, password=password)
        job_binary_id = connector.get_job_binary(sahara, job_binary_url)

        if not job_binary_id:
            job_binary_id = connector.create_job_binary(sahara, job_binary_name,
                                                        job_binary_url, extra)

        mains = [job_binary_id]

        job_template_id = connector.get_job_template(sahara, mains)
        if not job_template_id:
            job_template_id = connector.create_job_template(sahara,
                                                            job_template_name,
                                                            job_type, mains)

        job = connector.create_job_execution(sahara, job_template_id,
                                             cluster_id, configs=configs)

        spark_app_id = spark.get_running_app(master)
        job_exec_id = job.id
        job_status = connector.get_job_status(sahara, job_exec_id)

        LOG.log("%s | Sahara job status: %s" %
                (time.strftime("%H:%M:%S"), job_status))

        info_plugin = {"spark_submisson_url": "http://" + master,
                       "expected_time": expected_time}

        try:
            _start_monitor(spark_app_id, plugin_app, info_plugin, collect_period)
            _start_scaler(spark_app_id, scaler_plugin, actuator, metric_source, workers_id, check_interval,
                          trigger_down, trigger_up, min_cap, max_cap, actuation_size, metric_rounding)
        except Exception as e:
            print e.message
        #start_scaling_url, start_scaling_body = _get_scaling_data(
        #    controller_url, app_id, worker_instances)
        #start_monitor_url, start_monitor_body = _get_monitor_data(
        #    monitor_url, app_id, worker_instances)

        is_monitoring = False
        completed = failed = False
        start_time = datetime.now()
        while not (completed or failed):
            job_status = connector.get_job_status(sahara, job_exec_id)
            LOG.log("%s | Sahara current job status: %s" %
                    (time.strftime("%H:%M:%S"), job_status))
            if job_status == 'RUNNING' and not is_monitoring:
                is_monitoring = True

                # monitoring
                #requests.post(start_monitor_url, data=start_monitor_body)

                # controller
                #requests.post(start_scaling_url, data=start_scaling_body)

                time.sleep(10)

            current_time = datetime.now()
            current_job_time = (current_time - start_time).total_seconds()
            if current_job_time > 3600:
                LOG.log("Job execution killed due to inactivity")
                job_status = 'TIMEOUT'

            completed = connector.is_job_completed(job_status)
            failed = connector.is_job_failed(job_status)

        end_time = datetime.now()
        total_time = end_time - start_time
        LOG.log("%s | Sahara job took %s seconds to execute" %
                (time.strftime("%H:%M:%S"), str(total_time.total_seconds())))

        #_stop_monitoring(monitor_url, spark_app_id)
        #_stop_scaling(controller_url, spark_app_id)
    else:
        raise ex.ClusterNotCreatedException()

    #if cluster_delete:
        #print "Deleting cluster"
        # delete_cluster(saharaclient, cluster_id)
        # decrease_project_quota(novaclient, project_id, increase_dict)

    return job_status


def stop_app(app_id):
    # stop monitoring
    # stop scaling
    return 'ok'


def kill_all():
    return 'ok'


def _get_new_cluster_size(hosts):
    return predictor.predict(hosts)


def _get_scaler_data(scaler_plugin, actuator, metric_source, workers, check_interval,
                     trigger_down, trigger_up, min_cap, max_cap, actuation_size, metric_rounding):
    start_scaling_dict = {
        'plugin': scaler_plugin,
        'actuator': actuator,
        'metric_source': metric_source,
        'instances': workers,
        'check_interval': check_interval,
        'trigger_down': trigger_down,
        'trigger_up': trigger_up,
        'min_cap': min_cap,
        'max_cap': max_cap,
        'actuation_size': actuation_size,
        'metric_rounding': metric_rounding
    }
    start_scaler_body = json.dumps(start_scaling_dict)

    return start_scaler_body


def _get_monitor_data(plugin, info_plugin, collect_period):
    start_monitor_dict = {
        'plugin': plugin,
        'info_plugin': info_plugin,
        'collect_period': collect_period
    }
    start_monitor_body = json.dumps(start_monitor_dict)

    return start_monitor_body


def _start_monitor(app_id, plugin, info_plugin, collect_period):
    request_url = api.monitor_url + '/start/' + app_id
    headers = {'Content-type': 'application/json'}
    data = _get_monitor_data(plugin, info_plugin, collect_period)
    requests.post(request_url, data=data, headers=headers)


def _stop_monitoring(app_id):
    request_url = api.monitor_url + '/start/' + app_id
    headers = {'Content-type': 'application/json'}
    requests.post(request_url, headers=headers)


def _start_scaler(app_id, scaler_plugin, actuator, metric_source, workers, check_interval,
                  trigger_down, trigger_up, min_cap, max_cap, actuation_size, metric_rounding):
    request_url = api.controller_url + '/scaler/start_scaling/' + app_id
    headers = {'Content-type': 'application/json'}
    data = _get_scaler_data(scaler_plugin, actuator, metric_source, workers, check_interval,
                            trigger_down, trigger_up, min_cap, max_cap, actuation_size, metric_rounding)
    requests.post(request_url, data=data, headers=headers)

def _stop_scaler(controller_url, app_id):
    stop_scaling_url = controller_url + '/scaler/stop_scaling/' + app_id
    requests.post(stop_scaling_url)

