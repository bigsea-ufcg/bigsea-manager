# Copyright (c) 2013 Mirantis Inc.
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

from application_manager.utils import api as u

rest = u.Rest('v10', __name__)


# Cluster ops

@rest.post('/application_started/')
def application_started():
    # result = api.get_clusters(**u.get_request_args().to_dict())
    # return u.render(res=result, name='clusters')
    return 'testasdfasfadsfdsafsadfs'


# @rest.post('/clusters')
# def clusters_create(data):
#     return u.render(api.create_cluster(data).to_wrapped_dict())
#
#
# @rest.post('/clusters/multiple')
# def clusters_create_multiple(data):
#     return u.render(api.create_multiple_clusters(data))
#
#
# @rest.put('/clusters/<cluster_id>')
# def clusters_scale(cluster_id, data):
#     return u.to_wrapped_dict(api.scale_cluster, cluster_id, data)
#
#
# @rest.get('/clusters/<cluster_id>')
# def clusters_get(cluster_id):
#     data = u.get_request_args()
#     show_events = six.text_type(
#         data.get('show_progress', 'false')).lower() == 'true'
#     return u.to_wrapped_dict(api.get_cluster, cluster_id, show_events)
#
#
# @rest.patch('/clusters/<cluster_id>')
# def clusters_update(cluster_id, data):
#     return u.to_wrapped_dict(api.update_cluster, cluster_id, data)
#
#
# @rest.delete('/clusters/<cluster_id>')
# def clusters_delete(cluster_id):
#     api.terminate_cluster(cluster_id)
#     return u.render()
#
#
# # ClusterTemplate ops
#
# @rest.get('/cluster-templates')
# def cluster_templates_list():
#     result = api.get_cluster_templates(
#         **u.get_request_args().to_dict())
#
#     return u.render(res=result, name='cluster_templates')
#
#
# @rest.post('/cluster-templates')
# def cluster_templates_create(data):
#     return u.render(api.create_cluster_template(data).to_wrapped_dict())
#
#
# @rest.get('/cluster-templates/<cluster_template_id>')
# def cluster_templates_get(cluster_template_id):
#     return u.to_wrapped_dict(api.get_cluster_template, cluster_template_id)
#
#
# @rest.put('/cluster-templates/<cluster_template_id>')
# def cluster_templates_update(cluster_template_id, data):
#     return u.to_wrapped_dict(
#         api.update_cluster_template, cluster_template_id, data)
#
#
# @rest.delete('/cluster-templates/<cluster_template_id>')
# def cluster_templates_delete(cluster_template_id):
#     api.terminate_cluster_template(cluster_template_id)
#     return u.render()