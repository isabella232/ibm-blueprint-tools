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

import blueprint.schema.param as param
import blueprint.schema.source as src

from blueprint.lib.validator import ModuleValidator
from blueprint.lib.validator import BPError

from blueprint.lib.logger import logr
# import logging
# logr = logging.getLogger(__name__)

def eprint(*args, **kwargs):
    logr.error(*args)
    print(*args, file=sys.stderr, **kwargs)

#========================================================================
TerraformType = "terraform"

class Module(dict):
    def __init__(self, name, type=TerraformType, source={}, inputs=None, outputs=None, settings=None):
        self.name = name
        self.module_type = type
        self.source = source
        self.inputs = []
        self.outputs = []
        self.settings = []
        self.set_inputs(inputs)
        self.set_outputs(outputs)
        self.set_settings(settings)

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
        if self.name == None:
            del self.name
        if self.module_type == None:
            del self.module_type
        if self.source == None:
            del self.source

        if self.inputs == None or (self.inputs != None and len(self.inputs) == 0):
            del self.inputs
        else:
            for p in self.inputs:
                p.remove_null_entries()

        if self.outputs == None or (self.outputs != None and len(self.outputs) == 0):
            del self.outputs
        else:
            for p in self.outputs:
                p.remove_null_entries()

        if self.settings == None or (self.settings != None and len(self.settings) == 0):
            del self.settings
        else:
            for p in self.settings:
                p.remove_null_entries()

    def to_yaml(self):
        # yaml.encoding = None
        errors = self.validate(BPError)
        eprint(errors)
        return yaml.dump(self, sort_keys=False)

    @classmethod
    def from_json(cls, data):
        name = data['name']
        try:
            module_type = data['module_type']
        except KeyError:
            module_type = None
        try:
            source = src.Source.from_json(data['source'])
        except KeyError:
            source = None
        try:
            inputs = []
            for p in data['inputs']:
                inputs.append(param.Input.from_json(p))
        except (KeyError, UnboundLocalError, TypeError):
            inputs = None
        try:
            outputs = []
            for p in data['outputs']:
                outputs.append(param.Output.from_json(p))
        except (KeyError, UnboundLocalError, TypeError):
            outputs = None
        try:
            settings = []
            for p in data['settings']:
                settings.append(param.Setting.from_json(p))
        except (KeyError, UnboundLocalError, TypeError):
            settings = None
        
        return cls(name, module_type, source, inputs, outputs, settings)

    def validate(self, level=BPError):
        mod_validator = ModuleValidator()
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
        return self.validate(BPError)

    def module_ref(self, key):
        try:
            return self.input_ref(key)
        except:
            try:
                return self.output_ref(key)
            except:
                try:
                    return self.setting_ref(key)
                except:
                    raise ValueError('Module input parameter not found')

    def input_ref(self, key):
        if hasattr(self, "inputs"):
            for p in self.inputs:
                if p.name == key:
                    return "$module." + self.name + ".inputs." + key
        raise ValueError('Module input parameter not found')

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
                    return "$module." + self.name + ".outputs." + key
        raise ValueError('Module output parameter not found')

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
                    return "$module." + self.name + ".settings." + key
        raise ValueError('Module settings parameter not found')

    def find_setting_ref(self, value_ref):
        if hasattr(self, "settings"):
            for p in self.settings:
                if p.value == value_ref:
                    return p.name
        return None

    def set_source(self, source):
        errors = source.validate(BPError)
        self.source = source
        return errors

    def set_inputs(self, input_params):
        errors = []
        if(input_params == None):
            self.inputs = []
            return errors
        for param in input_params:
            errors += param.validate(BPError)
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
            errors += param.validate(BPError)
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
            errors += param.validate(BPError)
        if len(errors) == 0:
            for param in setting_params:
                self.settings.append(param)
        return errors

    def set_input_value(self, param_name, param_value):
        errors = []
        param_copy = []
        for p in self.inputs:
            if p.name == param_name:
                p.value = param_value
            e = p.validate(BPError)
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
            e = p.validate(BPError)
            if len(e) == 0:
                param_copy.append(p)
            errors += e
        self.inputs = param_copy
        return errors

    def set_output_value(self, param_name, param_value):
        errors = []
        param_copy = []
        for p in self.outputs:
            if p.name == param_name:
                p.value = param_value
            e = p.validate(BPError)
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
            e = p.validate(BPError)
            if len(e) == 0:
                param_copy.append(p)
            errors += e
        self.outputs = param_copy
        return errors

    def set_setting_value(self, param_name, param_value):
        errors = []
        param_copy = []
        for p in self.settings:
            if p.name == param_name:
                p.value = param_value
            e = p.validate(BPError)
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
            e = p.validate(BPError)
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
