# (C) Copyright IBM Corp. 2022.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
import yaml

from os.path import exists as file_exists
import giturlparse

from blueprint.schema import blueprint
from blueprint.schema import module
from blueprint.schema import param
from blueprint.schema import source as src

from blueprint.lib import git
from blueprint.lib import event
from blueprint.lib import bfile

from python_terraform import *

import subprocess

from blueprint.lib.logger import logr
# import logging
# logr = logging.getLogger(__name__)

def eprint(*args, **kwargs):
    logr.error(*args)
    print(*args, file=sys.stderr, **kwargs)

class BlueprintMorphius:

    def __init__(self, name: str, 
                description: str = '', 
                modules: module.Module = None):
        self.name = name
        self.description = description
        self.modules = modules

    @classmethod
    def from_yaml_file(cls, filename):
        if not file_exists(filename):
            raise ValueError('Blueprint manifest file does not exist')

        yaml_data = bfile.FileHelper.load(filename)        

        bp = BlueprintMorphius.from_yaml_data(yaml_data)
        return cls(bp.name, bp.description, bp.modules)

    @classmethod
    def from_yaml_str(cls, yaml_str):
        yaml_data = yaml.safe_load(yaml_str)
        bp = BlueprintMorphius.from_yaml_data(yaml_data)
        return cls(bp.name, bp.description, bp.modules)

    @classmethod
    def from_yaml_data(cls, yaml_data):
        name = yaml_data['name']
        try:
            description = yaml_data['description']
        except KeyError:
            description = None
        
        modules=[]
        try:
            modules = yaml_data['modules']
        except KeyError:
            modules=[]

        try:
            git_sources = yaml_data['git_sources']
            for s in git_sources:
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
                source = src.TemplateSource('github', git_source)

                modules.append(module.Module(name, module_type, source))

        except (KeyError, UnboundLocalError, TypeError) as e:
            logr.debug('Attribute error while reading & initializing modules from git_sources' + str(e))

        return cls(name, description, modules)

    def sync_blueprint(self, working_dir, annotate=False):
        cwd = os.getcwd()

        tic_path = os.getenv('TERRAFORM_CONFIG_INSPECT_PATH')
        if tic_path == None:
            err_msg = 'Could not find terraform-config-inspect.  Install and set install path in environment $TERRAFORM_CONFIG_INSPECT_PATH'
            logr.error(err_msg)
            raise ValueError('err_msg')

        if not os.path.exists(working_dir):
            logr.info('Working directory does not exists.  Creating the required working director : ' + str(os.path.abspath(working_dir)))
            os.makedirs(working_dir, exist_ok=True)
        working_dir = os.path.abspath(working_dir)
        os.chdir(working_dir)

        bp = blueprint.Blueprint(name = self.name, description = self.description, modules = self.modules)
        if bp.modules != None and len(bp.modules) > 0:
            for mod in bp.modules:
                git_url = mod.source.git.git_repo_url
                if hasattr(mod.source.git, 'git_token'):
                    git_token = mod.source.git.git_token
                else:
                    git_token = None
                
                downloader = git.GitDownloadTemplate(git_url, git_token, mod.name)
                wd = downloader.get_working_dir()

                result = subprocess.run([os.path.join(tic_path, 'terraform-config-inspect'), wd, '--json'], stdout=subprocess.PIPE)
                config_json = result.stdout
                config_json_data = yaml.safe_load(config_json)

                if config_json != None:
                    config_json_data = yaml.safe_load(config_json)
                    input_vars = list(config_json_data['variables'].keys())
                    logr.info('Processing inputs: ' + str(input_vars))
                    existing_input_vars = mod.get_input_var_names()

                    for key in input_vars:
                        # If key already present in the 'mod', then skip
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
                            description=''
                        if 'default' in value.keys():
                            val=value['default']
                        else:
                            val=None
                        if annotate:
                            p = param.Input(key, type=type, description='_sync: add> ' + description, value=val)
                        else:
                            p = param.Input(key, type=type, description=description, value=val)
                        mod.inputs.append(p)

                    input_vars = list(config_json_data['variables'].keys())
                    existing_input_vars = mod.get_input_var_names()
                    for key in existing_input_vars:
                        if key not in input_vars:
                            value = mod.get_input_attr(key, 'description')
                            if value == None:
                                value = ''

                            if annotate:
                                if '_sync: delete >' not in value:
                                    mod.set_input_attr(key, 'description', '_sync: delete> ' + value)
                            else:
                                mod.set_input_attr(key, 'description', value)
                        
                    output_vars = list(config_json_data['outputs'].keys())
                    logr.info('Processing outputs: ' + str(output_vars))
                    existing_output_vars = mod.get_output_var_names()
                    for key in output_vars:
                        # If key already present in the 'mod', then skip
                        if key in existing_output_vars:
                            continue

                        value = config_json_data['outputs'][key]
                        if 'description' in value.keys():
                            description=value['description']
                        else:
                            description=''
                        if annotate:
                            p = param.Output(key, description='_sync: add> ' + description)
                        else:
                            p = param.Output(key, description=description)
                        mod.outputs.append(p)

                    output_vars = list(config_json_data['outputs'].keys())
                    existing_output_vars = mod.get_input_var_names()
                    for key in existing_output_vars:
                        if key not in output_vars:
                            value = mod.get_output_attr(key, 'description')
                            if value == None:
                                value = ''

                            if annotate:
                                if '_sync: delete >' not in value:
                                    mod.set_output_attr(key, 'description', '_sync: delete> ' + value)
                            else:
                                mod.set_output_attr(key, 'description', value)

        os.chdir(cwd)
        return bp

