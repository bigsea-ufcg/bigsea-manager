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

from application_manager.utils import shell

def job_params(swift, connector, args):
    in_paths = []
    others = []
    container = get_container(args[0])

    for arg in args:
        if arg.startswith('swift://'):
            if connector.check_file_exists(swift, container,
                                           get_path(arg)):
                in_paths.append(get_path(arg))
            else:
                out_path = get_path(arg)
        else:
            others.append(arg)

    return in_paths, out_path, others, container

def get_path(arg):
    splitted = arg.split('/')
    swift_path = splitted[3]

    for i in range(len(splitted[4:])):
        swift_path = swift_path + '/' + splitted[i+4]

    return swift_path

def get_container(arg):
    splitted = arg.split('/')
    container = splitted[2]

    return container

def download(connector, swiftclient, swift_path, local_path, container):
    new_local_path = local_path

    for path in swift_path:
        for obj in swiftclient.get_container(container)[1]:
            if obj['name'].startswith(path) and not obj['name'][len(obj['name'])-1] != '/':
                splitted = obj['name'].split('/')
                new_local_path = local_path + splitted[len(splitted)-2]+'/'
                shell.make_directory(local_path + splitted[len(splitted)-2])

            if obj['name'].startswith(path) and obj['name'][len(obj['name'])-1] != '/':
                connector.download_file(swiftclient, obj['name'], new_local_path, container)
