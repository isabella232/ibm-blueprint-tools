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

from blueprint.lib.dag import BlueprintGraph
from blueprint.lib.event import ValidationEvent
from blueprint.lib.event import BPError
from blueprint.lib.event import BPWarning

from blueprint.lib.logger import logr
import logging
logr = logging.getLogger(__name__)

class BlueprintValidator:
    def validate_blueprint(self, bp, level=BPError):
        bperrors = []
        logr.debug("Validating blueprint name: " + bp.name)
        # validate all modules (parameters, bp-references, input-types)
        mod_validator = ModuleValidator()
        for m in bp.modules:
            mverror = mod_validator.validate_module(m, level)
            if len(mverror) > 0:
                e = ValidationEvent(BPError, "Error in blueprint modules", bp, m, mverror)
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
        output_bp_var_names     = set()
        uninit_bp_output_vals   = set()
        output_mod_value_refs   = set()
        if hasattr(bp, "modules") and bp.modules != None:
            for m in bp.modules:
                if hasattr(m, "inputs") and m.inputs != None:
                    for p in m.inputs:
                        input_mod_var_names.add(bp.module_input_ref(m.name, p.name))
                        if hasattr(p, "value") and isinstance(p.value, str) and (p.value != None and (p.value.startswith("$module.") or p.value.startswith("$blueprint."))):
                            value_refs.add(p.value)
                            input_mod_value_refs.add(p.value)
                if hasattr(m, "outputs") and m.outputs != None:
                    for p in m.outputs:
                        output_mod_var_names.add(bp.module_output_ref(m.name, p.name))
                        if hasattr(p, "value") and isinstance(p.value, str) and (p.value != None and (p.value.startswith("$module.") or p.value.startswith("$blueprint."))):
                            value_refs.add(p.value)
                            output_mod_value_refs.add(p.value)
                if hasattr(m, "settings") and m.settings != None:
                    for p in m.settings:
                        input_mod_var_names.add(bp.module_setting_ref(m.name, p.name))
                        if hasattr(p, "value") and (p.value != None and isinstance(p.value, str) and (p.value.startswith("$module.") or p.value.startswith("$blueprint."))):
                            value_refs.add(p.value)
                            input_mod_value_refs.add(p.value)
        if hasattr(bp, "inputs") and bp.inputs != None:
            for p in bp.inputs:
                input_bp_var_names.add(bp.input_ref(p.name))
                if hasattr(p, "value") and isinstance(p.value, str) and (p.value != None and (p.value.startswith("$module.") or p.value.startswith("$blueprint."))):
                    value_refs.add(p.value)
        if hasattr(bp, "outputs") and bp.outputs != None:
            for p in bp.outputs:
                output_bp_var_names.add(bp.output_ref(p.name))
                if hasattr(p, "value") and isinstance(p.value, str) and (p.value != None):
                    if (p.value.startswith("$module.") or p.value.startswith("$blueprint.")):
                        value_refs.add(p.value)
                        output_bp_value_refs.add(p.value)
                    else:
                        uninit_bp_output_vals.add(p.name)

        if hasattr(bp, "settings") and bp.settings != None:
            for p in bp.settings:
                input_bp_var_names.add(bp.setting_ref(p.name))
                if hasattr(p, "value") and isinstance(p.value, str) and (p.value != None and (p.value.startswith("$module.") or p.value.startswith("$blueprint."))):
                    value_refs.add(p.value)
        #===============================================
        unused_bp_vars = set()
        for bp_inputs in input_bp_var_names:
            if not (bp_inputs in value_refs):
                unused_bp_vars.add(bp_inputs)      

        if len(unused_bp_vars) > 0:
            if level >= BPWarning:
                e = ValidationEvent(BPWarning, "Unused input parameters declared in the blueprint", bp, list(unused_bp_vars))
                bperrors.append(e)
                logr.warning(str(e))
        #===============================================
        undeclared_bp_vars = set()
        for mod_inputs in input_mod_value_refs:
            if mod_inputs.startswith("$blueprint."):
                if mod_inputs not in input_bp_var_names:
                    undeclared_bp_vars.add(mod_inputs)      

        if len(undeclared_bp_vars) > 0:
            if level >= BPError:
                e = ValidationEvent(BPError, "Undeclared blueprint parameters used by modules", bp, list(undeclared_bp_vars))
                bperrors.append(e)
                logr.error(str(e))
        #===============================================
        undeclared_mod_vars = set()
        for mod_inputs in input_mod_value_refs:
            if mod_inputs.startswith("$module.") and ".outputs." in mod_inputs:
                if mod_inputs not in output_mod_var_names:
                    undeclared_mod_vars.add(mod_inputs)      

        if len(undeclared_mod_vars) > 0:
            if level >= BPError:
                e = ValidationEvent(BPError, "Undeclared output parameters used by modules", bp, list(undeclared_mod_vars))
                bperrors.append(e)
                logr.error(str(e))
        #===============================================
        unused_mod_vars = set()
        for mod in output_mod_var_names:
            if (not (mod in output_bp_value_refs)) and (not (mod in input_mod_value_refs)):
                unused_mod_vars.add(mod)

        if len(unused_mod_vars) > 0:
            if level >= BPWarning:
                e = ValidationEvent(BPWarning, "Unused output parameters declared in the modules", bp, list(unused_mod_vars))
                bperrors.append(e)
                logr.warning(str(e))
        #===============================================
        if len(uninit_bp_output_vals) > 0:
            if level >= BPError:
                e = ValidationEvent(BPError, "Blueprint output parameters is left hanging", bp, list(uninit_bp_output_vals))
                bperrors.append(e)
                logr.error(str(e))
        #===============================================
        # are there any circular references between modules
        dag = bp.build_dag()
        if dag.isCyclic() == True:
            if level >= BPError:
                e = ValidationEvent(BPError, "Found circular dependencies between modules", bp, dag.getCyclicPath())
                bperrors.append(e)
                logr.error(str(e))
        #===============================================

        if len(bperrors) > 0:
            logr.debug("Found issues in blueprint - " + bp.name)
            logr.debug(bperrors)

        return bperrors

