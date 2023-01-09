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
from blueprint.schema import blueprint
from blueprint.schema import module
from blueprint.lib import event

from blueprint.circuit.bus import Circuit, WireBus, Wire

from blueprint.lib.logger import logr
import logging
logr = logging.getLogger(__name__)

class CircuitModel:
    def __init__(self, circuit: Circuit):
        self.circuit = circuit

        self.bp_bus = []
        self.mod_bus = []

        self._prepare_bp_buses()

    def _prepare_bp_buses(self):
        for b in self.circuit.fleet:
            if isinstance(b.from_node, blueprint.Blueprint):
                self.bp_bus.append(b)
            elif isinstance(b.to_node, blueprint.Blueprint):
                self.bp_bus.append(b)
            else:
                self.mod_bus.append(b)

    def validate(self) -> List[event.ValidationEvent]:
        events = []
        logr.debug("Validating blueprint circuit: ")

        events.extend(self._validate_blueprint_bus())
        events.extend(self._validate_module_bus())

        return sorted(list(set(events)))

    def _validate_blueprint_bus(self) -> List[event.ValidationEvent]:
        events = []
        #===============================================
        # Type mismatch on the wire for the blueprint
        for b in self.bp_bus:
            bv = BusModel(b)
            events.extend(bv.validate())

        return events

    def _validate_module_bus(self) -> List[event.ValidationEvent]:
        events = []
        #===============================================
        # Type mismatch on the wire for the module
        for b in self.mod_bus:
            bv = BusModel(b)
            events.extend(bv.validate())

        return events

class BusModel:
    def __init__(self, bus: WireBus):
        self.bus = bus

    def validate(self) -> List[event.ValidationEvent]:
        events = []
        if not(isinstance(self.bus.from_node, blueprint.Blueprint) or isinstance(self.bus.from_node, module.Module)):
            events.append(event.ValidationEvent(event.BPError, "Invalid 'from' node in the bus", self.bus.from_node.name))

        if not(isinstance(self.bus.to_node, blueprint.Blueprint) or isinstance(self.bus.to_node, module.Module)):
            events.append(event.ValidationEvent(event.BPError, "Invalid 'to' node in the bus", self.bus.to_node.name))

        for w in self.bus.wires:
            wv = WireModel(w)
            events.extend(wv.validate())
        
        return events
        
