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
import time
import requests

from application_manager.utils.logger import Log
from application_manager.openstack import connector as os_connector
from application_manager.service.api import controller_url
from application_manager.service.api import monitor_url

LOG = Log("Servicev10", "serviceAPIv10.log")

# def application_started():


def application_started(data):
    cluster_id = data['cluster_id']
    project_id = data['project_id']
    app_id = data['app_id']
    token = data['token']
    connector = os_connector.OpenStackConnector(LOG)
    auth_ip = '0.0.0.0'
    sahara = connector.get_sahara_client(token, project_id, auth_ip)
    is_monitoring = False

    job_status = connector.get_job_status(sahara, app_id)

    LOG.log("%s | Sahara job status: %s" % (time.strftime("%H:%M:%S"),
                                            job_status))

    worker_instances = connector.get_worker_instances(sahara, cluster_id)
    start_scaling_dict = {
        'expected_time': 1000,
        'instances': worker_instances
    }
    start_scaling_body = json.dumps(start_scaling_dict)
    start_scaling_url = controller_url + '/start_scaling/' + app_id

    completed = failed = False
    start_time = datetime.now()
    while not (completed or failed):
        job_status = connector.get_job_status(sahara, app_id)
        LOG.log("%s | Sahara current job status: %s" % (time.strftime(
            "%H:%M:%S"), job_status))
        if job_status == 'RUNNING' and not is_monitoring:
            is_monitoring = True

            # monitoring

            # controller
            requests.post(start_scaling_url, data=start_scaling_body)

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
    return job_status, total_time.total_seconds()

    # return conductor.application_started()


def application_stopped(app_id, **kwargs):
    # stop monitoring
    stop_monitor_url = monitor_url + '/stop_monitor/' + app_id
    requests.post(stop_monitor_url)
    # stop scaling
    stop_scaling_url = controller_url + '/stop_scaling/' + app_id
    requests.post(stop_scaling_url)
