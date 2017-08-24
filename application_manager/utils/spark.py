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
import time
from application_manager.utils import swift
from application_manager.utils import remote
import os

def get_running_app(submission_url, applications):
    app_id = None
    while app_id is None:
        try:
            all_app = requests.get('http://' + submission_url +
                                   ':4040/api/v1/applications?status=running')
            for app in all_app.json():
                if app['attempts'][0]['completed'] == False:
                    if app['id'] not in applications:
                        print app['id']
                        return app['id']#, app['name']
        except:
            # self.logger.log("No application found")
            pass
            # return None

def submit_job(key, hdfs_path, master, main_class,
                job_binary_file, args):
    param = ''
    for arg in args:
        if arg.startswith('swift://'):
            path = swift.get_path(arg)

            param += ('hdfs://%(master)s%(hdfs_path)s/%(path)s ' %
                      {'master': master,
                       'hdfs_path': hdfs_path,
                       'path': path})
        else:
            param += arg + ' '

    spark_submit = ('/opt/spark/bin/spark-submit --class %(main_class)s '
                    '%(job_binary_file)s %(param)s ' %
                    {'main_class': main_class,
                     'job_binary_file': job_binary_file, 'param': param})

    remote.execute_command(key, master, spark_submit)

