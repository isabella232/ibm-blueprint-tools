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

from blueprint.lib import type_helper
from blueprint.validate import parameter_validator

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
                type: str           = None, 
                description: str    = None, 
                value: str          = None,
                comment: str       = None):
        """Parameter schema (base).

        :param name: Name of the parameter
        :param type: Type of parameter
        :param description: Description of the parameter
        :param value: Parameter value
        """

        self.name = name
        self.type = type
        if(description != None):
            self.description = description
        if(value != None):
            self.value = value
        if(comment != None):
            self.comment = comment
        

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.name = "__init__"

    def merge(self, p):
        self.name = p.name
        if hasattr(p, 'type') and p.type != None:
            self.type = p.type
        if hasattr(p, 'description') and p.description != None:
            self.description = p.description
        if hasattr(p, 'value') and p.value != None:
            self.value = p.value
        if hasattr(p, 'comment') and p.comment != None:
            self.comment = p.comment

    def remove_null_entries(self):
        if hasattr(self, 'name') and (self.name == None or len(self.name) == 0):
            del self.name
        if hasattr(self, 'type') and (self.type == None or len(self.type) == 0):
            del self.type
        if hasattr(self, 'description') and (self.description == None or len(self.description) == 0):
            del self.description
        if hasattr(self, 'value') and (self.value == None or (isinstance(self.value, str) and len(self.value) == 0)):
            del self.value
        if hasattr(self, 'comment') and (self.comment == None or len(self.comment) == 0):
            del self.comment

    def validate(self):
        param_validator = parameter_validator.ParameterModel(self)
        return param_validator.validate()

    def to_yaml(self):
        # yaml.encoding = None
        errors = self.validate()
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
            type = None
        try:
            description = yaml_data['description']
        except KeyError:
            description = None
        try:
            value = yaml_data['value']
        except KeyError:
            value = None
        try:
            comment = yaml_data['comment']
        except KeyError:
            comment = None

        return cls(name = name, 
                    type = type, 
                    description = description, 
                    value = value, 
                    comment = comment)

    @classmethod
    def from_yaml_list(cls, yaml_data_list):
        pars = []
        for yaml_data in yaml_data_list:
            pars.append(Parameter.from_yaml(yaml_data))

    def set_value(self, val):
        self.value = val

    def get_value(self):
        if hasattr(self, 'value'):
            return self.value
        else:
            return None

    def get_type(self):
        if hasattr(self, 'type') and self.type != None:
            return self.type
        else:
            if hasattr(self, 'value'):
                return type_helper.val_type(self.value)                    
            else:
                return 'unknown'

    def set_type(self, type):
        if type != 'unknown' and type != None:
            self.type = type
        else:
            if hasattr(self, 'type'):
                del self.type

