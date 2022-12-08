from diagrams import Diagram, Node, Cluster, Edge

import html
import textwrap
from typing import List, Union
import diagrams

def _format_text(text):
    """
    Formats the node description
    """
    wrapper = textwrap.TextWrapper(width=40, max_lines=3)
    lines = [html.escape(line) for line in wrapper.wrap(text)]
    lines += [""] * (3 - len(lines))  # fill up with empty lines so it is always three
    return "<br/>".join(lines)

#=======================================================================================#

# def Blueprint(name, **kwargs):
#     graph_attributes = {
#         "label": html.escape(name),
#         "bgcolor": "white",
#         "margin": "16",
#         "style": "dashed",
#     }
#     graph_attributes.update(kwargs)
#     return Cluster(name, graph_attr=graph_attributes)

class Blueprint(Cluster):

    def __init__(
                self,
                name: str = "cluster",
                description: str = "",
                inputs: List[str] = [], 
                outputs: List[str] = [],
                settings: List[str] = []
            ):
        """
        Blueprint represents a cluster context.

        :param name: Blueprint name.
        :param direction: Data flow direction. Default is 'left to right'.
        :param graph_attr: Provide graph_attr dot config attributes.
        """

        graph_attr = {
                    "label": html.escape(name),
                    "bgcolor": "white",
                    "margin": "16",
                    "style": "dashed",
                    "direction": "LR"
                }
        super().__init__(label = name, direction = "LR", graph_attr = graph_attr)
        diagrams.setcluster(self)
        self.bp_node = Module(name, description,
                inputs, outputs,settings, 
                type = "Blueprint")

    def _format_blueprint_label(self, name, description, inputs, outputs, settings):
        """
        Create a graphviz label string for Module - name, inputs, outputs, settings;
        """
        title = f'<font point-size="14"><b>{html.escape(name)}</b></font><br/>'
        subtitle = f'<font point-size="12">-------------------------------<br/></font>'
        subtitle += f'<font point-size="9">[{_format_text(description)}]<br/></font>' if description else ""
        text = f'<font point-size="12">-------------------------------<br/></font>' if description else ""
        if inputs != None:
            for i in inputs:
                text += f'<font point-size="12">input: {_format_text(i)}</font>' if i else ""
        if outputs != None:
            for o in outputs:
                text += f'<font point-size="12">output: {_format_text(o)}</font>' if o else ""
        if settings != None:
            for s in settings:
                text += f'<font point-size="12">setting: {_format_text(s)}</font>' if s else ""

        return f"<{title}{subtitle}{text}>"

#=======================================================================================#

# def Module(name, inputs=[], outputs=[], settings=[], type="Module", **kwargs):
#     line_count = len(inputs) + len(outputs) + len(settings)
#     height = 0.5*line_count
#     key = f"{type}"
#     node_attributes = {
#         "label": _format_module_label(name, key, inputs, outputs, settings),
#         "labelloc": "u",
#         "shape": "rect",
#         "width": "2.6",
#         "height": str(height),
#         "fixedsize": "true",
#         "style": "filled",
#         "fillcolor": "dodgerblue3",
#         "fontcolor": "white",
#     }
#     node_attributes.update(kwargs)
#     return Node(**node_attributes)

