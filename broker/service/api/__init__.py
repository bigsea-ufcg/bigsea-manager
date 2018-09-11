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


try:
    # Conf reading
    config = ConfigParser.RawConfigParser()
    config.read('./broker.cfg')
    
    """ Services configuration """
    monitor_url = config.get('services', 'monitor_url')
    controller_url = config.get('services', 'controller_url')
    authorization_url = config.get('services', 'authorization_url')
    optimizer_url = config.get('services', 'optimizer_url')
    
    """ General configuration """
    host = config.get("general", "host")
    print host
    port = config.getint('general', 'port')
    plugins = config.get('general', 'plugins').split(',')

    """ Validate if really exists a section to listed plugins """
    for plugin in plugins:
        if plugin != '' and plugin not in config.sections():
            raise Exception("plugin '%s' section missing" % plugin)
    
    if 'kubejobs' in plugins:
        k8s_conf_path = config.get('kubejobs', 'k8s_conf_path')
        redis_ip = config.get('kubejobs', 'redis_ip')
        redis_port = config.get('kubejobs', 'redis_port')
        redis_workload_path = config.get('kubejobs', 'redis_workload_path')
        count_queue = config.get('kubejobs', 'count_queue')
        scone_compose = config.get('kubejobs', 'scone_path')
        scone_command = config.get('kubejobs', 'scone_cmd')
        home_path = config.get('kubejobs', 'home_path')


    if 'openstack_generic' in plugins:
        public_key = config.get('openstack_generic', 'public_key')
        key_path = config.get('openstack_generic', 'key_path')
        user_domain_name = config.get('openstack_generic', 'user_domain_name')
        project_id = config.get('openstack_generic', 'project_id')
        auth_ip = config.get('openstack_generic', 'auth_ip')
        user = config.get('openstack_generic', 'user')
        password = config.get('openstack_generic', 'password')
        domain = config.get('openstack_generic', 'user_domain_name')
        log_path = config.get('openstack_generic', 'log_path')
    
    if 'spark_sahara' in plugins:
        log_path = config.get('openstack_generic', 'log_path')
        public_key = config.get('spark_sahara', 'public_key')
        key_path = config.get('spark_sahara', 'key_path')
        container = config.get('spark_sahara', 'swift_container')
        user_domain_name = config.get('spark_sahara', 'user_domain_name')
        project_id = config.get('spark_sahara', 'project_id')
        auth_ip = config.get('spark_sahara', 'auth_ip')
        user = config.get('spark_sahara', 'user')
        password = config.get('spark_sahara', 'password')
        domain = config.get('spark_sahara', 'user_domain_name')
        number_of_attempts = config.getint('spark_sahara', 'number_of_attempts')
        swift_logdir = config.get('spark_sahara', 'swift_logdir')
        remote_hdfs = config.get('spark_sahara', 'remote_hdfs')
        number_of_attempts = config.getint('spark_sahara', 'number_of_attempts')
        dummy_opportunistic = config.getboolean('spark_sahara', 'dummy_opportunistic')
        hosts = config.get('spark_sahara', 'hosts').split(',')
    
    if 'spark_generic' in plugins:
        key_path = config.get('spark_generic', 'key_path')
        number_of_attempts = config.getint('spark_generic', 'number_of_attempts')
        remote_hdfs = config.get('spark_generic', 'remote_hdfs')
        masters_ips = config.get('spark_generic', 'masters_ips').split(' ')
    
    if 'spark_mesos' in plugins:
        mesos_url = config.get('spark_mesos', 'mesos_url')
        mesos_port = config.get('spark_mesos', 'mesos_port')
        cluster_username = config.get('spark_mesos', 'cluster_username')
        cluster_password = config.get('spark_mesos', 'cluster_password')
        cluster_key_path = config.get('spark_mesos', 'key_path')
        one_url = config.get('spark_mesos', 'one_url')
        one_password = config.get('spark_mesos', 'one_password')
        one_username = config.get('spark_mesos', 'one_username')
        spark_path = config.get('spark_mesos', 'spark_path')
    
    if 'chronos' in plugins:
        chronos_url = config.get('chronos', 'url')
        chronos_username = config.get('chronos', 'username')
        chronos_password = config.get('chronos', 'password')
        supervisor_url = config.get('chronos', 'supervisor_url')

except Exception as e:
    print "Error: %s" % e.message
    quit()
