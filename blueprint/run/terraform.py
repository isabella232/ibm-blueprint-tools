# (C) Copyright IBM Corp. 2022.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from python_terraform import *

class TerraformRunner(Terraform):

    def __init__(self, working_dir, var_file=None):
        super().__init__(working_dir = working_dir, var_file = var_file)

    def init(self, capture_output = False, no_color=IsFlagged, raise_on_error = False):
        # print("terraform init")
        return super().init(capture_output, no_color=no_color, raise_on_error = raise_on_error)
    
    def plan(self, capture_output = False, no_color=IsFlagged, raise_on_error = False):
        # print("terraform plan")
        return super().plan(capture_output=capture_output, no_color=no_color, raise_on_error = raise_on_error)

    def apply(self, capture_output = False, no_color=IsFlagged, raise_on_error = False, skip_plan = True):
        # print("terraform apply")
        return super().apply(capture_output=capture_output, no_color=no_color, raise_on_error = raise_on_error, skip_plan = skip_plan)

    def output(self):
        # print("terraform output")
        return super().output()

