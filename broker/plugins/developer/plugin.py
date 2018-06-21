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

import uuid
import paramiko
import time
import threading

from broker.utils.openstack import connector as os_connector
from broker.plugins import base
from broker.service import api
from broker.utils.logger import *
from broker.utils.ids import ID_Generator
from broker.plugins.base import GenericApplicationExecutor


LOG = Log("DeveloperPlugin", "logs/developer_plugin.log")
application_time_log = Log("Application_time", "logs/application_time.log")
configure_logging()


class DeveloperApplicationExecutor(GenericApplicationExecutor):
    def __init__(self):
        self.application_state = "None"
        self.state_lock = threading.RLock()
        self.application_time = -1
        self.start_time = -1

    def get_application_state(self):
        with self.state_lock:
            state = self.application_state
        return state

    def update_application_state(self, state):
        print state
        with self.state_lock:
            self.application_state = state

    def get_application_execution_time(self):
        return self.application_time

    def get_application_start_time(self):
        return self.start_time

    def start_application(self, data):
        try:
            self.update_application_state("Running")

            # Openstack parameters
            user = api.user
            password = api.password
            project_id = api.project_id
            auth_ip = api.auth_ip
            domain = api.domain
            public_key = api.public_key

            # Client parameters
            image_id = data['image_id']
            flavor_id = data['flavor_id']
            command = data['command']

            # Get Nova (Openstack) client
            connector = os_connector.OpenStackConnector(LOG)
            nova = connector.get_nova_client(user, password, project_id,
                                             auth_ip, domain)
            print "Connected with Openstack"

            # Create instance
            instance = connector.create_instance(nova, image_id, flavor_id,
                                                 public_key)

            print "Instance: %s"  % (instance)

 
            # Retrive network information of instance
            instance_status = connector.get_instance_status(nova, instance)
            while instance_status != 'ACTIVE':
                instance_status = connector.get_instance_status(
                                      nova, instance)

                print "Instance status: %s" % (instance_status)
                time.sleep(2)

            time.sleep(20)
            instance_net = connector.get_instance_networks(nova, instance)
            instance_ip = instance_net.values()[0][0]
            conn = self._get_ssh_connection(instance_ip, api.key_path)

            # Execute application
            conn.exec_command(command)
            print "Executing application"

            # Verify if application is running
            application_running = True
            while application_running:
                status_instance = connector.get_instance_status(nova,
                                                                instance)
                if status_instance == 'SHUTOFF':
                    application_running = False

                time.sleep(2)

            print "End of execution"

            # Remove instances after the end of execution of application
            connector.remove_instance(nova, instance)
            print "Remove instance"

            self.update_application_state("OK")
            return "OK"

        except Exception as e:
            LOG.log(e.message)
            print e.message
            self.update_application_state("Error")

    def _get_ssh_connection(self, ip, key_path):
        keypair = paramiko.RSAKey.from_private_key_file(key_path)
        conn = paramiko.SSHClient()
        conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        conn.connect(hostname=ip, username="ubuntu", pkey=keypair)
        return conn


class DeveloperProvider(base.PluginInterface):
    def __init__(self):
        self.id_generator = ID_Generator()

    def get_title(self):
        return 'Developer Plugin'

    def get_description(self):
        return 'Developer Plugin'

    def to_dict(self):
        return {
            'name': self.name,
            'title': self.get_title(),
            'description': self.get_description(),
        }

    def execute(self, data):
        executor = DeveloperApplicationExecutor()
        handling_thread = threading.Thread(target=executor.start_application,
                                           args=(data,))
        handling_thread.start()
        app_id = "developer" + self.id_generator.get_ID()
        return (app_id, executor)
