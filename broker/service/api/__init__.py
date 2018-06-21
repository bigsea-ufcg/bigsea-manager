# Copyright (c) 2017 UFGG-LSD.
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

import ConfigParser


try:
    config = ConfigParser.RawConfigParser()
    config.read('./broker.cfg')
    
    # General configuration
    host = config.get("general", "host")
    port = config.getint('general', 'port')
    plugins = config.get('general', 'plugins').split(',')

    # Validate if really exists a section to listed plugins
    for plugin in plugins:
        if plugin not in config.sections():
            raise Exception("plugin '%s' section missing" % plugin)

    if 'developer' in plugins:
        public_key = config.get('developer', 'public_key')
        key_path = config.get('developer', 'key_path')
        project_id = config.get('developer', 'project_id')
        auth_ip = config.get('developer', 'auth_ip')
        user = config.get('developer', 'user')
        password = config.get('developer', 'password')
        domain = config.get('developer', 'user_domain_name')

except Exception as e:
    print "Error: %s" % e.message
    quit()
