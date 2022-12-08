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
import yaml
from yaml.loader import SafeLoader
from os.path import exists as file_exists
import re

from typing import List, Union
from blueprint.lib import event
from blueprint.lib import bfile 
from blueprint.schema import param, module, blueprint

class BlueprintManifest:
    def __init__(self, 
                    name: str                                 = "__init__", 
                    description: str                          = None, 
                    inputs: List[Union[str, param.Input]]     = None,  
                    outputs: List[Union[str, param.Output]]   = None, 
                    settings: List[Union[str, param.Setting]] = None,
                    modules: List[Union[str, module.Module]]  = None,
                    manifest_file_location: str               = None ):
        
        """Blueprint Manifest schema.

        :param name: Name of the blueprint
        :param description: Blueprint description
        :param inputs: List of input manifest files (str) or input parameter (type param.Input)
        :param outputs: List of output manifest files (str) or output parameters (type param.Output)
        :param settings: List of settings manifest files (str) or environment settings (type param.Setting)
        :param modules: List of module manifest files (str) or module data (type module.Module)
        :param manifest_file_location: Base file location of the manifest file 
        """
        self.name = name
        self.description = description

        self.inputs = inputs
        self.outputs = outputs
        self.settings = settings
        self.modules = modules
        self.manifest_file_location = manifest_file_location

    def generate_blueprint(self):
        error = []
        bp = blueprint.Blueprint(name = self.name, description = self.description)
        (bp1, e) = self._load_inputs(bp)
        error += e
        if e == None:
            bp = bp1
        (bp1, e) = self._load_outputs(bp)
        error += e
        if e == None:
            bp = bp1
        (bp1, e) = self._load_settings(bp)
        error += e
        if e == None:
            bp = bp1
        (bp1, e) = self._load_modules(bp)
        error += e
        if e == None:
            bp = bp1
        
        return bp, error

    def _hasattr(self, yaml, attr):
        try:
            x = yaml[attr]
            return True
        except KeyError:
            return False

    def _merge(self, obj_arr, yaml_arr):
        result = []
        names = []
        for obj in obj_arr:
            if(obj.name in names):
                self.bperrors.append(event.ValidationEvent(event.BPWarning, 'Duplicate parameter name: ' + obj.name))
            names.append(obj.name)
            result.append(obj)
        
        if isinstance(yaml_arr, dict):
            entry={}
            for key, value in yaml_arr.items():
                if key == "name":
                    if(value in names):
                        self.bperrors.append(event.ValidationEvent(event.BPWarning, 'Duplicate parameter name: ' + value))
                    names.append(value)
                entry[key]= value
            result.append(entry)
        else:
            for entry in yaml_arr:
                if(entry['name'] in names):
                    self.bperrors.append(event.ValidationEvent(event.BPWarning, 'Duplicate parameter name: ' + entry['name']))
                names.append(entry['name'])
                result.append(entry)
    
        return result

    @classmethod
    def from_yaml_file(cls, filename):
        if not file_exists(filename):
            raise ValueError('Blueprint manifest file does not exist')

        manifest_file_location = os.path.dirname(os.path.abspath(filename))
        yaml_data = bfile.FileHelper.load(filename)        
        
        bp = BlueprintManifest.from_yaml_data(yaml_data)
        return cls(bp.name, bp.description, 
                    bp.inputs, bp.outputs, bp.settings,
                    bp.modules, manifest_file_location)

    @classmethod
    def from_yaml_str(cls, yaml_str):
        yaml_data = yaml.safe_load(yaml_str)
        bp = BlueprintManifest.from_yaml_data(yaml_data)
        return cls(bp.name, bp.description, 
                    bp.inputs, bp.outputs, bp.settings,
                    bp.modules)

    @classmethod
    def from_yaml_data(cls, yaml_data):
        errors = []

        # (result, errors) = BlueprintManifest.validate(yaml_data)

        name = yaml_data['name']
        try:
            description = yaml_data['description']
        except KeyError:
            description = None
            errors.append(event.ValidationEvent(event.BPInfo, 'No description in the blueprint manifest file'))
        
        try:
            inputs=[]
            for p in yaml_data['inputs']:
                # inputs.append(param.Input.from_yaml(p))
                inputs.append(p)
        except (KeyError, UnboundLocalError, TypeError):
            inputs = None
            errors.append(event.ValidationEvent(event.BPInfo, 'No inputs in the blueprint manifest file'))

        try:
            outputs=[]
            for p in yaml_data['outputs']:
                # outputs.append(param.Output.from_yaml(p))
                outputs.append(p)
        except (KeyError, UnboundLocalError, TypeError):
            outputs = None
            errors.append(event.ValidationEvent(event.BPInfo, 'No outputs in the blueprint manifest file'))

        try:
            settings=[]
            for p in yaml_data['settings']:
                # settings.append(param.Setting.from_yaml(p))
                settings.append(p)
        except (KeyError, UnboundLocalError, TypeError):
            settings = None
            errors.append(event.ValidationEvent(event.BPInfo, 'No settings in the blueprint manifest file'))

        try:
            modules=[]
            for d in yaml_data['modules']:
                # modules.append(module.Module.from_yaml(d))
                modules.append(d)
        except (KeyError, UnboundLocalError, TypeError):
            modules = None
            errors.append(event.ValidationEvent(event.BPInfo, 'No modules in the blueprint manifest file'))

        # TODO: What to do with the errors / info ?

        return cls(name, description, 
                    inputs, outputs, settings, modules)


    def _load_inputs(self, bpyaml):
        """
        Load the input manifest files, and update the inputs section in the blueprint (bpyaml)
        """
        errors = []
        if self.inputs == None:
            errors.append(event.ValidationEvent(event.BPInfo, 'No inputs in the blueprint manifest file'))
            self.inputs = []

        cwd = os.getcwd()
        for input in self.inputs:
            if isinstance(input, str):
                m = re.search('\$\{\{(.*?)\}\}', input)
                if m:
                    input_filename = m.group(1)
                    rel_input_filename = os.path.basename(input_filename)
                    rel_input_filename = os.path.join(self.manifest_file_location, rel_input_filename)
                    input_yaml = bfile.FileHelper.load(rel_input_filename)
                    if self._hasattr(input_yaml, 'inputs') and input_yaml['inputs'] == None:
                        errors.append(event.ValidationEvent(event.BPWarning, 'Invalid inputs yaml stucture, skipping ' + input_filename))
                    else:
                        if (not hasattr(bpyaml, 'inputs')) or bpyaml.inputs == None:
                            bpyaml.inputs = param.Input.from_yaml_list(input_yaml['inputs'])
                        else:
                            bpyaml_inputs = self._merge(bpyaml.inputs, input_yaml['inputs'])
                            bpyaml.inputs = param.Input.from_yaml_list(bpyaml_inputs)
                else :
                    errors.append(event.ValidationEvent(event.BPError, 'Error parsing the input string: ' + str(input)))
            elif isinstance(input, param.Input):
                if hasattr(input, 'name'):
                    if not self._hasattr(bpyaml, 'inputs') or bpyaml.inputs == None:
                        bpyaml.inputs = param.Input.from_yaml_list([input])
                    else:
                        bpyaml_inputs = self._merge(bpyaml.inputs, input)
                        bpyaml.inputs = param.Input.from_yaml_list(bpyaml_inputs)
                else:
                    errors.append(event.ValidationEvent(event.BPError, 'Invalid input definition'))
            else :
                errors.append(event.ValidationEvent(event.BPError, 'Unknown input section: ' + str(input)))
        
        os.chdir(cwd)
        return (bpyaml, errors)


    def _load_outputs(self, bpyaml):
        """
        Load the output manifest files, and update the outputs section in the blueprint (bpyaml)
        """
        errors = []
        if self.outputs == None:
            errors.append(event.ValidationEvent(event.BPWarning, 'No outputs in the blueprint manifest file'))
            self.outputs = []
            
        cwd = os.getcwd()
        for output in self.outputs:
            if isinstance(output, str):
                m = re.search('\$\{\{(.*?)\}\}', output)
                if m:
                    output_filename = m.group(1)
                    rel_output_filename = os.path.basename(output_filename)
                    rel_output_filename = os.path.join(self.manifest_file_location, rel_output_filename)
                    output_yaml = bfile.FileHelper.load(rel_output_filename)
                    if self._hasattr(output_yaml, 'outputs') and output_yaml['outputs'] == None:
                        errors.append(event.ValidationEvent(event.BPWarning, 'Invalid outputs yaml stucture, skipping ' + output_filename))
                    else:
                        if not hasattr(bpyaml, 'outputs') or bpyaml.outputs == None:
                            bpyaml.outputs = param.Output.from_yaml_list(output_yaml['outputs'])
                        else:
                            bpyaml_outputs = self._merge(bpyaml.outputs, output_yaml['outputs'])
                            bpyaml.outputs = param.Output.from_yaml_list(bpyaml_outputs)
                else :
                    errors.append(event.ValidationEvent(event.BPError, 'Error parsing the output string: ' + str(output)))
            elif isinstance(output, param.Output):
                if hasattr(output, 'name'):
                    if not hasattr(bpyaml, 'outputs') or bpyaml.outputs == None:
                        bpyaml.outputs = param.Output.from_yaml_list([output])
                    else:
                        bpyaml_outputs = self._merge(bpyaml.outputs, output)
                        bpyaml.outputs = param.Output.from_yaml_list(bpyaml_outputs)
                else:
                    errors.append(event.ValidationEvent(event.BPError, 'Invalid output definition'))
            else :
                errors.append(event.ValidationEvent(event.BPError, 'Unknown output section: ' + str(output)))
       
        os.chdir(cwd)
        return (bpyaml, errors)

    def _load_settings(self, bpyaml):
        """
        Load the setting manifest files, and update the settings section in the blueprint (bpyaml)
        """
        errors = []
        if self.settings == None:
            errors.append(event.ValidationEvent(event.BPInfo, 'No settings in the blueprint manifest file'))
            self.settings = []

        cwd = os.getcwd()
        for setting in self.settings:
            if isinstance(setting, str):
                m = re.search('\$\{\{(.*?)\}\}', setting)
                if m:
                    setting_filename = m.group(1)
                    rel_setting_filename = os.path.basename(setting_filename)
                    rel_setting_filename = os.path.join(self.manifest_file_location, rel_setting_filename)
                    setting_yaml = bfile.FileHelper.load(rel_setting_filename)
                    if self._hasattr(setting_yaml, 'settings') and setting_yaml['settings'] == None:
                        errors.append(event.ValidationEvent(event.BPWarning, 'Invalid settings yaml stucture, skipping ' + setting_filename))
                    else:
                        if not hasattr(bpyaml, 'settings') or bpyaml.settings == None:
                            bpyaml.settings = param.Setting.from_yaml_list(setting_yaml['settings'])
                        else:
                            bpyaml_settings = self._merge(bpyaml.settings, setting_yaml['settings'])
                            bpyaml.settings = param.Setting.from_yaml_list(bpyaml_settings)
                else :
                    errors.append(event.ValidationEvent(event.BPError, 'Error parsing the setting string: ' + str(setting)))
            elif isinstance(setting, param.Input):
                if hasattr(setting, 'name'):
                    if not hasattr(bpyaml, 'settings') or bpyaml.settings == None:
                        bpyaml.settings = param.Setting.from_yaml_list([setting])
                    else:
                        bpyaml_settings = self._merge(bpyaml.settings, setting)
                        bpyaml.settings = param.Setting.from_yaml_list(bpyaml_settings)
                else:
                    errors.append(event.ValidationEvent(event.BPError, 'Invalid setting definition'))
            else :
                errors.append(event.ValidationEvent(event.BPError, 'Unknown setting section: ' + str(setting)))
        
        os.chdir(cwd)
        return (bpyaml, errors)


    def _load_modules(self, bpyaml):
        """
        Load the module manifest files, and update the modules section in the blueprint (bpyaml)
        """
        errors = []
        if self.modules == None:
            errors.append(event.ValidationEvent(event.BPWarning, 'No modules in the blueprint manifest file'))

        cwd = os.getcwd()
        for mod in self.modules:
            if isinstance(mod, str):
                m = re.search('\$\{\{(.*?)\}\}', mod)
                if m:
                    mod_filename = m.group(1)
                    rel_mod_filename = os.path.basename(mod_filename)
                    rel_mod_filename = os.path.join(self.manifest_file_location, rel_mod_filename)
                    mod_yaml = bfile.FileHelper.load(rel_mod_filename)
                    if self._hasattr(mod_yaml, 'modules') and mod_yaml['modules'] == None:
                        errors.append(event.ValidationEvent(event.BPWarning, 'Invalid modules yaml stucture, skipping ' + mod_filename))
                    else:
                        if not hasattr(bpyaml, 'modules') or bpyaml.modules == None:
                            bpyaml.modules = module.Module.from_yaml_list(mod_yaml['modules'])
                        else:
                            bpyaml_modules = self._merge(bpyaml.modules, mod_yaml['modules'])
                            bpyaml.modules = module.Module.from_yaml_list(bpyaml_modules)
                else :
                    errors.append(event.ValidationEvent(event.BPError, 'Error parsing the module string: ' + str(mod)))
            elif isinstance(mod, module.Module):
                if hasattr(mod, 'name'):
                    if not hasattr(bpyaml, 'modules') or bpyaml.modules == None:
                        bpyaml.modules = module.Module.from_yaml_list([mod])
                    else:
                        bpyaml_modules = self._merge(bpyaml.modules, mod)
                        bpyaml.modules = module.Module.from_yaml_list(bpyaml_modules)
                else:
                    errors.append(event.ValidationEvent(event.BPError, 'Invalid module definition'))
            else :
                errors.append(event.ValidationEvent(event.BPError, 'Unknown module section: ' + str(mod)))
        
        os.chdir(cwd)
        return (bpyaml, errors)

    @classmethod
    def validate(cls, bp_manifest):
        result = True
        errors = []
        if bp_manifest == None:
            errors.append(event.ValidationEvent(event.BPError, 'Load the blueprint manifest file, before validating'))
            result = False
        else:
            if not hasattr(bp_manifest, 'name'):
                errors.append(event.ValidationEvent(event.BPError, 'Blueprint manifest file must have a name'))
                result = False

            if not hasattr(bp_manifest, 'schema_version'):
                errors.append(event.ValidationEvent(event.BPError, 'Blueprint manifest file must have a schema_version'))
                result = False

            if not hasattr(bp_manifest, 'type'):
                errors.append(event.ValidationEvent(event.BPError, 'Blueprint manifest file must have a type'))
                result = False

        return (result, errors)

