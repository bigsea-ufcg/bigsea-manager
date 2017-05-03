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


LOG = Log("Servicev10", "serviceAPIv10.log")
predictor = r_predictor.RPredictor()


def execute(data):
    project_id = api.project_id
    auth_ip = api.auth_ip
    user = api.user
    password = api.password
    domain = api.domain
    public_key = api.public_key
    #TODO it must be optional. These informations are necessary only when
    # sahara plugin is loaded. Maybe the informations below also are necessary
    # only for specific plugins and this should be considered too.

    net_id = api.net_id
    hosts = api.hosts
    master_ng = api.master_ng
    slave_ng = api.slave_ng
    
    plugin = plugin_base.PLUGINS.get_plugin(data['plugin'])
    plugin.execute(data)

    return 'ok'

def stop_app(app_id):
    # stop monitoring
    # stop scaling
    return 'ok'


def kill_all():
    return 'ok'


def _get_new_cluster_size(hosts):
    return predictor.predict(hosts)

