# Copyright (c) 2017 UFCG-LSD and UPV-GRyCAP.
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
from urllib3 import response

from application_manager.plugins import base
from application_manager.service import api

import paramiko
import requests

class SparkMesosProvider(base.PluginInterface):

    def get_title(self):
        return 'Spark-Mesos plugin '

    def get_description(self):
        return 'It runs an spark application on a Mesos cluster'

    def to_dict(self):
        return {
            'name': self.name,
            'title': self.get_title(),
            'description': self.get_description(),
        }

    def execute(self, data):
        # TODO: Read data from request dict
        # mesos_url = api.mesos_url
        # cluster_username = api.cluster_username
        # cluster_password = api.cluster_password
        # supervisor_url = api.supervisor_url
        # one_url = api.one_url
        # one_username = api.one_username
        # one_password = api.one_password

        binary_url = data['binary_url']
        execution_class = data['execution_class']
        execution_parameters = data['execution_parameters']
        app_id = ''

        # TODO: Creates a connection ssh with Mesos cluster
        conn = self._get_ssh_connection(api.mesos_url,
                                        api.cluster_username,
                                        api.cluster_password,
                                        api.cluster_key_path)

        # TODO: Discovery ips of the executors from Mesos
        get_frameworks_url = "%s:%s" % (api.mesos_url, api.mesos_port)
        response = requests.get(get_frameworks_url).json()

        cluster_ips = []
        for t in response['framework'][0]['tasks']:
            for s in t['statuses']:
                for n in s['container_status']['network_infos']:
                    for i in n['ip_addresses']:
                        cluster_ips.append(i['ip_address'])

        # TODO: Discovery the ids on KVM using the ips
        conn.exec_command('')

        # TODO: Download the binary from a public link
        stdi, stdo, stdr = conn.exec_command('wget %s > /tmp/exec_bin.jar') \
                           % binary_url
        binary_path = stdo.read()
        # TODO: execute all the spark needed commands
        # to run an spark job from command line
        conn.exec_command('%s{sparkpath} --name %s ' +
                          '--executor-memory 512M ' +
                          '--num-executors 1 ' +
                          '--master mesos://%s:%s ' +
                          '--class %s %s %s') % (api.spark_path,
                                                 app_id,
                                                 api.mesos_url,
                                                 api.mesos_port,
                                                 binary_path,
                                                 execution_class,
                                                 execution_parameters)

        # TODO: start monitor service
        # TODO: start controller service
        # TODO: stop monitor
        # TODO: stop controller
        # TODO: remove binary
        conn.exec_command('rm -f /tmp/exec_bin.jar')
        return True

    def _get_ssh_connection(self, ip, username=None,
                            password=None, key_path=None):
        # Preparing SSH connection
        keypair = paramiko.RSAKey.from_private_key_file(key_path)
        conn = paramiko.SSHClient()
        conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # Checking if the connection will be established using
        # keys or passwords
        if key_path != "" and key_path is not None:
            conn.connect(hostname=ip, username=username, pkey=keypair)
        else:
            conn.connect(hostname=ip, username=username, password=password)

        return conn
