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
import diagrams

from typing import List

from blueprint.schema import blueprint
from blueprint.schema import module

from blueprint.lib import bfile
from blueprint.lib import event
from blueprint.sync import bpsync
from blueprint.merge import manifest

from blueprint.circuit import bus
from blueprint.circuit import bpdiagram as diag

from blueprint.validate import blueprint_validator

from blueprint.lib.logger import logr
# import logging
# logr = logging.getLogger(__name__)

def eprint(*args, **kwargs):
    logr.error(*args)
    print(*args, file=sys.stderr, **kwargs)

class BlueprintDraw:

    def __init__(self, blueprint_file: str = None, blueprint_object: blueprint.Blueprint = None):
        """
        BlueprintDraw - a canvas to draw the Blueprint configuration

        :param blueprint_file: Name of the Blueprint file ()
        :param blueprint_object: Blueprint object

        Initialized using one-of blueprint_file or blueprint_object; these parameters are mutually exclusive
        """ 
        if blueprint_file is not None and blueprint_object is not None:
            raise ValueError("Must be initialized using one-of blueprint_file or blueprint_object, but not both")

        self.bp_file    = blueprint_file
        self.bp         = blueprint_object # blueprint.Blueprint instance
        self.circuit    = None # circuit.Circuit instance
        self.validation = None


    def prepare(self,  working_dir = ".") -> List[event.ValidationEvent]:
        """
        Prepare the BlueprintDraw canvas using the blueprint file as input, and build the circuit.

        :param working_dir: Working directory used while processing the blueprint files and other intermediate / temporary files.
        """
        err = None
        if self.bp_file != None:
            logr.info("Prepare the blueprint object using the blueprint yaml file")
            filetype = bfile.FileHelper.discover(self.bp_file)
            if filetype == bfile.BPFile:
                print("file type: blueprint")
                self.bp = bfile.FileHelper.load_blueprint(self.bp_file)
            elif filetype == bfile.BPLite:
                print("file type: blueprint lite")
                bp_lite_data = bfile.FileHelper.load_blueprint_lite(self.bp_file)
                bm = bpsync.BlueprintMorphius.from_yaml_data(bp_lite_data)
                self.bp = bm.sync_blueprint(working_dir = working_dir, annotate = True)
            elif filetype == bfile.BPManifest:
                print("file type: blueprint manifest")
                bp_manifest_data = bfile.FileHelper.load_manifest(self.bp_file)
                bp_manifest = manifest.BlueprintManifest.from_yaml_data(bp_manifest_data)
                (self.bp, errors) = bp_manifest.generate_blueprint()
            else:
                eprint("Invalid blueprint file type")
        elif (self.bp != None):
            logr.info("The blueprint object is already primed")
        else:
            logr.error("The blueprint file & blueprint object is not initialized")
            err = event.ValidationEvent(event.BPError, "BlueprintDraw: blueprint file & blueprint object is not initialized", self)
            return [err]

        bpv = blueprint_validator.BlueprintModel(self.bp)
        self.validation = bpv.validate()

        self.circuit = bus.Circuit(self.bp)
        self.circuit.read()

        return self.validation

    def draw(self, annotate = ["validation"], out_file = "testbp", out_format = "png") -> List[event.ValidationEvent]:
        """
        Draw the Blueprint Configuation using GraphViz libraries

        :param out_file: Name of the output blueprint image file (with full path)
        :param out_format: Format of the output blueprint image file (png or jpg)
        """

        if self.bp == None:
            logr.error("The blueprint object is not initialized & prepared")
            err = event.ValidationEvent(event.BPError, "BlueprintDraw: blueprint object is not initialized & prepared", self)
            return [err]

        if self.circuit == None:
            logr.error("The blueprint circuit is prepared; call prepare() before draw()")
            err = event.ValidationEvent(event.BPError, "BlueprintDraw: blueprint circuit is prepared; call prepare() before draw()", self)
            return [err]

        logr.info("Draw the blueprint yaml")
        graph_attr = {
            "splines": "spline",
        }

        d = diagrams.Diagram(name = "Blueprint", filename = out_file, direction="TB", outformat = out_format, graph_attr=graph_attr)
        diagrams.setdiagram(d)

        bpd = diag.BlueprintPane(name = self.bp.name,
                                    description = self.bp.description  if hasattr(self.bp, 'description') else None,
                                    inputs      = self.bp.get_input_var_names(),
                                    outputs     = self.bp.get_output_var_names(),
                                    settings    = self.bp.get_setting_var_names()
                                    )
        diagrams.setcluster(bpd)

        # if annotate.contains('validation'):
        #     if len(self.validation) > 0:

        mods = self.bp.get_modules()
        if mods != None:
            mod_diag = dict()
            for mod in mods:
                mod_diag[mod.name] = diag.ModulePane(
                                            name        = mod.name,
                                            description = mod.description if hasattr(mod, 'description') else None,
                                            inputs      = mod.get_input_var_names(),
                                            outputs     = mod.get_output_var_names(),
                                            settings    = mod.get_setting_var_names()
                                        )

        for bus in self.circuit.fleet:
            start = bus.from_node
            end = bus.to_node
            for wire in bus.wires:
                if isinstance(start, blueprint.Blueprint):
                    start_pane = bpd.in_bp_node
                else: # isinstance(start, module.Module)
                    start_pane = mod_diag[start.name]
                
                if isinstance(end, blueprint.Blueprint):
                    end_pane = bpd.out_bp_node
                else: # isinstance(end, module.Module)
                    end_pane = mod_diag[end.name]

                if isinstance(bus.from_node, module.Module) and isinstance(bus.to_node, module.Module):
                    edge_attributes = {"style": "dashed", "color": " black"}
                if isinstance(bus.from_node, blueprint.Blueprint):
                    edge_attributes = {"style": "dashed", "color": "blue"}
                if isinstance(bus.to_node, blueprint.Blueprint):
                    edge_attributes = {"style": "dashed", "color": "red"}

                start_pane >> diag.Relation(from_param = wire.from_param, to_param = wire.to_param, edge_attributes = edge_attributes) >> end_pane

        if bpd._parent:
            bpd._parent.subgraph(bpd.dot)
        else:
            bpd._diagram.subgraph(bpd.dot)
        diagrams.setcluster(bpd._parent)

        d.render()
        os.remove(out_file)
        diagrams.setdiagram(None)

        return None
