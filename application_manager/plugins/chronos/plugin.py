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

import time
import json
import requests

from application_manager.utils.ManagerChronos import ManagerChronos
from application_manager.plugins.base import GenericApplicationExecutor
from application_manager.plugins import base
from application_manager.utils.ids import ID_Generator
from application_manager.utils.logger import Log
from application_manager.service import api


LOG = Log("ChronosPlugin", "chronos_plugin.log")
application_time_log = Log("Application_time", "application_time.log")

class ChronosApplicationExecutor(GenericApplicationExecutor):

    def __init__(self):
        self.id = ID_Generator().get_ID()

    def start_application(self, data):
        try:
            self.update_application_state("Running")
            
            # Credentials of framework
            url = api.chronos_url
            user = api.chronos_username
            password = api.chronos_password
            supervisor_url = api.supervisor_url

            chronos = ManagerChronos(url, user, password)

            # Obtain arguments 
            start_job = time.time()
            job = data['info_plugin']['job']            
            deadline = data['info_plugin']['qos']['deadline'] + start_job 
            job_duration = data['info_plugin']['qos']['duration'] # seconds
            desv_deadline = data['info_plugin']['qos']['desv_deadline'] # %/100 (e.g 5% --> desv_deadline=0.05 )
            jobname = job['name'] 

            # For supervisor
            payload = {
                'framework': 'chronos',
                'name': jobname,
                'job_duration': job_duration,
                'deadline': deadline,
                'desv_deadline': desv_deadline,
                'uuid': self.id,
                'iterations': int( job['schedule'].split('/')[0][1:] )
            }   

            job = self.modify_job(supervisor_url, jobname, job)
            if ( chronos.sendJob(job) ):
                self.init_webhook(supervisor_url, payload)
                print('Launch completed with UUID: '+ self.id)
            else:
                print('ERROR: Launch not completed')
        except:
            print "ERROR: run, forest, run!"
    
    def modify_job(self, api_rest_ip, jobname, job):
        updateCommand_1 = "startedAt=$(date +%s); "
        updateCommand_2 = ("; /usr/bin/curl -H 'Content-type: application/json' -X POST " +
                           api_rest_ip +
                           "/updateTask -d '"
                           "{\"name\": \"" +
                           jobname +
                           "\", \"finished_at\": "
                           "\"'$(date +%s)'\", " +
                           "\"started_at\": \""
                           "'$(echo $startedAt)'\", " +
                           "\"hostname\": " +
                           "\"'$(hostname)'\", "
                           "\"uuid\": \"" +
                           self.id + "\"}'")
        job['command'] = updateCommand_1 + job['command'] + updateCommand_2
        job['schedule'] = 'R//' + job['schedule'].split('/')[2] 
        return job

    def init_webhook(self, url_webhook, payload ):
        head = { 'Content-type':'application/json'}
        print head
        url = url_webhook+'/initTask'
        msg = json.dumps(payload)
        response = requests.post(url, headers=head, data=msg)
        print "Response " + str(response)




class ChronosGenericProvider(base.PluginInterface):

    def __init__(self):
        self.id_generator = ID_Generator()

    def get_title(self):
        return 'Chronos Plugin'

    def get_description(self):
        return 'Plugin that allows utilization of Chronos for run jobs on Apache Mesos'

    def to_dict(self):
        return {
            'name': self.name,
            'title': self.get_title(),
            'description': self.get_description(),
        }

    def execute(self, data):
        executor = ChronosApplicationExecutor()
        executor.start_application(data)
        app_id = "chronosjob" + executor.id
        return (app_id, executor)

