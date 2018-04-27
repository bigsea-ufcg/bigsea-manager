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

""" Services configuration """
monitor_url = config.get('services', 'monitor_url')
controller_url = config.get('services', 'controller_url')
authorization_url = config.get('services', 'authorization_url')
optimizer_url = config.get('services', 'optimizer_url')

""" General configuration """
plugins = config.get('general', 'plugins').split(',')
hosts = config.get('general', 'hosts').split(',')
port = config.getint('general', 'port')

if 'openstack_generic' in plugins:
    public_key = config.get('openstack-generic', 'public_key')
    key_path = config.get('openstack-generic', 'key_path')
    user_domain_name = config.get('openstack-generic', 'user_domain_name')
    project_id = config.get('openstack-generic', 'project_id')
    auth_ip = config.get('openstack-generic', 'auth_ip')
    user = config.get('openstack-generic', 'user')
    password = config.get('openstack-generic', 'password')
    domain = config.get('openstack-generic', 'user_domain_name')
    log_path = config.get('openstack-generic', 'log_path')

if 'spark_sahara' in plugins:
    log_path = config.get('openstack-generic', 'log_path')
    public_key = config.get('spark-sahara', 'public_key')
    key_path = config.get('spark-sahara', 'key_path')
    container = config.get('spark-sahara', 'swift_container')
    user_domain_name = config.get('spark-sahara', 'user_domain_name')
    project_id = config.get('spark-sahara', 'project_id')
    auth_ip = config.get('spark-sahara', 'auth_ip')
    user = config.get('spark-sahara', 'user')
    password = config.get('spark-sahara', 'password')
    domain = config.get('spark-sahara', 'user_domain_name')
    number_of_attempts = config.getint('spark-sahara', 'number_of_attempts')
    swift_logdir = config.get('spark-sahara', 'swift_logdir')
    remote_hdfs = config.get('spark-sahara', 'remote_hdfs')
    number_of_attempts = config.getint('spark-sahara', 'number_of_attempts')
    dummy_opportunistic = config.getboolean('spark-sahara',
                                            'dummy_opportunistic')

if 'spark_generic' in plugins:
    log_path = config.get('openstack-generic', 'log_path')
    public_key = config.get('spark-generic', 'public_key')
    key_path = config.get('spark-generic', 'key_path')
    container = config.get('spark-generic', 'swift_container')
    user_domain_name = config.get('spark-generic', 'user_domain_name')
    project_id = config.get('spark-generic', 'project_id')
    auth_ip = config.get('spark-generic', 'auth_ip')
    user = config.get('spark-generic', 'user')
    password = config.get('spark-generic', 'password')
    domain = config.get('spark-generic', 'user_domain_name')
    number_of_attempts = config.getint('spark-generic', 'number_of_attempts')
    swift_logdir = config.get('spark-generic', 'swift_logdir')
    remote_hdfs = config.get('spark-generic', 'remote_hdfs')
    number_of_attempts = config.getint('spark-generic', 'number_of_attempts')
    masters_ips = config.get('spark-generic', 'masters_ips').split(' ')

if 'spark_mesos' in plugins:
    mesos_url = config.get('spark-mesos', 'mesos_url')
    mesos_port = config.get('spark-mesos', 'mesos_port')
    cluster_username = config.get('spark-mesos', 'cluster_username')
    cluster_password = config.get('spark-mesos', 'cluster_password')
    cluster_key_path = config.get('spark-mesos', 'key_path')
    one_url = config.get('spark-mesos', 'one_url')
    one_password = config.get('spark-mesos', 'one_password')
    one_username = config.get('spark-mesos', 'one_username')
    spark_path = config.get('spark-mesos', 'spark_path')

if 'chronos' in plugins:
    chronos_url = config.get('chronos', 'url')
    chronos_username = config.get('chronos', 'username')
    chronos_password = config.get('chronos', 'password')
    supervisor_url = config.get('chronos', 'supervisor_url')
