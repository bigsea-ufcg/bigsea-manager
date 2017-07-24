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
from application_manager.utils import monitor
from application_manager.utils import scaler

from uuid import uuid4

import paramiko
import requests
import time


class SparkMesosProvider(base.PluginInterface):

    def __init__(self):
        self.get_frameworks_url = "%s:%s" % (api.mesos_url,
                                             api.mesos_port)
        self.app_id = app_id = "app-one-spark-mesos-"+str(uuid4())[:8]


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
        starting_cap = data['starting_cap']
        actuator = data['actuator']

        # TODO: Creates a connection ssh with Mesos cluster
        conn = self._get_ssh_connection(api.mesos_url,
                                        api.cluster_username,
                                        api.cluster_password,
                                        api.cluster_key_path)

        # TODO: Discovery the ids on KVM using the ips
        conn.exec_command('')

        # TODO: Download the binary from a public link
        stdi, stdo, stdr = conn.exec_command('wget %s > /tmp/exec_bin.jar') \
                           % binary_url

        binary_path = stdo.read()
        # TODO: execute all the spark needed commands
        # TODO: to run an spark job from command line
        conn.exec_command('%s --name %s ' +
                          '--executor-memory 512M ' +
                          '--num-executors 1 ' +
                          '--master mesos://%s:%s ' +
                          '--class %s %s %s') % (api.spark_path,
                                                 self.app_id,
                                                 api.mesos_url,
                                                 api.mesos_port,
                                                 binary_path,
                                                 execution_class,
                                                 execution_parameters)

        # TODO: It have to ensure that the application was
        # TODO: started before try to get the executors

        # TODO: Discovery ips of the executors from Mesos
        executors = self._get_executors_ip()


        # TODO: set up the initial configuration of cpu cap
        scaler.setup_environment(api.controller_url, executors[0],
                                 starting_cap, actuator)

        # TODO: start monitor service
        self._start_monitoring(executors[1], data)

        # TODO: start controller service
        self._start_controller(executors[0], data)

        # TODO: stop monitor
        # monitor.stop_monitor(api.monitor_url, self.app_id)
        # TODO: stop controller
        # scaler.stop_scaler(api.controller_url, self.app_id)
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

    def _get_executors_ip(self):
        frameworks = requests.get(self.get_frameworks_url).json()

        executors_ips = []
        framework = None
        for i in range(50):
            for f in frameworks:
                if 'bigsea_id' in f['labels'] and \
                    f['labels']['bigsea_id'] == self.app_id:
                    framework = f

            time.sleep(2)

        # TODO: look for app-id into the labels and
        # TODO: get the framework that contains it
        for t in frameworks['framework'][0]['tasks']:
            for s in t['statuses']:
                for n in s['container_status']['network_infos']:
                    for i in n['ip_addresses']:
                        # TODO: it must return a list with tuples (ip, host)
                        executors_ips.append(i['ip_address'])

        return executors_ips, framework['webui_url']

    def _start_contoller(self, executors_ips, data):
        scaler.start_scaler(api.controller_url,
                            self.app_id,
                            data['scaler_plugin'],
                            executors_ips,
                            data['scaling_parameters'])

    def _start_monitoring(self, master, data):
        print "Executing commands into the instance"
        # TODO Check if exec_command will work without blocking exec

        monitor_plugin = 'spark-progress'
        info_plugin = {
            "spark_submisson_url": master,
            "expected_time": data['reference_value']
        }
        collect_period = 1
        try:
            print "Starting monitoring"

            monitor.start_monitor(api.monitor_url, self.app_id,
                                  monitor_plugin, info_plugin,
                                  collect_period)

            print "Starting scaling"
        except Exception as e:
            print e.message
