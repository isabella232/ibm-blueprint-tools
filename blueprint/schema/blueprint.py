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
import re

from blueprint.schema import module
from blueprint.schema import param

from blueprint.lib import dag
from blueprint.lib import event
from blueprint.validate import blueprint_validator

from blueprint.lib.logger import logr
# import logging
# logr = logging.getLogger(__name__)

def eprint(*args, **kwargs):
    logr.error(*args)
    print(*args, file=sys.stderr, **kwargs)
#========================================================================

BlueprintType = "blueprint"

class Blueprint(dict):
    yaml_tag = u'!Blueprint'
    def __init__(self, 
                    name: str                       = "__init__", 
                    description: str                = None, 
                    inputs: List[param.Input]       = None, 
                    outputs: List[param.Output]     = None, 
                    settings: List[param.Setting]   = None,
                    modules: List[module.Module]    = None ):
        """Blueprint schema.

        :param name: Name of the blueprint
        :param description: Blueprint description
        :param inputs: List of input parameters (type param.Input)
        :param outputs: List of output parameters (type param.Output)
        :param settings: List of envitonment settings (type param.Setting)
        :param modules: List of modules in the blueprint (type module.Module)
        """

        self.schema_version = "1.0.0"
        self.type = BlueprintType
        self.name = name
        self.modules = []
        if(description != None):
            self.description = description
        else:
            self.description = None
        if(inputs != None):
            self.set_inputs(inputs)
        else:
            self.inputs = None
        if(outputs != None):
            self.set_outputs(outputs)
        else:
            self.outputs = None
        if(settings != None):
            self.set_settings(settings)
        else:
            self.settings = None
        if(modules != None):
            self.set_modules(modules)
        else:
            self.modules = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.name = "__init__"

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

    def __eq__(self, other):
        if other == None:
            return False

        self_name = "" if self.name == None else self.name
        self_schema_version = "" if self.schema_version == None else self.schema_version
        self_type = "" if not hasattr(self, 'type') or self.type == None else self.type
        self_description = "" if not hasattr(self, 'description') or self.description == None else self.description
        self_inputs = "" if not hasattr(self, 'inputs') or self.inputs == None else str(self.inputs)
        self_outputs = "" if not hasattr(self, 'outputs') or self.outputs == None else str(self.outputs)
        self_settings = "" if not hasattr(self, 'settings') or self.settings == None else str(self.settings)
        self_modules = "" if not hasattr(self, 'modules') or self.modules == None else str(self.modules)

        other_name = "" if other.name == None else other.name
        other_schema_version = "" if other.schema_version == None else other.schema_version
        other_type = "" if not hasattr(other, 'type') or other.type == None else other.type
        other_description = "" if not hasattr(other, 'description') or other.description == None else other.description
        other_inputs = "" if not hasattr(other, 'inputs') or other.inputs == None else str(other.inputs)
        other_outputs = "" if not hasattr(other, 'outputs') or other.outputs == None else str(other.outputs)
        other_settings = "" if not hasattr(other, 'settings') or other.settings == None else str(other.settings)
        other_modules = "" if not hasattr(other, 'modules') or other.modules == None else str(other.modules)

        return (self_name == other_name) and (self_type == other_type) and (self_schema_version == other_schema_version) \
            and (self_description == other_description) and (self_modules == other_modules) \
            and (self_inputs == other_inputs) and (self_outputs == other_outputs) and (self_settings == other_settings)

    def __hash__(self):
        self_name = "" if self.name == None else self.name
        self_schema_version = "" if self.schema_version == None else self.schema_version
        self_type = "" if not hasattr(self, 'type') or self.type == None else self.type
        self_description = "" if not hasattr(self, 'description') or self.description == None else self.description
        self_inputs = "" if not hasattr(self, 'inputs') or self.inputs == None else str(self.inputs)
        self_outputs = "" if not hasattr(self, 'outputs') or self.outputs == None else str(self.outputs)
        self_settings = "" if not hasattr(self, 'settings') or self.settings == None else str(self.settings)
        self_modules = "" if not hasattr(self, 'modules') or self.modules == None else str(self.modules)

        return hash((self_name, self_schema_version, self_type, self_description, self_inputs, self_outputs, self_settings, self_modules))


    def remove_null_entries(self):
        if self.name == None:
            del self.name
        if hasattr(self, 'type') and self.type == None:
            del self.type
        if hasattr(self, 'schema_version') and self.schema_version == None:
            del self.schema_version
        if hasattr(self, 'description') and self.description == None:
            del self.description

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

        if hasattr(self, 'modules'):
            if self.modules == None or (self.modules != None and len(self.modules) == 0):
                del self.modules
            else:
                for m in self.modules:
                    m.remove_null_entries()

    def to_yaml(self, stream = None):
        self.remove_null_entries()
        errors = self.validate()
        # eprint(errors)

        return (yaml.safe_load(self.to_yaml_str()), errors)

    def _process_comment(self, s):
        out_str = ""
        re_loc = re.finditer(pattern='comment:', string=s)
        loc = [ind.start() for ind in re_loc]
        start = 0
        for i in loc:
            out_str += s[start:i]
            j = s.find("'", i)
            out_str += s[i:j+1]
            j += 1

            while True:
                k = s.find("'", j)
                n = s.find("\n", j)
                if k < n:
                    out_str += s[j:k+1]
                    start = k+1
                    break
                else:
                    out_str += s[j:n+1]
                    k = n+1
                    lenn = 0
                    while True:
                        if s[k] != ' ':
                            break
                        k += 1
                        lenn += 1
                    k = 0
                    while k < lenn-2:
                        out_str += ' '
                        k += 1
                    out_str += '#'
                    out_str += ' '
                    j=n+1+lenn
                    start = j
        return out_str

    def to_yaml_str(self, do_validate = True, stream = None) -> str:
        self.remove_null_entries()
        errors = []
        if do_validate:
            errors = self.validate()
            # if len(errors) > 0:
            #     eprint(errors)
        yaml_str = yaml.dump(self, sort_keys=False)
        yaml_str = yaml_str.replace("comment: ", "# comment: ")
        yaml_str = self._process_comment(yaml_str)
        return (yaml_str, errors)

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

    @classmethod
    def from_yaml_str(cls, yaml_str):
        yaml_data = yaml.safe_load(yaml_str)
        bp = Blueprint.from_yaml_data(yaml_data)
        return cls(bp.name, bp.description, 
                    bp.inputs, bp.outputs, bp.settings,
                    bp.modules)

    @classmethod
    def from_yaml_data(cls, yaml_data):
        value_ref = dict()
        name = yaml_data['name']
        try:
            description = yaml_data['description']
        except KeyError:
            description = None
        
        try:
            inputs=[]
            for p in yaml_data['inputs']:
                in_param = param.Input.from_yaml(p)
                value_ref.update({"$blueprint." + in_param.name : "$blueprint.inputs." + in_param.name})
                inputs.append(in_param)
        except (KeyError, UnboundLocalError, TypeError):
            inputs = None

        try:
            outputs=[]
            for p in yaml_data['outputs']:
                out_param = param.Output.from_yaml(p)
                value_ref.update({"$blueprint." + out_param.name : "$blueprint.outputs." + out_param.name})
                outputs.append(out_param)

        except (KeyError, UnboundLocalError, TypeError):
            outputs = None

        try:
            settings=[]
            for p in yaml_data['settings']:
                env_param = param.Setting.from_yaml(p)
                value_ref.update({"$blueprint." + env_param.name : "$blueprint.settings." + env_param.name})
                settings.append(env_param)

        except (KeyError, UnboundLocalError, TypeError):
            settings = None

        try:
            modules=[]
            for d in yaml_data['modules']:
                mod = module.Module.from_yaml(d)
                mod.repair_module(value_ref)
                modules.append(mod)
                
        except (KeyError, UnboundLocalError, TypeError):
            modules = None

        return cls(name, description, 
                    inputs, outputs, settings, modules)

    def validate(self):
        bp_validator = blueprint_validator.BlueprintModel(self)
        return bp_validator.validate()

    def input_ref(self, key):
        if hasattr(self, "inputs") and self.inputs != None:
            for p in self.inputs:
                if p.name == key:
                    return ("$blueprint.inputs." + key, None)
        return (None, event.ValidationEvent(event.BPWarning, 'Blueprint input parameter not found', self))

    def output_ref(self, key):
        if hasattr(self, "outputs") and self.outputs != None:
            for p in self.outputs:
                if p.name == key:
                    return ("$blueprint.outputs." + key, None)
        return (None, event.ValidationEvent(event.BPWarning, 'Blueprint output parameter not found', self))

    def setting_ref(self, key):
        if hasattr(self, "settings") and self.settings != None:
            for p in self.settings:
                if p.name == key:
                    return ("$blueprint.settings." + key, None)
        return (None, event.ValidationEvent(event.BPWarning, 'Blueprint settings parameter not found', self))

    def module_ref(self, mod_name, key):
        if hasattr(self, "modules") and self.modules != None:
            (m, err) = self.get_module(mod_name)
            if err == None:
                (mod_ref, err) = m.module_ref(key)
                if err == None:
                    return (mod_ref, None)
                else:
                    return (None, err)
            else:
                return (None, err)
        return (None, event.ValidationEvent(event.BPWarning, 'Invalid modules in blueprint', self))

    def module_input_ref(self, mod_name, key):
        (m, err) = self.get_module(mod_name)
        if err == None:
            (mod_ref, err) = m.input_ref(key)
            if err == None:
                return (mod_ref, None)
            else:
                return (None, event.ValidationEvent(event.BPWarning, 'Invalid module input, in the blueprint', self, None, chain = err))
        else:
            return (None, event.ValidationEvent(event.BPWarning, 'Invalid module input, in the blueprint', self, None, chain = err))

    def module_output_ref(self, mod_name, key):
        (m, err) = self.get_module(mod_name)
        if err == None:
            (mod_ref, err) = m.output_ref(key)
            if err == None:
                return (mod_ref, None)
            else:
                return (None, event.ValidationEvent(event.BPWarning, 'Invalid module output in blueprint', self, None, chain=err))
        else:
            return (None, event.ValidationEvent(event.BPWarning, 'Invalid module output in blueprint', self, None, chain=err))

    def module_setting_ref(self, mod_name, key):
        (m, err) = self.get_module(mod_name)
        if err == None:
            (mod_ref, err) = m.setting_ref(key)
            if err == None:
                return (mod_ref, None)
            else:
                return (None, event.ValidationEvent(event.BPWarning, 'Invalid module setting in blueprint', self, None, chain=err))
        else:
            return (None, event.ValidationEvent(event.BPWarning, 'Invalid module setting in blueprint', self, None, chain=err))

    def get_input_var_names(self):
        if hasattr(self, "inputs") and self.inputs != None:
            param_names = []
            for p in self.inputs:
                param_names.append(p.name)
            return param_names
        return None

    def set_inputs(self, input_params):
        errors = []
        if(input_params == None):
            self.inputs = None
            return errors
        for param in input_params:
            errors += param.validate()
        self.inputs = []
        if len(errors) == 0:
            for param in input_params:
                self.inputs.append(param)
        return errors

    def add_input(self, input_param):
        if self.inputs == None:
            self.inputs = []
        errors = input_param.validate()
        if len(errors) == 0:
            self.inputs.append(input_param)
        return errors

    def add_inputs(self, input_params):
        if self.inputs == None:
            self.inputs = []
        errors = []
        for param in input_params:
            errors += param.validate()
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
            e = p.validate()
            if len(e) == 0:
                param_copy.append(p)
            errors += e
        self.inputs = param_copy
        return errors

    def get_output_var_names(self):
        if hasattr(self, "outputs") and self.outputs != None:
            param_names = []
            for p in self.outputs:
                param_names.append(p.name)
            return param_names
        return None

    def set_outputs(self, output_params):
        errors = []
        if(output_params == None):
            self.outputs = None
            return errors
        for param in output_params:
            errors += param.validate()
        self.outputs = []
        if len(errors) == 0:
            for param in output_params:
                self.outputs.append(param)
        return errors

    def add_output(self, output_param):
        if self.outputs == None:
            self.outputs = []
        errors = output_param.validate()
        if len(errors) == 0:
            self.outputs.append(output_param)
        return errors

    def add_outputs(self, output_params):
        errors = []
        if self.outputs == None:
            self.outputs = []
        for param in output_params:
            errors += param.validate()
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
            e = p.validate()
            if len(e) == 0:
                param_copy.append(p)
            errors += e
        self.outputs = param_copy
        return errors

    def get_setting_var_names(self):
        if hasattr(self, "inputs") and self.inputs != None:
            param_names = []
            for p in self.settings:
                param_names.append(p.name)
            return param_names
        return None

    def set_settings(self, setting_params):
        errors = []
        if(setting_params == None):
            self.settings = None
            return
        for param in setting_params:
            errors += param.validate()
        self.settings = []
        if len(errors) == 0:
            for param in setting_params:
                self.settings.append(param)
        return errors

    def add_setting(self, setting_param):
        if self.settings == None:
            self.settings = []
        errors = setting_param.validate()
        if len(errors) == 0:
            self.settings.append(setting_param)
        return errors

    def add_settings(self, setting_params):
        errors = []
        if self.settings == None:
            self.settings = []
        for param in setting_params:
            errors += param.validate()
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
            e = p.validate()
            if len(e) == 0:
                param_copy.append(p)
            errors += e
        self.settings = param_copy
        return errors

    def get_modules(self):
        return self.modules

    def get_module(self, mod_name):
        for m in self.modules:
            if mod_name == m.name:
                return (m, None)
        return (None, event.ValidationEvent(event.BPWarning, 'Invalid module name: ' + str(mod_name), self))

    def set_modules(self, mods):
        if(mods == None):
            self.modules = None
            return
        self.modules = []
        errors = []
        for mod in mods:
            e = mod.validate()
            if len(e) == 0:
                self.modules.append(mod)
            else:
                errors += e
        return errors

    def add_module(self, mod):
        errors = []
        errors = mod.validate()
        if len(errors) == 0:
            if self.modules == None:
                self.modules = []
            self.modules.append(mod)
        return errors

    def add_modules(self, mods):
        if(mods == None):
            self.modules = None
            return
        if self.modules == None:
            self.modules = []
        errors = []
        for mod in mods:
            e = mod.validate()
            if len(e) == 0:
                self.modules.append(mod)
            else:
                errors += e
        return errors

    def update_module(self, mod):
        errors = []
        if mod != None:
            if self.modules == None:
                self.modules = []
            try:
                (m, err) = self.get_module(mod.name)
                if err == None:
                    m.merge(mod)
                else:
                    errors += err
                return errors
            except:  
                self.modules.append(mod)
        return errors

    def set_module_inputs(self, mod_name, inputs):
        (m, err) = self.get_module(mod_name)
        if err == None:
            err = m.set_inputs(inputs)
        return err

