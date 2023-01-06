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

from blueprint.lib import event 
from blueprint.schema import blueprint
from blueprint.schema import module
from blueprint.schema import param

import copy
from typing import Union, List

Default = int(0)
Input = int(1)
Output = int(2)
Setting = int(3)
Bad = int(4)

class Wire:

    def __init__(self, 
                from_node: Union[blueprint.Blueprint, module.Module], 
                from_param_name: str, 
                to_node: Union[blueprint.Blueprint, module.Module], 
                to_param_name: str,
                from_connector_type: int = Default, # Enum[Input, Output, Setting]
                to_connector_type: int = Default    # Enum[Input, Output, Setting]
                ):
        
        """
        Wire connecting the parameters in the module or blueprint.

        :param from_node: starting point for the WireBus (type: Module or Blueprint)
        :param from_param_name: name of parameter in the start Module or Blueprint
        :param to_node: end point for the WireBus (type: Module or Blueprint)
        :param to_param_name: name of parameter in the end Module or Blueprint
        """
        self.from_node  = from_node
        self.to_node    = to_node

        self.from_connector_type = from_connector_type
        self.to_connector_type = to_connector_type
        self.from_param_ref = ""
        self.to_param_ref = ""
        self.errors = []

        self._prepare_from_connector(from_param_name)
        self._prepare_to_connector(to_param_name)
        self._dry_run()


    def __str__(self):
        txt = "wire("
        txt += f'from: {self.from_param_name}/{self.from_connector_type}, '
        txt += f'to: {self.to_param_name}/{self.to_connector_type}'
        txt += ")"
        return txt

    def __repr__(self):
        return self.__str__()

    def validate(self):
        e = []
        from blueprint.validate.circuit_validator import WireModel
        wv = WireModel(self)
        e.extend(wv.validate())
        return e

    def _prepare_from_connector(self, from_param_name):
        """
        Prepare the from_param_ref & connector_type in the Blueprint & Module definition
        """
        if self.from_connector_type == Default:
            if isinstance(self.from_node, blueprint.Blueprint):
                self.from_node_type         = "blueprint.Blueprint"
                (self.from_param, err)      = self.from_node.input_param(from_param_name)
                (self.from_param_ref, err)  = self.from_node.input_ref(from_param_name)
                self.from_param_name        = from_param_name
                self.from_connector_type    = Input
                if err != None: 
                    (self.from_param, err)      = self.from_node.output_param(from_param_name)
                    (self.from_param_ref, err)  = self.from_node.output_ref(from_param_name)
                    self.from_param_name        = from_param_name
                    self.from_connector_type    = Output
                    if err != None: 
                        (self.from_param, err)      = self.from_node.setting_param(from_param_name)
                        (self.from_param_ref, err)  = self.from_node.setting_ref(from_param_name)
                        self.from_param_name        = from_param_name
                        self.from_connector_type    = Setting
                        if err != None:
                            self.from_param         = None
                            self.from_param_name    = f'Error({from_param_name})'
                            self.from_connector_type  = Bad
                            self.errors.append(event.ValidationEvent(event.BPError, "Invalid 'from' parameter name in the wire", None, f'from($blueprint.{from_param_name})'))
            elif isinstance(self.from_node, module.Module):
                self.from_node_type         = "module.Module"
                (self.from_param, err)      = self.from_node.input_param(from_param_name)
                (self.from_param_ref, err)  = self.from_node.input_ref(from_param_name)
                self.from_param_name        = from_param_name
                self.from_connector_type    = Input
                if err != None: 
                    (self.from_param, err)      = self.from_node.output_param(from_param_name)
                    (self.from_param_ref, err)  = self.from_node.output_ref(from_param_name)
                    self.from_param_name        = from_param_name
                    self.from_connector_type    = Output
                    if err != None: 
                        (self.from_param, err)      = self.from_node.setting_param(from_param_name)
                        (self.from_param_ref, err)  = self.from_node.setting_ref(from_param_name)
                        self.from_param_name        = from_param_name
                        self.from_connector_type    = Setting
                        if err != None:
                            self.from_param         = None 
                            self.from_param_name    = f'Error({from_param_name})'
                            self.from_connector_type  = Bad
                            self.errors.append(event.ValidationEvent(event.BPError, "Invalid 'from' parameter name in the wire", None, f'from($module.{self.from_node.name}.{from_param_name})'))
            else:
                self.from_node_type = "Unknown"
                self.from_param_name = f'Error({from_param_name})'
                self.from_connector_type  = Bad
                self.errors.append(event.ValidationEvent(event.BPError, "Invalid 'from' parameter name in the wire", None, f'from({from_param_name})'))
        else:
            if isinstance(self.from_node, blueprint.Blueprint):
                self.from_node_type     = "blueprint.Blueprint"
                self.from_param_name    = from_param_name
                self.from_param         = None
                self.from_param_ref     = None

            elif isinstance(self.from_node, module.Module):
                self.from_node_type     = "module.Module"
                self.from_param_name    = from_param_name
                self.from_param         = None
                self.from_param_ref     = None


    def _prepare_to_connector(self, to_param_name):
        """
        Prepare the to_param_ref & connector_type in the Blueprint & Module definition
        """
        if self.to_connector_type == Default:
            if isinstance(self.to_node, blueprint.Blueprint):
                self.to_node_type = "blueprint.Blueprint"
                (self.to_param, err)        = self.to_node.input_param(to_param_name)
                (self.to_param_ref, err)    = self.to_node.input_ref(to_param_name)
                self.to_param_name          = to_param_name
                self.to_connector_type      = Input
                if err != None: 
                    (self.to_param, err)        = self.to_node.output_param(to_param_name)
                    (self.to_param_ref, err)    = self.to_node.output_ref(to_param_name)
                    self.to_param_name          = to_param_name
                    self.to_connector_type  = Output
                    if err != None: 
                        (self.to_param, err)        = self.to_node.setting_param(to_param_name)
                        (self.to_param_ref, err)    = self.to_node.setting_ref(to_param_name)
                        self.to_param_name          = to_param_name
                        self.to_connector_type      = Setting
                        if err != None: 
                            self.to_param           = None
                            self.to_param_name      = f'Error({to_param_name})'
                            self.to_connector_type  = Bad
                            self.errors.append(event.ValidationEvent(event.BPError, "Invalid 'to' parameter name in the wire", None, f'to($blueprint.{to_param_name})'))
            elif isinstance(self.to_node, module.Module):
                self.to_node_type = "module.Module"
                (self.to_param, err)        = self.to_node.input_param(to_param_name)
                (self.to_param_ref, err)    = self.to_node.input_ref(to_param_name)
                self.to_param_name          = to_param_name
                self.to_connector_type      = Input
                if err != None: 
                    (self.to_param, err)        = self.to_node.output_param(to_param_name)
                    (self.to_param_ref, err)    = self.to_node.output_ref(to_param_name)
                    self.to_param_name          = to_param_name
                    self.to_connector_type      = Output
                    if err != None: 
                        (self.to_param, err)        = self.to_node.setting_param(to_param_name)
                        (self.to_param_ref, err)    = self.to_node.setting_ref(to_param_name)
                        self.to_param_name          = to_param_name
                        self.to_connector_type      = Setting
                        if err != None: 
                            self.to_param           = None
                            self.to_param_name      = f'Error({to_param_name})'
                            self.to_connector_type  = Bad
                            self.errors.append(event.ValidationEvent(event.BPError, "Invalid 'to' parameter name in the wire", None, f'to($module.{self.to_node.name}.{to_param_name})'))
            else:
                self.to_node_type   = "Unknown"
                self.to_param       = None
                self.to_param_name  = f'Error({to_param_name})'
                self.to_connector_type  = Bad
                self.errors.append(event.ValidationEvent(event.BPError, "Invalid 'to' parameter name in the wire", None, f'to({to_param_name})'))

        else:
            if isinstance(self.to_node, blueprint.Blueprint):
                self.to_node_type     = "blueprint.Blueprint"
                self.to_param_name    = to_param_name
                self.to_param         = None
                self.to_param_ref     = None

            elif isinstance(self.to_node, module.Module):
                self.to_node_type     = "module.Module"
                self.to_param_name    = to_param_name
                self.to_param         = None
                self.to_param_ref     = None


    def _dry_run(self):
        """
        Dry-run to find wiring errors
        """
        if (self.from_connector_type == Bad or self.to_connector_type == Bad):
            self.errors.append(event.ValidationEvent(event.BPError, "Bad connectors on the wire", None, f"from: {self.from_param_name} to: {self.to_param_name}"))

        if self.from_node_type == "blueprint.Blueprint" and self.to_node_type == "module.Module":
            if self.from_connector_type == Input and self.to_connector_type == Input:
                pass
            elif self.from_connector_type == Input and self.to_connector_type == Setting:
                pass
            elif self.from_connector_type == Setting and self.to_connector_type == Setting:
                pass
            else:
                self.errors.append(event.ValidationEvent(event.BPError, "Incorrect wiring", None, f"from: {self.from_param_ref} to: {self.to_param_ref}"))

        elif self.from_node_type == "module.Module" and self.to_node_type == "module.Module":
            if self.from_connector_type == Output and self.to_connector_type == Input:
                pass
            elif self.from_connector_type == Output and self.to_connector_type == Setting:
                pass
            else:
                self.errors.append(event.ValidationEvent(event.BPError, "Incorrect wiring", None, f"from: {self.from_param_ref} to: {self.to_param_ref}"))

        elif self.from_node_type == "module.Module" and self.to_node_type == "blueprint.Blueprint":
            if self.from_connector_type == Output and self.to_connector_type == Output:
                pass
            else:
                self.errors.append(event.ValidationEvent(event.BPError, "Incorrect wiring", None, f"from: {self.from_param_ref} to: {self.to_param_ref}"))

        else:
            self.errors.append(event.ValidationEvent(event.BPError, "Incorrect wiring", None, f"from: {self.from_param_ref} to: {self.to_param_ref}"))


    def commit(self):
        
        if self.from_connector_type == Bad or self.to_connector_type == Bad:
            self.errors.append(event.ValidationEvent(event.BPError, "Bad connectors on the wire", None, f"from: {self.from_param_name} to: {self.to_param_name}"))

        """
        Add the Blueprint & Module params
        """
        existing_from_param = None
        existing_to_param = None
        if self.from_param == None:

            if isinstance(self.from_node, blueprint.Blueprint):
                if self.from_connector_type     == Input:
                    (tmp_from_param, err)       = self.from_node.input_param(self.from_param_name)
                    if err != None:
                        p = param.Input(name=self.from_param_name)
                        self.from_node.add_input(p)
                    else:
                        existing_from_param = copy.deepcopy(tmp_from_param)
                    (self.from_param, err)      = self.from_node.input_param(self.from_param_name)
                    (self.from_param_ref, err)  = self.from_node.input_ref(self.from_param_name)
                elif self.from_connector_type   == Output:
                    (tmp_from_param, err)       = self.from_node.output_param(self.from_param_name)
                    if err != None:
                        p = param.Output(name=self.from_param_name)
                        self.from_node.add_output(p)
                    else:
                        existing_from_param = copy.deepcopy(tmp_from_param)
                    (self.from_param, err)      = self.from_node.output_param(self.from_param_name)
                    (self.from_param_ref, err)  = self.from_node.output_ref(self.from_param_name)
                elif self.from_connector_type   == Setting:
                    (tmp_from_param, err)       = self.from_node.setting_param(self.from_param_name)
                    if err != None:
                        p = param.Setting(name=self.from_param_name)
                        self.from_node.add_setting(p)
                    else:
                        existing_from_param = copy.deepcopy(tmp_from_param)
                    (self.from_param, err)      = self.from_node.setting_param(self.from_param_name)
                    (self.from_param_ref, err)  = self.from_node.setting_ref(self.from_param_name)
                else:
                    self.errors.append(event.ValidationEvent(event.BPError, "Bad connectors on the wire", None, f"from: {self.from_param_name}"))
                    return

            elif isinstance(self.from_node, module.Module):
                if self.from_connector_type     == Input:
                    (tmp_from_param, err)       = self.from_node.input_param(self.from_param_name)
                    if err != None:
                        p = param.Input(name=self.from_param_name)
                    else:
                        existing_from_param = copy.deepcopy(tmp_from_param)
                        self.from_node.add_input(p)
                    (self.from_param, err)      = self.from_node.input_param(self.from_param_name)
                    (self.from_param_ref, err)  = self.from_node.input_ref(self.from_param_name)
                elif self.from_connector_type   == Output:
                    (tmp_from_param, err)       = self.from_node.output_param(self.from_param_name)
                    if err != None:
                        p = param.Output(name=self.from_param_name)
                        self.from_node.add_output(p)
                    else:
                        existing_from_param = copy.deepcopy(tmp_from_param)
                    (self.from_param, err)      = self.from_node.output_param(self.from_param_name)
                    (self.from_param_ref, err)  = self.from_node.output_ref(self.from_param_name)
                elif self.from_connector_type   == Setting:
                    (tmp_from_param, err)       = self.from_node.setting_param(self.from_param_name)
                    if err != None:
                        p = param.Setting(name=self.from_param_name)
                        self.from_node.add_setting(p)
                    else:
                        existing_from_param = copy.deepcopy(tmp_from_param)
                    (self.from_param, err)      = self.from_node.setting_param(self.from_param_name)
                    (self.from_param_ref, err)  = self.from_node.setting_ref(self.from_param_name)
                else:
                    self.errors.append(event.ValidationEvent(event.BPError, "Bad connectors on the wire", None, f"from: {self.from_param_name}"))
                    return
            else:
                self.errors.append(event.ValidationEvent(event.BPError, "Invalid 'from' nodes on the Bus", None, type(self.from_node)))
                return

        if self.to_param == None:

            if isinstance(self.to_node, blueprint.Blueprint):
                if self.to_connector_type       == Input:
                    (tmp_to_param, err)         = self.to_node.input_param(self.to_param_name)
                    if err != None:
                        p = param.Input(name=self.to_param_name)
                        self.to_node.add_input(p)
                    else:
                        existing_to_param       = copy.deepcopy(tmp_to_param)
                        existing_to_param.name  = self.from_param_name
                    (self.to_param, err)        = self.to_node.input_param(self.to_param_name)
                    (self.to_param_ref, err)    = self.to_node.input_ref(self.to_param_name)
                elif self.to_connector_type     == Output:
                    (tmp_to_param, err)         = self.to_node.output_param(self.to_param_name)
                    if err != None:
                        p = param.Output(name=self.to_param_name)
                        self.to_node.add_output(p)
                    else:
                        existing_to_param       = copy.deepcopy(tmp_to_param)
                        existing_to_param.name  = self.from_param_name
                    (self.to_param, err)        = self.to_node.output_param(self.to_param_name)
                    (self.to_param_ref, err)    = self.to_node.output_ref(self.to_param_name)
                elif self.to_connector_type     == Setting:
                    (tmp_to_param, err)         = self.to_node.setting_param(self.to_param_name)
                    if err != None:
                        p = param.Setting(name=self.to_param_name)
                        self.to_node.add_setting(p)
                    else:
                        existing_to_param       = copy.deepcopy(tmp_to_param)
                        existing_to_param.name  = self.from_param_name
                    (self.to_param, err)        = self.to_node.setting_param(self.to_param_name)
                    (self.to_param_ref, err)    = self.to_node.setting_ref(self.to_param_name)
                else:
                    self.errors.append(event.ValidationEvent(event.BPError, "Bad connectors on the wire", None, f"to: {self.to_param_name}"))

            elif err == None and isinstance(self.to_node, module.Module):
                if self.to_connector_type       == Input:
                    (tmp_to_param, err)         = self.to_node.input_param(self.to_param_name)
                    if err != None:
                        p = param.Input(name=self.to_param_name)
                        self.to_node.add_input(p)
                    else:
                        existing_to_param       = copy.deepcopy(tmp_to_param)
                        existing_to_param.name  = self.from_param_name
                    (self.to_param, err)        = self.to_node.input_param(self.to_param_name)
                    (self.to_param_ref, err)    = self.to_node.input_ref(self.to_param_name)
                elif self.to_connector_type     == Output:
                    (tmp_to_param, err)        = self.to_node.output_param(self.to_param_name)
                    if err != None:
                        p = param.Output(name=self.to_param_name)
                        self.to_node.add_output(p)
                    else:
                        existing_to_param       = copy.deepcopy(tmp_to_param)
                        existing_to_param.name  = self.from_param_name
                    (self.to_param, err)        = self.to_node.output_param(self.to_param_name)
                    (self.to_param_ref, err)    = self.to_node.output_ref(self.to_param_name)
                elif self.to_connector_type     == Setting:
                    (tmp_to_param, err)         = self.to_node.setting_param(self.to_param_name)
                    if err != None:
                        p = param.Setting(name=self.to_param_name)
                        self.to_node.add_setting(p)
                    else:
                        existing_to_param       = copy.deepcopy(tmp_to_param)
                        existing_to_param.name  = self.from_param_name
                    (self.to_param, err)        = self.to_node.setting_param(self.to_param_name)
                    (self.to_param_ref, err)    = self.to_node.setting_ref(self.to_param_name)
                else:
                    self.errors.append(event.ValidationEvent(event.BPError, "Bad connectors on the wire", None, f"to: {self.to_param_name}"))
                    return
            else:
                self.errors.append(event.ValidationEvent(event.BPError, "Invalid 'to' nodes on the Bus", None, type(self.to_node)))
                return

        """
        Save the connection in the Blueprint & Module, by modifying the parameter values with the linked-data-references
        """
        if self.from_node_type == "blueprint.Blueprint" and self.to_node_type == "module.Module":
            if self.from_connector_type == Input and self.to_connector_type == Input:
                self.to_node.set_input_value(self.to_param_name, self.from_param_ref)
                if existing_to_param != None:
                    self.from_node.update_input(existing_to_param)
            elif self.from_connector_type == Input and self.to_connector_type == Setting:
                self.to_node.set_setting_value(self.to_param_name, self.from_param_ref)
                if existing_to_param != None:
                    self.from_node.update_input(existing_to_param)
            elif self.from_connector_type == Setting and self.to_connector_type == Setting:
                self.to_node.set_setting_value(self.to_param_name, self.from_param_ref)
                if existing_to_param != None:
                    self.from_node.update_setting(existing_to_param)
            else:
                self.errors.append(event.ValidationEvent(event.BPError, "Incorrect wiring", None, f"from: {self.from_param_ref} to: {self.to_param_ref}"))

        elif self.from_node_type == "module.Module" and self.to_node_type == "module.Module":
            if self.from_connector_type == Output and self.to_connector_type == Input:
                self.to_node.set_input_value(self.to_param_name, self.from_param_ref)
                if existing_to_param != None:
                    self.from_node.update_output(existing_to_param)
            elif self.from_connector_type == Output and self.to_connector_type == Setting:
                self.to_node.set_setting_value(self.to_param_name, self.from_param_ref)
                if existing_to_param != None:
                    self.from_node.update_output(existing_to_param)
            else:
                self.errors.append(event.ValidationEvent(event.BPError, "Incorrect wiring", None, f"from: {self.from_param_ref} to: {self.to_param_ref}"))

        elif self.from_node_type == "module.Module" and self.to_node_type == "blueprint.Blueprint":
            if self.from_connector_type == Output and self.to_connector_type == Output:
                self.to_node.set_output_value(self.to_param_name, self.from_param_ref)
                if existing_to_param != None:
                    self.from_node.update_output(existing_to_param)
            else:
                self.errors.append(event.ValidationEvent(event.BPError, "Incorrect wiring", None, f"from: {self.from_param_ref} to: {self.to_param_ref}"))

        else:
            self.errors.append(event.ValidationEvent(event.BPError, "Incorrect wiring", None, f"from: {self.from_param_ref} to: {self.to_param_ref}"))

        """
        Sync the type in the from & to parameters in the wire
        """
        from_param_type = None
        if self.from_param != None:
            from_param_type = self.from_param.get_type()

        to_param_type = None
        if self.to_param != None:
            to_param_type = self.to_param.get_type()

        if self.from_param != None and from_param_type != to_param_type and (from_param_type == None or from_param_type == 'unknown'):
            from_param_type = to_param_type if to_param_type != 'linked' else None
            self.from_param.set_type(from_param_type)

        elif self.to_param != None and from_param_type != to_param_type and (to_param_type == None or to_param_type == 'unknown'):
            to_param_type = to_param_type if to_param_type != 'linked' else None
            self.to_param.set_type(to_param_type)
        
        else:
            from_param_type = 'unknown' if from_param_type  == None else from_param_type
            to_param_type   = 'unknown' if to_param_type    == None else to_param_type
            self.errors.append(event.ValidationEvent(event.BPError, "Type mismatch on the wire", None, 
                                    f'from: {from_param_type} T {self.from_param_ref} to: {to_param_type} T {self.to_param_ref}'))

