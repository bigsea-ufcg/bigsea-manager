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


def write_file_to(remote_file, data, run_as_root=False, timeout=120):
    """Create remote file and write the given data to it.

    Uses existing ssh connection.
    """


def append_to_file(r_file, data, run_as_root=False, timeout=120):
    """Append the given data to remote file.

    Uses existing ssh connection.
    """


def write_files_to(files, run_as_root=False, timeout=120):
    """Copy file->data dictionary in a single ssh connection."""


def append_to_files(files, run_as_root=False, timeout=120):
    """Copy file->data dictionary in a single ssh connection."""


def read_file_from(remote_file, run_as_root=False, timeout=120):
    """Read remote file from the specified host and return given data."""


def execute_command(remote, key_path, command):
    command = ('ssh -i %(key_path)s ubuntu@%(remote)s %(command)s' %
               {'remote': remote, 'key_path': key_path, 'command': command})

    subprocess.call(command, shell=True)


def copy_to_remote(remote, key_path, source, destination):
    command = ('scp -i %(key_path)s -r %(source)s %(destination)s' %
               {'key_path': key_path, 'source': source,
                'destination': destination})

    subprocess.call(command, shell=True)
