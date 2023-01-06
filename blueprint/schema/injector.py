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
from typing import List, Union

from blueprint.schema import param
from blueprint.schema import source as src

from blueprint.lib.logger import logr
# import logging
# logr = logging.getLogger(__name__)

def eprint(*args, **kwargs):
    logr.error(*args)
    print(*args, file=sys.stderr, **kwargs)

#========================================================================
TerraformType = "terraform"

class Injector(dict):
    def __init__(self, 
            tft_git_url: str                        = "https://github.com/Cloud-Schematics/tf-templates",
            tft_name: str                           = "ibm",
            injection_type:str                      = 'override',
            tft_parameters: List[param.Parameter]   = None):

            self.tft_git_url    = tft_git_url
            self.tft_name       = tft_name
            self.injection_type = injection_type
            self.tft_parameters = tft_parameters

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.tft_git_url = "https://github.com/Cloud-Schematics/tf-templates"

    def __str__(self):
        txt = "Injector("
        txt += "tft_git_url:"    + (self.tft_git_url        if hasattr(self, 'tft_git_url') else 'None')    + ", "
        txt += "tft_name:"       + (self.tft_name           if hasattr(self, 'tft_name') else 'None')       + ", "
        txt += "injection_type:" + (self.injection_type     if hasattr(self, 'injection_type') else 'None') + ", "
        txt += "tft_parameters:" + str(self.tft_parameters  if hasattr(self, 'tft_parameters') else 'None')
        txt += ")"
        return txt

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if other == None:
            return False

        self_tft_git_url    = "" if self.tft_git_url == None else self.tft_git_url
        self_tft_name       = "" if not hasattr(self, 'tft_name') or self.tft_name == None else self.tft_name
        self_injection_type = "" if not hasattr(self, 'injection_type') or self.injection_type == None else str(self.injection_type)
        self_tft_parameters = "" if not hasattr(self, 'tft_parameters') or self.tft_parameters == None else str(self.tft_parameters)

        other_tft_git_url    = "" if other.tft_git_url == None else other.tft_git_url
        other_tft_name       = "" if not hasattr(other, 'tft_name') or other.tft_name == None else other.tft_name
        other_injection_type = "" if not hasattr(other, 'injection_type') or other.injection_type == None else other.injection_type
        other_tft_parameters = "" if not hasattr(other, 'tft_parameters') or other.tft_parameters == None else str(other.tft_parameters)

        return (self_tft_git_url == other_tft_git_url) and (self_tft_name == other_tft_name) \
            and (self_injection_type == other_injection_type) and (self_tft_parameters == other_tft_parameters)

    def __hash__(self):
        self_tft_git_url    = "" if self.tft_git_url == None else self.tft_git_url
        self_tft_name       = "" if not hasattr(self, 'tft_name') or self.tft_name == None else self.tft_name
        self_injection_type = "" if not hasattr(self, 'injection_type') or self.injection_type == None else str(self.injection_type)
        self_tft_parameters = "" if not hasattr(self, 'tft_parameters') or self.tft_parameters == None else str(self.tft_parameters)

        return hash((self_tft_git_url, self_tft_name, self_injection_type, self_tft_parameters))

    def remove_null_entries(self):
        if hasattr(self, 'tft_git_url') and self.tft_git_url == None:
            del self.tft_git_url
        if hasattr(self, 'tft_name') and self.tft_name == None:
            del self.tft_name
        if hasattr(self, 'injection_type') and self.injection_type == None:
            del self.injection_type
        if hasattr(self, 'tft_parameters'):
            if self.tft_parameters == None:
                del self.tft_parameters
            else:
                for t in self.tft_parameters:
                    t.remove_null_entries()


    def validate(self):
        # TODO: Add a validator for the injectors
        return None

    def to_yaml(self):
        # yaml.encoding = None
        errors = self.validate()
        # eprint(errors)
        return (yaml.dump(self, sort_keys=False), errors)

    @classmethod
    def from_yaml(cls, yaml_data):
        
        if isinstance(yaml_data, Injector):
            return yaml_data

        tft_git_url = yaml_data['tft_git_url']
        try:
            tft_name = yaml_data['tft_name']
        except KeyError:
            tft_name = None
        try:
            injection_type = yaml_data['injection_type']
        except KeyError:
            injection_type = None
        try:
            tft_parameters = []
            for p in yaml_data['tft_parameters']:
                tft_parameters.append(param.Parameter.from_yaml(p))
        except (KeyError, UnboundLocalError, TypeError):
            tft_parameters = None

        return cls(tft_git_url, tft_name, injection_type, tft_parameters)


    @classmethod
    def from_yaml_list(cls, yaml_data_list):
        injectors = []

        for yaml_data in yaml_data_list:
            injectors.append(Injector.from_yaml(yaml_data))

        return injectors

