
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


def _get_authorization_data(data):
    authorization_body = json.dumps(data)
    return authorization_body


def get_authorization(optimizer_url, data):
    request_url = optimizer_url + '/run_application/'
    headers = {'Content-type': 'application/json'}
    data = _get_authorization_data(data)
    return requests.post(request_url, data=data, headers=headers)