class WireModel:
    def __init__(self, wire: Wire):
        self.wire = wire

    def validate(self) -> List[event.ValidationEvent]:
        
        from blueprint.circuit import bus
        events = self.wire.errors
        """
        Validate the from-param, to-param & connection in the Blueprint & Module definition
        """
        if self.wire.from_node_type == "blueprint.Blueprint" and self.wire.to_node_type == "module.Module":
            if self.wire.from_connector_type == bus.Input:
                if self.wire.to_connector_type == bus.Output:
                    events.append(event.ValidationEvent(event.BPError, "Incorrect wiring", None, f'from: {self.wire.from_param_ref} to: {self.wire.to_param_ref}'))
            elif self.wire.from_connector_type == bus.Output:
                if self.wire.to_connector_type == bus.Input:
                    events.append(event.ValidationEvent(event.BPError, "Incorrect wiring", None, f'from: {self.wire.from_param_ref} to: {self.wire.to_param_ref}'))
                elif self.wire.to_connector_type == bus.Setting:
                    events.append(event.ValidationEvent(event.BPError, "Incorrect wiring", None, f'from: {self.wire.from_param_ref} to: {self.wire.to_param_ref}'))
                elif self.wire.to_connector_type == bus.Output:
                    events.append(event.ValidationEvent(event.BPError, "Incorrect wiring", None, f'from: {self.wire.from_param_ref} to: {self.wire.to_param_ref}'))
            if self.wire.from_connector_type == bus.Setting:
                if self.wire.to_connector_type == bus.Input:
                    events.append(event.ValidationEvent(event.BPError, "Incorrect wiring", None, f'from: {self.wire.from_param_ref} to: {self.wire.to_param_ref}'))
                elif self.wire.to_connector_type == bus.Output:
                    events.append(event.ValidationEvent(event.BPError, "Incorrect wiring", None, f'from: {self.wire.from_param_ref} to: {self.wire.to_param_ref}'))
        
        elif self.wire.from_node_type == "module.Module" and self.wire.to_node_type == "module.Module":
            if self.wire.from_connector_type == bus.Input:
                if self.wire.to_connector_type == bus.Input:
                    events.append(event.ValidationEvent(event.BPError, "Incorrect wiring", None, f'from: {self.wire.from_param_ref} to: {self.wire.to_param_ref}'))
                elif self.wire.to_connector_type == bus.Setting:
                    events.append(event.ValidationEvent(event.BPError, "Incorrect wiring", None, f'from: {self.wire.from_param_ref} to: {self.wire.to_param_ref}'))
                elif self.wire.to_connector_type == bus.Output:
                    events.append(event.ValidationEvent(event.BPError, "Incorrect wiring", None, f'from: {self.wire.from_param_ref} to: {self.wire.to_param_ref}'))
            elif self.wire.from_connector_type == bus.Output:
                if self.wire.to_connector_type == bus.Output:
                    events.append(event.ValidationEvent(event.BPError, "Incorrect wiring", None, f'from: {self.wire.from_param_ref} to: {self.wire.to_param_ref}'))
            if self.wire.from_connector_type == bus.Setting:
                if self.wire.to_connector_type == bus.Input:
                    events.append(event.ValidationEvent(event.BPError, "Incorrect wiring", None, f'from: {self.wire.from_param_ref} to: {self.wire.to_param_ref}'))
                elif self.wire.to_connector_type == bus.Setting:
                    events.append(event.ValidationEvent(event.BPError, "Incorrect wiring", None, f'from: {self.wire.from_param_ref} to: {self.wire.to_param_ref}'))
                elif self.wire.to_connector_type == bus.Output:
                    events.append(event.ValidationEvent(event.BPError, "Incorrect wiring", None, f'from: {self.wire.from_param_ref} to: {self.wire.to_param_ref}'))

        elif self.wire.from_node_type == "module.Module" and self.wire.to_node_type == "blueprint.Blueprint":
            if self.wire.from_connector_type == bus.Input:
                if self.wire.to_connector_type == bus.Input:
                    events.append(event.ValidationEvent(event.BPError, "Incorrect wiring", None, f'from: {self.wire.from_param_ref} to: {self.wire.to_param_ref}'))
                elif self.wire.to_connector_type == bus.Output:
                    events.append(event.ValidationEvent(event.BPError, "Incorrect wiring", None, f'from: {self.wire.from_param_ref} to: {self.wire.to_param_ref}'))
                elif self.wire.to_connector_type == bus.Setting:
                    events.append(event.ValidationEvent(event.BPError, "Incorrect wiring", None, f'from: {self.wire.from_param_ref} to: {self.wire.to_param_ref}'))
            elif self.wire.from_connector_type == bus.Output:
                if self.wire.to_connector_type == bus.Input:
                    events.append(event.ValidationEvent(event.BPError, "Incorrect wiring", None, f'from: {self.wire.from_param_ref} to: {self.wire.to_param_ref}'))
                if self.wire.to_connector_type == bus.Setting:
                    events.append(event.ValidationEvent(event.BPError, "Incorrect wiring", None, f'from: {self.wire.from_param_ref} to: {self.wire.to_param_ref}'))
            if self.wire.from_connector_type == bus.Setting:
                if self.wire.to_connector_type == bus.Input:
                    events.append(event.ValidationEvent(event.BPError, "Incorrect wiring", None, f'from: {self.wire.from_param_ref} to: {self.wire.to_param_ref}'))
                elif self.wire.to_connector_type == bus.Output:
                    events.append(event.ValidationEvent(event.BPError, "Incorrect wiring", None, f'from: {self.wire.from_param_ref} to: {self.wire.to_param_ref}'))
                elif self.wire.to_connector_type == bus.Setting:
                    events.append(event.ValidationEvent(event.BPError, "Incorrect wiring", None, f'from: {self.wire.from_param_ref} to: {self.wire.to_param_ref}'))
        else:
            events.append(event.ValidationEvent(event.BPError, "Incorrect bus", None, f'from: {self.wire.from_param_ref} to: {self.wire.to_param_ref}'))

        """
        Validate the data-types in from-param and to-param
        """
        from_param = self.wire.from_param
        if from_param != None:
            from_param_type = from_param.get_type()
        else:
            from_param_type = 'unknown'
        
        to_param = self.wire.to_param
        if to_param != None:
            to_param_type = to_param.get_type()
        else:
            to_param_type = 'unknown'

        if str(from_param_type).lower() != str(to_param_type).lower():
            events.append(event.ValidationEvent(event.BPWarning, "Type mismatch on the wire", None, 
                                        f'from: {from_param_type} T {self.wire.from_param_ref} to: {to_param_type} T {self.wire.to_param_ref}'))

        return events