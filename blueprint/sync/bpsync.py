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
import yaml

import giturlparse

from blueprint.schema import blueprint
from blueprint.schema import module
from blueprint.schema import param
from blueprint.schema import source as src

from blueprint.lib import git
from blueprint.lib import event

from python_terraform import *

import subprocess

from blueprint.lib.logger import logr
# import logging
# logr = logging.getLogger(__name__)

def eprint(*args, **kwargs):
    logr.error(*args)
    print(*args, file=sys.stderr, **kwargs)

class BlueprintMorphius:

    def __init__(self, blueprint_lite_file, working_dir = '.'):
        self.tic_path = os.getenv("TERRAFORM_CONFIG_INSPECT_PATH")
        if self.tic_path == None:
            err_msg = "Could not find terraform-config-inspect.  Install and set install path in environment $TERRAFORM_CONFIG_INSPECT_PATH"
            logr.error(err_msg)
            raise ValueError("err_msg")

        self.blueprint_lite_file = blueprint_lite_file

        if not os.path.exists(working_dir):
            os.makedirs(working_dir, exist_ok=True)

        self.working_dir = os.path.abspath(working_dir)
        self.errors = []
        self.lite = None
        self.bp = blueprint.Blueprint("Temp")
        self.config_variables = []
        self.config_output = []

        self.load_bplite_file()

    def load_bplite_file(self):
        logr.debug("Loading blueprint lite file " + self.blueprint_lite_file + " ...")
        with open(self.blueprint_lite_file) as f:
            yaml_str = f.read()
            data = yaml.safe_load(yaml_str)
            try:
                sources = data['git_sources']
                self.from_bplite_yaml_str(yaml_str)
            except KeyError:
                self.bp.from_yaml_str(yaml_str)
        
        logr.info("Success loading blueprint lite file " + self.blueprint_lite_file)

    def from_bplite_yaml_str(self, yaml_str):
        data = yaml.safe_load(yaml_str)
        # print(data)
        self.bp.name = data['name']
        try:
            self.bp.schema_version = data['schema_version']
        except:
            self.bp.schema_version = '1.0.0'
        try:
            self.bp.type = data['type']
        except KeyError:
            self.bp.type = 'blueprint'
        try:
            self.bp.description = data['description']
        except KeyError:
            self.bp.description = None
        
        try:
            self.bp.modules=[]
            for s in data['git_sources']:
                git_url = s['git_repo_url']
                try:
                    git_branch = s['git_branch']
                except KeyError:
                    git_branch = None
                try:
                    git_token = s['git_token']
                except KeyError:
                    git_token = None
                p = giturlparse.parse(git_url)
                name = p.name
                module_type = 'terraform'
                git_source = src.GitSource(git_url, git_branch, git_token)
                source = src.Source('github', git_source)
                self.bp.modules.append(module.Module(name, module_type, source))
        except (KeyError, UnboundLocalError, TypeError) as e:
            logr.debug("Attribute error while reading & initializing modules" + str(e))
            self.bp.modules = None

    def sync(self):
        cwd = os.getcwd()
        if self.bp.modules != None and len(self.bp.modules) > 0:
            for mod in self.bp.modules:
                git_url = mod.source.git.git_repo_url
                if hasattr(mod.source.git, 'git_token'):
                    git_token = mod.source.git.git_token
                else:
                    git_token = None
                
                if os.path.exists(self.working_dir):
                    os.chdir(self.working_dir)
                else:
                    os.makedirs(self.working_dir, exist_ok=True)
                    os.chdir(self.working_dir)

                downloader = git.GitDownloadTemplate(git_url, git_token, mod.name)
                wd = downloader.get_working_dir()
                result = subprocess.run([os.path.join(self.tic_path, 'terraform-config-inspect'), wd, '--json'], stdout=subprocess.PIPE)
                config_json = result.stdout
                config_json_data = yaml.safe_load(config_json)

                if config_json != None:
                    config_json_data = yaml.safe_load(config_json)
                    # self.config_variables.append(config_json_data['variables'])
                    input_vars = list(config_json_data['variables'].keys())
                    print("inputs: " + str(input_vars))
                    existing_input_vars = mod.get_input_var_names()
                    for key in input_vars:
                        # If key already present in the "mod", then skip
                        if key in existing_input_vars:
                            continue

                        value = config_json_data['variables'][key]
                        if 'type' in value.keys():
                            type=value['type']
                        else:
                            type=None
                        if 'description' in value.keys():
                            description=value['description']
                        else:
                            description=""
                        if 'default' in value.keys():
                            val=value['default']
                        else:
                            val=None
                        p = param.Input(key, type=type, description="bpsync: add> " + description, value=val)
                        mod.inputs.append(p)

                    input_vars = list(config_json_data['variables'].keys())
                    existing_input_vars = mod.get_input_var_names()
                    for key in existing_input_vars:
                        if key not in input_vars:
                            value = mod.get_input_attr(key, "description")
                            if value != None:
                                if "bpsync: delete >" not in value:
                                    mod.set_input_attr(key, "description", "bpsync: delete> " + value)
                            else:
                                mod.set_input_attr(key, "description",  "bpsync: delete> ")
                        
                    output_vars = list(config_json_data['outputs'].keys())
                    print("outputs: " + str(output_vars))
                    existing_output_vars = mod.get_output_var_names()
                    for key in output_vars:
                        # If key already present in the "mod", then skip
                        if key in existing_output_vars:
                            continue

                        value = config_json_data['outputs'][key]
                        if 'description' in value.keys():
                            description=value['description']
                        else:
                            description=""
                        p = param.Output(key, description="bpsync: add> " + description)
                        mod.outputs.append(p)

                    output_vars = list(config_json_data['outputs'].keys())
                    existing_output_vars = mod.get_input_var_names()
                    for key in existing_output_vars:
                        if key not in output_vars:
                            value = mod.get_output_attr(key, 'description')
                            if value != None:
                                if "bpsync: delete >" not in value:
                                    mod.set_output_attr(key, 'description', "bpsync: delete> " + value)
                            else:
                                mod.set_output_attr(key, 'description', "bpsync: delete> ")

                os.chdir(cwd)
        return self.bp

    def get_errors(self):

        return self.errors
