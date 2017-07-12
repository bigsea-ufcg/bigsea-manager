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


def get_job_config(connector, plugin, cluster_size=None, username=None,
                   password=None, args=None, main_class=None):
    if plugin == 'hadoop':
        configs = connector.get_job_configs(plugin,
                                            cluster_size=cluster_size)
    else:
        configs = connector.get_job_configs(plugin, username=username,
                                            password=password,
                                            args=args,
                                            main_class=main_class)
    return configs
