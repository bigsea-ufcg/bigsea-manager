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


def _get_scaler_data(workers, data):
    data["scaling_parameters"]["instances"] = workers
    start_scaler_body = json.dumps(data)
    return start_scaler_body    

def start_scaler(controller_url, app_id, workers, data):
    request_url = controller_url + '/controller/start_scaling/' + app_id
    headers = {'Content-type': 'application/json'}
    data = _get_scaler_data(workers, data)
    requests.post(request_url, data=data, headers=headers)

def start_scaler(controller_url, app_id, data):
    request_url = controller_url + '/controller/start_scaling/' + app_id
    headers = {'Content-type': 'application/json'}
    data.update({"app_id": app_id})
    data = json.dumps(data)
    requests.post(request_url, data=data, headers=headers)


def stop_scaler(controller_url, app_id):
    stop_scaling_url = controller_url + '/controller/stop_scaling/' + app_id
    headers = {'Content-type': 'application/json'}
    requests.post(stop_scaling_url, headers=headers)

def _get_setup_environment_data(instances, cap, data):
    instances_cap = {}
    
    for instance in instances:
        instances_cap[instance] = cap    
    
    data["instances_cap"] = instances_cap
    
    return json.dumps(data)


def setup_environment(controller_url, instances, cap, data):
    setup_enviroment_url = controller_url + '/controller/setup_env'
    headers = {'Content-type': 'application/json'}
    data = _get_setup_environment_data(instances, cap, data)
    requests.post(setup_enviroment_url, data=data, headers=headers)

