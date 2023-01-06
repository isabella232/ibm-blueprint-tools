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

from typing import List

import schemdraw
import schemdraw.elements as elm
import networkx as nx

from blueprint.schema import blueprint
from blueprint.schema import module
from blueprint.lib import bfile
from blueprint.lib import event
from blueprint.sync import bpsync
from blueprint.merge import manifest

from blueprint.circuit import bus as wirebus
from blueprint.circuit import schem_diagram as diag

from blueprint.lib.logger import logr
# import logging
# logr = logging.getLogger(__name__)

def eprint(*args, **kwargs):
    logr.error(*args)
    print(*args, file=sys.stderr, **kwargs)

def transform(node_pos, width, height):
    keys = node_pos.keys()
    # rotate
    # for ic in keys:
    #     (x, y) = node_pos[ic]
    #     node_pos[ic] = (y, x)
    
    # boundary
    maxx = -sys.maxsize - 1
    minx = sys.maxsize
    maxy = -sys.maxsize - 1
    miny = sys.maxsize
    for ic in keys:
        (x, y) = node_pos[ic]
        if x > maxx:
            maxx = x
        if x < minx:
            minx = x
        if y > maxy:
            maxy = y
        if y < miny:
            miny = y 
    
    # scale & move
    xrange = maxx - minx
    yrange = maxy - miny
    width = width - 6
    height = height - 6
    for ic in keys:
        (x, y) = node_pos[ic]
        node_pos[ic] = (x-minx, y-miny)

        (x, y) = node_pos[ic]
        node_pos[ic] = (x * width / xrange, y * height / yrange)

        (x, y) = node_pos[ic]
        node_pos[ic] = (x+2, y+2)
    
    return node_pos

def bound(node_pos):
    keys = node_pos.keys()
    
    # boundary
    maxx = -sys.maxsize - 1
    minx = sys.maxsize
    maxy = -sys.maxsize - 1
    miny = sys.maxsize
    for ic in keys:
        (x, y) = node_pos[ic]
        if x > maxx:
            maxx = x
        if x < minx:
            minx = x
        if y > maxy:
            maxy = y
        if y < miny:
            miny = y 
    
    return (maxx + 4, maxy + 4)

