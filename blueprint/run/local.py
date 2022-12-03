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
from git import Repo
import giturlparse
from pathlib import Path
import shutil

class PsuedoGenTemplate:
    def __init__(self, git_url, mod):
        self.git_url = git_url
        self.mod_name = mod.name

        cwd = os.getcwd()
        d = Path(os.path.join(cwd, mod.name))
        if d.exists() and d.is_dir():
            shutil.rmtree(d)

        p = giturlparse.parse(git_url)
        folder_name = p.name
        # print(mod.name + "/" + folder_name)
        d = Path(os.path.join(Path(cwd), mod.name, folder_name))
        if d.exists() and d.is_dir():
            shutil.rmtree(d)
        d.mkdir(parents=True, exist_ok=True)
        os.chdir(d)
        self.working_dir = d
        
        self.generate_vars_tf(mod.inputs)
        self.generate_output_tf(mod.outputs)
        os.chdir(cwd)

        # if p.resource != None:
        #     new_git_url = git_url[0:git_url.find(p.resource)]
        # else:
        #     new_git_url = git_url
        # Clone all the files from the git repo
        # Repo.clone_from(new_git_url, mod.name)
        # self.working_dir = os.path.join(Path(cwd), mod.name)

        # Remove unnecessary files from the cloned git repo (in the local file-system)
        # files = os.listdir(self.working_dir)
        # for f in files:
        #     if f != str(p.name):
        #         d = Path(os.path.join(cwd, mod.name, f))
        #         if d.exists() and d.is_dir():
        #             shutil.rmtree(d)
        #         if d.exists() and d.is_file():
        #             # TODO: Don't remove the blueprint.tfstate & blueprint.tfvars files
        #             os.remove(d)
        # self.working_dir = os.path.join(Path(cwd), mod.name, p.name)
        # os.chdir(cwd)

    def get_working_dir(self):
        return self.working_dir

    def generate_vars_tf(self, mod_inputs):
        
        var_temp_str1 = 'variable "{}" {{ \n  description = "About variable {}."\n}}\n\n'
        var_temp_str2 = 'variable "{}" {{ \n  description = "About variable {}."\n  default = "{}"\n}}\n\n'

        if mod_inputs == None:
            with open("vars.tf", 'w') as var_file:
                var_file.write("# Generated empty input var file \n\n")
            return
        else:
            with open("vars.tf", 'w') as var_file:
                var_file.write("# Generated input var file \n\n")
                for p in mod_inputs:
                    if p.type == None or p.value == None:
                        var_file.write(var_temp_str1.format(p.name, p.name))
                    else:
                        if p.type.lower() == "string" :
                            var_file.write(var_temp_str2.format(p.name, p.name, p.value))
                        elif p.type.lower() == "boolean" :
                            if p.value == True:
                                var_file.write(var_temp_str2.format(p.name, p.name, 'True'))
                            else:
                                var_file.write(var_temp_str2.format(p.name, p.name, 'False'))
                        elif p.type.lower() == "number" or p.type.tolower() == "integer" :
                            var_file.write(var_temp_str2.format(p.name, p.name, p.value))
                        elif p.type.lower() == "date" or p.type.tolower() == "date-time" :
                            var_file.write(var_temp_str2.format(p.name, p.name, "2000-12-30 19:21:03.478039"))
                        else:
                            var_file.write(var_temp_str1.format(p.name, p.name))

    def generate_output_tf(self, mod_outputs):

        output_temp_str1 = 'output "{}" {{\n  value = "{}"\n}}\n\n'
        if mod_outputs == None:
            with open("output.tf", 'w') as var_file:
                var_file.write("# Generated empty output file \n\n")
            return
        else:
            with open("output.tf", 'w') as var_file:
                var_file.write("# Generated output file \n\n")
                for p in mod_outputs:
                    var_file.write(output_temp_str1.format(p.name, p.name))
