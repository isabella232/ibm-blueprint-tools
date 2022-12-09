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
import diagrams

from blueprint.schema import blueprint
from blueprint.lib import bfile
from blueprint.sync import bpsync
from blueprint.merge import manifest

from blueprint.circuit import bus
from blueprint.circuit import diagram as diag

from blueprint.lib.logger import logr
# import logging
# logr = logging.getLogger(__name__)

def eprint(*args, **kwargs):
    logr.error(*args)
    print(*args, file=sys.stderr, **kwargs)

class BlueprintDraw:

    def __init__(self, blueprint_file: str = None):
        self.bp_file    = blueprint_file
        self.bp         = None # blueprint.Blueprint instance
        self.circuit    = None # circuit.Circuit instance


    def prepare(self,  working_dir = "."):
        if self.bp_file != None:
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

        self.circuit = bus.Circuit(self.bp)
        self.circuit.read()

    def draw(self, out_file = "testbp", outformat = "png"):
        logr.info("Draw the blueprint yaml")
        graph_attr = {
            "splines": "spline",
        }

        d = diagrams.Diagram(name = "Blueprint", filename = out_file, direction="TB", outformat = outformat, graph_attr=graph_attr)
        diagrams.setdiagram(d)

        bpd = diag.BlueprintPane(name = self.bp.name,
                                    description = self.bp.description  if hasattr(self.bp, 'description') else None,
                                    inputs      = self.bp.get_input_var_names(),
                                    outputs     = self.bp.get_output_var_names(),
                                    settings    = self.bp.get_setting_var_names()
                                    )
        diagrams.setcluster(bpd)

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
                    start_pane = bpd.bp_node
                else: # isinstance(start, module.Module)
                    start_pane = mod_diag[start.name]
                
                if isinstance(end, blueprint.Blueprint):
                    end_pane = bpd.bp_node
                else: # isinstance(end, module.Module)
                    end_pane = mod_diag[end.name]
                
                start_pane >> diag.Relation(wire.from_param, wire.to_param) >> end_pane

        if bpd._parent:
            bpd._parent.subgraph(bpd.dot)
        else:
            bpd._diagram.subgraph(bpd.dot)
        diagrams.setcluster(bpd._parent)

        d.render()
        os.remove(out_file)
        diagrams.setdiagram(None)