class Module(Node):
    def __init__(
                self, 
                name: str, 
                description: str = "",
                inputs: List[str] = [], 
                outputs: List[str] = [],
                settings: List[str] = [], 
                type: str = "Module"
            ):
        """
        Module represents a blueprint component.

        :param name: Name of the module.
        :param inputs: List of input parameter names 
        :param outputs: List of output parameter names 
        :param settings: List of environment parameter names 
        """
        self.name = name

        line_count = len(inputs) + len(outputs) + len(settings)
        height = 0.5 * (line_count+1)
        key = f"{type}"
        node_attributes = {
            "label": self._format_module_label(name, key, description, inputs, outputs, settings),
            "labelloc": "u",
            "shape": "rect",
            "width": "2.6",
            "height": str(height),
            "fixedsize": "false",
            "style": "filled",
            "fillcolor": self._module_color(type),
            "fontcolor": "white",
        }
        
        super().__init__(**node_attributes)
    
    def _module_color(self, type):
        if type.lower() == "module":
            return "gold4"
        elif type.lower() == "blueprint":
            return "dodgerblue3"
        else:
            return "gray30"

    def _format_module_label(self, name, key, description, inputs, outputs, settings):
        """
        Create a graphviz label string for Module - name, inputs, outputs, settings;
        """
        title = f'<font point-size="14"><b>{html.escape(name)}</b></font><br/>'
        subtitle = f'<font point-size="8">[{html.escape(key)}]<br/></font>' if key else ""
        subtitle += f'<font point-size="12">-------------------------------<br/></font>'
        subtitle += f'<font point-size="9">[{_format_text(description)}]<br/></font>' if description else ""
        text = f'<font point-size="12">-------------------------------<br/></font>' if description else ""
        if inputs != None:
            for i in inputs:
                text += f'<font point-size="12">input: {_format_text(i)}</font>' if i else ""
        if outputs != None:
            for o in outputs:
                text += f'<font point-size="12">output: {_format_text(o)}</font>' if o else ""
        if settings != None:
            for s in settings:
                text += f'<font point-size="12">setting: {_format_text(s)}</font>' if s else ""

        return f"<{title}{subtitle}{text}>"

    def __str__(self) -> str:
        return str(self.name)

    # def __rshift__(self, other: Union["Module", List["Module"], "Wire"]):
    #     """Implements Self >> Module, Self >> [Modules] and Self Wire."""
    #     if isinstance(other, list):
    #         print("N1:" + str(other))
    #     elif isinstance(other, Module):
    #         print("N2:" + str(other))
    #     else:
    #         print("N3:" + str(other))

    #     super().__rshift__(other)

    # def __lshift__(self, other: Union["Module", List["Module"], "Wire"]):
    #     super().__lshift__(other)

    # def __rrshift__(self, other: Union[List["Module"], List["Wire"]]):
    #     """Called for [Modules] and [Wires] >> Self because list don't have __rshift__ operators."""
    #     print("N4: " + str(other))
    #     if other != None:
    #         super().__rrshift__(other)

    # def __rlshift__(self, other: Union[List["Module"], List["Wire"]]):
    #     """Called for [Modules] << Self because list of Modules don't have __lshift__ operators."""
    #     print("N5: " + str(other))
    #     if other != None:
    #         super().__rlshift__(other)

#=======================================================================================#

# def Wire(from_pin="", to_pin="", **kwargs):
#     edge_attribtues = {"style": "dashed", "color": "gray60"}
#     if from_pin and to_pin:
#         label = from_pin + '-->>--' + to_pin
#         edge_attribtues.update({"label": _format_wire_label(label)})
#     edge_attribtues.update(kwargs)
#     return Edge(**edge_attribtues)

class Wire(Edge):

    def __init__(
                self,
                from_pin: str = None, 
                to_pin: str = None
            ):
        """
        Wire connects the output of one module to inputs of another module.

        :param from_pin: From module output parameter name
        :param to_pin: To module input parameter name
        """
        self.name = f'{from_pin} >> {to_pin}'
        edge_attribtues = {"style": "dashed", "color": "gray60"}
        if from_pin and to_pin:
            label = from_pin + '-->>--' + to_pin
            edge_attribtues.update({"label": self._format_wire_label(label)})
        
        super().__init__(**edge_attribtues)

    def _format_wire_label(self, description):
        """
        Create a graphviz label string for a Wire that connects two modules
        """
        wrapper = textwrap.TextWrapper(width=24, max_lines=3)
        lines = [html.escape(line) for line in wrapper.wrap(description)]
        text = "<br/>".join(lines)
        return f'<<font point-size="10">{text}</font>>'

    def __str__(self) -> str:
        return str(self.name)

    # def __rshift__(self, other: Union["Module", "Wire", List["Module"]]):
    #     """Implements Self >> Module or Wire and Self >> [Modules]."""
    #     if isinstance(other, list):
    #         print("E1:" + str(other))
    #     elif isinstance(other, Module):
    #         print("E2:" + str(other))
    #     else:
    #         print("E3:" + str(other))

    #     super().__rshift__(other)

    # def __lshift__(self, other: Union["Module", "Wire", List["Module"]]):
    #     """Implements Self << Module or Wire and Self << [Modules]."""
    #     super().__lshift__(other)

    # def __rrshift__(self, other: Union[List["Module"], List["Wire"]]) -> List["Wire"]:
    #     """Called for [Modules] or [Wires] >> Self because list of Wires don't have __rshift__ operators."""
    #     print("E4: " + str(other))
    #     if other != None:
    #         super().__rrshift__(other)

    # def __rlshift__(self, other: Union[List["Module"], List["Wire"]]) -> List["Wire"]:
    #     """Called for [Modules] or [Wires] << Self because list of Wires don't have __lshift__ operators."""
    #     print("E5: " + str(other))
    #     if other != None:
    #         super().__rlshift__(other)

#=======================================================================================#