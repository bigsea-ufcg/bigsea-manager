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

class RPredictor():
    def __init__(self):
        self.sh_handler = shell.Shell()
        self.pred_file = 'predictor.R'
        self.pred_unit = 2  # 2 horizons of 15 minutes = 30 minutes prediction

    def get_title(self):
        return 'R Predictor'

    def predict(self, hosts):
        cluster_size = 0
        for host in hosts:
            machines = self.sh_handler.execute_r_script(self.pred_file,
                                    [('%s.txt' % host),"%s" % self.pred_unit])
            cluster_size += machines

        return max(cluster_size, 3)