#========================================================================

    def find_replace_in_module(self, param_ref, value):
        errors = []
        if self.modules != None:
            for mod in self.modules:
                param_ref_alias = param_ref.replace("$blueprint.inputs.", "$blueprint.")
                param_name = mod.find_input_ref(param_ref)
                if param_name == None:
                    param_name = mod.find_input_ref(param_ref_alias)
                if param_name != None:
                    mod.set_input_value(param_name, value)
                else:
                    param_name = mod.find_setting_ref(param_ref)
                    if param_name == None:
                        param_name = mod.find_setting_ref(param_ref_alias)
                    if param_name != None:
                        mod.set_setting_value(param_name, value)

                param_ref_alias = param_ref.replace("$blueprint.settings.", "$blueprint.")
                param_name = mod.find_setting_ref(param_ref)
                if param_name == None:
                    param_name = mod.find_setting_ref(param_ref_alias)
                if param_name != None:
                    mod.set_setting_value(param_name, value)
                else:
                    param_name = mod.find_input_ref(param_ref)
                    if param_name == None:
                        param_name = mod.find_input_ref(param_ref_alias)
                    if param_name != None:
                        mod.set_input_value(param_name, value)

        return errors

    def propagate_blueprint_input_data(self):
        errors = []
        for p in self.inputs:
            if p.value != None:
                (p_ref, err) = self.input_ref(p.name)
                if err != None:
                    self.find_replace_in_module(p_ref, p.value)

        for p in self.settings:
            if p.value != None:
                (p_ref, err) = self.setting_ref(p.name)
                if err != None:
                    self.find_replace_in_module(p_ref, p.value)

        return errors

    def propagate_module_data(self, module_data):
        # module_data -> dict
        errors = []
        if self.modules != None:
            for mod in self.modules:
                for p in mod.inputs:
                    if p.value != None and p.value in module_data.keys():
                        mod.set_input_value(p.name, module_data[p.value])

                for p in mod.settings:
                    if p.value != None and p.value in module_data.keys():
                        mod.set_setting_value(p.name, module_data[p.value])

        if self.outputs != None:
            for p in self.outputs:
                if p.value != None:
                    if p.value != None and p.value in module_data.keys():
                        self.set_output_value(p.name, module_data[p.value])

        return errors

#======================================================================

    def build_dag(self):
        g = dag.BlueprintGraph()
        if hasattr(self, "modules") and self.modules != None:        
            for m in self.modules:
                iref = m.input_value_refs()
                for i in iref:
                    if i.startswith("$module.") :
                        n = i[8:i.find(".", 8)]
                        if n != m.name:
                            g.addEdge(m.name, n)
                    elif i.startswith("$blueprint.") :
                        g.addEdge(m.name, "blueprint")

                oref = m.output_refs()
                for o in oref:
                    if o.startswith("$module.") :
                        n = o[8:o.find(".", 8)]
                        if n != m.name:
                            g.addEdge(n, m.name)
                    elif o.startswith("$blueprint.") :
                        g.addEdge("blueprint", m.name)
                
                g.addEdge("root", m.name)
        
        return g

    def is_dag_empty(self, bp_graph):
        return bp_graph.isEmpty()

    def dag_next_node(self, bp_graph):
        if bp_graph.isEmpty():
            return None
        
        while not bp_graph.isEmpty():
            node_name = bp_graph.getAnIndependentNode()
            if node_name == "root" or node_name == "blueprint":
                bp_graph.popNode(node_name)
            else:
                return node_name
        
        return None


#======================================================================