class WireBus:

    def __init__(self, 
                from_node: Union[blueprint.Blueprint, module.Module], 
                to_node: Union[blueprint.Blueprint, module.Module], 
                wires: List[Wire] = None ):
        """
        WireBus as a collection of wires connecting two modules, or with blueprint.

        :param from_node: starting point for the WireBus (type: Module or Blueprint)
        :param to_node: end point for the WireBus (type: Module or Blueprint)
        :param wires: Collection of wires connecting the parameters (type bus.Wire)
        """

        self.from_node  = from_node
        self.to_node    = to_node
        self.wires      = [] if wires == None else wires

    def __str__(self):
        txt = "bus("
        txt += "start:" + str(self.from_node if hasattr(self, 'from_node') else 'None') + ", "
        txt += "end:"   + str(self.to_node if hasattr(self, 'to_node') else 'None')
        txt += "wires:" + str(self.wires if hasattr(self, 'wires') else 'None')
        txt += ")"
        return txt

    def __repr__(self):
        return self.__str__()

    def validate(self):
        e = []
        from blueprint.validate.circuit_validator import BusModel
        bv = BusModel(self)
        e.extend(bv.validate())
        return e

    def add_wire(self, from_param_name, to_param_name,
                from_connector_type: int = Default, # Enum[Input, Output, Setting]
                to_connector_type: int = Default    # Enum[Input, Output, Setting]
                ):
        try:
            w1 = Wire(self.from_node, from_param_name, self.to_node, to_param_name,
                        from_connector_type = from_connector_type,
                        to_connector_type = to_connector_type) 
            errors = w1.validate()
            w1.commit()
            # if len(errors) == 0:
            #     self.wires.append(w1)
            self.wires.append(w1)
            return errors
        except ValueError as e:
            return [event.ValidationEvent(event.BPError, "Invalid wiring between (" + from_param_name + ", " + to_param_name + ")", self, str(e))]

    def commit(self):
        e = []
        for w in self.wires:
            e += w.commit()
        return e


