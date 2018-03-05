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

import logging
import os
import texttable
import time
from datetime import datetime


class Log:
    def __init__(self, name, output_file_path):
        self._verify_existing_paths()
        self.logger = logging.getLogger(name)
        if not len(self.logger.handlers):
            handler = logging.StreamHandler()
            handler.setLevel(logging.INFO)
            self.logger.addHandler(handler)
            handler = logging.FileHandler(output_file_path)
            self.logger.addHandler(handler)

    def log(self, text):
        self.logger.info(text)

    def _verify_existing_paths(self):
        if not os.path.exists('logs'):
            os.mkdir('logs')

class TableLog:
    def __init__(self, name, output_file_path):
        self.logger = Log(name, output_file_path)
        self.table = texttable.Texttable()
        self.table.set_cols_align(["c", "c", "c", "c"])
        self.table.set_cols_width([8, 15, 15, 60])
        
    def log(self, app_id, plugin_name, action):
        timestamp = time.strftime("%H:%M:%S")

        line = [timestamp, app_id, plugin_name, action]
        self.table.add_row(line)
        last_line = self.table.draw().split('\n')[-2]
        self.logger.log(last_line)

    def header_log(self):
        header_row = [["Time", "Execution ID", "Plugin Name", "Action"]]
        self.table.add_rows(header_row)
        last_line = self.table.draw().split('\n')[:3]
        self.logger.log(last_line[0])
        self.logger.log(last_line[1])
        self.logger.log(last_line[2])

def configure_logging():
    logging.basicConfig(level=logging.INFO)
