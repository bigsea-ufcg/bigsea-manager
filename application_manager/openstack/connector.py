# Copyright (c) 2017 LSD - UFCG.
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

import datetime

from keystoneauth1.identity import v3
from keystoneauth1 import session
from saharaclient.api.client import Client as saharaclient

class OpenStackConnector(object):
    def __init__(self, logger):
        self.logger = logger

    def get_sahara_client(self, token, project_id, auth_ip):
        auth = v3.Token(auth_url=auth_ip + ':5000/v3',
                        token=token,
                        project_id=project_id)
        ses = session.Session(auth=auth)

        return saharaclient('1.1', session=ses)

    def get_cluster_status(self, sahara, cluster_id):
        cluster = sahara.clusters.get(cluster_id)
        return cluster.status

    def get_cluster_by_name(self, sahara, cluster_name):
        self.logger.log("Searching for cluster named " + cluster_name)
        query = {'name': cluster_name}
        clusters = sahara.clusters.list(query)
        if len(clusters) > 0:
            return clusters[0]
        return None

    def get_timestamp_raw(self):
        return datetime.datetime.now().strftime('%Y%m%d%H%M%S')

    def get_job_status(self, sahara, job_id):
        return sahara.job_executions.get(job_id).info['status']

    def is_job_completed(self, job_status):
        success = ('SUCCEEDED', ' ', '')
        succeeded = job_status in success

        return succeeded

    def is_job_failed(self, job_status):
        fails = ('KILLED', 'FAILED', 'TIMEOUT', 'DONEWITHERROR')
        return job_status in fails

    def is_on_same_host(self, nova, instance_id, host):
        instance_ref = nova.servers.get(instance_id)
        instance_host = instance_ref.__dict__['OS-EXT-SRV-ATTR:host']
        return instance_host == host

    def pick_random_instance(self, sahara, nova, cluster_id, host):
        cluster = sahara.clusters.get(cluster_id)
        node_groups = cluster.node_groups
        for n in node_groups:
            if "slave" in n['node_group_name']:
                for ins in n['instances']:
                    instance_id = ins
                    if self.is_on_same_host(nova, instance_id, host):
                        return instance_id
        self.logger.log("There is no slave instance on host: %s" % host)
        return None

    def get_worker_instances(self, sahara, cluster_id):
        instances = []
        cluster = sahara.clusters.get(cluster_id)
        node_groups = cluster.node_groups
        for node_group in node_groups:
            if 'datanode' in node_group['node_processes']:
                for instance in node_group['instances']:
                    instance_name = instance
                    instances.append(instance_name)
        return instances

    def get_master_instance(self, sahara, cluster_id):
        cluster = sahara.clusters.get(cluster_id)
        node_groups = cluster.node_groups
        for node_group in node_groups:
            if 'namenode' in node_group['node_processes']:
                for instance in node_group['instances']:
                    return instance

        return None