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
import yaml
import os
import subprocess

from broker.service import api

def load_yaml(redis_host):
    with open(api.scone_compose + "compose.scone.yml", "r") as scone_compose:
        actual_compose = yaml.load(scone_compose)
    try:
        cmd = actual_compose["services"]["copel-analytics"]["command"]
        cmd = cmd + (" %s" % redis_host)
        actual_compose["services"]["copel-analytics"]["command"] = cmd
    except yaml.YAMLError as e:
        print e
    print "creating dir: %s" % (api.scone_compose + redis_host)
    os.makedirs(api.scone_compose + redis_host)
    with open(api.scone_compose + "%s/compose.scone.yml" % redis_host, "w") as new_compose:
        yaml.dump(actual_compose, new_compose)
    return api.scone_compose + "%s/compose.scone.yml" % redis_host
    
def split(file_path):
    print "run: %s %s" % (api.scone_command, file_path)
    os.environ["RUST_BACKTRACE"] = "full"
    os.environ["HOME"] = "/home/igornsa"
    proc = subprocess.Popen(
        "%s %s" % (api.scone_command, file_path),
        shell=True
    )
    print "split successful"
    return proc.returncode
