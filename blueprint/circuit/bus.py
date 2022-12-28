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
from blueprint.circuit import bus

from typing import Union, List

Default = int(0)
Input = int(1)
Output = int(2)
Setting = int(3)

class Wire:

    def __init__(self, 
                from_node: Union[blueprint.Blueprint, module.Module], 
                from_param_name: str, 
                to_node: Union[blueprint.Blueprint, module.Module], 
                to_param_name: str ):
        
        """
        Wire connecting the parameters in the module or blueprint.

        :param from_node: starting point for the Bus (type: Module or Blueprint)
        :param from_param_name: name of parameter in the start Module or Blueprint
        :param to_node: end point for the Bus (type: Module or Blueprint)
        :param to_param_name: name of parameter in the end Module or Blueprint
        """
        self.from_param = from_param_name
        self.to_param   = to_param_name
        self.from_node  = from_node
        self.to_node    = to_node

        self.from_connector_type = Default
        self.to_connector_type = Default
        self.from_param_ref = ""
        self.to_param_ref = ""

    def __str__(self):
        txt = "wire("
        txt += "from:"  + str(self.from_param if hasattr(self, 'from_param') else 'None') + ", "
        txt += "to:"    + str(self.to_param if hasattr(self, 'to_param') else 'None')
        txt += ")"
        return txt

    def __repr__(self):
        return self.__str__()

    def validate(self):
        """
        Validate the from-param, to-param & connection in the Blueprint & Module definition
        """
        errors = []
        if isinstance(self.from_node, blueprint.Blueprint):
            self.from_node_type = "blueprint.Blueprint"
            (self.from_param_ref, err) = self.from_node.input_ref(self.from_param)
            self.from_connector_type = Input
            if err != None: 
                (self.from_param_ref, err) = self.from_node.output_ref(self.from_param)
                self.from_connector_type = Output
                if err != None: 
                    (self.from_param_ref, err) = self.from_node.setting_ref(self.from_param)
                    self.from_connector_type = Setting
                    if err != None:
                        errors.append(event.ValidationEvent(event.BPError, "Invalid 'from' parameter name in the wire", self))
        elif isinstance(self.from_node, module.Module):
            self.from_node_type = "module.Module"
            (self.from_param_ref, err)  = self.from_node.input_ref(self.from_param)
            self.from_connector_type = Input
            if err != None: 
                (self.from_param_ref, err) = self.from_node.output_ref(self.from_param)
                self.from_connector_type = Output
                if err != None: 
                    (self.from_param_ref, err)  = self.from_node.setting_ref(self.from_param)
                    self.from_connector_type = Setting
                    if err != None: 
                        errors.append(event.ValidationEvent(event.BPError, "Invalid 'from' parameter name in the wire", self))
        else:
            self.from_node_type = "Unknown"
            errors.append(event.ValidationEvent(event.BPError, "Invalid 'from' parameter name in the wire", self))

        if isinstance(self.to_node, blueprint.Blueprint):
            self.to_node_type = "blueprint.Blueprint"
            (self.to_param_ref, err) = self.to_node.input_ref(self.to_param)
            self.to_connector_type = Input
            if err != None: 
                (self.to_param_ref, err) = self.to_node.output_ref(self.to_param)
                self.to_connector_type = Output
                if err != None: 
                    (self.to_param_ref, err) = self.to_node.setting_ref(self.to_param)
                    self.to_connector_type = Setting
                    if err != None: 
                        errors.append(event.ValidationEvent(event.BPError, "Invalid 'to' parameter name in the wire", self))
        elif isinstance(self.to_node, module.Module):
            self.to_node_type = "module.Module"
            (self.to_param_ref, err) = self.to_node.input_ref(self.to_param)
            self.to_connector_type = Input
            if err != None: 
                (self.to_param_ref, err) = self.to_node.output_ref(self.to_param)
                self.to_connector_type = Output
                if err != None: 
                    (self.to_param_ref, err) = self.to_node.setting_ref(self.to_param)
                    self.to_connector_type = Setting
                    if err != None: 
                        errors.append(event.ValidationEvent(event.BPError, "Invalid 'to' parameter name in the wire", self))
        else:
            self.to_node_type = "Unknown"
            errors.append(event.ValidationEvent(event.BPError, "Invalid 'to' parameter name in the wire", self))
        
        return errors

    def commit(self):
        """
        Save the connection in the Blueprint & Module, by modifying the parameter values with the linked-data-references
        """
        errors = []
        if self.from_node_type == "blueprint.Blueprint" and self.to_node_type == "module.Module":
            if self.from_connector_type == Input:
                if self.to_connector_type == Input:
                    self.to_node.set_input_value(self.to_param, self.from_param_ref)
                elif self.to_connector_type == Setting:
                    self.to_node.set_setting_value(self.to_param, self.from_param_ref)
                elif self.to_connector_type == Output:
                    errors.append(event.ValidationEvent(event.BPError, "Incorrect wiring from blueprint.Blueprint.input to module.Module.output", self))
            elif self.from_connector_type == Output:
                if self.to_connector_type == Input:
                    errors.append(event.ValidationEvent(event.BPError, "Incorrect wiring from blueprint.Blueprint.output to module.Module.input", self))
                elif self.to_connector_type == Setting:
                    errors.append(event.ValidationEvent(event.BPError, "Incorrect wiring from blueprint.Blueprint.output to module.Module.setting", self))
                elif self.to_connector_type == Output:
                    errors.append(event.ValidationEvent(event.BPError, "Incorrect wiring from blueprint.Blueprint.output to module.Module.output", self))
            if self.from_connector_type == Setting:
                if self.to_connector_type == Input:
                    errors.append(event.ValidationEvent(event.BPError, "Incorrect wiring from blueprint.Blueprint.setting to module.Module.input", self))
                elif self.to_connector_type == Setting:
                    self.to_node.set_setting_value(self.to_param, self.from_param_ref)
                elif self.to_connector_type == Output:
                    errors.append(event.ValidationEvent(event.BPError, "Incorrect wiring from blueprint.Blueprint.setting to module.Module.output", self))
        
        elif self.from_node_type == "module.Module" and self.to_node_type == "module.Module":
            if self.from_connector_type == Input:
                if self.to_connector_type == Input:
                    errors.append(event.ValidationEvent(event.BPError, "Incorrect wiring from module.Module.input to module.Module.input", self))
                elif self.to_connector_type == Setting:
                    errors.append(event.ValidationEvent(event.BPError, "Incorrect wiring from module.Module.input to module.Module.setting", self))
                elif self.to_connector_type == Output:
                    errors.append(event.ValidationEvent(event.BPError, "Incorrect wiring from module.Module.input to module.Module.output", self))
            elif self.from_connector_type == Output:
                if self.to_connector_type == Input:
                    self.to_node.set_input_value(self.to_param, self.from_param_ref)
                elif self.to_connector_type == Setting:
                    self.to_node.set_setting_value(self.to_param, self.from_param_ref)
                elif self.to_connector_type == Output:
                    errors.append(event.ValidationEvent(event.BPError, "Incorrect wiring from module.Module.output to module.Module.output", self))
            if self.from_connector_type == Setting:
                if self.to_connector_type == Input:
                    errors.append(event.ValidationEvent(event.BPError, "Incorrect wiring from module.Module.setting to module.Module.input", self))
                elif self.to_connector_type == Setting:
                    errors.append(event.ValidationEvent(event.BPError, "Incorrect wiring from module.Module.setting to module.Module.setting", self))
                elif self.to_connector_type == Output:
                    errors.append(event.ValidationEvent(event.BPError, "Incorrect wiring from module.Module.setting to module.Module.output", self))

        elif self.from_node_type == "module.Module" and self.to_node_type == "blueprint.Blueprint":
            if self.from_connector_type == Input:
                if self.to_connector_type == Input:
                    errors.append(event.ValidationEvent(event.BPError, "Incorrect wiring from module.Module.input to blueprint.Blueprint.input", self))
                elif self.to_connector_type == Output:
                    errors.append(event.ValidationEvent(event.BPError, "Incorrect wiring from module.Module.input to blueprint.Blueprint.output", self))
                elif self.to_connector_type == Setting:
                    errors.append(event.ValidationEvent(event.BPError, "Incorrect wiring from module.Module.input to blueprint.Blueprint.setting", self))
            elif self.from_connector_type == Output:
                if self.to_connector_type == Input:
                    errors.append(event.ValidationEvent(event.BPError, "Incorrect wiring of module.Module.output to blueprint.Blueprint.input", self))
                elif self.to_connector_type == Output:
                    self.to_node.set_output_value(self.to_param, self.from_param_ref)
                if self.to_connector_type == Setting:
                    errors.append(event.ValidationEvent(event.BPError, "Incorrect wiring of module.Module.output to blueprint.Blueprint.setting", self))
            if self.from_connector_type == Setting:
                if self.to_connector_type == Input:
                    errors.append(event.ValidationEvent(event.BPError, "Incorrect wiring from module.Module.setting to blueprint.Blueprint.input", self))
                elif self.to_connector_type == Output:
                    errors.append(event.ValidationEvent(event.BPError, "Incorrect wiring from module.Module.setting to blueprint.Blueprint.output", self))
                elif self.to_connector_type == Setting:
                    errors.append(event.ValidationEvent(event.BPError, "Incorrect wiring from module.Module.setting to blueprint.Blueprint.setting", self))
        else:
            errors.append(event.ValidationEvent(event.BPError, "Bad bus from blueprint.Blueprint to blueprint.Blueprint", self))

        return errors

