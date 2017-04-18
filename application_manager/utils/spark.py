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

import requests


def get_running_app(self, submission_url):
    try:
        all_app = requests.get(self.submission_url +
                               ':8080/api/v1/applications?status=running')
        for app in all_app.json():
            if app['attempts'][0]['completed'] == False:
                return app['id'], app['name']
        return None
    except:
        self.logger.log("No application found")
        return None

