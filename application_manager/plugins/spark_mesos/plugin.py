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

from application_manager.plugins import base
from application_manager.service import api
from application_manager.utils import monitor
from application_manager.utils import scaler

from uuid import uuid4

import json
import paramiko
import time


class SparkMesosProvider(base.PluginInterface):

    def __init__(self):
        self.get_frameworks_url = "%s:%s" % (api.mesos_url,
                                             api.mesos_port)
        self.app_id = "app-spark-mesos-" + str(uuid4())[:8]


    def get_title(self):
        return 'Spark-Mesos on Open Nebula plugin for BigSea framework'

    def get_description(self):
        return 'It runs an spark application on a Mesos cluster'

    def to_dict(self):
        return {
            'name': self.name,
            'title': self.get_title(),
            'description': self.get_description(),
        }

    def execute(self, data):
        # mesos_url = api.mesos_url
        # cluster_username = api.cluster_username
        # cluster_password = api.cluster_password
        # one_url = api.one_url
        # one_username = api.one_username
        # one_password = api.one_password

        binary_url = str(data['binary_url'])
        execution_class = str(data['execution_class'])
        execution_parameters = str(data['execution_parameters'])
        starting_cap = 0 if data['starting_cap'] == "" else int(data['starting_cap'])
        actuator = str(data['actuator'])

        # DONE: Creates a connection ssh with Mesos cluster
        conn = self._get_ssh_connection(api.mesos_url,
                                        api.cluster_username,
                                        api.cluster_password,
                                        api.cluster_key_path)
        # DONE: execute all the spark needed commands
        # DONE: to run an spark job from command line
        if execution_class != "" and execution_class is not None:
            # If the class field is empty, it means that the
            # job binary is python
            binary_path = '~/exec_bin.jar'
            spark_run = ('sudo %s --name %s ' +
                              '--master mesos://%s:%s ' +
                              '--class %s %s %s')
        else:
            binary_path = '~/exec_bin.py'
            spark_run = ('sudo %s --name %s ' +
                              '--master mesos://%s:%s ' +
                              '%s %s %s')

        # DONE: Download the binary from a public link

        print ">>>>>>>>>>>>>>>>> ID: " + self.app_id
        try:
            stdin, stdout, stderr = conn.exec_command('wget %s -O %s' %
                                                      (binary_url,
                                                       binary_path))
            print "waiting to download the binary"
            print stdout.read()
            print "binary downloaded"

        except Exception as e:
            print "Error downloading binary"
            print e.message

        i, o, e = conn.exec_command(spark_run % (api.spark_path,
                                                 self.app_id,
                                                 api.mesos_url,
                                                 api.mesos_port,
                                                 execution_class,
                                                 binary_path,
                                                 execution_parameters))

        # print 'ERROR RUNNING APPLCATION: ' + e.read()

        # TODO: Discovery ips of the executors from Mesos
        # TODO: Discovery the ids on KVM using the ips
        list_vms_one = 'onevm list --user %s --password %s --endpoint %s' % \
                       (api.one_username, api.one_password, api.one_url)
        stdin, stdout, stderr = conn.exec_command(list_vms_one)

        list_response = stdout.read()
        executors = self._get_executors_ip(conn)
        vms_ips = executors[0]
        vms_ids = self._extract_vms_ids(list_response)

        executors_vms_ids = []
        for ip in vms_ips:
            for id in vms_ids:
                vm_info_one = 'onevm show %s --user %s --password %s --endpoint %s' % \
                              (id, api.one_username, api.one_password, api.one_url)

                stdin, stdout, stderr = conn.exec_command(vm_info_one)
                if ip in stdout.read():
                    executors_vms_ids.append(id)
                    break

        print executors_vms_ids

        # DONE: set up the initial configuration of cpu cap
        #scaler.setup_environment(api.controller_url, executors_vms_ids,
        #                         starting_cap, actuator)

        # DONE: start monitor service
        # self._start_monitoring(executors[1], data)

        # DONE: start controller service
        # self._start_controller(executors_vms_ids, data)

        # This command locks the plugin execution until the execution be done
        # o.read()
        # TODO: stop monitor
        # monitor.stop_monitor(api.monitor_url, self.app_id)
        # TODO: stop controller
        # scaler.stop_scaler(api.controller_url, self.app_id)
        # DONE: remove binaries
        conn.exec_command('rm -rf ~/exec_bin.*')
        return None, None

    def _get_ssh_connection(self, ip, username=None,
                            password=None, key_path=None):
        # Preparing SSH connection
        conn = paramiko.SSHClient()
        conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Checking if the connection will be established using
        # keys or passwords
        if key_path != "" and key_path is not None:
            keypair = paramiko.RSAKey.from_private_key_file(key_path)
            conn.connect(hostname=ip, username=username, pkey=keypair)
        else:
            conn.connect(hostname=ip, username=username, password=password)

        return conn

    # It must be mad by ssh access
    # FIXME
    def _get_executors_ip(self, conn):
        frameworks_call = 'curl http://' + self.get_frameworks_url + '/frameworks'

        stdin, stdout, sterr = conn.exec_command(frameworks_call)

        try:
            output = stdout.read()
            mesos_resp = json.loads(output)
            # print mesos_resp
        except Exception as e:
            print e.message
            # print str(e)
            mesos_resp = {}

        executors_ips = []
        framework = None
        find_fw = False

        # print mesos_resp

        # DONE: It must to ensure that the application was
        # DONE: started before try to get the executors

        while not find_fw:
            for f in mesos_resp['frameworks']:
                if f['name'] == self.app_id:
                    framework = f
                    find_fw = True
                    break
            if not find_fw:
                print 'Trying to find framework'
                stdin, stdout, sterr = conn.exec_command(frameworks_call)
                mesos_resp = json.loads(stdout.read())

            time.sleep(2)

        # DONE: look for app-id into the labels and
        # DONE: get the framework that contains it
        for t in framework['tasks']:
            for s in t['statuses']:
                for n in s['container_status']['network_infos']:
                    for i in n['ip_addresses']:
                        # TODO: it must return a list with tuples (ip, host)
                        executors_ips.append(i['ip_address'])

        print executors_ips, framework['webui_url']
        return executors_ips, framework['webui_url']

    def _extract_vms_ids(self, output):
        lines = output.split('\n')
        ids = []
        for i in range(1, len(lines)-1):
            ids.append(lines[i].split()[0])

        return ids

    def _start_contoller(self, executors_ids, data):
        data['scaling_parameters']['cluster_password'] = api.cluster_password
        data['scaling_parameters']['cluster_username'] = api.cluster_username
        data['scaling_parameters']['cluster_ip'] = api.mesos_url
        scaler.start_scaler(api.controller_url,
                            self.app_id,
                            data['scaler_plugin'],
                            executors_ids,
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
