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

import sys
import yaml
from blueprint.schema import blueprint
from blueprint.merge import manifest
from blueprint.sync import bpsync

from blueprint.lib.logger import logr
# import logging
# logr = logging.getLogger(__name__)

BPFile          = "blueprint"
BPManifest      = "manifest"
BPLite          = "lite"
OtherDataFile   = "Other"

def eprint(*args, **kwargs):
    logr.error(*args)
    print(*args, file=sys.stderr, **kwargs)

class FileHelper:

    @classmethod
    def discover(cls, filename):
        """
        Discover the type of input file.  
        It returns BPFile, BPManifest, BPLite or OtherDataFile
        """
        with open(filename) as f:
            yaml_str = f.read()
            yaml_data = yaml.load(yaml_str, yaml.SafeLoader)

            if yaml_str.find('git_sources') != -1:
                filetype = BPLite
            elif (yaml_str.find('${{') != -1) and (yaml_str.find('}}') != -1):
                filetype = BPManifest
            else:
                try:
                    type = yaml_data['type'] 
                    if type == "blueprint":
                        filetype = BPFile
                    else:
                        filetype = OtherDataFile
                except:
                    filetype = OtherDataFile
        
        return filetype

    @classmethod
    def load(cls, filename): 
        """
        Load an yaml file, and returns the yaml data.
        """
        with open(filename) as f:
            yaml_str = f.read()
            try:
                yaml_data = yaml.load(yaml_str, yaml.SafeLoader)
                return yaml_data

            except yaml.YAMLError as exception:
                
                print ("Error parsing YAML file:")
                if hasattr(exception, 'problem_mark'):
                    if exception.context != None:
                        print ('  parser says\n' + str(exception.problem_mark) + '\n  ' +
                            str(exception.problem) + ' ' + str(exception.context) +
                            '\nPlease correct data and retry.')
                    else:
                        print ('  parser says\n' + str(exception.problem_mark) + '\n  ' +
                            str(exception.problem) + '\nPlease correct data and retry.')
                else:
                    print ("Error while parsing yaml file")
                return None

    @classmethod
    def load_blueprint(cls, filename): 
        """
        Load a blueprint yaml file, and returns the Blueprint instance
        """
        if FileHelper.discover(filename) == BPFile:

            yaml_data = FileHelper.load(filename)
            bp = blueprint.Blueprint.from_yaml_data(yaml_data)
            return bp
        
        return None

    @classmethod
    def load_manifest(cls, filename): 
        """
        Load a blueprint manifest file, and returns the Manifest instance
        """
        if FileHelper.discover(filename) == BPManifest:
            input_manifest_file = filename
            bp_manifest = manifest.BlueprintManifest.from_yaml_file(input_manifest_file)
            return bp_manifest
        
        return None

    @classmethod
    def load_blueprint_lite(cls, filename): 
        """
        Load a blueprint lite file, and returns the Blueprint Lite instance
        """
        if FileHelper.discover(filename) == BPLite:
            input_bplite_file = filename
            bp_lite = bpsync.BlueprintMorphius.from_yaml_file(input_bplite_file)
            return bp_lite
        
        return None

