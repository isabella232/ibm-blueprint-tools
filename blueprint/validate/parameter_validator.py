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

class ParameterModel:
    def __init__(self, param, param_type = None):
        self.param = param
        self.name = param.name
        self.param_type = param_type
        self.value = None
        self.value_ref = None
        self.default = param.default if hasattr(param, 'default') else None
        self.description = param.description if hasattr(param, 'description') else ""

        if hasattr(param, 'type') and param.type != None:
            self.type = param.type 
        else:
            if hasattr(param, 'value') and param.value != None:
                self.type = val_type(param.value)
            else:
                self.type = 'unknown'

        if hasattr(param, 'value'):
            if isinstance(param.value, str) and \
                (param.value.startswith("$blueprint.") or param.value.startswith("$module.")):
                self.value_ref = param.value
            else:
                self.value = param.value
        else:
            self.value = None

    def validate(self) -> List[event.ValidationEvent]:
        events = []
        logr.debug("Validating parameter: " + self.name)

        events.extend(self._validate_param_types())
        
        return sorted(list(set(events)))

    def _validate_param_types(self) -> List[event.ValidationEvent]:
        events = []

        #===============================================
        # Type mismatch for parameter value
        if self.value != None and not is_val_type(self.value, self.type):
            e = event.ValidationEvent(event.BPWarning, f"Type mismatch for {self.param_type} parameter's value", self.type, self.name)
            events.append(e)

        #===============================================
        # Type mismatch for parameter defaults
        if self.default != None and not is_val_type(self.default, self.type):
            e = event.ValidationEvent(event.BPWarning, f"Type mismatch for {self.param_type} parameter's default value", self.type, self.name)
            events.append(e)

        return events

