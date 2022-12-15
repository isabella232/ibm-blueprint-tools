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
import sys
from blueprint.lib import git
from blueprint.lib import mock
from blueprint.lib import terraform
from blueprint.lib import event

from blueprint.lib.logger import logr
# import logging
# logr = logging.getLogger(__name__)

def eprint(*args, **kwargs):
    logr.error(*args)
    print(*args, file=sys.stderr, **kwargs)

class ModuleRunner:

    def __init__(self, parent, module, dry_run=False):
        self.parent = parent
        self.errors = []
        if dry_run:
            self.setup_dry_module(module)
        else:
            self.setup_module(module) # set modules, download template, set working_dir

    def setup_module(self, module):
        # Create a folder with the module name (or switch to the existing folder)
        if module == None:
            self.errors.append(event.ValidationEvent(event.BPError, "Error in blueprint modules", self))
            return
        self.module = module
        # Download the git repo to the module folder
        cwd = os.getcwd()
        git_url = self.module.source.git.git_repo_url
        if not hasattr(self.module.source.git, "git_token"):
            git_token = self.module.source.git.git_token
        else:
            git_token = None
        downloader = git.GitDownloadTemplate(git_url, git_token, self.module.name)
        self.working_dir = downloader.get_working_dir()

    def setup_dry_module(self, module):
        # Create a folder with the module name (or switch to the existing folder)
        if module == None:
            self.errors.append(event.ValidationEvent(event.BPError, "Error in blueprint modules", self))
            return
        self.module = module
        # Generate terraform template in the module folder
        cwd = os.getcwd()
        git_url = self.module.source.git.git_repo_url
        pseudoTemplate = mock.MockTemplate(git_url, self.module)
        self.working_dir = pseudoTemplate.get_working_dir()

    def get_errors(self):
        return self.errors

    def init_module(self):
        
        self.errors = []
        print("==================================================================")
        print("Preparing for terraform init : " + str(self.module.name))
        tfvars_file, self.errors = self.prepare_tfvars()
        self.set_env()
        tr = terraform.TerraformRunner(self.working_dir, var_file="blueprint.tfvars")
        print("Running terraform init : " + str(self.module.name))
        ret_code, stdout, stderr = tr.init()
        print("terraform init, return code: " + str(ret_code))
        # print(stdout)
        # eprint(stderr)
        print("==================================================================")
        return self.errors

    def plan_module(self):
        
        self.errors = []
        print("==================================================================")
        print("Preparing for terraform plan : " + str(self.module.name))
        tfvars_file, self.errors = self.prepare_tfvars()
        if len(self.errors) == 0:
            self.set_env()
            tr = terraform.TerraformRunner(self.working_dir, var_file="blueprint.tfvars")
            print("Running terraform plan : " + str(self.module.name))
            ret_code, stdout, stderr = tr.plan()
            print("terraform plan, return code: " + str(ret_code))
            # print(stdout)
            # eprint(stderr)
        else:
            self.errors.append(event.ValidationEvent(event.BPError, "Did not run plan, since all the input parameters have not been dereferenced"))
            print("Did not run terraform plan : " + str(self.module.name))

        print("==================================================================")
        return self.errors

    def apply_module(self):
        
        self.errors = []
        print("==================================================================")
        print("Preparing for terraform apply : " + str(self.module.name))
        tfvars_file, self.errors = self.prepare_tfvars()
        if len(self.errors) == 0:
            if self.module.inputs != None:
                input_data = {}
                for input in self.module.inputs:
                    if not (str(input.value).startswith("$")):
                        (mod_vars, err) = self.module.input_ref(input.name)
                        if err == None:
                            input_data[mod_vars] = input.value
                        else:
                            (mod_vars, err) = self.module.setting_ref(input.name)
                            if err == None:
                                input_data[mod_vars] = input.value
                            else:
                                input_data[input.name] = input.value
                self.parent.save_module_input_data(input_data)

            self.set_env()
            tr = terraform.TerraformRunner(self.working_dir, var_file="blueprint.tfvars")
            print("Running terraform apply : " + str(self.module.name))
            ret_code, stdout, stderr = tr.apply()
            print("terraform apply, return code: " + str(ret_code))
            # print(stdout)
            # eprint(stderr)

            out_dict = tr.output()
            # print("output : " + str(out_dict))
            module_output_data_names = []
            for output in self.module.outputs:
                module_output_data_names.append(output.name)

            if len(module_output_data_names) > 0:
                output_data = dict()
                for key in out_dict.keys():
                    if key in module_output_data_names:
                        (mod_vars, err) = self.module.output_ref(key)
                        if err == None:
                            output_data[mod_vars] = out_dict[key]["value"]
                        else:
                            self.errors.append(err)
                # print(output_data)
                self.parent.save_module_output_data(output_data)
        else:
            self.errors.append(event.ValidationEvent(event.BPError, "Did not run apply, some input parameters are not dereferenced"))
            print("Did not run terraform apply : " + str(self.module.name))

        print("==================================================================")
        return self.errors

    def destroy_module(self):
        
        self.errors = []
        print("==================================================================")
        print("Preparing for terraform destroy : " + str(self.module.name))
        tfvars_file, self.errors = self.prepare_tfvars()
        if len(self.errors) == 0:
            self.set_env()
            tr = terraform.TerraformRunner(self.working_dir, var_file="blueprint.tfvars")
            print("terraform destroy : " + str(self.module.name))
            ret_code, stdout, stderr = tr.destroy()
            print("terraform destroy, return code: " + str(ret_code))
            # print(stdout)
            # eprint(stderr)
        else:
            self.errors.append(event.ValidationEvent(event.BPError, "Did not run destroy, since all the input parameters have not been dereferenced"))
            print("Did not run terraform destroy : " + str(self.module.name))
        
        print("==================================================================")
        return self.errors

    def prepare_tfvars(self):

        inputs = self.module.inputs
        if inputs == None or inputs == "":
            return (None, self.errors)
        tfvars_str = ""
        for input in inputs:
            # TODO: Try to dereference the input values ?
            if str(input.value).startswith("$"):
                self.errors.append(event.ValidationEvent(event.BPWarning, "Parameter value is not dereferenced for " + input.name))
            else:
                if input.type != None: 
                    if input.type.lower() != "string":
                        tfvars_str += (input.name + ' = ' + str(input.value))
                    else:
                        tfvars_str += (input.name + ' = "' + str(input.value) + '"')    
                else:
                    # assume the type is string
                    tfvars_str += (input.name + ' = "' + str(input.value) + '"')
                tfvars_str += "\n"

        tfvars_file_name = os.path.join(self.working_dir, "blueprint.tfvars")
        with open(tfvars_file_name, "w") as tfvars_file:
            tfvars_file.write(tfvars_str)

        return (tfvars_str, self.errors)

    def set_env(self):

        settings = self.module.settings
        if settings == None or settings == "":
            return (None, self.errors)
        
        for env in settings:
            if str(env.value).startswith("$"):
                self.errors.append(event.ValidationEvent(event.BPWarning, "Parameter value is not dereferenced for " + env.name))
            else:
                os.environ[env.name] = str(env.value)
        
