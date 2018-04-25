# Copyright (c) 2017 LSD - UFCG.
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

from broker.utils import api as u
from broker.service.api import v10 as api


rest = u.Rest('v10', __name__)


@rest.post('/submit')
def submit(data):
    return u.render(api.submit(data)) 


@rest.post('/stop')
def stop(data):
    return u.render(api.stop(data))


@rest.get('/submissions')
def submissions():
    return u.render(api.submissions())


@rest.get('/submissions/<id>')
def submission():
    return u.render(api.submission())


@rest.post('/log/submission/<id>')
def log_submission(data):
    return u.render(api.log_submission(data))


@rest.post('/log/execution/<id>')
def log_execution(data):
    return u.render(api.log_execution(data))


#-------------

@rest.post('/manager/execute')
def execute(data):
    return u.render(api.execute(data))

@rest.post('/manager/stop_app/<app_id>')
def stop_app(app_id, data):
    api.stop_app(app_id)
    return u.render()

@rest.post('/manager/kill_all')
def kill_all(data):
    api.kill_all()
    return u.render()

@rest.get('/manager/status')
def status():
    return u.render(api.status())

@rest.get('/manager/logs/execution/<app_id>')
def execution_log(app_id):
    return u.render(api.execution_log(app_id))

@rest.get('/manager/logs/std/<app_id>')
def std_log(app_id):
    return u.render(api.std_log(app_id))
