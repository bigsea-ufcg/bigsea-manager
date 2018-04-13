# Copyright (c) 2018 UFCG-LSD.
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

import kubernetes as kube

from application_manager.service import api


def create_job(app_id, env_name, env_value,
               args, cmd, img, working_dir,
               init_size):

    kube.config.load_kube_config(api.k8s_conf_path)

    obj_meta = kube.client.V1ObjectMeta(
        name=app_id)
    queue = kube.client.V1EnvVar(
        name="STD_QUEUE",
        value=app_id)
    env = kube.client.V1EnvVar(
        name=env_name,
        value=env_value)
    container_spec = kube.client.V1Container(
        args=args,
        command=cmd,
        env=[env, queue],
        image=img,
        image_pull_policy="Always",
        name=app_id,
        tty=True,
        working_dir=working_dir)
    pod_spec = kube.client.V1PodSpec(
        containers=[container_spec],
        restart_policy="OnFailure")
    pod = kube.client.V1PodTemplateSpec(
        metadata=obj_meta,
        spec=pod_spec)
    job_spec = kube.client.V1JobSpec(
        parallelism=init_size,
        template=pod)
    job = kube.client.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=obj_meta,
        spec=job_spec)

    batch_v1 = kube.client.BatchV1Api()
    batch_v1.create_namespaced_job("default", job)

    return job