#========================================================================
class Input (Parameter):

    def __init__(self, 
                name: str           = "__init__", 
                type: str           = None, 
                description: str    = None, 
                value: str          = None,
                default: str        = None,
                optional: bool      = False,
                comment: str       = None
                ):
        """Input parameter.

        :param name: Name of the input parameter
        :param type: Type of input parameter
        :param description: Description of the input parameter
        :param value: Input parameter value
        """
        self.default = default
        self.optional = optional
        super().__init__(name, type, description, value, comment)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.name = "__init__"

    def __str__(self):
        txt = "in("
        txt += "name:"      + (self.name        if hasattr(self, 'name')     else 'None') + ", "
        txt += "type:"      + str(self.type     if hasattr(self, 'type')     else 'None') + ", "
        txt += "value:"     + str(self.value    if hasattr(self, 'value')    else 'None') + ", "
        txt += "default:"   + str(self.default  if hasattr(self, 'default')  else 'None') + ", "
        txt += "optional:"  + str(self.optional if hasattr(self, 'optional') else  False) + ", "
        txt += "description:"  + str(self.description if hasattr(self, 'description') else  'None')
        txt += ")"
        return txt

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if other == None:
            return False
        self_name = "" if self.name == None else self.name
        self_type = "" if not hasattr(self, 'type') or self.type == None else self.type
        self_value = "" if not hasattr(self, 'value') or self.value == None else self.value
        self_description = "" if not hasattr(self, 'description') or self.description == None else self.description
        self_default = "" if not hasattr(self, 'default') or self.default == None else self.default
        self_optional = False if not hasattr(self, 'optional') else self.optional

        other_name = "" if other.name == None else other.name
        other_type = "" if not hasattr(other, 'type') or other.type == None else other.type
        other_value = "" if not hasattr(other, 'value') or other.value == None else other.value
        other_description = "" if not hasattr(other, 'description') or other.description == None else other.description
        other_default = "" if not hasattr(other, 'default') or other.default == None else other.default
        other_optional = False if not hasattr(other, 'optional') else other.optional

        return (self_name == other_name) and (self_type == other_type) and (self_value == other_value) \
                and (self_description == other_description) and (self_default == other_default) \
                and (self_optional == other_optional)

    def __hash__(self):
        self_name = "" if self.name == None else self.name
        self_type = "" if not hasattr(self, 'type') or self.type == None else self.type
        self_value = "" if not hasattr(self, 'value') or self.value == None else str(self.value)
        self_description = "" if not hasattr(self, 'description') or self.description == None else self.description
        self_default = "" if not hasattr(self, 'default') or self.default == None else self.default
        self_optional = False if not hasattr(self, 'optional') else self.optional

        return hash((self_name, self_type, self_value, self_description, self_default, self_optional))

    def merge(self, p):
        super().merge(p)
        if hasattr(p, 'default') and p.default != None:
            self.default = p.default
        if hasattr(p, 'optional') and p.optional != None:
            self.optional = p.optional
    
    def remove_null_entries(self):
        super().remove_null_entries()
        if hasattr(self, 'default') and self.default == None:
            del self.default
        if hasattr(self, 'optional') and self.optional == None:
            del self.optional

    def to_yaml(self):
        # yaml.encoding = None
        errors = self.validate()
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
            type = None
        try:
            description = yaml_data['description']
        except KeyError:
            description = None
        try:
            value = yaml_data['value']
        except KeyError:
            value = None
        try:
            default = yaml_data['default']
        except KeyError:
            default = None
        try:
            optional = yaml_data['optional']
        except KeyError:
            optional = None

        return cls(name = name, 
                    type = type, 
                    description = description, 
                    value = value, 
                    default = default, 
                    optional = optional)

    @classmethod
    def from_yaml_list(cls, yaml_data_list):
        pars = []
        for yaml_data in yaml_data_list:
            pars.append(Input.from_yaml(yaml_data))

        return pars

    def validate(self):
        param_validator = parameter_validator.ParameterModel(self, param_type = 'input')
        return param_validator.validate()

    def set_value(self, val):
        super().set_value(val)

#========================================================================
class Output (Parameter):
    def __init__(self,
                name: str           = "__init__", 
                type: str           = None, 
                description: str    = None, 
                value: str          = None,
                comment: str       = None):
        """Output parameter.

        :param name: Name of the output parameter
        :param type: Type of output parameter
        :param description: Description of the output parameter
        :param value: Output parameter value
        """
        super().__init__(name, type, description, value, comment)

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

    def __eq__(self, other):
        if other == None:
            return False
        self_name = "" if self.name == None else self.name
        self_type = "" if not hasattr(self, 'type') or self.type == None else self.type
        self_value = "" if not hasattr(self, 'value') or self.value == None else self.value
        self_description = "" if not hasattr(self, 'description') or self.description == None else self.description

        other_name = "" if other.name == None else other.name
        other_type = "" if not hasattr(other, 'type') or other.type == None else other.type
        other_value = "" if not hasattr(other, 'value') or other.value == None else other.value
        other_description = "" if not hasattr(other, 'description') or other.description == None else other.description

        return (self_name == other_name) and (self_type == other_type) and (self_value == other_value) \
                and (self_description == other_description)

    def __hash__(self):
        self_name = "" if self.name == None else self.name
        self_type = "" if not hasattr(self, 'type') or self.type == None else self.type
        self_value = "" if not hasattr(self, 'value') or self.value == None else str(self.value)
        self_description = "" if not hasattr(self, 'description') or self.description == None else self.description

        return hash((self_name, self_type, self_value, self_description))

    def merge(self, p):
        super().merge(p)

    def remove_null_entries(self):
        super().remove_null_entries()

    def to_yaml(self):
        # yaml.encoding = None
        errors = self.validate()
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
            type = None
        
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

    def validate(self):
        param_validator = parameter_validator.ParameterModel(self, param_type = 'output')
        return param_validator.validate()

    def set_value(self, val):
        super().set_value(val)

