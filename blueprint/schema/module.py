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

import yaml
import sys
from typing import List

from blueprint.schema import param
from blueprint.schema import source as src

from blueprint.validate import blueprint_validator
from blueprint.lib import event

from blueprint.lib.logger import logr
# import logging
# logr = logging.getLogger(__name__)

def eprint(*args, **kwargs):
    logr.error(*args)
    print(*args, file=sys.stderr, **kwargs)

#========================================================================
TerraformType = "terraform"

class Module(dict):
    def __init__(self, 
                    name: str                       = "__init__", 
                    type: str                       = TerraformType, 
                    source: src.TemplateSource              = {}, 
                    inputs: List[param.Input]       = None, 
                    outputs: List[param.Output]     = None, 
                    settings: List[param.Setting]   = None):
        """Module schema.

        :param name: Name of the module
        :param type: Type of module (default is `terraform`)
        :param source: Source of module - Git source or Catalog source
        :param inputs: List of input parameters (type param.Input)
        :param outputs: List of output parameters (type param.Output)
        :param settings: List of envitonment settings (type param.Setting)
        """
        self.name = name
        self.module_type = type
        self.source = source
        self.inputs = []
        self.outputs = []
        self.settings = []
        self.set_inputs(inputs)
        self.set_outputs(outputs)
        self.set_settings(settings)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.name = "__init__"

    def __str__(self):
        txt = "Modules("
        txt += "name:" + (self.name if hasattr(self, 'name') else 'None') + ", "
        txt += "type:" + (self.module_type if hasattr(self, 'module_type') else 'None') + ", "
        txt += "inputs:" + str(self.inputs if hasattr(self, 'inputs') else 'None') + ", "
        txt += "outputs:" + str(self.outputs if hasattr(self, 'outputs') else 'None') + ", "
        txt += "settings:" + str(self.settings if hasattr(self, 'settings') else 'None') + ", "
        txt += "source:" + str(self.source if hasattr(self, 'source') else 'None')
        txt += ")"
        return txt

    def __repr__(self):
        return self.__str__()

    def remove_null_entries(self):
        if hasattr(self, 'name') and self.name == None:
            del self.name
        if hasattr(self, 'module_type') and self.module_type == None:
            del self.module_type
        if hasattr(self, 'source') and self.source == None:
            del self.source

        if hasattr(self, 'inputs'):
            if self.inputs == None or (self.inputs != None and len(self.inputs) == 0):
                del self.inputs
            else:
                for p in self.inputs:
                    p.remove_null_entries()

        if hasattr(self, 'outputs'):
            if self.outputs == None or (self.outputs != None and len(self.outputs) == 0):
                del self.outputs
            else:
                for p in self.outputs:
                    p.remove_null_entries()

        if hasattr(self, 'settings'):
            if self.settings == None or (self.settings != None and len(self.settings) == 0):
                del self.settings
            else:
                for p in self.settings:
                    p.remove_null_entries()

    def to_yaml(self):
        # yaml.encoding = None
        errors = self.validate(event.BPError)
        # eprint(errors)
        return (yaml.dump(self, sort_keys=False), errors)

    @classmethod
    def from_yaml(cls, yaml_data):
        
        if isinstance(yaml_data, Module):
            return yaml_data

        name = yaml_data['name']
        try:
            module_type = yaml_data['module_type']
        except KeyError:
            module_type = None
        try:
            source = src.TemplateSource.from_yaml(yaml_data['source'])
        except KeyError:
            source = None
        try:
            inputs = []
            for p in yaml_data['inputs']:
                inputs.append(param.Input.from_yaml(p))
        except (KeyError, UnboundLocalError, TypeError):
            inputs = None
        try:
            outputs = []
            for p in yaml_data['outputs']:
                outputs.append(param.Output.from_yaml(p))
        except (KeyError, UnboundLocalError, TypeError):
            outputs = None
        try:
            settings = []
            for p in yaml_data['settings']:
                settings.append(param.Setting.from_yaml(p))
        except (KeyError, UnboundLocalError, TypeError):
            settings = None
        
        return cls(name, module_type, source, inputs, outputs, settings)


    @classmethod
    def from_yaml_list(cls, yaml_data_list):
        mods = []

        for yaml_data in yaml_data_list:
            mods.append(Module.from_yaml(yaml_data))

        return mods

    def validate(self, level=event.BPError):
        mod_validator = blueprint_validator.ModuleValidator()
        return mod_validator.validate_module(self, level)

    def input_value_refs(self):
        value_refs = []
        if hasattr(self, "inputs"):
            for p in self.inputs:
                if hasattr(p, "value") and isinstance(p.value, str) and (p.value != None and (p.value.startswith("$module.") or p.value.startswith("$blueprint."))):
                    value_refs.append(p.value)
        if hasattr(self, "settings"):
            for p in self.settings:
                if hasattr(p, "value") and isinstance(p.value, str) and (p.value != None and (p.value.startswith("$module.") or p.value.startswith("$blueprint."))):
                    value_refs.append(p.value)
        return value_refs

    def output_value_refs(self):
        value_refs = []
        if hasattr(self, "outputs"):
            for p in self.outputs:
                if hasattr(p, "value") and isinstance(p.value, str) and (p.value != None and (p.value.startswith("$module.") or p.value.startswith("$blueprint."))):
                    value_refs.append(p.value)
        return value_refs

    def merge(self, m):
        if self.name != m.name:
            raise ValueError('Module names do not match')
        self.module_type = m.module_type
        self.source = m.source
        self.set_inputs(m.inputs)
        self.set_outputs(m.outputs)
        self.set_settings(m.settings)
        return self.validate(event.BPError)

    def module_ref(self, key):
        (mod_vars, err) = self.input_ref(key)
        if err != None:
            (mod_vars, err) = self.output_ref(key)
            if err != None:
                (mod_vars, err) = self.setting_ref(key)
                if err != None:
                    return (None, event.ValidationEvent(event.BPWarning, 'Module input parameter not found', self))
                else:
                    return mod_vars
            else:
                return mod_vars
        else:
            return mod_vars

    def input_ref(self, key):
        if hasattr(self, "inputs"):
            for p in self.inputs:
                if p.name == key:
                    return ("$module." + self.name + ".inputs." + key, None)
        return (None, event.ValidationEvent(event.BPWarning, 'Module input parameter not found', self))

    def find_input_ref(self, value_ref):
        if hasattr(self, "inputs"):
            for p in self.inputs:
                if p.value == value_ref:
                    return p.name
        return None

    def output_ref(self, key):
        if hasattr(self, "outputs"):
            for p in self.outputs:
                if p.name == key:
                    return ("$module." + self.name + ".outputs." + key, None)
        return (None, event.ValidationEvent(event.BPWarning, 'Module output parameter not found', self))

    def output_refs(self):
        value_refs = []
        if hasattr(self, "outputs"):
            for p in self.outputs:
                value_refs.append("$module." + self.name + ".outputs." + p.name)
        return value_refs

    def find_output_ref(self, value_ref):
        if hasattr(self, "outputs"):
            for p in self.outputs:
                if p.value == value_ref:
                    return p.name
        return None

    def setting_ref(self, key):
        if hasattr(self, "settings"):
            for p in self.settings:
                if p.name == key:
                    return ("$module." + self.name + ".settings." + key, None)
        return (None, event.ValidationEvent(event.BPWarning, 'Module settings parameter not found', self))

    def find_setting_ref(self, value_ref):
        if hasattr(self, "settings"):
            for p in self.settings:
                if p.value == value_ref:
                    return p.name
        return None
    
    def get_input_var_names(self):
        var_names = []
        if self.inputs != None and len(self.inputs) == 0:
            return var_names

        for p in self.inputs:
            var_names.append(p.name)
        
        return var_names

    def get_output_var_names(self):
        var_names = []
        if self.outputs != None and len(self.outputs) == 0:
            return var_names        

        for p in self.outputs:
            var_names.append(p.name)
        
        return var_names

    def get_setting_var_names(self):
        var_names = []
        if self.settings != None and len(self.settings) == 0:
            return var_names        

        for p in self.settings:
            var_names.append(p.name)
        
        return var_names

    def set_source(self, source):
        errors = source.validate(event.BPError)
        self.source = source
        return errors

    def set_inputs(self, input_params):
        errors = []
        if(input_params == None):
            self.inputs = []
            return errors
        for param in input_params:
            errors += param.validate(event.BPError)
        if len(errors) == 0:
            for param in input_params:
                self.inputs.append(param)
        return errors

    def set_outputs(self, output_params):
        errors = []
        if(output_params == None):
            self.outputs = []
            return errors
        for param in output_params:
            errors += param.validate(event.BPError)
        if len(errors) == 0:
            for param in output_params:
                self.outputs.append(param)
        return errors

    def set_settings(self, setting_params):
        errors = []
        if(setting_params == None):
            self.settings = []
            return errors
        for param in setting_params:
            errors += param.validate(event.BPError)
        if len(errors) == 0:
            for param in setting_params:
                self.settings.append(param)
        return errors

    def get_input_attr(self, param_name, param_attr):
        for p in self.inputs:
            if p.name == param_name:
                if hasattr(p, param_attr):
                    return getattr(p, param_attr)
                else:
                    return None
        return None

    def set_input_attr(self, param_name, param_attr, param_value):
        errors = []
        param_copy = []
        for p in self.inputs:
            if p.name == param_name:
                setattr(p, param_attr, param_value)
            e = p.validate(event.BPError)
            if len(e) == 0:
                param_copy.append(p)
            errors += e
        self.inputs = param_copy
        return errors

    def set_input_value(self, param_name, param_value):
        errors = []
        param_copy = []
        for p in self.inputs:
            if p.name == param_name:
                p.value = param_value
            e = p.validate(event.BPError)
            if len(e) == 0:
                param_copy.append(p)
            errors += e
        self.inputs = param_copy
        return errors

    def update_input(self, param):
        errors = []
        param_copy = []
        for p in self.inputs:
            if p.name == param.name:
                p.merge(param)
            e = p.validate(event.BPError)
            if len(e) == 0:
                param_copy.append(p)
            errors += e
        self.inputs = param_copy
        return errors

    def get_output_attr(self, param_name, param_attr):
        for p in self.outputs:
            if p.name == param_name:
                if hasattr(p, param_attr):
                    return getattr(p, param_attr)
                else:
                    return None
        return None

    def set_output_attr(self, param_name, param_attr, param_value):
        errors = []
        param_copy = []
        for p in self.outputs:
            if p.name == param_name:
                setattr(p, param_attr, param_value)
            e = p.validate(event.BPError)
            if len(e) == 0:
                param_copy.append(p)
            errors += e
        self.outputs = param_copy
        return errors

    def set_output_value(self, param_name, param_value):
        errors = []
        param_copy = []
        for p in self.outputs:
            if p.name == param_name:
                p.value = param_value
            e = p.validate(event.BPError)
            if len(e) == 0:
                param_copy.append(p)
            errors += e
        self.outputs = param_copy
        return errors

    def update_output(self, param):
        errors = []
        param_copy = []
        for p in self.outputs:
            if p.name == param.name:
                p.merge(param)
            e = p.validate(event.BPError)
            if len(e) == 0:
                param_copy.append(p)
            errors += e
        self.outputs = param_copy
        return errors

    def get_setting_attr(self, param_name, param_attr):
        for p in self.settings:
            if p.name == param_name:
                if hasattr(p, param_attr):
                    return getattr(p, param_attr)
                else:
                    return None
        return None

    def set_setting_attr(self, param_name, param_attr, param_value):
        errors = []
        param_copy = []
        for p in self.settings:
            if p.name == param_name:
                setattr(p, param_attr, param_value)
            e = p.validate(event.BPError)
            if len(e) == 0:
                param_copy.append(p)
            errors += e
        self.settings = param_copy
        return errors

    def set_setting_value(self, param_name, param_value):
        errors = []
        param_copy = []
        for p in self.settings:
            if p.name == param_name:
                p.value = param_value
            e = p.validate(event.BPError)
            if len(e) == 0:
                param_copy.append(p)
            errors += e
        self.settings = param_copy
        return errors

    def update_setting(self, param):
        errors = []
        param_copy = []
        for p in self.settings:
            if p.name == param.name:
                p.merge(param)
            e = p.validate(event.BPError)
            if len(e) == 0:
                param_copy.append(p)
            errors += e
        self.settings = param_copy
        return errors

    def delete_output(self, param):
        param_copy = []
        found = False
        for p in self.outputs:
            if p.name != param.name:
                param_copy.append(p)
            else:
                found = True
        self.outputs = param_copy
        return found

    def delete_input(self, param):
        param_copy = []
        found = False
        for p in self.inputs:
            if p.name != param.name:
                param_copy.append(p)
            else:
                found = True
        self.inputs = param_copy
        return found


    def delete_setting(self, param):
        param_copy = []
        found = False
        for p in self.settings:
            if p.name != param.name:
                param_copy.append(p)
            else:
                found = True
        self.settings = param_copy
        return found

#========================================================================