class BlueprintBoard:

    def __init__(self, blueprint_file: str = None, blueprint_object: blueprint.Blueprint = None):
        """
        BlueprintBoard - a breadboard to draw the Blueprint circuit

        :param blueprint_file: Name of the Blueprint file ()
        :param blueprint_object: Blueprint object

        Initialized using one-of blueprint_file or blueprint_object; these parameters are mutually exclusive
        """ 
        self.bp_file    = blueprint_file
        self.bp         = blueprint_object # blueprint.Blueprint instance
        self.circuit    = None # circuit.Circuit instance


    def prepare(self, width=24, height=10, working_dir = ".")  -> List[event.ValidationEvent]:
        """
        Prepare the Blueprint breadboard using the blueprint file as input, and build the circuit.

        :param working_dir: Working directory used while processing the blueprint files and other intermediate / temporary files.
        """
        err = None
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
        elif (self.bp != None):
            logr.info("The blueprint object is already primed")
        else:
            logr.error("The blueprint file & blueprint object is not initialized")
            err = event.ValidationEvent(event.BPError, "BlueprintBoard: blueprint file & blueprint object is not initialized", self)
            return [err]

        self.circuit = wirebus.Circuit(self.bp)
        self.circuit.read()

        G = nx.DiGraph()
        self.max_width = width
        self.max_height = height

        mods = self.bp.get_modules()
        if mods != None:
            for bus in self.circuit.fleet:
                for wire in bus.wires:
                    if isinstance(wire.from_node, blueprint.Blueprint):
                        G.add_edge('in:'+wire.from_node.name, wire.to_node.name)
                    elif isinstance(wire.to_node, blueprint.Blueprint):
                        G.add_edge(wire.from_node.name, 'out:'+wire.to_node.name)
                    else:
                        G.add_edge(wire.from_node.name, wire.to_node.name)

            node_pos = nx.drawing.nx_agraph.graphviz_layout(G,prog='neato')

            self.node_pos = transform(node_pos, self.max_width, self.max_height)
            (self.width, self.height) = bound(self.node_pos)

        return err


    def draw(self, shape='L', bend='n', arrow = '->', out_file = None, out_format = "png") -> List[event.ValidationEvent]:
        """
        Draw the Blueprint Configuation using SchemeDraw libraries

        :param out_file: Name of the output blueprint image file (with full path)
        :param out_format: Format of the output blueprint image file (png or jpg)
        """

        if self.bp == None:
            logr.error("The blueprint object is not initialized & prepared")
            err = event.ValidationEvent(event.BPError, "BlueprintBoard: blueprint object is not initialized & prepared", self)
            return [err]

        if self.circuit == None:
            logr.error("The blueprint circuit is prepared; call prepare() before draw()")
            err = event.ValidationEvent(event.BPError, "BlueprintBoard: blueprint circuit is prepared; call prepare() before draw()", self)
            return [err]

        logr.info("Draw the blueprint yaml")

        d = schemdraw.Drawing()

        bpic = diag.BlueprintIc(self.width, self.height, name = self.bp.name,
                                    description = self.bp.description  if hasattr(self.bp, 'description') else None,
                                    inputs      = self.bp.list_input_param_names(),
                                    outputs     = self.bp.list_output_param_names(),
                                    settings    = self.bp.list_setting_param_names()
                                    )
        bpic.draw_ic(d, loc_x=0, loc_y=0)

        mods = self.bp.get_modules()
        if mods != None:
            mod_ics = dict()
            for mod in mods:
                mod_ics[mod.name] = diag.ModuleIc(name  = mod.name,
                                            description = mod.description if hasattr(mod, 'description') else None,
                                            inputs      = mod.list_input_param_names(),
                                            outputs     = mod.list_output_param_names(),
                                            settings    = mod.list_setting_param_names()
                                        )

            for bus in self.circuit.fleet:
                if isinstance(bus.from_node, blueprint.Blueprint):
                    start = bpic
                else:
                    start = mod_ics[bus.from_node.name]
                if isinstance(bus.to_node, blueprint.Blueprint):
                    end = bpic
                else:
                    end = mod_ics[bus.to_node.name]

            for ic in mod_ics.keys():
                (x, y) = self.node_pos[ic]
                mod_ics[ic].draw_ic(d, loc_x=x, loc_y=y)

            links = []
            for bus in self.circuit.fleet:
                color='black'
                if isinstance(bus.from_node, blueprint.Blueprint):
                    start = bpic
                else:
                    start = mod_ics[bus.from_node.name]
                if isinstance(bus.to_node, blueprint.Blueprint):
                    end = bpic
                else:
                    end = mod_ics[bus.to_node.name]
                
                if isinstance(bus.from_node, module.Module) and isinstance(bus.to_node, module.Module):
                    color = 'black'
                if isinstance(bus.from_node, blueprint.Blueprint):
                    color = 'blue'
                if isinstance(bus.to_node, blueprint.Blueprint):
                    color = 'red'
                
                for wire in bus.wires:
                    (from_Ic,   from_IcPin) = start.get_pin(wire.from_param)
                    (to_Ic,     to_IcPin)   = end.get_pin(wire.to_param)
                    link = diag.Link(shape=shape, bend=bend, arrow=arrow, color=color, 
                                        from_Ic = from_Ic,  from_IcPin  = from_IcPin, 
                                        to_Ic   = to_Ic,    to_IcPin    = to_IcPin )
                    links.append(link)

            for link in links:
                link.draw_ic(d)
        
        d.draw(show=True)
        if out_file != None:
            if out_file.endswith('.png', '.svg', '.jpg'):
                d.save(fname = out_file, transparent=False)
            else:
                if out_format == None:
                    d.save(fname = out_file+'.png', transparent=False)
                elif out_format.endswith('png', 'svg', 'jpg'):
                    d.save(fname = out_file+out_format, transparent=False)
                else:
                    d.save(fname = out_file+'.png', transparent=False)
        
        return None