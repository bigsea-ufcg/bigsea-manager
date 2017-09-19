# Copyright (c) 2017 UFGG-LSD.
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

import ConfigParser

# Conf reading
config = ConfigParser.RawConfigParser()
config.read('./manager.lsd.cfg')

monitor_url = config.get('services', 'monitor_url')
controller_url = config.get('services', 'controller_url')
authorization_url = config.get('services', 'authorization_url')
optimizer_url = config.get('services', 'optimizer_url')
plugins = config.get('services', 'plugins').split(',')


public_key = config.get('os-generic', 'public_key')
key_path = config.get('os-generic', 'key_path')
user_domain_name = config.get('os-generic', 'user_domain_name')
project_id = config.get('os-generic', 'project_id')
auth_ip = config.get('os-generic', 'auth_ip')

user = config.get('os-generic', 'user')
password = config.get('os-generic', 'password')
domain = config.get('os-generic', 'user_domain_name')
log_path = config.get('os-generic', 'log_path')

container = config.get('spark-sahara', 'swift_container')
#user_domain_name = config.get('spark-sahara', 'user_domain_name')
#project_id = config.get('spark-sahara', 'project_id')
#auth_ip = config.get('spark-sahara', 'auth_ip')
#user = config.get('spark-sahara', 'user')
#password = config.get('spark-sahara', 'password')
#domain = config.get('spark-sahara', 'user_domain_name')
remote_hdfs = config.get('spark-sahara', 'remote_hdfs')


hosts = config.get('infra', 'hosts').split(' ')


chronos_url = config.get('chronos', 'url')
chronos_username = config.get('chronos', 'username')
chronos_password = config.get('chronos', 'password')
supervisor_ip = config.get('chronos', 'supervisor_ip')
