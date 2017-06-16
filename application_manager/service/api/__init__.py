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
config.read('./manager.cfg')

monitor_url = config.get('services', 'monitor_url')
controller_url = config.get('services', 'controller_url')
authorization_url = config.get('services', 'authorization_url')
optimizer_url = config.get('services', 'optimizer_url')
plugins = config.get('services', 'plugins').split(',')

monasca_username = config.get('monasca', 'username')
monasca_password = config.get('monasca', 'password')
monasca_auth_url = config.get('monasca', 'auth_url')
monasca_project_name = config.get('monasca', 'project_name')
monasca_api_version = config.get('monasca', 'api_version')

net_id = config.get('openstack', 'net_id')
master_ng = config.get('openstack', 'master_ng')
slave_ng = config.get('openstack', 'slave_ng')

public_key = config.get('credentials', 'public_key')
key_path = config.get('credentials', 'key_path')
user_domain_name = config.get('credentials', 'user_domain_name')
project_id = config.get('credentials', 'project_id')
auth_ip = config.get('credentials', 'auth_ip')
user = config.get('credentials', 'user')
password = config.get('credentials', 'password')
domain = config.get('credentials', 'user_domain_name')

hosts = config.get('infra', 'hosts').split(' ')
