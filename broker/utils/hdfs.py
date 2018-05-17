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

import subprocess
from broker.utils import remote


def create_hdfs_path(hdfs_address, user, hdfs_path):
    command = (
        'export HADOOP_USER_NAME=%(user)s && hdfs dfs '
        '-fs hdfs://%(hdfs_address)s:8020/ -mkdir -p '
        '%(path)s' % {'hdfs_address': hdfs_address, 'user': user,
                      'path': hdfs_path}
    )

    subprocess.call(command, shell=True)


def copy_to_hdfs(hdfs_address, user, local_path, hdfs_path):

    command = (
        'export HADOOP_USER_NAME=%(user)s && hdfs dfs -fs '
        'hdfs://%(hdfs_url)s:8020/ -put %(local_path)s '
        '%(hdfs_path)s' % {'hdfs_address': hdfs_address,
                           'local_path': local_path,
                           'hdfs_path': hdfs_path}
    )

    subprocess.call(command, shell=True)


def copy_from_hdfs(hdfs_address, hdfs_path, local_path):
    command = (
        'export HADOOP_USER_NAME=ubuntu && hdfs dfs -fs '
        'hdfs://%(hdfs_address)s:8020/ -copyToLocal '
        '%(hdfs_path)s %(local_path)s' % {'hdfs_address': hdfs_address,
                                          'local_path': local_path,
                                          'hdfs_path': hdfs_path}
    )

    subprocess.call(command, shell=True)


def check_file_exists(hdfs_url, file_path):
    command = (
        'export HADOOP_USER_NAME=ubuntu && hdfs dfs -fs '
        'hdfs://%(hdfs_url)s:8020/ -test -e '
        '%(file_path)s && echo $?' % {'hdfs_url': hdfs_url,
                                      'file_path': file_path}
    )

    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)

    output, err = process.communicate()

    return True if output else False


def get_job_params(key_path, hdfs_url, args):
    in_paths = []
    out_paths = []
    others = []

    for arg in args:
        if arg.startswith('hdfs://'):
            if remote.check_file_exists(key_path, hdfs_url,
                                        get_path(arg)):
                in_paths.append(get_path(arg))
            else:
                out_paths.append(get_path(arg))
        else:
            others.append(arg)

    return in_paths, out_paths, others


def get_path(arg):
    delimeter = '/'
    splitted = arg.split(delimeter)
    hdfs_path = delimeter + (delimeter).join(splitted[3:])

    return hdfs_path
