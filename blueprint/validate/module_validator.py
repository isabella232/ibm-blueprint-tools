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

from typing import List 
from blueprint.lib import event
from copy import deepcopy
from blueprint.lib.type_helper import val_type, is_val_type

from blueprint.lib.logger import logr
import logging
logr = logging.getLogger(__name__)

class ModuleModel:
    def __init__(self, mod):
        self.mod = mod
        self.name = mod.name
        self.description = mod.description if hasattr(mod, 'description') else ""
        self.type = mod.module_type
        self.mod_source = deepcopy(mod.source) if hasattr(mod, 'source') else None
        self.mod_inputs = deepcopy(mod.inputs) if hasattr(mod, 'inputs') else None
        self.mod_outputs = deepcopy(mod.outputs) if hasattr(mod, 'outputs') else None
        self.mod_settings = deepcopy(mod.settings) if hasattr(mod, 'settings') else None

        self.mod_input_refs = []
        self.mod_output_refs = []
        self.mod_setting_refs = []

        self.mod_input_value_refs = dict()
        self.mod_input_value = dict()
        self.mod_output_value_refs = dict()
        self.mod_output_value = dict()
        self.mod_setting_value_refs = dict()
        self.mod_setting_value = dict()

        self._prepare_mod_params()
        self._prepare_mod_param_values()

    def _prepare_mod_params(self):
        if self.mod == None:
            return

        if self.mod_inputs != None:
            for p in self.mod_inputs:
                mod_input_ref, err = self.mod.input_ref(p.name)
                if hasattr(p, 'type') and p.type != None:
                    self.mod_input_refs.append((mod_input_ref, p.type))
                else:
                    if hasattr(p, 'value') and p.value != None:
                        self.mod_input_refs.append((mod_input_ref, val_type(p.value)))
                    else:
                        self.mod_input_refs.append((mod_input_ref, 'unknown'))


        if self.mod_outputs != None:
            for p in self.mod_outputs:
                mod_output_ref, err = self.mod.output_ref(p.name)
                if hasattr(p, 'type') and p.type != None:
                    self.mod_output_refs.append((mod_output_ref, p.type))
                else:
                    if hasattr(p, 'value') and p.value != None:
                        self.mod_output_refs.append((mod_output_ref, val_type(p.value)))
                    else:
                        self.mod_output_refs.append((mod_output_ref, 'unknown'))

        if self.mod_settings != None:
            for p in self.mod_settings:
                mod_setting_ref, err = self.mod.setting_ref(p.name)
                if hasattr(p, 'type') and p.type != None:
                    self.mod_setting_refs.append((mod_setting_ref, p.type))
                else:
                    if hasattr(p, 'value') and p.value != None:
                        self.mod_setting_refs.append((mod_setting_ref, val_type(p.value)))
                    else:
                        self.mod_setting_refs.append((mod_setting_ref, 'unknown'))

    def _prepare_mod_param_values(self):
        if self.mod == None:
            return

        if self.mod_inputs != None:
            for p in self.mod_inputs:
                mod_input_ref, err = self.mod.input_ref(p.name)
                if hasattr(p, 'value'):
                    if isinstance(p.value, str) and \
                        (p.value.startswith("$blueprint") or p.value.startswith("$module")):
                        self.mod_input_value_refs[mod_input_ref] = p.value
                    else:
                        self.mod_input_value[mod_input_ref] = p.value
                else:
                    self.mod_input_value[mod_input_ref] =  None

        if self.mod_outputs != None:
            for p in self.mod_outputs:
                mod_output_ref, err = self.mod.output_ref(p.name)
                if hasattr(p, 'value'):
                    if isinstance(p.value, str) and \
                        (p.value.startswith("$blueprint") or p.value.startswith("$module")):
                        self.mod_output_value_refs[mod_output_ref] = p.value
                    else:
                        self.mod_output_value[mod_output_ref] = p.value
                else:
                    self.mod_output_value[mod_output_ref] = None

        if self.mod_settings != None:
            for p in self.mod_settings:
                mod_setting_ref, err = self.mod.setting_ref(p.name)
                if hasattr(p, 'value'):
                    if isinstance(p.value, str) and \
                        (p.value.startswith("$blueprint") or p.value.startswith("$module")):
                        self.mod_setting_value_refs[mod_setting_ref] = p.value
                    else:
                        self.mod_setting_value[mod_setting_ref] = p.value
                else:
                    self.mod_setting_value[mod_setting_ref] = None

    def validate(self) -> List[event.ValidationEvent]:
        events = []
        logr.debug("Validating module: " + self.mod.name)

        events.extend(self._validate_module_input_param_values())
        events.extend(self._validate_module_setting_param_values())
        events.extend(self._validate_module_output_param_values())
        events.extend(self._validate_module_duplicate_params())
        events.extend(self._validate_module_self_references())
        return sorted(list(set(events)))

    def _validate_module_input_param_values(self) -> List[event.ValidationEvent]:
        events = []
        #===============================================
        # Empty input value for module parameter 

        for k in self.mod_input_value:
            v = self.mod_input_value[k]
            if v == None:
                e = event.ValidationEvent(event.BPError, "Uninitialized or unlinked input parameter, for module parameter", k, str(v))
                events.append(e)

        #===============================================
        # Type mismatch for inputs parameter in the modules
        for pt in self.mod_input_refs:
            (p, t) = pt
            if p in self.mod_input_value.keys():
                if not is_val_type(self.mod_input_value[p], t):
                    e = event.ValidationEvent(event.BPWarning, "Type mismatch for input parameter of the module", t, p)
                    events.append(e)

        return events

    def _validate_module_setting_param_values(self) -> List[event.ValidationEvent]:
        events = []
        #===============================================
        # Empty setting value for module parameter 

        for k in self.mod_setting_value:
            v = self.mod_setting_value[k]
            if v == None:
                e = event.ValidationEvent(event.BPError, "Uninitialized or unlinked setting parameter, for module parameter", k, str(v))
                events.append(e)

        #===============================================
        # Type mismatch for settings parameter in the module
        for pt in self.mod_setting_refs:
            (p, t) = pt
            if p in self.mod_setting_value.keys():
                if not is_val_type(self.mod_setting_value[p], t):
                    e = event.ValidationEvent(event.BPWarning, "Type mismatch for setting parameter of the module", t, p)
                    events.append(e)

        return events

    def _validate_module_output_param_values(self) -> List[event.ValidationEvent]:
        events = []
        #===============================================
        # Empty outputs value for module parameter 

        # for k in self.mod_output_value:
        #     v = self.mod_output_value[k]
        #     if v == None:
        #         e = event.ValidationEvent(event.BPError, "Uninitialized or unlinked output parameter, for module parameter", k, str(v))
        #         events.append(e)

        #===============================================
        # Type mismatch for output parameter in the module
        for pt in self.mod_output_refs:
            (p, t) = pt
            if p in self.mod_output_value.keys():
                if not is_val_type(self.mod_output_value[p], t):
                    e = event.ValidationEvent(event.BPWarning, "Type mismatch for output parameter of the module", t, p)
                    events.append(e)

        return events

    def _validate_module_duplicate_params(self) -> List[event.ValidationEvent]:
        events = []
        #===============================================
        # Duplicate input parameters in module
        if self.mod_inputs != None:
            p_names = []
            for p in self.mod_inputs:
                p_in_ref, err = self.mod.input_ref(p.name)
                if p_in_ref in p_names:
                    e = event.ValidationEvent(event.BPError, "Duplicate input parameters in module", None, p_in_ref)
                    events.append(e)
                else:
                    p_names.append(p_in_ref)

        if self.mod_outputs != None:
            p_names = []
            for p in self.mod_outputs:
                p_out_ref, err = self.mod.output_ref(p.name)
                if p_out_ref in p_names:
                    e = event.ValidationEvent(event.BPError, "Duplicate output parameters in module", None, p_out_ref)
                    events.append(e)
                else:
                    p_names.append(p_out_ref)

        if self.mod_settings != None:
            p_names = []
            for p in self.mod_settings:
                p_env_ref, err = self.mod.setting_ref(p.name)
                if p_env_ref in p_names:
                    e = event.ValidationEvent(event.BPError, "Duplicate setting parameters in module", None, p_env_ref)
                    events.append(e)
                else:
                    p_names.append(p_env_ref)

        return events

    def _validate_module_self_references(self) -> List[event.ValidationEvent]:
        events = []
        #===============================================
        # Invalid module linked data, used by modules 
        temp_input_refs = []
        if self.mod_inputs != None:
            for p in self.mod_inputs:
                p_in_ref, err = self.mod.input_ref(p.name)
                temp_input_refs.append(p_in_ref)

        if self.mod_settings != None:
            for p in self.mod_settings:
                p_in_ref, err = self.mod.setting_ref(p.name)
                temp_input_refs.append(p_in_ref)

        if self.mod_outputs != None:
            for p in self.mod_outputs:
                if hasattr(p, 'value'):
                    if isinstance(p.value, str) and \
                        p.value.startswith("$module.") and \
                        p.value in temp_input_refs:
                        e = event.ValidationEvent(event.BPError, "Found self-references in module", p.name, p.value)
                        events.append(e)
        return events
