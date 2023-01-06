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
from blueprint.schema import param
from copy import deepcopy
from blueprint.lib.type_helper import val_type, is_val_type

from blueprint.lib.logger import logr
import logging
logr = logging.getLogger(__name__)

class BlueprintModel:
    def __init__(self, bp):
        self.bp             = bp
        self.name           = bp.name
        self.description    = bp.description if hasattr(bp, 'description') else ""
        self.schema_version = bp.schema_version
        self.type           = bp.type
        self.bp_inputs      = bp.inputs if hasattr(bp, 'inputs') else None
        self.bp_outputs     = bp.outputs if hasattr(bp, 'outputs') else None
        self.bp_settings    = bp.settings if hasattr(bp, 'settings') else None
        self.bp_modules     = bp.modules if hasattr(bp, 'modules') else None

        self.bp_input_refs      = [] # List of tuple (input_ref & type)
        self.bp_output_refs     = [] # List of tuple (output_ref & type)
        self.bp_setting_refs    = [] # List of tuple (setting_ref & type)

        self.bp_input_value_refs    = dict()
        self.bp_input_value         = dict()
        self.bp_output_value_refs   = dict()
        self.bp_output_value        = dict()
        self.bp_setting_value_refs  = dict()
        self.bp_setting_value       = dict()

        self.unused_bp_input_refs       = [] # List of input_ref
        self.unused_bp_setting_refs     = [] # List of setting_ref
        # self.unused_bp_output_refs    = [] # List of output_ref

        self.mod_input_refs     = [] # List of tuple (input_ref & type)
        self.mod_output_refs    = [] # List of tuple (output_ref & type)
        self.mod_setting_refs   = [] # List of tuple (setting_ref & type)

        self.mod_input_value_refs   = dict()
        self.mod_input_value        = dict()
        self.mod_output_value_refs  = dict()
        self.mod_output_value       = dict()
        self.mod_setting_value_refs = dict()
        self.mod_setting_value      = dict()

        # self.unused_mod_input_refs    = [] # List of input_ref
        # self.unused_mod_setting_refs  = [] # List of setting_ref
        self.unused_mod_output_refs     = [] # List of input_ref

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
        if self.bp_inputs != None:
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
            if hasattr(mod, 'inputs') and mod.inputs != None:
                for p in mod.inputs:
                    mod_input_ref, err = self.bp.module_input_ref(mod.name, p.name)
                    if hasattr(p, 'type') and p.type != None:
                        self.mod_input_refs.append((mod_input_ref, p.type))
                    else:
                        if hasattr(p, 'value') and p.value != None:
                            self.mod_input_refs.append((mod_input_ref, val_type(p.value)))
                        else:
                            self.mod_input_refs.append((mod_input_ref, 'unknown'))


            if hasattr(mod, 'outputs') and mod.outputs != None:
                for p in mod.outputs:
                    mod_output_ref, err = self.bp.module_output_ref(mod.name, p.name)
                    if hasattr(p, 'type') and p.type != None:
                        self.mod_output_refs.append((mod_output_ref, p.type))
                    else:
                        if hasattr(p, 'value') and p.value != None:
                            self.mod_output_refs.append((mod_output_ref, val_type(p.value)))
                        else:
                            self.mod_output_refs.append((mod_output_ref, 'unknown'))

            if hasattr(mod, 'settings') and mod.settings != None:
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
            if hasattr(mod, 'inputs') and mod.inputs != None:
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

            if hasattr(mod, 'outputs') and mod.outputs != None:
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

            if hasattr(mod, 'settings') and mod.settings != None:
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

    def validate(self) -> List[event.ValidationEvent]:
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
                if self.bp_input_value[p] != None and not is_val_type(self.bp_input_value[p], t):
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
                self.unused_bp_input_refs.append(p)
                e = event.ValidationEvent(event.BPWarning, "Unused input parameters declared in the blueprint", None, p)
                events.append(e)

        #===============================================
        # Unused setting parameters declared in the blueprint
        for pt in self.bp_setting_refs:
            (p, t) = pt
            if p not in temp_param_value_refs.keys():
                self.unused_bp_setting_refs.append(p)
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
            if hasattr(m, 'inputs') and m.inputs != None:
                p_names = []
                for p in m.inputs:
                    p_in_ref, err = self.bp.module_input_ref(m.name, p.name)
                    if p_in_ref in p_names:
                        e = event.ValidationEvent(event.BPError, "Duplicate input parameters in module", None, p_in_ref)
                        events.append(e)
                    else:
                        p_names.append(p_in_ref)

            if hasattr(m, 'outputs') and m.outputs != None:
                p_names = []
                for p in m.outputs:
                    p_out_ref, err = self.bp.module_output_ref(m.name, p.name)
                    if p_out_ref in p_names:
                        e = event.ValidationEvent(event.BPError, "Duplicate output parameters in module", None, p_out_ref)
                        events.append(e)
                    else:
                        p_names.append(p_out_ref)

            if hasattr(m, 'settings') and m.settings != None:
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
                self.unused_mod_output_refs.append(v)
                e = event.ValidationEvent(event.BPError, "Unused output parameters declared in the modules", None, v)
                events.append(e)

        #===============================================
        temp_param_value_refs = dict()
        temp_param_value_refs.update(self.bp_output_value_refs)
        temp_param_value_refs.update(self.bp_setting_value_refs)
        temp_param_value_refs.update(self.mod_input_value_refs)
        temp_param_value_refs.update(self.mod_setting_value_refs)

        temp_output_refs = []
        temp_output_refs.extend(self.mod_input_refs)
        temp_output_refs.extend(self.mod_setting_refs)

        #===============================================
        # Unused input parameters declared in the modules

        for vt in temp_output_refs:
            (v, t) = vt
            if v != None \
                and v not in temp_param_value_refs.values():
                self.unused_mod_output_refs.append(v)
                e = event.ValidationEvent(event.BPError, "Unused input parameters declared in the modules", None, v)
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
            if hasattr(m, 'inputs') and m.inputs != None:
                for p in m.inputs:
                    p_in_ref, err = self.bp.module_input_ref(m.name, p.name)
                    temp_input_refs.append(p_in_ref)

            if hasattr(m, 'settings') and m.settings != None:
                for p in m.settings:
                    p_in_ref, err = self.bp.module_setting_ref(m.name, p.name)
                    temp_input_refs.append(p_in_ref)

            if hasattr(m, 'outputs') and m.outputs != None:
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

