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

from blueprint.lib.logger import logr
import logging
logr = logging.getLogger(__name__)

def val_type(val) -> str:
    if val == None:
        return 'unknown'
    elif isinstance(val, str):
        return 'string'
    elif isinstance(val, int):
        return 'integer'
    elif isinstance(val, float):
        return 'float'
    elif isinstance(val, bool):
        return 'bool'
    elif isinstance(val, list):
        return 'list'
    elif isinstance(val, dict):
        return 'map'
    else:
        return 'unknown'

def is_val_type(val, type) -> bool:
    if val == None:
        if type == 'unknown':
            return True    
        else:
            return False
    if isinstance(val, str):
        if type == 'string':
            return True    
        else:
            return False
    if isinstance(val, int):
        if type == 'integer':
            return True
        else:
            return False
    if isinstance(val, float):
        if type == 'float':
            return True
        else:
            return False
    if isinstance(val, bool):
        if type == 'bool':
            return True
        else:
            return False
    if isinstance(val, list):
        if type.startswith('list'):
            return True
        else:
            return False
    if isinstance(val, dict):
        if type.startswith('map'):
            return True
        else:
            return False
    return False
    

class BlueprintModel:
    def __init__(self, bp):
        self.bp = bp
        self.name = bp.name
        self.description = bp.description if hasattr(bp, 'description') else ""
        self.schema_version = bp.schema_version
        self.type = bp.type
        self.bp_inputs = deepcopy(bp.inputs) if hasattr(bp, 'inputs') else None
        self.bp_outputs = deepcopy(bp.outputs) if hasattr(bp, 'outputs') else None
        self.bp_settings = deepcopy(bp.settings) if hasattr(bp, 'settings') else None
        self.bp_modules = deepcopy(bp.modules) if hasattr(bp, 'modules') else None

        self.bp_input_refs = []
        self.bp_output_refs = []
        self.bp_setting_refs = []

        self.bp_input_value_refs = dict()
        self.bp_input_value = dict()
        self.bp_output_value_refs = dict()
        self.bp_output_value = dict()
        self.bp_setting_value_refs = dict()
        self.bp_setting_value = dict()

        self.mod_input_refs = []
        self.mod_output_refs = []
        self.mod_setting_refs = []

        self.mod_input_value_refs = dict()
        self.mod_input_value = dict()
        self.mod_output_value_refs = dict()
        self.mod_output_value = dict()
        self.mod_setting_value_refs = dict()
        self.mod_setting_value = dict()

        self._prepare_bp_params()
        self._prepare_bp_param_values()
        self._prepare_mod_params()
        self._prepare_mod_param_values()

    def _prepare_bp_params(self):
        if self.bp_inputs != None:
            for p in self.bp_inputs:
                p_in_ref, err = self.bp.input_ref(p.name)
                if hasattr(p, 'type') and p.type != None:
                    self.bp_input_refs.append((p_in_ref, p.type))
                else:
                    if hasattr(p, 'value') and p.value != None:
                        self.bp_input_refs.append((p_in_ref, val_type(p.value)))
                    else:
                        self.bp_input_refs.append((p_in_ref, 'unknown'))

        if self.bp_outputs != None:
            for p in self.bp_outputs:
                p_out_ref, err = self.bp.output_ref(p.name)
                if hasattr(p, 'type') and p.type != None:
                    self.bp_output_refs.append((p_out_ref, p.type))
                else:
                    if hasattr(p, 'value') and p.value != None:
                        self.bp_output_refs.append((p_out_ref, val_type(p.value)))
                    else:
                        self.bp_output_refs.append((p_out_ref, 'unknown'))

        if self.bp_settings != None:
            for p in self.bp_settings:
                p_env_ref, err = self.bp.setting_ref(p.name)
                if hasattr(p, 'type') and p.type != None:
                    self.bp_setting_refs.append((p_env_ref, p.type))
                else:
                    if hasattr(p, 'value') and p.value != None:
                        self.bp_setting_refs.append((p_env_ref, val_type(p.value)))
                    else:
                        self.bp_setting_refs.append((p_env_ref, 'unknown'))

    def _prepare_bp_param_values(self):
        if self.bp_inputs == None:
            for p in self.bp_inputs:
                bp_input_ref, err = self.bp.input_ref(p.name)
                if hasattr(p, 'value'):
                    if isinstance(p.value, str) and \
                         (p.value.startswith("$blueprint") or p.value.startswith("$module")):
                        self.bp_input_value_refs[bp_input_ref] = p.value
                    else:
                        self.bp_input_value[bp_input_ref] = p.value
                else:
                    self.bp_input_value[bp_input_ref] = None

        if self.bp_outputs != None:
            for p in self.bp_outputs:
                bp_output_ref, err = self.bp.output_ref(p.name)
                if hasattr(p, 'value'):
                    if isinstance(p.value, str) and \
                         (p.value.startswith("$blueprint") or p.value.startswith("$module")):
                        self.bp_output_value_refs[bp_output_ref] = p.value
                    else:
                        self.bp_output_value[bp_output_ref] = p.value
                else:
                    self.bp_output_value[bp_output_ref] = None

        if self.bp_settings != None:
            for p in self.bp_settings:
                bp_setting_ref, err = self.bp.setting_ref(p.name)
                if hasattr(p, 'value'):
                    if isinstance(p.value, str) and \
                         (p.value.startswith("$blueprint") or p.value.startswith("$module")):
                        self.bp_setting_value_refs[bp_setting_ref] = p.value
                    else:
                        self.bp_setting_value[bp_setting_ref] = p.value
                else:
                    self.bp_setting_value[bp_setting_ref] = None

    def _prepare_mod_params(self):
        if self.bp_modules == None:
            return

        for mod in self.bp_modules:
            if mod.inputs != None:
                for p in mod.inputs:
                    mod_input_ref, err = self.bp.module_input_ref(mod.name, p.name)
                    if hasattr(p, 'type') and p.type != None:
                        self.mod_input_refs.append((mod_input_ref, p.type))
                    else:
                        if hasattr(p, 'value') and p.value != None:
                            self.mod_input_refs.append((mod_input_ref, val_type(p.value)))
                        else:
                            self.mod_input_refs.append((mod_input_ref, 'unknown'))


            if mod.outputs != None:
                for p in mod.outputs:
                    mod_output_ref, err = self.bp.module_output_ref(mod.name, p.name)
                    if hasattr(p, 'type') and p.type != None:
                        self.mod_output_refs.append((mod_output_ref, p.type))
                    else:
                        if hasattr(p, 'value') and p.value != None:
                            self.mod_output_refs.append((mod_output_ref, val_type(p.value)))
                        else:
                            self.mod_output_refs.append((mod_output_ref, 'unknown'))

            if mod.settings != None:
                for p in mod.settings:
                    mod_setting_ref, err = self.bp.module_setting_ref(mod.name, p.name)
                    if hasattr(p, 'type') and p.type != None:
                        self.mod_setting_refs.append((mod_setting_ref, p.type))
                    else:
                        if hasattr(p, 'value') and p.value != None:
                            self.mod_setting_refs.append((mod_setting_ref, val_type(p.value)))
                        else:
                            self.mod_setting_refs.append((mod_setting_ref, 'unknown'))

    def _prepare_mod_param_values(self):
        if self.bp_modules == None:
            return

        for mod in self.bp_modules:
            if mod.inputs != None:
                for p in mod.inputs:
                    mod_input_ref, err = self.bp.module_input_ref(mod.name, p.name)
                    if hasattr(p, 'value'):
                        if isinstance(p.value, str) and \
                            (p.value.startswith("$blueprint") or p.value.startswith("$module")):
                            self.mod_input_value_refs[mod_input_ref] = p.value
                        else:
                            self.mod_input_value[mod_input_ref] = p.value
                    else:
                        self.mod_input_value[mod_input_ref] =  None

            if mod.outputs != None:
                for p in mod.outputs:
                    mod_output_ref, err = self.bp.module_output_ref(mod.name, p.name)
                    if hasattr(p, 'value'):
                        if isinstance(p.value, str) and \
                            (p.value.startswith("$blueprint") or p.value.startswith("$module")):
                            self.mod_output_value_refs[mod_output_ref] = p.value
                        else:
                            self.mod_output_value[mod_output_ref] = p.value
                    else:
                        self.mod_output_value[mod_output_ref] = None

            if mod.settings != None:
                for p in mod.settings:
                    mod_setting_ref, err = self.bp.module_setting_ref(mod.name, p.name)
                    if hasattr(p, 'value'):
                        if isinstance(p.value, str) and \
                            (p.value.startswith("$blueprint") or p.value.startswith("$module")):
                            self.mod_setting_value_refs[mod_setting_ref] = p.value
                        else:
                            self.mod_setting_value[mod_setting_ref] = p.value
                    else:
                        self.mod_setting_value[mod_setting_ref] = None

    def validate_model(self) -> List[event.ValidationEvent]:
        events = []
        logr.debug("Validating blueprint: " + self.bp.name)

        events.extend(self._validate_blueprint_conflicting_params())
        events.extend(self._validate_blueprint_input_param_values())
        events.extend(self._validate_blueprint_settings_param_values())
        events.extend(self._validate_blueprint_output_param_values())
        events.extend(self._validate_blueprint_unused_params())
        events.extend(self._validate_blueprint_linked_data())
        events.extend(self._validate_module_input_param_values())
        events.extend(self._validate_module_setting_param_values())
        events.extend(self._validate_module_output_param_values())
        events.extend(self._validate_module_duplicate_params())
        events.extend(self._validate_module_unused_params())
        events.extend(self._validate_module_linked_data())
        events.extend(self._validate_module_self_references())
        events.extend(self._validate_modules_circular_dependency())
        return sorted(list(set(events)))

    def _validate_blueprint_conflicting_params(self) -> List[event.ValidationEvent]:
        events = []
        #===============================================
        # Conflicting parameter names in inputs, outputs & settings in the blueprint
        bp_input_names = []
        bp_output_names = []
        bp_setting_names = []
        if self.bp_inputs != None:
            for p in self.bp_inputs:
                bp_input_names.append(p.name)
        if self.bp_outputs != None:
            for p in self.bp_outputs:
                bp_output_names.append(p.name)
        if self.bp_settings != None:
            for p in self.bp_settings:
                bp_setting_names.append(p.name)

        input_output_overlaps = list(set(bp_input_names).intersection(bp_output_names))
        input_setting_overlaps = list(set(bp_input_names).intersection(bp_setting_names))
        setting_output_overlaps = list(set(bp_setting_names).intersection(bp_output_names))
        if len(input_output_overlaps) > 0:
            for p in input_output_overlaps:
                e = event.ValidationEvent(event.BPError, "Conflicting parameter names in inputs & outputs in the blueprint", None, p)
                events.append(e)

        if len(input_setting_overlaps) > 0:
            for p in input_setting_overlaps:
                e = event.ValidationEvent(event.BPError, "Conflicting parameter names in inputs & settings in the blueprint", None, p)
                events.append(e)

        if len(setting_output_overlaps) > 0:
            for p in setting_output_overlaps:
                e = event.ValidationEvent(event.BPError, "Conflicting parameter names in outputs & settings in the blueprint", None, p)
                events.append(e)
        
        return events


    def _validate_blueprint_input_param_values(self) -> List[event.ValidationEvent]:
        events = []
        #===============================================
        # Invalid inputs parameter values in the blueprint
        for k in self.bp_input_value_refs:
            v = self.bp_input_value_refs[k]
            if v.startswith("$module.") or v.startswith("$blueprint."):
                e = event.ValidationEvent(event.BPWarning, "Invalid linked data for input parameter of the blueprint", k, v)
                events.append(e)

        #===============================================
        # Type mismatch for inputs parameter in the blueprint
        for pt in self.bp_input_refs:
            (p, t) = pt
            if p in self.bp_input_value.keys():
                if not is_val_type(self.bp_input_value[p], t):
                    e = event.ValidationEvent(event.BPWarning, "Type mismatch for input parameter of the blueprint", t, p)
                    events.append(e)

        return events

    def _validate_blueprint_settings_param_values(self) -> List[event.ValidationEvent]:
        events = []
        #===============================================
        # Invalid settings parameter values in the blueprint
        for k in self.bp_setting_value_refs:
            v = self.bp_setting_value_refs[k]
            if v.startswith("$module.") or v.startswith("$blueprint."):
                e = event.ValidationEvent(event.BPWarning, "Invalid linked data for setting parameter of the blueprint", k, v)
                events.append(e)

        #===============================================
        # Type mismatch for settings parameter in the blueprint
        for pt in self.bp_setting_refs:
            (p, t) = pt
            if p in self.bp_setting_value.keys():
                if not is_val_type(self.bp_setting_value[p], t):
                    e = event.ValidationEvent(event.BPWarning, "Type mismatch for setting parameter of the blueprint", t, p)
                    events.append(e)

        return events

    def _validate_blueprint_output_param_values(self) -> List[event.ValidationEvent]:
        events = []
        #===============================================
        # Invalid inputs parameter values in the blueprint
        for k in self.bp_output_value:
            v = self.bp_output_value[k]
            if v == None:
                e = event.ValidationEvent(event.BPWarning, "Uninitialized or unlinked - blueprint output parameter", k, str(v))
                events.append(e)

        #===============================================
        # Type mismatch for output parameter in the blueprint
        for pt in self.bp_output_refs:
            (p, t) = pt
            if p in self.bp_output_value.keys():
                if not is_val_type(self.bp_output_value[p], t):
                    e = event.ValidationEvent(event.BPWarning, "Type mismatch for output parameter of the blueprint", t, p)
                    events.append(e)

        return events


    def _validate_blueprint_unused_params(self) -> List[event.ValidationEvent]:
        events = []
        #===============================================
        temp_param_value_refs = dict()
        temp_param_value_refs.update(self.bp_input_value_refs)
        temp_param_value_refs.update(self.bp_output_value_refs)
        temp_param_value_refs.update(self.bp_setting_value_refs)
        temp_param_value_refs.update(self.mod_input_value_refs)
        temp_param_value_refs.update(self.mod_output_value_refs)
        temp_param_value_refs.update(self.mod_setting_value_refs)

        #===============================================
        # Unused input parameters declared in the blueprint
        for pt in self.bp_input_refs:
            (p, t) = pt
            if p not in temp_param_value_refs.values():
                e = event.ValidationEvent(event.BPWarning, "Unused input parameters declared in the blueprint", None, p)
                events.append(e)

        #===============================================
        # Unused setting parameters declared in the blueprint
        for pt in self.bp_setting_refs:
            (p, t) = pt
            if p not in temp_param_value_refs.keys():
                e = event.ValidationEvent(event.BPWarning, "Unused setting parameters declared in the blueprint", None, p)
                events.append(e)

        return events

    def _validate_blueprint_linked_data(self) -> List[event.ValidationEvent]:
        events = []
        #===============================================
        # Undeclared blueprint linked data, used by modules
        temp_input_value_refs = dict()
        temp_input_value_refs.update(self.mod_input_value_refs)
        temp_input_value_refs.update(self.mod_setting_value_refs)

        temp_output_refs = []
        temp_output_refs.extend([x[0] for x in self.bp_input_refs])
        temp_output_refs.extend([x[0] for x in self.bp_setting_refs])

        for k in temp_input_value_refs:
            v = temp_input_value_refs[k]
            if v != None and \
                v.startswith("$blueprint.") and \
                v not in temp_output_refs:
                e = event.ValidationEvent(event.BPError, "Undeclared blueprint linked data, used by modules", k, v)
                events.append(e)

        #===============================================
        # Undeclared blueprint linked data, used by blueprint
        temp_input_value_refs = dict()
        temp_input_value_refs.update(self.bp_output_value_refs)

        temp_output_refs = []
        temp_output_refs.extend([x[0] for x in self.bp_input_refs])
        temp_output_refs.extend([x[0] for x in self.bp_setting_refs])

        for k in temp_input_value_refs:
            v = temp_input_value_refs[k]
            if v != None and \
                v.startswith("$blueprint.") and \
                v not in temp_output_refs:
                e = event.ValidationEvent(event.BPError, "Undeclared blueprint linked data, used by blueprint", k, v)
                events.append(e)
                logr.error(str(e))

        return events

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
        for m in self.bp_modules:
            if m.inputs != None:
                p_names = []
                for p in m.inputs:
                    p_in_ref, err = self.bp.module_input_ref(m.name, p.name)
                    if p_in_ref in p_names:
                        e = event.ValidationEvent(event.BPError, "Duplicate input parameters in module", None, p_in_ref)
                        events.append(e)
                    else:
                        p_names.append(p_in_ref)

            if m.outputs != None:
                p_names = []
                for p in m.outputs:
                    p_out_ref, err = self.bp.module_output_ref(m.name, p.name)
                    if p_out_ref in p_names:
                        e = event.ValidationEvent(event.BPError, "Duplicate output parameters in module", None, p_out_ref)
                        events.append(e)
                    else:
                        p_names.append(p_out_ref)

            if m.settings != None:
                p_names = []
                for p in m.settings:
                    p_env_ref, err = self.bp.module_setting_ref(m.name, p.name)
                    if p_env_ref in p_names:
                        e = event.ValidationEvent(event.BPError, "Duplicate setting parameters in module", None, p_env_ref)
                        events.append(e)
                    else:
                        p_names.append(p_env_ref)

        return events

    def _validate_module_unused_params(self) -> List[event.ValidationEvent]:
        events = []
        #===============================================
        temp_param_value_refs = dict()
        temp_param_value_refs.update(self.bp_output_value_refs)
        temp_param_value_refs.update(self.bp_setting_value_refs)
        temp_param_value_refs.update(self.mod_input_value_refs)
        temp_param_value_refs.update(self.mod_setting_value_refs)

        temp_output_refs = []
        temp_output_refs.extend([x[0] for x in self.mod_output_refs])

        #===============================================
        # Unused output parameters declared in the modules

        for v in temp_output_refs:
            if v != None and \
                v not in temp_param_value_refs.values():
                e = event.ValidationEvent(event.BPError, "Unused output parameters declared in the modules", None, v)
                events.append(e)

        return events

    def _validate_module_linked_data(self) -> List[event.ValidationEvent]:
        events = []
        #===============================================
        # Invalid module linked data, used by modules 
        temp_input_value_refs = dict()
        temp_input_value_refs.update(self.mod_input_value_refs)
        temp_input_value_refs.update(self.mod_setting_value_refs)

        temp_output_refs = []
        temp_output_refs.extend([x[0] for x in self.mod_output_refs])

        for k in temp_input_value_refs:
            v = temp_input_value_refs[k]
            if v != None and \
                v.startswith("$module.") and \
                v not in temp_output_refs:
                e = event.ValidationEvent(event.BPError, "Undeclared module linked data, used by modules", k, v)
                events.append(e)

        #===============================================
        # Invalid module linked data, used by blueprint 
        temp_input_value_refs = dict()
        temp_input_value_refs.update(self.bp_output_value_refs)

        temp_output_refs = []
        temp_output_refs.extend([x[0] for x in self.bp_setting_refs])
        temp_output_refs.extend([x[0] for x in self.mod_output_refs])

        for k in temp_input_value_refs:
            v = temp_input_value_refs[k]
            if v != None and \
                v.startswith("$module.") and \
                v not in temp_output_refs:
                e = event.ValidationEvent(event.BPError, "Undeclared module linked data, used by blueprint", k, v)
                events.append(e)
        
        return events

    def _validate_module_self_references(self) -> List[event.ValidationEvent]:
        events = []
        #===============================================
        # Invalid module linked data, used by modules 
        temp_input_refs = []
        for m in self.bp_modules:
            if m.inputs != None:
                for p in m.inputs:
                    p_in_ref, err = self.bp.module_input_ref(m.name, p.name)
                    temp_input_refs.append(p_in_ref)

            if m.settings != None:
                for p in m.settings:
                    p_in_ref, err = self.bp.module_setting_ref(m.name, p.name)
                    temp_input_refs.append(p_in_ref)

            if m.outputs != None:
                for p in m.outputs:
                    if hasattr(p, 'value'):
                        if isinstance(p.value, str) and \
                            p.value.startswith("$module.") and \
                            p.value in temp_input_refs:
                            e = event.ValidationEvent(event.BPError, "Found self-references in module", p.name, p.value)
                            events.append(e)
        return events

    def _validate_modules_circular_dependency(self) -> List[event.ValidationEvent]:
        events = []
        #===============================================
        # are there any circular references between modules
        dag = self.bp.build_dag()
        if dag.isCyclic() == True:
            dag.getCyclicPath()
            e = event.ValidationEvent(event.BPError, "Found circular dependencies between modules", None, dag.getCyclicPath())
            events.append(e)
        
        return events

    '''
    
class BlueprintValidator:

    def validate_blueprint(self, bp, level=event.BPError) -> List[event.ValidationEvent]:
        bperrors = []
        logr.debug("Validating blueprint name: " + bp.name)
        # validate all modules (parameters, bp-references, input-types)
        mod_validator = ModuleValidator()
        if hasattr(bp, 'modules') and bp.modules != None:
            for m in bp.modules:
                mverror = mod_validator.validate_module(m, level)
                if len(mverror) > 0:
                    e = event.ValidationEvent(event.BPError, "Error in blueprint modules", bp, m, mverror)
                    bperrors.append(e)
                    logr.debug("Found issues in module - " + m.name)
                    logr.debug(e)

        # hanging inputs & outputs
        value_refs = set()
        output_bp_value_refs    = set()
        input_mod_value_refs    = set()
        input_mod_var_names     = set()
        output_mod_var_names    = set()
        input_bp_var_names      = set()
        setting_bp_var_names    = set()
        output_bp_var_names     = set()
        uninit_bp_output_vals   = set()
        output_mod_value_refs   = set()
        if hasattr(bp, "modules") and bp.modules != None:
            for m in bp.modules:
                if hasattr(m, "inputs") and m.inputs != None:
                    for p in m.inputs:
                        (mod_vars, err) = bp.module_input_ref(m.name, p.name)
                        if err == None:
                            input_mod_var_names.add((mod_vars, p))
                        if hasattr(p, "value") and isinstance(p.value, str) and (p.value != None and (p.value.startswith("$module.") or p.value.startswith("$blueprint."))):
                            value_refs.add(p.value)
                            input_mod_value_refs.add((p.value, p))
                if hasattr(m, "outputs") and m.outputs != None:
                    for p in m.outputs:
                        (mod_vars, err) = bp.module_output_ref(m.name, p.name)
                        if err == None:
                            output_mod_var_names.add((mod_vars, p))
                        if hasattr(p, "value") and isinstance(p.value, str) and (p.value != None and (p.value.startswith("$module.") or p.value.startswith("$blueprint."))):
                            value_refs.add(p.value)
                            output_mod_value_refs.add((p.value, p))
                if hasattr(m, "settings") and m.settings != None:
                    for p in m.settings:
                        (mod_vars, err) = bp.module_setting_ref(m.name, p.name)
                        if err == None:
                            input_mod_var_names.add((mod_vars, p))
                        if hasattr(p, "value") and (p.value != None and isinstance(p.value, str) and (p.value.startswith("$module.") or p.value.startswith("$blueprint."))):
                            value_refs.add(p.value)
                            input_mod_value_refs.add((p.value, p))
        if hasattr(bp, "inputs") and bp.inputs != None:
            for p in bp.inputs:
                (bp_vars, err) = bp.input_ref(p.name)
                if err == None:
                    input_bp_var_names.add((bp_vars, p))
                    # alias_bp_vars = bp_vars.replace("$blueprint.inputs.", "$blueprint.")
                    # input_bp_var_names.add((alias_bp_vars, p))
                if hasattr(p, "value") and isinstance(p.value, str) and (p.value != None and (p.value.startswith("$module.") or p.value.startswith("$blueprint."))):
                    value_refs.add(p.value)
        if hasattr(bp, "outputs") and bp.outputs != None:
            for p in bp.outputs:
                (bp_vars, err) = bp.output_ref(p.name)
                if err == None:
                    output_bp_var_names.add(bp_vars)
                if hasattr(p, "value") and isinstance(p.value, str) and (p.value != None):
                    if (p.value.startswith("$module.") or p.value.startswith("$blueprint.")):
                        value_refs.add(p.value)
                        output_bp_value_refs.add((p.value, p))
                    else:
                        uninit_bp_output_vals.add((p.name, p))

        if hasattr(bp, "settings") and bp.settings != None:
            for p in bp.settings:
                (bp_vars, err) = bp.setting_ref(p.name)
                if err == None:
                    setting_bp_var_names.add((bp_vars, p))
                    # alias_bp_vars = bp_vars.replace("$blueprint.settings.", "$blueprint.")
                    # setting_bp_var_names.add((alias_bp_vars, p))
                if hasattr(p, "value") and isinstance(p.value, str) and (p.value != None and (p.value.startswith("$module.") or p.value.startswith("$blueprint."))):
                    value_refs.add(p.value)
        #===============================================
        unused_bp_vars = set()
        for bp_inputs_tup in input_bp_var_names:
            (bp_inputs, ctx) = bp_inputs_tup
            if not (bp_inputs in value_refs):
                unused_bp_vars.add(bp_inputs_tup)

        if len(unused_bp_vars) > 0:
            for var_tup in unused_bp_vars:
                (var, ctx) = var_tup
                if level >= event.BPWarning:
                    e = event.ValidationEvent(event.BPWarning, "Unused input parameters declared in the blueprint", ctx, var)
                    bperrors.append(e)
                    logr.warning(str(e))
        #===============================================
        unused_bp_vars = set()
        for bp_settings_tup in setting_bp_var_names:
            (bp_settings, ctx) = bp_settings_tup
            if not (bp_settings in value_refs):
                unused_bp_vars.add(bp_settings_tup)

        if len(unused_bp_vars) > 0:
            for var_tup in unused_bp_vars:
                (var, ctx) = var_tup
                if level >= event.BPWarning:
                    e = event.ValidationEvent(event.BPWarning, "Unused setting parameters declared in the blueprint", ctx, var)
                    bperrors.append(e)
                    logr.warning(str(e))
        #===============================================
        undeclared_bp_vars = set()
        i_bp_var_names = list(map(lambda x: x[0], input_bp_var_names))
        s_bp_var_names = list(map(lambda x: x[0], setting_bp_var_names))
        for mod_inputs_tup in input_mod_value_refs:
            (mod_inputs, ctx) = mod_inputs_tup
            if mod_inputs.startswith("$blueprint."):
                if mod_inputs not in i_bp_var_names and mod_inputs not in s_bp_var_names:
                    undeclared_bp_vars.add((mod_inputs, ctx))

        if len(undeclared_bp_vars) > 0:
            for var_tup in undeclared_bp_vars:
                (var, ctx) = var_tup
                if level >= event.BPError:
                    e = event.ValidationEvent(event.BPError, "Undeclared blueprint parameters used by modules", ctx, var)
                    bperrors.append(e)
                    logr.error(str(e))
        #===============================================
        undeclared_mod_vars = set()
        for mod_inputs_tup in input_mod_value_refs:
            (mod_inputs, ctx) = mod_inputs_tup
            if mod_inputs.startswith("$module.") and ".outputs." in mod_inputs:
                o_mod_var_names = list(map(lambda x: x[0], output_mod_var_names))
                if mod_inputs not in o_mod_var_names:
                    undeclared_mod_vars.add((mod_inputs, ctx))

        if len(undeclared_mod_vars) > 0:
            for var_tup in undeclared_mod_vars:
                (var, ctx) = var_tup
                if level >= event.BPError:
                    e = event.ValidationEvent(event.BPError, "Undeclared output parameters used by modules", ctx, var)
                    bperrors.append(e)
                    logr.error(str(e))
        #===============================================
        unused_mod_vars = set()
        i_mod_value_refs = list(map(lambda x: x[0], input_mod_value_refs))
        o_bp_value_refs = list(map(lambda x: x[0], output_bp_value_refs))
        for mod_tup in output_mod_var_names:
            (mod, ctx) = mod_tup
            if (mod not in o_bp_value_refs) and (mod not in i_mod_value_refs):
                unused_mod_vars.add((mod, ctx))

        if len(unused_mod_vars) > 0:
            for var_tup in unused_mod_vars:
                (var, ctx) = var_tup
                if level >= event.BPWarning:
                    e = event.ValidationEvent(event.BPWarning, "Unused output parameters declared in the modules", ctx, var)
                    bperrors.append(e)
                    logr.warning(str(e))
        #===============================================
        if len(uninit_bp_output_vals) > 0:
            for var_tup in uninit_bp_output_vals:
                (var, ctx) = var_tup
                if level >= event.BPError:
                    e = event.ValidationEvent(event.BPError, "Blueprint output parameters is left hanging", ctx, var)
                    bperrors.append(e)
                    logr.error(str(e))
        #===============================================
        # are there any circular references between modules
        dag = bp.build_dag()
        if dag.isCyclic() == True:
            if level >= event.BPError:
                dag.getCyclicPath()
                e = event.ValidationEvent(event.BPError, "Found circular dependencies between modules", None, dag.getCyclicPath())
                bperrors.append(e)
                logr.error(str(e))
        #===============================================

        if len(bperrors) > 0:
            logr.debug("Found issues in blueprint - " + bp.name)
            logr.debug(bperrors)

        return bperrors

##====================================================================##

class ModuleValidator:
    def validate_module(self, mod, level=event.BPError):
        param_names = []
        duplicate_names = []
        value_refs = []
        invalid_params = []
        mverrors = []
        param_validator = ParameterValidator()
        if hasattr(mod, "inputs") :
            for p in mod.inputs:
                if p.name in param_names:
                    (mod_vars, err) = mod.input_ref(p.name)
                    if err != None:
                        duplicate_names.append(mod_vars)
                else: 
                    param_names.append(p.name)
                if hasattr(p, "value") and p.value != None and isinstance(p.value, str) and (p.value.startswith('$module.') or p.value.startswith('$blueprint.')):
                    value_refs.append(p.value)
                pverrors = param_validator.validate_input(p, level)
                if len(pverrors) > 0 :
                    (mod_vars, err) = mod.input_ref(p.name)
                    if err == None:
                        invalid_params.append(mod_vars)
                    else:
                        mverrors.append(err)
                    mverrors.append(pverrors)

        if hasattr(mod, "outputs") :
            for p in mod.outputs:
                if p.name in param_names:
                    (mod_vars, err) = mod.output_ref(p.name)
                    if err != None:
                        duplicate_names.append(mod_vars)
                else:
                    param_names.append(p.name)
                if hasattr(p, "value") and p.value != None and isinstance(p.value, str) and (p.value.startswith('$module.') or p.value.startswith('$blueprint.')):
                    value_refs.append(p.value)
                pverrors = param_validator.validate_output(p, level)
                if len(pverrors) > 0 :
                    (mod_vars, err) = mod.output_ref(p.name)
                    if err == None:
                        invalid_params.append(mod_vars)
                    else:
                        mverrors.append(err)
                    mverrors.append(pverrors)

        if hasattr(mod, "settings") :
            for p in mod.settings:
                if p.name in param_names:
                    (mod_vars, err) = mod.setting_ref(p.name)
                    if err != None:
                        duplicate_names.append(mod_vars)
                else:
                    param_names.append(p.name)
                if hasattr(p, "value") and p.value != None and isinstance(p.value, str) and (p.value.startswith('$module.') or p.value.startswith('$blueprint.')):
                    value_refs.append(p.value)
                pverrors = param_validator.validate_setting(p, level)
                if len(pverrors) > 0 :
                    (mod_vars, err) = mod.setting_ref(p.name)
                    if err == None:
                        invalid_params.append(mod_vars)
                    else:
                        mverrors.append(err)
                    mverrors.append(pverrors)

        ret_errors = []
        # parameters with empty input values
        if len(invalid_params) > 0:
            for p in invalid_params:
                if level >= event.BPError:
                    e = event.ValidationEvent(event.BPError, "Error in the input parameters for the modules", self, p)
                    ret_errors.append(e)
                    logr.error(str(e))

        # duplicate parameters (inputs, outputs, settings) with same name
        if len(duplicate_names) > 0:
            for p in duplicate_names:
                if level >= event.BPWarning:
                    e = event.ValidationEvent(event.BPWarning, "Duplicate parameter names in the module", self, p)
                    ret_errors.append(e)
                    logr.warning(str(e))

        # self referential values in parameters (inputs, outputs, settings)
        invalid_self_references = []
        for val in value_refs:
            if val.startswith('$module.'+ mod.name):
                invalid_self_references.append(val)

        if len(invalid_self_references) > 0:
            for p in invalid_self_references:            
                if level >= event.BPError:
                    e = event.ValidationEvent(event.BPError, "Self referential values in the module", self, p)
                    ret_errors.append(e)
                    logr.error(str(e))

        return ret_errors

##====================================================================##

class ParameterValidator:

    def validate_param(self, param, level=event.BPError):
        pverrors = []        
        if hasattr(param, "type") and (param.type != None and param.type.lower() == "boolean"):
            if hasattr(param, "value") and param.value != None:
                if isinstance(param.value, str) and (param.value.lower() == "true" or param.value.lower() == "false"):
                    param.value = True if param.value.lower() == "true" else False
                if not (param.value == True or param.value == False) :
                    if level >= event.BPError:
                        e = event.ValidationEvent(event.BPError, "Type mismatch for boolean parameter", param, param.value)
                        pverrors.append(e)
                        logr.error(str(e))
        return pverrors

    def validate_input(self, param, level=event.BPError):
        pverrors = self.validate_param(param, level)
        if hasattr(param, "value") and param.value == None:
            if level >= event.BPWarning:
                e = event.ValidationEvent(event.BPWarning, "Input parameter is not initialized with any value", param, param.value)
                pverrors.append(e)
                logr.warning(str(e))
        return pverrors

    def validate_output(self, param, level=event.BPError):
        pverrors = self.validate_param(param, level)
        # if hasattr(param, "value") and param.value == None:
        #     if level >= event.BPWarning:
        #         event.ValidationEvent(event.BPWarning, "Output parameter is not initialized with any value", param, param.value)
        #         pverrors.append(e)
        #         logr.warning(str(e))
        return pverrors

    def validate_setting(self, param, level=event.BPError):
        pverrors = self.validate_param(param, level)
        if param.value == None:
            if level >= event.BPWarning:
                e = event.ValidationEvent(event.BPWarning, "Setting parameter is not initialized with any value", param, param.value)
                pverrors.append(e)
                logr.warning(str(e))
        return pverrors

##====================================================================##

'''