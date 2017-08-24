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

def execute_command(key, master, command):
    subprocess.call("ssh -o 'StrictHostKeyChecking no' -o 'UserKnownHostsFile=/dev/null' -i %s ubuntu@%s %s" % (key, master, command), shell=True)

def copy(key, source, destination):
    subprocess.call("scp -i %s -r %s %s" % (key, source, destination), shell=True)