#========================================================================
class Setting (Parameter):

    def __init__(self,
                name: str           = "__init__", 
                type: str           = None, 
                description: str    = None, 
                default: str        = None,
                value: str          = None,
                comment: str       = None):
        """Environment settings parameter.

        :param name: Name of the setting parameter
        :param type: Type of setting parameter
        :param description: Description of the setting parameter
        :param value: Environment setting parameter value
        """
        self.default = default
        super().__init__(name, type, description, value, comment)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.name = "__init__"

    def __str__(self):
        txt = "env("
        txt += "name:" + (self.name if hasattr(self, 'name') else 'None') + ", "
        txt += "type:" + str(self.type if hasattr(self, 'type') else 'None') + ", "
        txt += "value:" + str(self.value if hasattr(self, 'value') else 'None') + ", "
        txt += "default:"   + str(self.default  if hasattr(self, 'default')  else 'None') + ", "
        txt += "description:"  + str(self.description if hasattr(self, 'description') else  'None')
        txt += ")"
        return txt

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if other == None:
            return False
        self_name = "" if self.name == None else self.name
        self_type = "" if not hasattr(self, 'type') or self.type == None else self.type
        self_value = "" if not hasattr(self, 'value') or self.value == None else self.value
        self_description = "" if not hasattr(self, 'description') or self.description == None else self.description
        self_default = "" if not hasattr(self, 'default') or self.default == None else self.default

        other_name = "" if other.name == None else other.name
        other_type = "" if not hasattr(other, 'type') or other.type == None else other.type
        other_value = "" if not hasattr(other, 'value') or other.value == None else other.value
        other_description = "" if not hasattr(other, 'description') or other.description == None else other.description
        other_default = "" if not hasattr(other, 'default') or other.default == None else other.default

        return (self_name == other_name) and (self_type == other_type) and (self_value == other_value) \
                and (self_description == other_description)  and (self_default == other_default) 

    def __hash__(self):
        self_name = "" if self.name == None else self.name
        self_type = "" if not hasattr(self, 'type') or self.type == None else self.type
        self_value = "" if not hasattr(self, 'value') or self.value == None else str(self.value)
        self_description = "" if not hasattr(self, 'description') or self.description == None else self.description
        self_default = "" if not hasattr(self, 'default') or self.default == None else self.default

        return hash((self_name, self_type, self_value, self_default, self_description))

    def merge(self, p):
        super().merge(p)
        if hasattr(p, 'default') and p.default != None:
            self.default = p.default

    def remove_null_entries(self):
        super().remove_null_entries()
        if hasattr(self, 'default') and self.default == None:
            del self.default

    def to_yaml(self):
        # yaml.encoding = None
        errors = self.validate()
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
            type = None
        
        try:
            description = yaml_data['description']
        except KeyError:
            description = None
        try:
            value = yaml_data['value']
        except KeyError:
            value = None
        try:
            default = yaml_data['default']
        except KeyError:
            default = None
        
        return cls(name = name, 
                    type = type, 
                    description = description, 
                    value = value, 
                    default = default)


    @classmethod
    def from_yaml_list(cls, yaml_data_list):
        pars = []
        for yaml_data in yaml_data_list:
            pars.append(Setting.from_yaml(yaml_data))

        return pars

    def validate(self):
        param_validator = parameter_validator.ParameterModel(self, param_type = 'setting')
        return param_validator.validate()

    def set_value(self, val):
        super().set_value(val)

#========================================================================