class Circuit:
    def __init__(self, bp: blueprint.Blueprint):
        """
        Circuit as a collection of bus & wires in a blueprint.

        :param bp: Blueprint to engineer or reverse-engineer the Circuit
        """
        self.bp     = bp # Blueprint
        self.fleet  = [] # List of buses

        self._prepare()

    def _find_bus(self, from_node, to_node):

        if self.fleet == None or len(self.fleet) == 0:
            return None
        
        if from_node == None or to_node == None:
            return None

        for b in self.fleet:
            if b.from_node.name == from_node.name and b.to_node.name == to_node.name:
                return b
        
        return None

    def _add_wire(self, from_node, from_param_name, to_node, to_param_name):
        if from_node == None or to_node == None:
            raise ValueError(f"Invalid bus for the wire, with from node: {from_node}, to node: {to_node}")

        if from_param_name == None or to_param_name == None:
            raise ValueError(f"Invalid wire for the bus, with from param: {from_param_name}, to param: {to_param_name}")

        # find bus in the fleet, add bus (if if does not exist)
        bus = self._find_bus(from_node, to_node)
        if bus == None:
            new_wire = Wire(from_node, from_param_name, to_node, to_param_name)
            new_bus = WireBus(from_node, to_node, [new_wire]) 
            self.fleet.append(new_bus)
        else:
            new_wire = Wire(from_node, from_param_name, to_node, to_param_name)
            bus.add_wire(from_param_name, to_param_name)

    def _prepare(self):
        if hasattr(self.bp, 'outputs') and self.bp.outputs != None:
            for outp in self.bp.outputs:
                val = outp.get_value()
                if val != None and isinstance(val, str):
                    if val.startswith('$module.'):
                        split_val = val.split('.')
                        # output-val = $module.mod_name.type.var_name
                        node = split_val[0]
                        mod_name = split_val[1]
                        type = split_val[2]
                        var_name = split_val[3]

                        (from_mod, error) = self.bp.get_module(mod_name)
                        self._add_wire(from_mod, var_name, self.bp, outp.name)
                    
                    elif val.startswith('$blueprint.'):
                        split_val = val.split('.')
                        # val = $blueprint.type.var_name
                        node = split_val[0]
                        type = split_val[1]
                        var_name = split_val[2]

                        self._add_wire(self.bp, var_name, self.bp, outp.name)

        if hasattr(self.bp, 'modules') and self.bp.outputs != None:
            for mod in self.bp.modules:
                if hasattr(mod, 'inputs') and mod.inputs != None and len(mod.inputs) > 0:
                    for inp in mod.inputs:
                        val = inp.get_value()
                        if val != None and isinstance(val, str):
                            if val.startswith('$module.'):
                                # input-val = $module.mod_name.type.var_name
                                split_val = val.split('.')
                                node = split_val[0]
                                mod_name = split_val[1]
                                type = split_val[2]
                                var_name = split_val[3]

                                (from_mod, error) = self.bp.get_module(mod_name)
                                self._add_wire(from_mod, var_name, mod, inp.name)
                            
                            elif val.startswith('$blueprint.'):
                                split_val = val.split('.')
                                # val = $blueprint.var_name
                                if len(split_val) == 3:
                                    node = split_val[0]
                                    type = split_val[1]
                                    var_name = split_val[2]
                                elif len(split_val) == 2:
                                    node = split_val[0]
                                    var_name = split_val[1]
                            
                                self._add_wire(self.bp, var_name, mod, inp.name)

                if hasattr(mod, 'settings') and mod.settings != None and len(mod.settings) > 0:
                    for envp in mod.settings:
                        val = envp.get_value()
                        if val != None and isinstance(val, str):
                            if val.startswith('$module.'):
                                # setting-val = $module.mod_name.type.var_name
                                split_val = val.split('.')
                                node = split_val[0]
                                mod_name = split_val[1]
                                type = split_val[2]
                                var_name = split_val[3]

                                (from_mod, error) = self.bp.get_module(mod_name)
                                self._add_wire(from_mod, var_name, mod, envp.name)
                            
                            elif val.startswith('$blueprint.'):
                                split_val = val.split('.')
                                # val = $blueprint.type.var_name
                                node = split_val[0]
                                type = split_val[1]
                                var_name = split_val[2]

                                self._add_wire(self.bp, var_name, mod, envp.name)

    def validate(self):
        e = []
        from blueprint.validate.circuit_validator import CircuitModel
        cv = CircuitModel(self)
        e.extend(cv.validate())
        return e
