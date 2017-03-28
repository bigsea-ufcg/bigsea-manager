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

import datetime
import json

from application_manager.exceptions import *

from keystoneauth1.identity import v3
from keystoneauth1 import session
from saharaclient.api.client import Client as saharaclient
from subprocess import *

import sys

R_PREFIX = 'Rscript '
PYTHON_PREFIX = 'python '


class Shell(object):
    def execute_r_script(self, script, args):
        command = R_PREFIX + script + " " + " ".join(args)
        p_status = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        out, err = p_status.communicate()
        try:
            print(out, err)
            value = float(out)
            return value
        except Exception as e:
            print e
            print("Error message captured:", err)
            raise

    def execute_async_python_script(self, script, args):
        args = [str(i) + "\n" for i in args]
        command = PYTHON_PREFIX + script + " " + " ".join(args)
        p = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        for line in iter(p.stdout.readline, ''):
            line = line.replace('\r', '').replace('\n', '')
            print line
            sys.stdout.flush()


class ActionDispatcher(object):
    """Maps method name to local methods through action name."""

    def dispatch(self, *args, **kwargs):
        """Find and call local method."""
        action = kwargs.pop('action', 'default')
        action_method = getattr(self, str(action), self.default)
        return action_method(*args, **kwargs)

    def default(self, data):
        raise NotImplementedError()


class DictSerializer(ActionDispatcher):
    """Default request body serialization."""

    def serialize(self, data, action='default'):
        return self.dispatch(data, action=action)

    def default(self, data):
        return ""


class JSONDictSerializer(DictSerializer):
    """Default JSON request body serialization."""

    def default(self, data):
        def sanitizer(obj):
            if isinstance(obj, datetime.datetime):
                _dtime = obj - datetime.timedelta(microseconds=obj.microsecond)
                return _dtime.isoformat()
            return six.text_type(obj)
        return json.dumps(data, default=sanitizer)


class TextDeserializer(ActionDispatcher):
    """Default request body deserialization."""

    def deserialize(self, datastring, action='default'):
        return self.dispatch(datastring, action=action)

    def default(self, datastring):
        return {}


class JSONDeserializer(TextDeserializer):

    def _from_json(self, datastring):
        try:
            return json.loads(datastring)
        except ValueError:
            msg = ("cannot understand JSON")
            raise MalformedRequestBody(msg)

    def default(self, datastring):
        return {'body': self._from_json(datastring)}
