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

import blueprint.schema.module as module
import blueprint.schema.param as param

from blueprint.lib.validator import BlueprintValidator
from blueprint.lib.validator import BPError
from blueprint.lib.validator import BPWarning

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
#========================================================================

BlueprintType = "blueprint"

class Blueprint(dict):
    yaml_tag = u'!Blueprint'
    def __init__(self, 
                    name, type="blueprint", description=None, 
                    inputs=None, outputs=None, settings=None,
                    modules=None):
        self.schema_version = "1.0.0"
        self.name = name
        self.type = type
        self.modules = []
        if(description != None):
            self.description = description
        if(inputs != None):
            self.set_inputs(inputs)
        if(outputs != None):
            self.set_outputs(outputs)
        if(settings != None):
            self.set_settings(settings)
        if(modules != None):
            self.set_modules(modules)

    def __str__(self):
        txt = "Blueprint("
        txt += "name:" + (self.name if hasattr(self, 'name') else 'None') + ", "
        txt += "inputs:" + str(self.inputs if hasattr(self, 'inputs') else 'None') + ", "
        txt += "outputs:" + str(self.outputs if hasattr(self, 'outputs') else 'None') + ", "
        txt += "settings:" + str(self.settings if hasattr(self, 'settings') else 'None') + ", "
        txt += "modules:" + str(self.modules if hasattr(self, 'modules') else 'None')
        txt += ")"
        return txt

    def __repr__(self):
        return self.__str__()

    def noop(self, *args, **kw):
        pass
        
    yaml.emitter.Emitter.process_tag = noop

    def remove_null_entries(self):
        if self.name == None:
            del self.name
        if self.type == None:
            del self.type
        if self.schema_version == None:
            del self.schema_version
        if self.description == None:
            del self.description

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

        if self.modules == None or (self.modules != None and len(self.modules) == 0):
            del self.modules
        else:
            for m in self.modules:
                m.remove_null_entries()

    def to_yaml(self, stream = None):
        self.remove_null_entries()
        errors = self.validate(BPWarning)
        eprint(errors)

        return yaml.safe_load(self.to_yaml_str())

    def to_yaml_str(self, stream = None) -> str:
        self.remove_null_entries()
        errors = self.validate(BPWarning)
        if len(errors) > 0:
            eprint(errors)
        return yaml.dump(self, sort_keys=False)


    def generate_input_file(self, stream = None):
        inputs_data = {}
        for p in self.inputs:
            if p.type != None:
                if p.type.lower() == "string" :
                    inputs_data[p.name] = "sample string for " + p.name
                elif p.type.lower() == "boolean" :
                    inputs_data[p.name] = False
                elif p.type.lower() == "number" or p.type.tolower() == "integer" :
                    inputs_data[p.name] = 0
                elif p.type.lower() == "date" or p.type.tolower() == "date-time" :
                    inputs_data[p.name] = "2000-12-30 19:21:03.478039"
                else:
                    inputs_data[p.name] = ""
            else:
                inputs_data[p.name] = ""

        return yaml.dump(inputs_data, sort_keys=False)

    def from_yaml_str(self, yaml_str):
        data = yaml.safe_load(yaml_str)
        # print(data)
        self.name = data['name']
        self.schema_version = data['schema_version']
        self.type = data['type']
        try:
            self.description = data['description']
        except KeyError:
            self.description = None
        
        try:
            self.inputs=[]
            for p in data['inputs']:
                self.inputs.append(param.Input.from_json(p))
        except (KeyError, UnboundLocalError, TypeError):
            self.inputs = None

        try:
            self.outputs=[]
            for p in data['outputs']:
                self.outputs.append(param.Output.from_json(p))
        except (KeyError, UnboundLocalError, TypeError):
            self.outputs = None

        try:
            self.settings=[]
            for p in data['settings']:
                self.settings.append(param.Setting.from_json(p))
        except (KeyError, UnboundLocalError, TypeError):
            self.settings = None

        try:
            self.modules=[]
            for d in data['modules']:
                self.modules.append(module.Module.from_json(d))
        except (KeyError, UnboundLocalError, TypeError):
            self.modules = None

    def validate(self, level=BPError):
        bp_validator = BlueprintValidator()
        return bp_validator.validate_blueprint(self, level)

    def input_ref(self, key):
        for p in self.inputs:
            if p.name == key:
                return "$blueprint.inputs." + key
        raise ValueError('Blueprint input parameter not found')

    def output_ref(self, key):
        for p in self.outputs:
            if p.name == key:
                return "$blueprint.outputs." + key
        raise ValueError('Blueprint output parameter not found')

    def setting_ref(self, key):
        for p in self.settings:
            if p.name == key:
                return "$blueprint.settings." + key
        raise ValueError('Blueprint settings parameter not found')

    def module_ref(self, mod_name, key):
        m = self.get_module(mod_name)
        if m != None:
            return m.module_ref(key)
        raise ValueError('Invalid module name')

    def module_input_ref(self, mod_name, key):
        m = self.get_module(mod_name)
        if m != None:
            return m.input_ref(key)
        raise ValueError('Invalid module name')

    def module_output_ref(self, mod_name, key):
        m = self.get_module(mod_name)
        if m != None:
            return m.output_ref(key)
        raise ValueError('Invalid module name')

    def module_setting_ref(self, mod_name, key):
        m = self.get_module(mod_name)
        if m != None:
            return m.setting_ref(key)
        raise ValueError('Invalid module name')

    def set_inputs(self, input_params):
        errors = []
        if(input_params == None):
            self.inputs = None
            return errors
        for param in input_params:
            errors += param.validate(BPError)
        self.inputs = []
        if len(errors) == 0:
            for param in input_params:
                self.inputs.append(param)
        return errors

    def add_input(self, input_param):
        if self.inputs == None:
            self.inputs = []
        errors = input_param.validate(BPError)
        if len(errors) == 0:
            self.inputs.append(input_param)
        return errors

    def add_inputs(self, input_params):
        if self.inputs == None:
            self.inputs = []
        errors = []
        for param in input_params:
            errors += param.validate(BPError)
        if len(errors) == 0:
            for param in input_params:
                self.inputs.append(param)
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

    def set_outputs(self, output_params):
        errors = []
        if(output_params == None):
            self.outputs = None
            return errors
        for param in output_params:
            errors += param.validate(BPError)
        self.outputs = []
        if len(errors) == 0:
            for param in output_params:
                self.outputs.append(param)
        return errors

    def add_output(self, output_param):
        if self.outputs == None:
            self.outputs = []
        errors = output_param.validate(BPError)
        if len(errors) == 0:
            self.outputs.append(output_param)
        return errors

    def add_outputs(self, output_params):
        errors = []
        if self.outputs == None:
            self.outputs = []
        for param in output_params:
            errors += param.validate(BPError)
        if len(errors) == 0:
            for param in output_params:
                self.outputs.append(param)
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

    def set_settings(self, setting_params):
        errors = []
        if(setting_params == None):
            self.settings = None
            return
        for param in setting_params:
            errors += param.validate(BPError)
        self.settings = []
        if len(errors) == 0:
            for param in setting_params:
                self.settings.append(param)
        return errors

    def add_setting(self, setting_param):
        if self.settings == None:
            self.settings = []
        errors = setting_param.validate(BPError)
        if len(errors) == 0:
            self.settings.append(setting_param)
        return errors

    def add_settings(self, setting_params):
        errors = []
        if self.settings == None:
            self.settings = []
        for param in setting_params:
            errors += param.validate(BPError)
        if len(errors) == 0:
            for param in setting_params:
                self.settings.append(param)
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

    def get_module(self, mod_name):
        for m in self.modules:
            if mod_name == m.name:
                return m
        raise ValueError('Invalid module name: ' + str(mod_name))

    def set_modules(self, mods):
        if(mods == None):
            self.modules = None
            return
        self.modules = []
        errors = []
        for mod in mods:
            errors += mod.validate(BPError)
        if len(errors) == 0:
            self.modules.append(mods)
        return errors

    def add_module(self, mod):
        errors = mod.validate(BPError)
        if len(errors) == 0:
            self.modules.append(mod)
        return errors

    def add_modules(self, mods):
        if(mods == None):
            self.modules = None
            return
        errors = []
        for mod in mods:
            errors += mod.validate(BPError)
        if len(errors) == 0:
            self.modules.append(mods)
        return errors

    def update_module(self, mod):
        errors = []
        if mod != None:
            if self.modules == None:
                self.modules = []
            try:
                m = self.get_module(mod.name)
                errors += m.merge(mod)
                return errors
            except:  
                self.modules.append(mod)
        return errors

    def set_module_inputs(self, mod_name, inputs):
        try:
            m = self.get_module(mod_name)
            if m != None:
                m.set_inputs(inputs)
            else:
                raise ValueError('Invalid module name')
        except:  
            raise ValueError('Invalid module name')

#========================================================================

