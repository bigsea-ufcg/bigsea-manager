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
from application_manager.service.horizontal_scale import r_predictor
from application_manager.utils.logger import Log
from application_manager.utils import authorizer


LOG = Log("Servicev10", "serviceAPIv10.log")
predictor = r_predictor.RPredictor()

applications = {}

def execute(data):
    authorization = authorizer.get_authorization(api.authorization_url, data)
    if authorization.status_code == 401:
        return 'Not authorized'

    plugin = plugin_base.PLUGINS.get_plugin(data['plugin'])
    app_id, executor = plugin.execute(data)
    applications[app_id] = executor

    return app_id

def stop_app(app_id):
    # stop monitoring
    # stop scaling
    return 'ok'


def kill_all():
    return 'ok'

def status():
    application_status = {} 
    
    for app_id in applications.keys():
        stat = applications[app_id].get_application_state()
        application_status[app_id] = stat
    
    return application_status


def _get_new_cluster_size(hosts):
    return predictor.predict(hosts)