class Bus:

    def __init__(self, 
                from_node: Union[blueprint.Blueprint, module.Module], 
                to_node: Union[blueprint.Blueprint, module.Module], 
                wires: List[Wire] = None ):
        """
        Bus as a collection of wires connecting two modules, or with blueprint.

        :param from_node: starting point for the Bus (type: Module or Blueprint)
        :param to_node: end point for the Bus (type: Module or Blueprint)
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
        if not(isinstance(self.from_node, blueprint.Blueprint) or isinstance(self.from_node, module.Module)):
            e.append(event.ValidationEvent(event.BPError, "Invalid 'from' node in the bus", self))

        if not(isinstance(self.to_node, blueprint.Blueprint) or isinstance(self.to_node, module.Module)):
            e.append(event.ValidationEvent(event.BPError, "Invalid 'to' node in the bus", self))

        for w in self.wires:
            e += w.validate()
        return e

    def add_wire(self, from_param_name, to_param_name):
        try:
            w1 = Wire(self.from_node, from_param_name, self.to_node, to_param_name) 
            errors = w1.validate()
            errors += w1.commit()
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

    def _find_bus(self, from_node, to_node):

        if self.fleet == None or len(self.fleet) == 0:
            return None

        for b in self.fleet:
            if b.from_node.name == from_node.name and b.to_node.name == to_node.name:
                return b
        
        return None
    def _add_wire(self, from_node, from_param_name, to_node, to_param_name):
        # find bus in the fleet, add bus (if if does not exist)
        bus = self._find_bus(from_node, to_node)
        if bus == None:
            new_wire = Wire(from_node, from_param_name, to_node, to_param_name)
            new_bus = Bus(from_node, to_node, [new_wire]) 
            self.fleet.append(new_bus)
        else:
            new_wire = Wire(from_node, from_param_name, to_node, to_param_name)
            bus.add_wire(from_param_name, to_param_name)

    def read(self):
        
        for outp in self.bp.outputs:
            val = outp.get_value()
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

        for mod in self.bp.modules:
            if hasattr(mod, 'inputs') and mod.inputs != None and len(mod.inputs) > 0:
                for inp in mod.inputs:
                    val = inp.get_value()
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
