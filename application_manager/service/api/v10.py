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

LOG = Log("Servicev10", "logs/serviceAPIv10.log")

applications = {}


def execute(data):
    username = data['authorizer']['username']
    password = data['authorizer']['password']

    authorization = authorizer.get_authorization(api.authorization_url,
                                                 username,
                                                 password)
    if not authorization['success']:
        return 'Error: Authentication failed. User not authorized'

    plugin = plugin_base.PLUGINS.get_plugin(data['broker']['plugin'])
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
        application_stat["status"] = (applications[app_id].
                                      get_application_state())

        application_stat["time"] = (applications[app_id].
                                    get_application_execution_time())

        application_stat["start_time"] = (applications[app_id].
                                          get_application_start_time())
    
    return applications_status

def execution_log(app_id):
    if app_id not in applications:
        return "App %(app_id)s doesn't exist" % {'app_id': app_id} 

    log = open("logs/apps/%s/execution" % app_id, "r")
    str_log = map(_remove_newline, log.readlines())
    
    log.close()

    return str_log

def std_log(app_id):
    if app_id not in applications:
        return "App %(app_id)s doesn't exist" % {'app_id': app_id}

    stderr = open("logs/apps/%s/stderr" % app_id, "r")
    stdout = open("logs/apps/%s/stdout" % app_id, "r")

    err = stderr.read()
    out = stdout.read()

    stderr.close()
    stdout.close()

    return out, err

def _get_new_cluster_size(hosts):
    return optimizer.get_cluster_size(api.optimizer_url, hosts)

def _remove_newline(string):
    return string.replace("\n", "")


if __name__ == "__main__":
    data = {'cluster_size': 3}
    execute(data)
