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
import sys
import yaml
from blueprint.run import modrunner

from blueprint.schema import blueprint
from blueprint.lib import event
from blueprint.lib import bfile

import shutil

from blueprint.lib.logger import logr
# import logging
# logr = logging.getLogger(__name__)

def eprint(*args, **kwargs):
    logr.error(*args)
    print(*args, file=sys.stderr, **kwargs)

class BlueprintRunner:

    def __init__(self, blueprint_file, input_data_file, dry_run = False, ignore_validation_errors = False, working_dir = '.'):
        self.bp =  blueprint.Blueprint("Temp")
        self.blueprint_file = blueprint_file
        self.input_data_file = input_data_file
        self.working_dir = working_dir
        self.dry_run = dry_run
        self.ignore_validation_errors = ignore_validation_errors

        self.module_runners = dict()
        self.input_data = dict()
        self.module_data = dict()

        file_exists = os.path.exists(blueprint_file)
        if not file_exists:
            raise ValueError("Invalid blueprint file (with path)")

        file_exists = os.path.exists(input_data_file)
        if not file_exists:
            raise ValueError("Invalid input file (with path)")

        if not os.path.exists(working_dir):
            os.makedirs(working_dir)
        # else:
        #     shutil.rmtree(working_dir)
        #     os.makedirs(working_dir)
        # copy the blueprint.yaml & input file to the working_dir
        blueprint_file_name = blueprint_file[len(os.path.dirname(blueprint_file))+1:]
        input_data_file_name = input_data_file[len(os.path.dirname(input_data_file))+1:]

        shutil.copyfile(blueprint_file, os.path.join(working_dir, blueprint_file_name))
        self.blueprint_file = os.path.join(working_dir, blueprint_file_name)

        shutil.copyfile(input_data_file, os.path.join(working_dir, input_data_file_name))
        self.input_data_file = os.path.join(working_dir, input_data_file_name)

        # change current-working-directory to the working_dir
        os.chdir(working_dir)

        logr.debug("Loading blueprint in BlueprintRunner")
        e = self.load_blueprint()
        if len(e) > 0:
            logr.error("Errors found while loading blueprint: " + str(e))

        logr.debug("Loading input data for the blueprint in BlueprintRunner")
        e = self.load_input_data()
        if len(e) > 0:
            logr.error("Errors found while loading input data for the blueprint: " + str(e))
        
        logr.debug("Loading ModuleRunners for the blueprint")
        e = self.load_module_runners(dry_run, ignore_validation_errors)
        if len(e) > 0:
            logr.error("Errors found while loading ModuleRunner: " + str(e))


    def load_blueprint(self):
        
        logr.debug("Loading blueprint file " + self.blueprint_file + " ...")
        with open(self.blueprint_file) as f:
            yaml_str = f.read()
            self.bp = blueprint.Blueprint.from_yaml_str(yaml_str)
        logr.info("Success loading blueprint file " + self.blueprint_file + ". \nValidating ...")
        errors = self.bp.validate(event.BPWarning)
        
        return errors

    def load_input_data(self):
        
        logr.debug("Loading input data file " + self.input_data_file + " ...")
        errors = []
        self.input_data = bfile.FileHelper.load(self.input_data_file)
        logr.info("Success loading input data file " + self.input_data_file)
        logr.debug("Validating ...")
        for name in self.input_data:
            self.bp.set_input_value(name, self.input_data[name])
            (bp_vars, err) = self.bp.input_ref(name)
            if err == None:
                self.module_data[bp_vars] = self.input_data[name]
            else:
                (bp_vars, err) = self.bp.setting_ref(name)
                if err == None:
                    self.module_data[bp_vars] = self.input_data[name]
                else:
                    self.module_data[name] = self.input_data[name]
        logr.debug("Propagating the blueprint input data ...")
        self.bp.propagate_blueprint_input_data()
        return errors

    def load_module_runners(self, dry_run=False, ignore_validation_errors=False):
        errors = []
        for mod in self.bp.modules:
            logr.debug("Loading module-runner for module : " + mod.name)
            self.module_runners[mod.name] = modrunner.ModuleRunner(self, mod, dry_run, ignore_validation_errors)
            errors.append(self.module_runners[mod.name].get_errors())
        logr.debug("Successful load all module-runners")
        
        if len(errors) > 0:
            logr.debug("Errors found while loading module runnner.  Count = " + str(len(errors)))

        return errors

    def init_modules(self):
        errors = []
        # print(self.bp.modules)
        bp_graph = self.bp.build_dag()
        while not self.bp.is_dag_empty(bp_graph):
            mod_name = self.bp.dag_next_node(bp_graph)
            if mod_name == None:
                break

            mr = self.module_runners[mod_name]
            e = mr.init_module()
            self.bp.propagate_module_data(self.module_data)

            bp_graph.popNode(mod_name)
            errors.append(e)

        if len(errors) > 0:
            logr.debug("Errors found during init modules.  Count = " + str(len(errors)))

        return errors

    def plan_modules(self):
        errors = []
        # print(self.bp.modules)
        bp_graph = self.bp.build_dag()
        while not self.bp.is_dag_empty(bp_graph):
            mod_name = self.bp.dag_next_node(bp_graph)
            if mod_name == None:
                break

            mr = self.module_runners[mod_name]
            e = mr.plan_module()
            self.bp.propagate_module_data(self.module_data)

            bp_graph.popNode(mod_name)
            errors.append(e)
        
        if len(errors) > 0:
            logr.debug("Errors found during plan modules.  Count = " + str(len(errors)))
        
        return errors

    def apply_modules(self):
        errors = []
        # print(self.bp.modules)
        bp_graph = self.bp.build_dag()
        while not self.bp.is_dag_empty(bp_graph):
            mod_name = self.bp.dag_next_node(bp_graph)
            if mod_name == None:
                break

            mr = self.module_runners[mod_name]
            e = mr.apply_module()
            self.bp.propagate_module_data(self.module_data)

            bp_graph.popNode(mod_name)
            errors.append(e)
        
        if len(errors) > 0:
            logr.debug("Errors found during apply modules.  Count = " + str(len(errors)))

        return errors

    def destroy_modules(self):
        errors = []
        # print(self.bp.modules)
        bp_graph = self.bp.build_dag()
        while not self.bp.is_dag_empty(bp_graph):
            mod_name = self.bp.dag_next_node(bp_graph)
            if mod_name == None:
                break

            mr = self.module_runners[mod_name]
            e = mr.destroy_module()
            self.bp.propagate_module_data(self.module_data)

            bp_graph.popNode(mod_name)
            errors.append(e)
        
        if len(errors) > 0:
            logr.debug("Errors found during destroy modules.  Count = " + str(len(errors)))

        return errors

    def save_module_output_data(self, output_data):
        # output_data -> dict
        # self.module_data -> dict
        if output_data != None:
            self.module_data.update(output_data)

    def save_module_input_data(self, input_data):
        # input_data -> dict
        # self.module_data -> dict
        if input_data != None:
            self.module_data.update(input_data)