# (C) Copyright IBM Corp. 2022.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
import re
from typing import List
import copy

from os.path import exists as file_exists

from blueprint.schema import blueprint
from blueprint.schema import module
from blueprint.schema import param
from blueprint.schema import source as src

from blueprint.validate import blueprint_validator
from blueprint.circuit import bus

from blueprint.lib import type_helper

from python_terraform import *

import subprocess

from blueprint.lib.logger import logr
# import logging
# logr = logging.getLogger(__name__)

def eprint(*args, **kwargs):
    logr.error(*args)
    print(*args, file=sys.stderr, **kwargs)

class BlueprintReconciler:

    def __init__(self, bp: blueprint.Blueprint):
        self.bp = bp
        self.cqt = bus.Circuit(bp)

    def _linked_type(self, val):
        if not (val.startswith('$blueprint') or val.startswith('$module')):
            return None
        p = '\$module\.(.*)\.(.*)\.(.*)'
        result = re.search(p, val)
        if result != None:
            mod_name = result[1]
            param_name = result[2]
            if self.bp.modules != None:
                for mod in self.bp.modules:
                    if mod.name == mod_name:
                        if hasattr(mod, 'inputs') and mod.inputs != None:
                            for param in mod.inputs:
                                if param.name == param_name:
                                    if hasattr(param, 'type') and param.type != None:
                                        type = param.type
                                    elif hasattr(param, 'value') and param.value != None:
                                        type = type_helper.val_type(param.value)
                                    else:
                                        type = None
                                    if type == 'unknown':
                                        type = None
                                    elif type == 'linked':
                                        type = self._linked_type(param.value)
                                    return type

                        if hasattr(mod, 'outputs') and mod.outputs != None:
                            for param in mod.outputs:
                                if param.name == param_name:
                                    if hasattr(param, 'type') and param.type != None:
                                        type = param.type
                                    elif hasattr(param, 'value') and param.value != None:
                                        type = type_helper.val_type(param.value)
                                    else:
                                        type = None
                                    if type == 'unknown':
                                        type = None
                                    elif type == 'linked':
                                        type = self._linked_type(param.value)
                                    return type

                        if hasattr(mod, 'settings') and mod.settings != None:
                            for param in mod.settings:
                                if param.name == param_name:
                                    if hasattr(param, 'type') and param.type != None:
                                        type = param.type
                                    elif hasattr(param, 'value') and param.value != None:
                                        type = type_helper.val_type(param.value)
                                    else:
                                        type = None
                                    if type == 'unknown':
                                        type = None
                                    elif type == 'linked':
                                        type = self._linked_type(param.value)
                                    return type
        
                        if hasattr(mod, 'injectors') and mod.injectors != None:
                            for injtrs in mod.injectors:
                                if hasattr(injtrs, 'tft_parameters') and injtrs.tft_parameters != None:
                                    for param in injtrs.tft_parameters:
                                        if hasattr(param, 'type') and param.type != None:
                                            type = param.type
                                        elif hasattr(param, 'value') and param.value != None:
                                            type = type_helper.val_type(param.value)
                                        else:
                                            type = None
                                        if type == 'unknown':
                                            type = None
                                        elif type == 'linked':
                                            type = self._linked_type(param.value)
                                        param.type = type

        elif val.startswith('$blueprint.inputs.'):
            param_name = val[len('$blueprint.inputs.'):]
            for param in self.bp.inputs:
                if param.name == param_name:
                    if hasattr(param, 'type') and param.type != None:
                        type = param.type
                    elif hasattr(param, 'value') and param.value != None:
                        type = type_helper.val_type(param.value)
                    else:
                        type = None
                    if type == 'unknown':
                        type = None
                    elif type == 'linked':
                        type = self._linked_type(param.value)
                    return type
        
        elif val.startswith('$blueprint.outputs.'):
            param_name = val[len('$blueprint.outputs.'):]
            for param in self.bp.outputs:
                if param.name == param_name:
                    if hasattr(param, 'type') and param.type != None:
                        type = param.type
                    elif hasattr(param, 'value') and param.value != None:
                        type = type_helper.val_type(param.value)
                    else:
                        type = None
                    if type == 'unknown':
                        type = None
                    elif type == 'linked':
                        type = self._linked_type(param.value)
                    return type

        elif val.startswith('$blueprint.settings.'):
            param_name = val[len('$blueprint.settings.'):]
            for param in self.bp.settings:
                if param.name == param_name:
                    if hasattr(param, 'type') and param.type != None:
                        type = param.type
                    elif hasattr(param, 'value') and param.value != None:
                        type = type_helper.val_type(param.value)
                    else:
                        type = None
                    if type == 'unknown':
                        type = None
                    elif type == 'linked':
                        type = self._linked_type(param.value)
                    return type

        return None
    #---_linked_type(val)------------------------------------------------

    def _reconcile_blueprint_types(self):
        if hasattr(self.bp, 'inputs') and self.bp.inputs != None:
            for param in self.bp.inputs:
                if hasattr(param, 'type') and param.type != None:
                    type = param.type
                elif hasattr(param, 'value') and param.value != None:
                    type = type_helper.val_type(param.value)
                else:
                    type = None
                if type == 'unknown':
                    type = None
                elif type == 'linked':
                    type = self._linked_type(param.value)
                param.type = type

        if hasattr(self.bp, 'outputs') and self.bp.outputs != None:
            for param in self.bp.outputs:
                if hasattr(param, 'type') and param.type != None:
                    type = param.type
                elif hasattr(param, 'value') and param.value != None:
                    type = type_helper.val_type(param.value)
                else:
                    type = None
                if type == 'unknown':
                    type = None
                elif type == 'linked':
                    type = self._linked_type(param.value)
                param.type = type

        if hasattr(self.bp, 'settings') and self.bp.settings != None:
            for param in self.bp.settings:
                if hasattr(param, 'type') and param.type != None:
                    type = param.type
                elif hasattr(param, 'value') and param.value != None:
                    type = type_helper.val_type(param.value)
                else:
                    type = None
                if type == 'unknown':
                    type = None
                elif type == 'linked':
                    type = self._linked_type(param.value)
                param.type = type
        
        else:
            pass
    #---------------------------------------------------------------

    def _reconcile_module_types(self):
        if hasattr(self.bp, 'modules') and self.bp.modules != None:
            for mod in self.bp.modules:
                if hasattr(mod, 'inputs') and mod.inputs != None:
                    for param in mod.inputs:
                        if hasattr(param, 'type') and param.type != None:
                            type = param.type
                        elif hasattr(param, 'value') and param.value != None:
                            type = type_helper.val_type(param.value)
                        else:
                            type = None
                        if type == 'unknown':
                            type = None
                        elif type == 'linked':
                            type = self._linked_type(param.value)
                        param.type = type

                if hasattr(mod, 'outputs') and mod.outputs != None:
                    for param in mod.outputs:
                        if hasattr(param, 'type') and param.type != None:
                            type = param.type
                        elif hasattr(param, 'value') and param.value != None:
                            type = type_helper.val_type(param.value)
                        else:
                            type = None
                        if type == 'unknown':
                            type = None
                        elif type == 'linked':
                            type = self._linked_type(param.value)
                        param.type = type

                if hasattr(mod, 'settings') and mod.settings != None:
                    for param in mod.settings:
                        if hasattr(param, 'type') and param.type != None:
                            type = param.type
                        elif hasattr(param, 'value') and param.value != None:
                            type = type_helper.val_type(param.value)
                        else:
                            type = None
                        if type == 'unknown':
                            type = None
                        elif type == 'linked':
                            type = self._linked_type(param.value)
                        param.type = type

                if hasattr(mod, 'injectors') and mod.injectors != None:
                    for injtrs in mod.injectors:
                        if hasattr(injtrs, 'tft_parameters') and injtrs.tft_parameters != None:
                            for param in injtrs.tft_parameters:
                                if hasattr(param, 'type') and param.type != None:
                                    type = param.type
                                elif hasattr(param, 'value') and param.value != None:
                                    type = type_helper.val_type(param.value)
                                else:
                                    type = None
                                if type == 'unknown':
                                    type = None
                                elif type == 'linked':
                                    type = self._linked_type(param.value)
                                param.type = type

    #---------------------------------------------------------------

    def _promote_unlinked_mod_params(self):
        if hasattr(self.bp, 'modules') and self.bp.modules != None:
            bpm = blueprint_validator.BlueprintModel(self.bp)
            mod_input_refs = bpm.mod_input_value.keys()
            mod_input_vars = [x.split('.')[-1] for x in mod_input_refs]
            if hasattr(self.bp, 'inputs') and self.bp.inputs != None:
                bp_input_vars = [x.name for x in self.bp.inputs]
            else:
                bp_input_vars = []

            mod_output_refs = bpm.mod_output_value.keys()
            mod_output_vars = [x.split('.')[-1] for x in mod_output_refs]
            if hasattr(self.bp, 'outputs') and self.bp.outputs != None:
                bp_output_vars = [x.name for x in self.bp.outputs]
            else:
                bp_output_vars = []

            mod_setting_refs = bpm.mod_setting_value.keys()
            mod_setting_vars = [x.split('.')[-1] for x in mod_setting_refs]
            if hasattr(self.bp, 'settings') and self.bp.settings != None:
                bp_setting_vars = [x.name for x in self.bp.settings]
            else:
                bp_setting_vars = []

            for pname in mod_input_vars:
                if pname not in bp_input_vars:
                    for mod in self.bp.modules:
                        if hasattr(mod, 'inputs') and mod.inputs != None:
                            input_param = None
                            for x in mod.inputs:
                                if x.name == pname:
                                    input_param = x
                                    break
                            if input_param != None:
                                bp_bus = bus.WireBus(self.bp, mod)
                                mod_acy = mod.get_acronym().upper()
                                bp_pname = mod_acy + '_' + pname
                                bp_bus.add_wire(bp_pname, pname, from_connector_type=bus.Input, to_connector_type=bus.Input)
                                break

            for pname in mod_output_vars:
                if pname not in bp_output_vars:
                    for mod in self.bp.modules:
                        if hasattr(mod, 'outputs') and mod.outputs != None:
                            output_param = None
                            for x in mod.outputs:
                                if x.name == pname:
                                    output_param = x
                                    break
                            if output_param != None:
                                bp_bus = bus.WireBus(mod, self.bp)
                                mod_acy = mod.get_acronym().upper()
                                bp_pname = mod_acy + '_' + pname
                                bp_bus.add_wire(pname, bp_pname, from_connector_type=bus.Output, to_connector_type=bus.Output)
                                break

            for pname in mod_setting_vars:
                if pname not in bp_setting_vars:
                    for mod in self.bp.modules:
                        if hasattr(mod, 'settings') and mod.settings != None:
                            setting_param = None
                            for x in mod.settings:
                                if x.name == pname:
                                    setting_param = x
                                    break
                            if setting_param != None:
                                bp_bus = bus.WireBus(self.bp, mod)
                                mod_acy = mod.get_acronym().upper()
                                bp_pname = mod_acy + '_' + pname
                                bp_bus.add_wire(bp_pname, pname, from_connector_type=bus.Setting, to_connector_type=bus.Setting)
                                break

    #---------------------------------------------------------------

    def reconcile(self):
        
        self._reconcile_blueprint_types()
        self._reconcile_module_types()
        self._promote_unlinked_mod_params()


