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

class BlueprintValidator:
    def validate_blueprint(self, bp, level=BPError):
        bperrors = []
        # validate all modules (parameters, bp-references, input-types)
        mod_validator = ModuleValidator()
        for m in bp.modules:
            mverror = mod_validator.validate_module(m, level)
            if len(mverror) > 0:
                bperrors.append(ValidationEvent(BPError, "Error in blueprint modules", bp, m, mverror))

        # hanging inputs & outputs
        value_refs = []
        output_bp_value_refs = []
        input_mod_value_refs = []
        input_mod_var_names = []
        output_mod_var_names = []
        input_bp_var_names = []
        output_bp_var_names = []
        uninit_bp_output_vals = []
        if hasattr(bp, "modules") and bp.modules != None:
            for m in bp.modules:
                if hasattr(m, "inputs") and m.inputs != None:
                    for p in m.inputs:
                        input_mod_var_names.append(bp.module_input_ref(m.name, p.name))
                        if hasattr(p, "value") and isinstance(p.value, str) and (p.value != None and (p.value.startswith("$module." + m.name) or p.value.startswith("$blueprint."))):
                            value_refs.append(p.value)
                            input_mod_value_refs.append(p.value)
                if hasattr(m, "outputs") and m.outputs != None:
                    for p in m.outputs:
                        output_mod_var_names.append(bp.module_output_ref(m.name, p.name))
                        if hasattr(p, "value") and isinstance(p.value, str) and (p.value != None and (p.value.startswith("$module." + m.name) or p.value.startswith("$blueprint."))):
                            value_refs.append(p.value)
                if hasattr(m, "settings") and m.settings != None:
                    for p in m.settings:
                        input_mod_var_names.append(bp.module_setting_ref(m.name, p.name))
                        if hasattr(p, "value") and (p.value != None and isinstance(p.value, str) and (p.value.startswith("$module." + m.name) or p.value.startswith("$blueprint."))):
                            value_refs.append(p.value)
                            input_mod_value_refs.append(p.value)
        if hasattr(bp, "inputs") and bp.inputs != None:
            for p in bp.inputs:
                input_bp_var_names.append(bp.input_ref(p.name))
                if hasattr(p, "value") and isinstance(p.value, str) and (p.value != None and (p.value.startswith("$module.") or p.value.startswith("$blueprint."))):
                    value_refs.append(p.value)
        if hasattr(bp, "outputs") and bp.outputs != None:
            for p in bp.outputs:
                output_bp_var_names.append(bp.output_ref(p.name))
                if hasattr(p, "value") and isinstance(p.value, str) and (p.value != None):
                    if (p.value.startswith("$module.") or p.value.startswith("$blueprint.")):
                        value_refs.append(p.value)
                        output_bp_value_refs.append(p.value)
                    else:
                        uninit_bp_output_vals.append(p.name)

        if hasattr(bp, "settings") and bp.settings != None:
            for p in bp.settings:
                input_bp_var_names.append(bp.setting_ref(p.name))
                if hasattr(p, "value") and isinstance(p.value, str) and (p.value != None and (p.value.startswith("$module.") or p.value.startswith("$blueprint."))):
                    value_refs.append(p.value)
        #===============================================
        unused_bp_vars = []
        for bp_inputs in input_bp_var_names:
            if not (bp in value_refs):
                unused_bp_vars.append(bp_inputs)      

        if len(unused_bp_vars) > 0:
            if level >= BPWarning:
                bperrors.append(ValidationEvent(BPWarning, "Unused input parameters declared in the blueprint", bp, unused_bp_vars))
        #===============================================
        unused_mod_vars = []
        for mod in output_mod_var_names:
            if (not (mod in output_bp_value_refs)) and (not (mod in input_mod_value_refs)):
                unused_mod_vars.append(mod)

        if len(unused_mod_vars) > 0:
            if level >= BPWarning:
                bperrors.append(ValidationEvent(BPWarning, "Unused output parameters declared in the modules", bp, unused_mod_vars))
        #===============================================
        if len(uninit_bp_output_vals) > 0:
            if level >= BPError:
                bperrors.append(ValidationEvent(BPError, "Blueprint output parameters is left hanging", bp, uninit_bp_output_vals))
        #===============================================
        # are there any circular references between modules
        dag = self.build_dag(bp)
        if dag.isCyclic() == True:
            if level >= BPError:
                bperrors.append(ValidationEvent(BPError, "Found circular dependencies between modules", bp, dag.getCyclicPath()))
        #===============================================
        return bperrors

    def build_dag(self, bp):
        g = BlueprintGraph(len(bp.modules))
        for m in bp.modules:
            iref = m.input_value_refs()
            for i in iref:
                if i.startswith("$module.") :
                    n = i[8:i.find(".", 8)]
                    g.addEdge(n, m.name)
                elif i.startswith("$blueprint.") :
                    g.addEdge("blueprint", m.name)

            oref = m.output_value_refs()
            for o in oref:
                if o.startswith("$module.") :
                    n = o[8:o.find(".", 8)]
                    g.addEdge(m.name, n)
                elif o.startswith("$blueprint.") :
                    g.addEdge(m.name, "blueprint")
        return g

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
                ret_errors.append(ValidationEvent(BPError, "Error in the input parameters for the modules", self, invalid_params, mverrors))

        # duplicate parameters (inputs, outputs, settings) with same name
        if len(duplicate_names) > 0:
            if level >= BPWarning:
                ret_errors.append(ValidationEvent(BPWarning, "Duplicate parameter names in the module", self, duplicate_names, mverrors))

        # self referential values in parameters (inputs, outputs, settings)
        invalid_self_references = []
        for val in value_refs:
            if val.startswith('$module.'+ mod.name):
                invalid_self_references.append(val)

        if len(invalid_self_references) > 0:
            if level >= BPError:
                ret_errors.append(ValidationEvent(BPError, "Self referencial values in the module", self, invalid_self_references, mverrors))

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
                        pverrors.append(ValidationEvent(BPError, "Type mismatch for boolean parameter", param, param.value))
        return pverrors

    def validate_input(self, param, level=BPError):
        pverrors = self.validate_param(param, level)
        if hasattr(param, "value") and param.value == None:
            if level >= BPWarning:
                pverrors.append(ValidationEvent(BPWarning, "Input parameter is not initialized with any value", param, param.value))
        return pverrors

    def validate_output(self, param, level=BPError):
        pverrors = self.validate_param(param, level)
        # if hasattr(param, "value") and param.value == None:
        #     if level >= BPWarning:
        #         pverrors.append(ValidationEvent(BPWarning, "Output parameter is not initialized with any value", param, param.value))
        return pverrors

    def validate_setting(self, param, level=BPError):
        pverrors = self.validate_param(param, level)
        if param.value == None:
            if level >= BPWarning:
                pverrors.append(ValidationEvent(BPWarning, "Setting parameter is not initialized with any value", param, param.value))
        return pverrors

##====================================================================##