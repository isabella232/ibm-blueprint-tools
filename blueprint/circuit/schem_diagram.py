import schemdraw.elements as elem
from schemdraw.elements import Ic, Wire, Arc2, ArcZ, ArcN

from typing import List

class BlueprintIc:

    def __init__(self,
                width: float = 10,
                height: float = 10,
                name: str = "blueprint",
                description: str = "",
                inputs: List[str] = [], 
                outputs: List[str] = [],
                settings: List[str] = [],
                **kwargs):
        """
        BlueprintIc represents a Blueprint cluster context.

        :param name: Blueprint name.
        :param description: Blueprint description 
        :param inputs: List of input parameter names for the Blueprint
        :param outputs: List of output parameter names for the Blueprint
        :param settings: List of env setting parameter names for the Blueprint
        """        
        self.name = name
        self.width = width
        self.height = height

        self.in_pin_names = []
        for inp_name in inputs:
            self.in_pin_names.append(inp_name)

        self.out_pin_names = []        
        for outp_name in outputs:
            self.out_pin_names.append(outp_name)

        self.env_pin_names = []        
        for envp_name in settings:
            self.env_pin_names.append(envp_name)
            
        if description != None:
            label = name + '\n(' + description + ')'
        else:
            label = name

        self.rect = elem.Rect(corner1=(0,0), corner2=(width, height), toplabel = label).hold()
        self.in_connector = elem.Header(rows=len(self.in_pin_names), col=1, pinsleft=self.in_pin_names).hold()
        self.out_connector = elem.Header(rows=len(self.out_pin_names), col=1, pinsright=self.out_pin_names).hold()
        self.env_connector = elem.Header(rows=1, col=len(self.env_pin_names), pinsleft=self.env_pin_names).hold()

    def get_pin(self, pin_name):
        
        if(pin_name in self.in_pin_names):
            return (self.in_connector, 'pin'+str(self.in_pin_names.index(pin_name)+1))
        elif (pin_name in self.out_pin_names):
            return (self.out_connector, 'pin'+str(self.out_pin_names.index(pin_name)+1))
        elif (pin_name in self.env_pin_names):
            return (self.env_connector, 'pin'+str(self.env_pin_names.index(pin_name)+1))
        else:
            return (None, None)

    def draw_ic(self, d, loc_x=0, loc_y=0):
        d.here = (0,0)
        d += self.rect
        d.here = (0,0)
        d.move(dx=loc_x,            dy=loc_y+self.height/2)
        d += self.in_connector
        d.here = (0,0)
        d.move(dx=loc_x+self.width-0.6, dy=loc_y+self.height/2)
        d += self.out_connector
        d.here = (0,0)
        d.move(dx=loc_x+self.width/2, dy=loc_y)
        d += self.env_connector

#=======================================================================================#

class ModuleIc:
    def __init__(
                self, 
                name: str = "module", 
                description: str = "",
                inputs: List[str] = [], 
                outputs: List[str] = [],
                settings: List[str] = [], 
                **kwargs):
        """
        ModulePane represents a module component, in a blueprint

        :param name: Name of the module.
        :param inputs: List of input parameter names 
        :param outputs: List of output parameter names 
        :param settings: List of environment parameter names 
        """
        self.name = name

        pins = []
        pos = 1
        size = len(inputs)
        self.in_pin_names = []
        self.in_pins = []
        for inp_name in inputs:
            slt = f'{pos}/{size}'
            self.in_pin_names.append(inp_name)
            self.in_pins.append(
                    elem.IcPin(pin=inp_name, anchorname=inp_name, side='L', slot=slt)
                )
            pos+=1

        pos = 1
        size = len(outputs)
        self.out_pin_names = []
        self.out_pins = []
        for outp_name in outputs:
            slt = f'{pos}/{size}'
            self.out_pin_names.append(outp_name)
            self.out_pins.append(
                    elem.IcPin(pin=outp_name, anchorname=outp_name, side='R', slot=slt)
                )
            pos+=1
        
        height = max(len(self.in_pins), len(self.out_pins))
        height = len(self.in_pins) if len(self.in_pins) > len(self.out_pins) else len(self.out_pins)
        height = 2 if height/2 < 2 else height/2

        pos = 1
        size = len(settings)
        self.env_pin_names = []
        self.env_pins = []
        for envp_name in settings:
            slt = f'{pos}/{size}'
            self.env_pin_names.append(envp_name)
            self.env_pins.append(
                    elem.IcPin(pin=envp_name, anchorname=envp_name, side='B', slot=slt, rotation=90)
                )
            pos+=1
        
        width = len(self.env_pins)
        width = 1 if width/2 < 1 else width/2

        if description != None:
            label = name + '\n(' + description + ')'
        else:
            label = name
        
        pins = self.in_pins + self.out_pins + self.env_pins
        self.ic = Ic(size=(width, height), pins=pins, lsize=10, plblsize=10, toplabel = label, **kwargs)

    def get_pin(self, pin_name):
        
        if(pin_name in self.in_pin_names):
            return (self.ic, pin_name)
            # return (self.in_pins[self.in_pin_names.index(pin_name)], pin_name)
        elif (pin_name in self.out_pin_names):
            return (self.ic, pin_name)
            # return (self.out_pins[self.out_pin_names.index(pin_name)], pin_name)
        elif (pin_name in self.env_pin_names):
            return (self.ic, pin_name)
            # return (self.env_pins[self.env_pin_names.index(pin_name)], pin_name)
        else:
            return (None, None)

    def draw_ic(self, d, loc_x=0, loc_y=0):
        d.here = (0,0)
        d.move(loc_x, loc_y)
        d += self.ic

#=======================================================================================#

class Link:

    def __init__(
                self,
                shape: str='L', # L (for line)  A (for Arc)
                bend: str='-', 
                arrow: str=None, 
                color: str='#FFFFFF',
                from_Ic: Ic = None, 
                from_IcPin: str = None, 
                to_Ic: Ic = None, 
                to_IcPin: str = None, 
                **kwargs
            ):
        """
        Relation connects the output of one module to inputs of another module.

        :param from_Ic: Name of the start module-ic
        :param from_IcPin: Name of the start module-ic pin
        :param to_Ic: Name of the end module-ic
        :param to_IcPin: Name of the end module-ic pin
        """

        if shape.lower() == 'a':
            if bend == 'z':
                self.wire = ArcZ(arrow=arrow, color=color, **kwargs).at(getattr(from_Ic, from_IcPin)).to(getattr(to_Ic, to_IcPin))
            elif shape.lower() == 'n':
                self.wire = ArcN(arrow=arrow, color=color, **kwargs).at(getattr(from_Ic, from_IcPin)).to(getattr(to_Ic, to_IcPin))
            else:
                self.wire = Arc2(arrow=arrow, color=color, **kwargs).at(getattr(from_Ic, from_IcPin)).to(getattr(to_Ic, to_IcPin))
        else:
            self.wire = Wire(shape=bend, arrow=arrow, color=color, **kwargs).at(getattr(from_Ic, from_IcPin)).to(getattr(to_Ic, to_IcPin))

    def draw_ic(self, d):
        d += self.wire


#=======================================================================================#