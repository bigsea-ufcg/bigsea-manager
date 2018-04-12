# Copyright (c) 2017 UPV-GryCAP & UFCG-LSD.
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
import subprocess
import redis
import threading
import time
import uuid

from application_manager.plugins.base import GenericApplicationExecutor
from application_manager.plugins import base
from application_manager.utils.ids import ID_Generator
from application_manager.utils.logger import Log
from application_manager.utils import k8s
from application_manager.service import api

LOG = Log("ChronosPlugin", "logs/chronos_plugin.log")
application_time_log = Log("Application_time", "logs/application_time.log")


class KubeJobsExecutor(GenericApplicationExecutor):

    def __init__(self, app_id):
        self.id = ID_Generator().get_ID()
        self.app_id = app_id

    def start_application(self, data):
        try:

            # Download files that contains the items
            dwnld_cmd = 'wget %s -O %s' % (data['redis_file'],
                                           api.redis_workload_path)

            subprocess.call(dwnld_cmd, shell=True)
            redis_file = open(api.redis_workload_path, "r").read()
            jobs = redis_file.split('\n')

            rds = redis.StrictRedis(host=api.redis_ip,
                                    port=api.redis_port)
            queue_size = len(jobs)

            print "Creating Redis queue"
            for job in jobs:
                rds.rpush("job", job)

            print "Creating Job"
            k8s.create_job(self.app_id, data['env_name'],
                           data['env_value'], data['args'],
                           data['cmd'], data['img'],
                           data['working_dir'], data['init_size'])

            jobs_completed = requests.get(api.count_queue).json()

            while jobs_completed < queue_size:
                jobs_completed = requests.get(api.count_queue).json()

        except Exception as ex:
            print "ERROR: %s" % ex


class KubeJobsProvider(base.PluginInterface):

    def __init__(self):
        self.id_generator = ID_Generator()

    def get_title(self):
        return 'Kubernetes Batch Jobs Plugin'

    def get_description(self):
        return 'Plugin that allows utilization of Batch Jobs over a k8s cluster'

    def to_dict(self):
        return {
            'name': self.name,
            'title': self.get_title(),
            'description': self.get_description(),
        }

    def execute(self, data):
        app_id = 'kj-' + str(uuid.uuid4())[0:7]
        executor = KubeJobsExecutor(app_id)

        handling_thread = threading.Thread(target=executor.start_application,
                                           args=(data,))
        handling_thread.start()
        return app_id, executor

