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

from application_manager.plugins import base as plugin_base
from application_manager.service import api
from application_manager.utils.logger import Log
from application_manager.utils import authorizer
from application_manager.utils import optimizer

LOG = Log("Servicev10", "serviceAPIv10.log")

applications = {}


def execute(data):
#    authorization = authorizer.get_authorization(api.authorization_url,
#                                                 data['bigsea_username'],
#                                                 data['bigsea_password'])
#    if not authorization['success']:
#        return 'Error: Authentication failed. User not authorized'
#

    plugin = plugin_base.PLUGINS.get_plugin(data['plugin'])
    app_id, executor = plugin.execute(data)
    applications[app_id] = executor

    return app_id


def stop_app(app_id):
    # stop monitoring
    # stop scaling
    return 'App %(app_id)s stopped' % {'app_id': app_id}


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
    return optimizer.get_cluster_size(api.optimizer_url, hosts)


if __name__ == "__main__":
    data = {'cluster_size': 3}
    execute(data)
