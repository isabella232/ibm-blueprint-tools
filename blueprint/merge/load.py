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

import os
import yaml
from yaml.loader import SafeLoader
from os.path import exists as file_exists
import re

from blueprint.lib.event import ValidationEvent
from blueprint.lib.event import BPError
from blueprint.lib.event import BPWarning

class BPLoader:
    def __init__(self, filename):
        if file_exists(filename):
            self.filename = filename
        else:
            raise ValueError('Blueprint manifest file does not exist')
        
        self.cwd = os.path.dirname(filename)
        self.bpyaml = {}
        self.bperrors = []

        with open(self.filename) as f:
            self.bp_manifest = yaml.load(f, Loader=SafeLoader)

        result = self.validate_manifest()
        if result == False:
            raise ValueError('Error in Blueprint manifest headers: ' + str(self.get_errors()))
        self.load_inputs()
        self.load_outputs()
        self.load_modules()

    def get_errors(self):
        errors = []
        for e in self.bperrors:
            if e.level == BPError:
                if len(errors) == 0:
                    errors = [e]
                else:
                    errors = errors + e
        return errors

    def get_warnings(self):
        warnings = []
        for w in self.bperrors:
            if w.level == BPWarning:
                warnings = warnings + w
        return warnings

    def to_yaml(self):
        return self.bpyaml

    def to_yaml_str(self, stream = None):
        return yaml.dump(self.bpyaml, sort_keys=False)

    def hasattr(self, yaml, attr):
        try:
            x = yaml[attr]
            return True
        except KeyError:
            return False

    def merge(self, arr1, arr2):
        result = []
        names = []
        for entry in arr1:
            if(entry['name'] in names):
                self.bperrors.append(ValidationEvent(BPWarning, 'Duplicate parameter name: ' + entry['name']))
            names.append(entry['name'])
            result.append(entry)
        
        if isinstance(arr2, dict):
            entry={}
            for key, value in arr2.items():
                if key == "name":
                    if(value in names):
                        self.bperrors.append(ValidationEvent(BPWarning, 'Duplicate parameter name: ' + value))
                    names.append(value)
                entry[key]= value
            result.append(entry)
        else:
            for entry in arr2:
                if(entry['name'] in names):
                    self.bperrors.append(ValidationEvent(BPWarning, 'Duplicate parameter name: ' + entry['name']))
                names.append(entry['name'])
                result.append(entry)
    
        return result

    def load_inputs(self):

        if self.bp_manifest == None:
            self.bperrors.append(ValidationEvent(BPError, 'Load the blueprint manifest file, before loading the inputs block'))

        if self.bp_manifest['inputs'] == None:
            self.bperrors.append(ValidationEvent(BPWarning, 'No inputs in the blueprint manifest file'))

        for input in self.bp_manifest['inputs']:
            if isinstance(input, str):
                m = re.search('\$\{\{(.*?)\}\}', input)
                if m:
                    input_filename = m.group(1)
                    rel_input_filename = os.path.basename(input_filename)
                    rel_input_filename = os.path.join(self.cwd, rel_input_filename)
                    with open(rel_input_filename) as f:
                        input_yaml = yaml.load(f, Loader=SafeLoader)
                        if self.hasattr(input_yaml, 'inputs') and input_yaml['inputs'] == None:
                            self.bperrors.append(ValidationEvent(BPWarning, 'Invalid inputs yaml stucture, skipping ' + input_filename))
                        else:
                            if not self.hasattr(self.bpyaml, 'inputs') or self.bpyaml['inputs'] == None:
                                self.bpyaml['inputs'] = input_yaml['inputs']
                            else:
                                self.bpyaml['inputs'] = self.merge(self.bpyaml['inputs'], input_yaml['inputs'])
                else :
                    self.bperrors.append(ValidationEvent(BPError, 'Error parsing the input string: ' + str(input)))
            elif isinstance(input, dict):
                if self.hasattr(input, 'name'):
                    if not self.hasattr(self.bpyaml, 'inputs') or self.bpyaml['inputs'] == None:
                        self.bpyaml['inputs'] = [input]
                    else:
                        self.bpyaml['inputs'] = self.merge(self.bpyaml['inputs'], input)
                else:
                    self.bperrors.append(ValidationEvent(BPError, 'Invalid input definition'))
            else :
                self.bperrors.append(ValidationEvent(BPError, 'Unknown input section: ' + str(input)))

        return

    def load_outputs(self):

        if self.bp_manifest == None:
            self.bperrors.append(ValidationEvent(BPError, 'Load the blueprint manifest file, before loading the output block'))
            return

        if not self.hasattr(self.bp_manifest, 'outputs') or self.bp_manifest['outputs'] == None:
            self.bperrors.append(ValidationEvent(BPWarning, 'No outputs in the blueprint manifest file'))
            return

        for output in self.bp_manifest['outputs']:
            if isinstance(output, str):
                m = re.search('\$\{\{(.*?)\}\}', output)
                if m:
                    output_filename = m.group(1)
                    rel_output_filename = os.path.basename(output_filename)
                    rel_output_filename = os.path.join(self.cwd, rel_output_filename)
                    with open(rel_output_filename) as f:
                        output_yaml = yaml.load(f, Loader=SafeLoader)
                        if self.hasattr(output_yaml, 'outputs') and output_yaml['outputs'] == None:
                            self.bperrors.append(ValidationEvent(BPWarning, 'Invalid outputs yaml stucture, skipping ' + output_filename))
                        else:
                            if not self.hasattr(self.bpyaml, 'outputs') or self.bpyaml['outputs'] == None:
                                self.bpyaml['outputs'] = output_yaml['outputs']
                            else:
                                self.bpyaml['outputs'] = self.merge(self.bpyaml['outputs'], output_yaml['outputs'])
                else :
                    self.bperrors.append(ValidationEvent(BPError, 'Error parsing the output string: ' + str(output)))
            elif isinstance(output, dict):
                if self.hasattr(output, 'name'):
                    if not self.hasattr(self.bpyaml, 'outputs') or self.bpyaml['outputs'] == None:
                        self.bpyaml['outputs'] = [output]
                    else:
                        self.bpyaml['outputs'] = self.merge(self.bpyaml['outputs'], output)
                else:
                    self.bperrors.append(ValidationEvent(BPError, 'Invalid output definition'))
            else :
                self.bperrors.append(ValidationEvent(BPError, 'Unknown output section: ' + str(output)))
        
        return

    def load_modules(self):

        if self.bp_manifest == None:
            self.bperrors.append(ValidationEvent(BPError, 'Load the blueprint manifest file, before loading the output block'))
            return

        if not self.hasattr(self.bp_manifest, 'modules') or self.bp_manifest['modules'] == None:
            self.bperrors.append(ValidationEvent(BPWarning, 'No modules in the blueprint manifest file'))
            return

        for mod in self.bp_manifest['modules']:
            if isinstance(mod, str):
                m = re.search('\$\{\{(.*?)\}\}', mod)
                if m:
                    mod_filename = m.group(1)
                    rel_mod_filename = os.path.basename(mod_filename)
                    rel_mod_filename = os.path.join(self.cwd, rel_mod_filename)
                    with open(rel_mod_filename) as f:
                        mod_yaml = yaml.load(f, Loader=SafeLoader)
                        if self.hasattr(mod_yaml, 'modules') and mod_yaml['modules'] == None:
                            self.bperrors.append(ValidationEvent(BPWarning, 'Invalid modules yaml stucture, skipping ' + mod_filename))
                        else:
                            if not self.hasattr(self.bpyaml, 'modules') or self.bpyaml['modules'] == None:
                                self.bpyaml['modules'] = mod_yaml['modules']
                            else:
                                self.bpyaml['modules'] = self.merge(self.bpyaml['modules'], mod_yaml['modules'])
                else :
                    self.bperrors.append(ValidationEvent(BPError, 'Error parsing the module string: ' + str(mod)))
            elif isinstance(mod, dict):
                if self.hasattr(mod, 'name'):
                    if not self.hasattr(self.bpyaml, 'modules') or self.bpyaml['modules'] == None:
                        self.bpyaml['modules'] = [mod]
                    else:
                        self.bpyaml['modules'] = self.merge(self.bpyaml['modules'], mod)
                else:
                    self.bperrors.append(ValidationEvent(BPError, 'Invalid module definition'))
            else :
                self.bperrors.append(ValidationEvent(BPError, 'Unknown module section: ' + str(mod)))

        return

    def validate_manifest(self):
        result = True
        if self.bp_manifest == None:
            self.bperrors.append(ValidationEvent(BPError, 'Load the blueprint manifest file, before validating'))
            result = False
        else:
            if self.hasattr(self.bp_manifest, 'name'):
                self.bpyaml['name'] = self.bp_manifest['name']
            else:
                self.bperrors.append(ValidationEvent(BPError, 'Blueprint manifest file must have a name'))
                result = False

            if self.hasattr(self.bp_manifest, 'schema_version'):
                self.bpyaml['schema_version'] = self.bp_manifest['schema_version']
            else:
                self.bperrors.append(ValidationEvent(BPError, 'Blueprint manifest file must have a schema_version'))
                result = False

            if self.hasattr(self.bp_manifest, 'type'):
                self.bpyaml['type'] = self.bp_manifest['type']
            else:
                self.bperrors.append(ValidationEvent(BPError, 'Blueprint manifest file must have a type'))
                result = False

            if self.hasattr(self.bp_manifest, 'description'):
                self.bpyaml['description'] = self.bp_manifest['description']
        
        return result