##====================================================================##

class ModuleValidator:
    def validate_module(self, mod, level=BPError):
        param_names = []
        duplicate_names = []
        value_refs = []
        invalid_params = []
        mverrors = []
        param_validator = ParameterValidator()
        if hasattr(mod, "inputs") :
            for p in mod.inputs:
                if p.name in param_names:
                    duplicate_names.append(mod.input_ref(p.name))
                else: 
                    param_names.append(p.name)
                if hasattr(p, "value") and p.value != None and isinstance(p.value, str) and (p.value.startswith('$module.') or p.value.startswith('$blueprint.')):
                    value_refs.append(p.value)
                pverrors = param_validator.validate_input(p, level)
                if len(pverrors) > 0 :
                    invalid_params.append(mod.input_ref(p.name))
                    mverrors.append(pverrors)

        if hasattr(mod, "outputs") :
            for p in mod.outputs:
                if p.name in param_names:
                    duplicate_names.append(mod.output_ref(p.name))
                else:
                    param_names.append(p.name)
                if hasattr(p, "value") and p.value != None and isinstance(p.value, str) and (p.value.startswith('$module.') or p.value.startswith('$blueprint.')):
                    value_refs.append(p.value)
                pverrors = param_validator.validate_output(p, level)
                if len(pverrors) > 0 :
                    invalid_params.append(mod.output_ref(p.name))
                    mverrors.append(pverrors)

        if hasattr(mod, "settings") :
            for p in mod.settings:
                if p.name in param_names:
                    duplicate_names.append(mod.setting_ref(p.name))
                else:
                    param_names.append(p.name)
                if hasattr(p, "value") and p.value != None and isinstance(p.value, str) and (p.value.startswith('$module.') or p.value.startswith('$blueprint.')):
                    value_refs.append(p.value)
                pverrors = param_validator.validate_setting(p, level)
                if len(pverrors) > 0 :
                    invalid_params.append(mod.setting_ref(p.name))
                    mverrors.append(pverrors)

        ret_errors = []
        # parameters with empty input values
        if len(invalid_params) > 0:
            if level >= BPError:
                e = ValidationEvent(BPError, "Error in the input parameters for the modules", self, invalid_params, mverrors)
                ret_errors.append(e)
                logr.error(str(e))

        # duplicate parameters (inputs, outputs, settings) with same name
        if len(duplicate_names) > 0:
            if level >= BPWarning:
                e = ValidationEvent(BPWarning, "Duplicate parameter names in the module", self, duplicate_names, mverrors)
                ret_errors.append(e)
                logr.warning(str(e))

        # self referential values in parameters (inputs, outputs, settings)
        invalid_self_references = []
        for val in value_refs:
            if val.startswith('$module.'+ mod.name):
                invalid_self_references.append(val)

        if len(invalid_self_references) > 0:
            if level >= BPError:
                e = ValidationEvent(BPError, "Self referencial values in the module", self, invalid_self_references, mverrors)
                ret_errors.append(e)
                logr.error(str(e))

        return ret_errors

##====================================================================##

class ParameterValidator:

    def validate_param(self, param, level=BPError):
        pverrors = []        
        if hasattr(param, "type") and (param.type != None and param.type.lower() == "boolean"):
            if hasattr(param, "value") and param.value != None:
                if isinstance(param.value, str) and (param.value.lower() == "true" or param.value.lower() == "false"):
                    param.value = True if param.value.lower() == "true" else False
                if not (param.value == True or param.value == False) :
                    if level >= BPError:
                        e = ValidationEvent(BPError, "Type mismatch for boolean parameter", param, param.value)
                        pverrors.append(e)
                        logr.error(str(e))
        return pverrors

    def validate_input(self, param, level=BPError):
        pverrors = self.validate_param(param, level)
        if hasattr(param, "value") and param.value == None:
            if level >= BPWarning:
                e = ValidationEvent(BPWarning, "Input parameter is not initialized with any value", param, param.value)
                pverrors.append(e)
                logr.warning(str(e))
        return pverrors

    def validate_output(self, param, level=BPError):
        pverrors = self.validate_param(param, level)
        # if hasattr(param, "value") and param.value == None:
        #     if level >= BPWarning:
        #         ValidationEvent(BPWarning, "Output parameter is not initialized with any value", param, param.value)
        #         pverrors.append(e)
        #         logr.warning(str(e))
        return pverrors

    def validate_setting(self, param, level=BPError):
        pverrors = self.validate_param(param, level)
        if param.value == None:
            if level >= BPWarning:
                e = ValidationEvent(BPWarning, "Setting parameter is not initialized with any value", param, param.value)
                pverrors.append(e)
                logr.warning(str(e))
        return pverrors

##====================================================================##