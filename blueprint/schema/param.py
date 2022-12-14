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
from blueprint.validate import blueprint_validator

from blueprint.lib.logger import logr
# import logging
# logr = logging.getLogger(__name__)

def eprint(*args, **kwargs):
    logr.error(*args)
    print(*args, file=sys.stderr, **kwargs)

#========================================================================
class Parameter(dict):
    def __init__(self, 
                name: str           = "__init__", 
                type: str           = "string", 
                description: str    = None, 
                value: str          = None):
        """Parameter schema (base).

        :param name: Name of the parameter
        :param type: Type of paramter
        :param description: Description of the parameter
        :param value: Parameter value
        """

        self.name = name
        self.type = type
        if(description != None):
            self.description = description
        if(value != None):
            self.value = value

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.name = "__init__"

    def merge(self, p):
        self.name = p.name
        if p.type != None:
            self.type = p.type
        if p.description != None:
            self.description = p.description
        if p.value != None:
            self.value = p.value

    def remove_null_entries(self):
        if hasattr(self, 'name') and self.name == None:
            del self.name
        if hasattr(self, 'type') and self.type == None:
            del self.type
        if hasattr(self, 'description') and self.description == None:
            del self.description
        if hasattr(self, 'value') and self.value == None:
            del self.value

    def validate(self, level=event.BPError):
        param_validator = blueprint_validator.ParameterValidator()
        return param_validator.validate_param(self, level)

    def set_value(self, val):
            self.value = val

    def get_value(self):
            return self.value

#========================================================================
class Input (Parameter):

    def __init__(self, 
                name: str           = "__init__", 
                type: str           = "string", 
                description: str    = None, 
                value: str          = None):
        """Input parameter.

        :param name: Name of the input parameter
        :param type: Type of input paramter
        :param description: Description of the input parameter
        :param value: Input parameter value
        """
        super().__init__(name, type, description, value)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.name = "__init__"

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
        super().remove_null_entries()
        # if self.name == None:
        #     del self.name
        # if self.type == None:
        #     del self.type
        # if self.description == None:
        #     del self.description
        # if self.value == None:
        #     del self.value

    def to_yaml(self):
        # yaml.encoding = None
        errors = self.validate(event.BPWarning)
        # eprint(errors)
        return (yaml.dump(self, sort_keys=False), errors)

    @classmethod
    def from_yaml(cls, yaml_data):

        if isinstance(yaml_data, Input):
            return yaml_data

        name = yaml_data['name']
        try:
            type = yaml_data['type']
        except KeyError:
            type = "string"
        try:
            description = yaml_data['description']
        except KeyError:
            description = None
        try:
            value = yaml_data['value']
        except KeyError:
            value = None

        return cls(name, type, description, value)

    @classmethod
    def from_yaml_list(cls, yaml_data_list):
        pars = []
        for yaml_data in yaml_data_list:
            pars.append(Input.from_yaml(yaml_data))

        return pars

    def validate(self, level=event.BPError):
        param_validator = blueprint_validator.ParameterValidator()
        return param_validator.validate_input(self, level)

    def set_value(self, val):
        super().set_value(val)

#========================================================================
class Output (Parameter):
    def __init__(self,
                name: str           = "__init__", 
                type: str           = "string", 
                description: str    = None, 
                value: str          = None):
        """Output parameter.

        :param name: Name of the output parameter
        :param type: Type of output paramter
        :param description: Description of the output parameter
        :param value: Output parameter value
        """
        super().__init__(name, type, description, value)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.name = "__init__"

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
        super().remove_null_entries()
        # if self.name == None:
        #     del self.name
        # if self.type == None:
        #     del self.type
        # if self.description == None:
        #     del self.description
        # if self.value == None:
        #     del self.value

    def to_yaml(self):
        # yaml.encoding = None
        errors = self.validate(event.BPWarning)
        # eprint(errors)
        return (yaml.dump(self, sort_keys=False), errors)

    @classmethod
    def from_yaml(cls, yaml_data):

        if isinstance(yaml_data, Output):
            return yaml_data

        name = yaml_data['name']
        try:
            type = yaml_data['type']
        except KeyError:
            type = "string"
        
        try:
            description = yaml_data['description']
        except KeyError:
            description = None

        try:
            value = yaml_data['value']
        except KeyError:
            value = None
        
        return cls(name, type, description, value)

    @classmethod
    def from_yaml_list(cls, yaml_data_list):
        pars = []
        for yaml_data in yaml_data_list:
            pars.append(Output.from_yaml(yaml_data))

        return pars

    def validate(self, level=event.BPError):
        param_validator = blueprint_validator.ParameterValidator()
        return param_validator.validate_output(self, level)

    def set_value(self, val):
        super().set_value(val)

#========================================================================
class Setting (Parameter):

    def __init__(self,
                name: str           = "__init__", 
                type: str           = "string", 
                description: str    = None, 
                value: str          = None):
        """Environment settings parameter.

        :param name: Name of the setting parameter
        :param type: Type of setting paramter
        :param description: Description of the setting parameter
        :param value: Environment setting parameter value
        """
        super().__init__(name, type, description, value)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.name = "__init__"

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
        super().remove_null_entries()
        # if self.name == None:
        #     del self.name
        # if self.type == None:
        #     del self.type
        # if self.description == None:
        #     del self.description
        # if self.value == None:
        #     del self.value

    def to_yaml(self):
        # yaml.encoding = None
        errors = self.validate(event.BPWarning)
        # eprint(errors)
        return (yaml.dump(self, sort_keys=False), errors)

    @classmethod
    def from_yaml(cls, yaml_data):

        if isinstance(yaml_data, Setting):
            return yaml_data

        name = yaml_data['name']
        try:
            type = yaml_data['type']
        except KeyError:
            type = "string"
        
        try:
            description = yaml_data['description']
        except KeyError:
            description = None

        try:
            value = yaml_data['value']
        except KeyError:
            value = None
        
        return cls(name, type, description, value)

    @classmethod
    def from_yaml_list(cls, yaml_data_list):
        pars = []
        for yaml_data in yaml_data_list:
            pars.append(Setting.from_yaml(yaml_data))

        return pars


    def validate(self, level=event.BPError):
        param_validator = blueprint_validator.ParameterValidator()
        return param_validator.validate_setting(self, level)

    def set_value(self, val):
        super().set_value(val)

#========================================================================
