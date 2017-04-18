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
import time
import six
import base64

from keystoneauth1.identity import v3
from keystoneauth1 import session
from saharaclient.api.client import Client as saharaclient
from saharaclient.api.base import APIException as SaharaAPIException
from subprocess import *


class OpenStackConnector(object):
    def __init__(self, logger):
        self.logger = logger

    def get_sahara_client(self, username, password, project_id, auth_ip,
                          domain):
        auth = v3.Password(auth_url=auth_ip + ':5000/v3',
                           username=username,
                           password=password,
                           project_id=project_id,
                           user_domain_name=domain)
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

    def get_existing_cluster_by_size(self, sahara, size):
        clusters = sahara.clusters.list()
        for cluster in clusters:
            for node_group in cluster.node_groups:
                if 'slave' in node_group['name']:
                    if node_group['count'] == size:
                        return cluster.id
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
        for node_group in cluster.node_groups:
            if 'datanode' in node_group['node_processes']:
                for instance in node_group['instances']:
                    instance_name = instance
                    instances.append(instance_name)
        return instances

    def get_master_instance(self, sahara, cluster_id):
        cluster = sahara.clusters.get(cluster_id)
        for node_group in cluster.node_groups:
            if 'namenode' in node_group['node_processes']:
                for instance in node_group['instances']:
                    return instance
        return None

    def get_job_configs(self, plugin, cluster_size=None, username=None,
                        password=None, args=[], main_class=None):
        if plugin == 'hadoop':
            reducers = int(cluster_size) * 2
            configs = {'configs': {'mapreduce.job.reduces': reducers}}
        else:
            configs = {'configs': {
                            'edp.java.main_class': main_class,
                            'edp.spark.adapt_for_swift': 'True',
                            'fs.swift.service.sahara.password': password,
                            'fs.swift.service.sahara.username': username
                            },
                       'args': args
                       }

        return configs

    def create_job_execution(self, sahara, job_id, cluster_id,
                             input_ds_id=None, output_ds_id=None,
                             configs=None):
        return sahara.job_executions.create(job_id, cluster_id, input_ds_id,
                                            output_ds_id, configs=configs)

    def create_cluster(self, sahara, cluster_size, public_key, net_id,
                       image_id, plugin, version, master, slave):
        #size = max(3, cluster_size - 1)
        import pdb; pdb.set_trace()
        size = 3
        cluster_template = self.get_cluster_template(sahara, size, plugin)
        cluster_template_id = cluster_template.id
        if cluster_template:
            cluster = self._create_cluster(sahara, cluster_template_id,
                                           public_key, net_id, image_id,
                                           plugin, version)
        else:
            cluster_temp_name = "cluster-osahara-" + self.get_timestamp_raw()
            node_groups = []
            node_groups.append(result_mng)
            node_groups.append(result_sng)
            cluster_template = self.create_cluster_template(sahara,
                                                            cluster_temp_name,
                                                            plugin, version,
                                                            node_groups)

            cluster = self._create_cluster(saharaclient, cluster_template_id,
                                           public_key, net_id, image_id,
                                           plugin, version)

        return cluster.id

    def _create_cluster(self, sahara, cluster_template, public_key_name,
                        net_id, image_id, plugin, version, max_tries=5):
        cluster_is_ready = False
        cluster_tries = 0
        cluster_name = "cluster-osahara-" + self.get_timestamp_raw()
        while not cluster_is_ready and cluster_tries < max_tries:
            cluster_tries += 1
            self.logger.log("Tyring to create cluster. Try " +
                            str(cluster_tries))

            cluster = self._create_sahara_cluster(sahara, cluster_template,
                                                  cluster_name, public_key_name,
                                                  net_id, image_id, plugin,
                                                  version)
            time.sleep(30)

            if not self.is_cluster_in_api_error(cluster):
                cluster_id = cluster.id
                self.logger.log("Cluster is being created with id " +
                                cluster_id)
                cluster_status = self.get_cluster_status(sahara, cluster_id)
            else:
                self.logger.log("Sahara returned API error")
                cluster_status = 'Error'
                cluster_id = None

            already_deleted_cluster = False
            while cluster_status != 'Active' and not already_deleted_cluster:
                self.logger.log("Cluster is in status %s" % cluster_status)
                if cluster_status == 'Error':
                    self.logger.log(
                        "Cluster %s is in ERROR status and will be deleted." %
                        str(cluster))
                    self.delete_cluster(sahara, cluster_id, cluster_name)
                    self.logger.log("Cluster deleted.")
                    already_deleted_cluster = True
                    time.sleep(60)
                else:
                    time.sleep(10)
                    cluster_status = self.get_cluster_status(
                        sahara, cluster_id)
            cluster_is_ready = cluster_status == 'Active'

        return cluster

    def _create_sahara_cluster(self, sahara, cluster_template_id, cluster_name,
                               public_key_name, net_id, image_id, plugin,
                               version):
        import pdb; pdb.set_trace()
        self.logger.log(cluster_name)
        self.logger.log(cluster_template_id)
        self.logger.log(image_id)
        self.logger.log(net_id)
        self.logger.log(public_key_name)
        try:

            return sahara.clusters.create(cluster_name, plugin, version,
                                          cluster_template_id,
                                          image_id, net_id=net_id,
                                          user_keypair_id=public_key_name)

        except SaharaAPIException as e:
            self.logger.log('Exception returned by sahara: %s' % e)
            if "Quota exceeded" in str(e):
                raise e
            return 'api_exception'

    def get_worker_host_ip(self, worker_id):
        # FIXME hardcoded
        hosts = ["c4-compute11", "c4-compute12"]
        for host in hosts:
            if int(check_output("ssh root@%s test -e "
                                "\"/var/lib/nova/instances/%s\" && echo "
                                "\"1\" || echo \"0\"" % (host, worker_id),
                                shell=True)) == 1:
                return host
        return None

    def get_cluster_template(self, sahara, size, plugin):
        cluster_templates = sahara.cluster_templates.list()
        for template in cluster_templates:
            if template.plugin_name.lower() == plugin.lower():
                for node_group in template.node_groups:
                    if 'slave' in node_group['name'].lower():
                        if node_group['count'] == size:
                            return template
        return None

    def create_cluster_template(self, sahara, name, plugin_name,
                                plugin_version, node_groups):

        cluster_template = sahara.cluster_templates.create(
            name, plugin_name, plugin_version, node_groups=node_groups)
        return cluster_template['id']

    def create_job_template(self, sahara, name, job_type, mains=None,
                            libs=None):

        job_template = sahara.jobs.create(name, job_type, mains, libs)

        return job_template.id

    def delete_cluster(self, sahara, cluster_id, cluster_name=None):
        if not cluster_id:
            cluster = self.get_cluster_by_name(sahara, cluster_name)
            if cluster:
                cluster_id = cluster.id
        if cluster_id:
            sahara.clusters.delete(cluster_id)

    def create_job_binary(self, sahara, name, url, extra):
        job_binary = sahara.job_binaries.create(name, url, extra=extra)
        return job_binary.id

    def upload_job_binary(self, binary):
        return None

    def get_node_group(self, sahara, plugin, node_group):
        node_groups = sahara.node_group_templates.list()
        for ng in node_groups:
            if ng.plugin_name.lower() == plugin.lower():
                if node_group in ng.name:
                    return ng

    def is_cluster_in_api_error(self, cluster):
        return cluster == 'api_exception'

    def get_job_binary(self, sahara, job_binary_url):
        for job_binary in sahara.job_binaries.list():
            if job_binary.url == job_binary_url:
                return job_binary.id
        return None

    def get_job_template(self, sahara, mains):
        import pdb; pdb.set_trace()
        for job_template in sahara.jobs.list():
            for main in job_template.mains:
                if main['id'] in mains:
                    mains.remove(main['id'])
                    if not mains:
                        return job_template.id
        return None

