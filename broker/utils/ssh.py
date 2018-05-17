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

import paramiko


def get_connection(ip, username=None, password=None, key_path=None):

    # Preparing SSH connection
    conn = paramiko.SSHClient()
    conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Checking if the connection will be established using
    # keys or passwords
    if key_path != "" and key_path is not None:
        keypair = paramiko.RSAKey.from_private_key_file(key_path)
        conn.connect(hostname=ip, username=username, pkey=keypair)
    else:
        conn.connect(hostname=ip, username=username, password=password)

    return conn
