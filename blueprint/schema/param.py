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

import yaml
import sys

from blueprint.lib import event
from blueprint.lib import validator

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
#========================================================================
class Parameter(dict):
    def __init__(self, name, type="string", description=None, value=None):
        self.name = name
        self.type = type
        if(description != None):
            self.description = description
        if(value != None):
            self.value = value

    def merge(self, p):
        self.name = p.name
        if p.type != None:
            self.type = p.type
        if p.description != None:
            self.description = p.description
        if p.value != None:
            self.value = p.value

    def remove_null_entries(self):
        if self.name == None:
            del self.name
        if self.type == None:
            del self.type
        if self.description == None:
            del self.description
        if self.value == None:
            del self.value

    def validate(self, level=event.BPError):
        param_validator = validator.ParameterValidator()
        return param_validator.validate_param(self, level)

    def set_value(self, val):
            self.value = val

#========================================================================
class Input (Parameter):

    def __init__(self, name, type="string", description=None, value=None):
        self.description = description
        self.value = value
        super().__init__(name, type, description, value)

    def __str__(self):
        txt = "in("
        txt += "name:" + (self.name if hasattr(self, 'name') else 'None') + ", "
        txt += "type:" + str(self.type if hasattr(self, 'type') else 'None') + ", "
        txt += "value:" + str(self.value if hasattr(self, 'value') else 'None')
        txt += ")"
        return txt


    def __repr__(self):
        return self.__str__()

    def remove_null_entries(self):
        if self.name == None:
            del self.name
        if self.type == None:
            del self.type
        if self.description == None:
            del self.description
        if self.value == None:
            del self.value

    def to_yaml(self):
        # yaml.encoding = None
        errors = self.validate(event.BPWarning)
        eprint(errors)
        return yaml.dump(self, sort_keys=False)

    @classmethod
    def from_json(cls, data):
        name = data['name']
        try:
            type = data['type']
        except KeyError:
            type = "string"
        try:
            description = data['description']
        except KeyError:
            description = None
        try:
            value = data['value']
        except KeyError:
            value = None

        return cls(name, type, description, value)
        
    def validate(self, level=event.BPError):
        param_validator = validator.ParameterValidator()
        return param_validator.validate_input(self, level)

    def set_value(self, val):
        super().set_value(val)

#========================================================================
class Output (Parameter):
    def __init__(self, name, type="string", description=None, value=None):
        self.description = description
        self.value = value
        super().__init__(name, type, description, value)

    def __str__(self):
        txt = "out("
        txt += "name:" + (self.name if hasattr(self, 'name') else 'None') + ", "
        txt += "type:" + str(self.type if hasattr(self, 'type') else 'None') + ", "
        txt += "value:" + str(self.value if hasattr(self, 'value') else 'None')
        txt += ")"
        return txt

    def __repr__(self):
        return self.__str__()

    def remove_null_entries(self):
        if self.name == None:
            del self.name
        if self.type == None:
            del self.type
        if self.description == None:
            del self.description
        if self.value == None:
            del self.value

    def to_yaml(self):
        # yaml.encoding = None
        errors = self.validate(event.BPWarning)
        eprint(errors)
        return yaml.dump(self, sort_keys=False)

    @classmethod
    def from_json(cls, data):
        name = data['name']
        try:
            type = data['type']
        except KeyError:
            type = "string"
        
        try:
            description = data['description']
        except KeyError:
            description = None

        try:
            value = data['value']
        except KeyError:
            value = None
        
        return cls(name, type, description, value)

    def validate(self, level=event.BPError):
        param_validator = validator.ParameterValidator()
        return param_validator.validate_output(self, level)

    def set_value(self, val):
        super().set_value(val)

#========================================================================
class Setting (Parameter):

    def __init__(self, name, type="string", description=None, value=None):
        self.description = description
        self.value = value
        super().__init__(name, type, description, value)

    def __str__(self):
        txt = "env("
        txt += "name:" + (self.name if hasattr(self, 'name') else 'None') + ", "
        txt += "type:" + str(self.type if hasattr(self, 'type') else 'None') + ", "
        txt += "value:" + str(self.value if hasattr(self, 'value') else 'None')
        txt += ")"
        return txt

    def __repr__(self):
        return self.__str__()

    def remove_null_entries(self):
        if self.name == None:
            del self.name
        if self.type == None:
            del self.type
        if self.description == None:
            del self.description
        if self.value == None:
            del self.value

    def to_yaml(self):
        # yaml.encoding = None
        errors = self.validate(event.BPWarning)
        eprint(errors)
        return yaml.dump(self, sort_keys=False)

    @classmethod
    def from_json(cls, data):
        name = data['name']
        try:
            type = data['type']
        except KeyError:
            type = "string"
        
        try:
            description = data['description']
        except KeyError:
            description = None

        try:
            value = data['value']
        except KeyError:
            value = None
        
        return cls(name, type, description, value)

    def validate(self, level=event.BPError):
        param_validator = validator.ParameterValidator()
        return param_validator.validate_setting(self, level)

    def set_value(self, val):
        super().set_value(val)

#========================================================================
