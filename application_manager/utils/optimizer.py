
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


def _get_optimizer_data(application_type, flavor, cluster_size):
    start_monitor_dict = {
        'application_type': application_type,
        'flavor': flavor,
        'cluster_size': cluster_size
    }
    start_monitor_body = json.dumps(start_monitor_dict)

    return start_monitor_body


def get_initial_size(optimizer_url, application_type, flavor, cluster_size):
    request_url = optimizer_url + '/initial_cluster_size/'
    headers = {'Content-type': 'application/json'}
    data = _get_optimizer_data(application_type, flavor, cluster_size)
    request = requests.post(request_url, data=data, headers=headers)
    data = request.json()

    return data['initial_size']

