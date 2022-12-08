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

Default = int(0)
Input = int(1)
Output = int(2)
Setting = int(3)

class Bus:

    def __init__(self, from_node, to_node, wires=None):
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

class Wire:

    def __init__(self, from_node, from_param_name, to_node, to_param_name):
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
                    self.to_node.set_input_value(self.to_param, self.from_param_ref)
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

