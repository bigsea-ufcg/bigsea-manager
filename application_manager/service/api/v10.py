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

from application_manager.plugins import base as plugin_base
from application_manager.service import api
from application_manager.service.horizontal_scale import r_predictor
from application_manager.utils.logger import Log
from application_manager.utils import authorizer
from application_manager.utils import monasca
from application_manager.utils import shell


LOG = Log("Servicev10", "serviceAPIv10.log")
predictor = r_predictor.RPredictor()
monasca_monitor = monasca.MonascaMonitor()

applications = {}

def execute(data):
    authorization = authorizer.get_authorization(api.authorization_url,
                                                 data['bigsea_username'],
                                                 data['bigsea_password'])
    print authorization
    if not authorization['success']:
        return 'Error: Authentication failed. User not authorized'

    hosts = api.hosts

    _populate_host_utilization_files(hosts)
    pred_cluster_size = _get_new_cluster_size(hosts)

    if pred_cluster_size > data['cluster_size']:
        data['cluster_size'] = pred_cluster_size

    plugin = plugin_base.PLUGINS.get_plugin(data['plugin'])
    app_id, executor = plugin.execute(data)
    applications[app_id] = executor

    return app_id


def stop_app(app_id):
    # stop monitoring
    # stop scaling
    return 'App %{app_id}s stopped' % {'app_id': app_id}


def kill_all():
        return 'Apps killed'


def status():
    applications_status = {} 

    for app_id in applications.keys():
        application_stat = {}
        applications_status[app_id] = application_stat
        application_stat["status"] = applications[app_id].get_application_state() 
        application_stat["time"] = applications[app_id].get_application_execution_time()
        application_stat["start_time"] = applications[app_id].get_application_start_time()

    return applications_status

def _get_new_cluster_size(hosts):
    return predictor.predict(hosts)


def _get_start_time(time_diff):
    now = datetime.datetime.utcnow()
    delta = datetime.timedelta(hours=time_diff)
    return (now - delta).strftime('%Y-%m-%dT%H:%M:%SZ')


def _from_mb_to_gb(size, precision=2):
    size = size/1024.0
    return "%.*f" % (precision, size)


def _get_used_mem(value):
    return (100 - value) / 100.0


def _populate_host_utilization_files(hosts):
    for host in hosts:
        output_file = '%s.txt' % host
        dimensions = {'hostname': host}

        cpu_info = monasca_monitor.get_stats_measurements('cpu.percent',
                                                          dimensions,
                                                          _get_start_time(2))
        mem_info = monasca_monitor.get_stats_measurements('mem.usable_perc',
                                                          dimensions,
                                                          _get_start_time(2))
        total_cpu = monasca_monitor.last_measurement('cpu.total_logical_cores',
                                                     dimensions,
                                                     _get_start_time(1))[1]
        total_mem = _from_mb_to_gb(
            monasca_monitor.last_measurement('mem.total_mb', dimensions,
                                             _get_start_time(1))[1])

        counter = 0
        index = 0
        for i in range(len(cpu_info)):
            if counter % 3 == 0:
                index += 1
            cpu = cpu_info[i][1]/100
            mem = _get_used_mem(mem_info[i][1])

            line = '%s;%s;%s;%s;%s\n' % (cpu, mem, total_cpu, total_mem, index)
            counter += 1

            shell.write_to_file(output_file, line)


if __name__ == "__main__":
    data = {'cluster_size': 3}
    execute(data)
