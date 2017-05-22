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
import json
import requests

def _get_scaler_data(scaler_plugin, workers, scaling_parameters):
    scaling_parameters["instances"] = workers
    start_scaling_dict = {
        'plugin': scaler_plugin,
        'scaling_parameters': scaling_parameters
    }
    start_scaler_body = json.dumps(start_scaling_dict)

    return start_scaler_body    

def start_scaler(controller_url, app_id, scaler_plugin, workers, scaling_parameters):
    request_url = controller_url + '/scaler/start_scaling/' + app_id
    headers = {'Content-type': 'application/json'}
    data = _get_scaler_data(scaler_plugin, workers, scaling_parameters)
    requests.post(request_url, data=data, headers=headers)

def stop_scaler(controller_url, app_id):
    stop_scaling_url = controller_url + '/scaler/stop_scaling/' + app_id
    headers = {'Content-type': 'application/json'}
    requests.post(stop_scaling_url, headers=headers)
