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

def pull(master, hdfs_path, local_path):
    hadoop_command = "hadoop fs -get %s %s" % (hdfs_path, local_path)
    subprocess.call("ssh -o 'StrictHostKeyChecking no' -o 'UserKnownHostsFile=/dev/null' -i /home/ubuntu/.ssh/bigsea ubuntu@%s '%s'" % (master, hadoop_command), shell=True)

def make_directory(master, hdfs_path):
    hadoop_command = "hadoop fs -mkdir -p %s" % (hdfs_path)
    subprocess.call("ssh -o 'StrictHostKeyChecking no' -o 'UserKnownHostsFile=/dev/null' -i /home/ubuntu/.ssh/bigsea ubuntu@%s '%s'" % (master, hadoop_command), shell=True)

def push(master, local_path, hdfs_path):
    hadoop_mkdir_command = ("export HADOOP_USER_NAME=ubuntu && hadoop fs "
                            "-fs hdfs://%(master)s:8020/ -mkdir -p "
                            "%(path)s" % {'master': master,
                                          'path': hdfs_path})

    subprocess.call("ssh -o 'StrictHostKeyChecking no' -o 'UserKnownHostsFile=/dev/null' -i /home/ubuntu/.ssh/bigsea ubuntu@%s '%s'" % (master, hadoop_mkdir_command), shell=True)

    hadoop_command = ("export HADOOP_USER_NAME=ubuntu && hadoop fs -fs "
                      "hdfs://%(master)s:8020/ -put %(local_path)s "
                      "%(hdfs_path)s" % {'master': master,
                                         'local_path': local_path,
                                         'hdfs_path': hdfs_path})

    subprocess.call("ssh -o 'StrictHostKeyChecking no' -o 'UserKnownHostsFile=/dev/null' -i /home/ubuntu/.ssh/bigsea ubuntu@%s '%s'" % (master, hadoop_command), shell=True)
