#!/home/alon/LocalInstalls/miniconda3/envs/pyoccenv741/bin/python

import ifcopenshell, ifcopenshell.geom
from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB
from OCC.Display.SimpleGui import init_display
import numpy as np
import toposort

def ifcshow(ifc):
    settings = ifcopenshell.geom.settings()
    settings.set(settings.USE_PYTHON_OPENCASCADE, True)
    occ_display, start_display, add_menu, add_function_to_menu = init_display()
    cam = occ_display.View.Camera()
    products = ifc.by_type("IfcProduct")
    for product in products:
        if product.is_a("IfcOpeningElement"): continue
        if product.Representation:
            shape = ifcopenshell.geom.create_shape(settings, product)
            r, g, b, a = shape.styles[0] # the shape color
            color = Quantity_Color(abs(r), abs(g), abs(b), Quantity_TOC_RGB)
            display_shape = occ_display.DisplayShape(shape.geometry,color=color, transparency=abs(1 -a),update=True)
    start_display() #must be used or kernel crashes

def OptimizeIFC(f):
    g = ifcopenshell.file(schema=f.schema)
#from https://academy.ifcopenshell.org/posts/ifcopenshell-optimizer-tutorial/

    def generate_instances_and_references():
        """
        Generator which yields an entity id and 
        the set of all of its references contained in its attributes. 
        """
        for inst in f:
            yield inst.id(), set(i.id() for i in f.traverse(inst)[1:] if i.id())

            
    instance_mapping = {}

    def map_value(v):
        """
        Recursive function which replicates an entity instance, with 
        its attributes, mapping references to already registered
        instances. Indeed, because of the toposort we know that 
        forward attribute value instances are mapped before the instances
        that reference them.
        """
        if isinstance(v, (list, tuple)):
            # lists are recursively traversed
            return type(v)(map(map_value, v))
        elif isinstance(v, ifcopenshell.entity_instance):
            if v.id() == 0:
                # express simple types are not part of the toposort and just copied
                return g.create_entity(v.is_a(), v[0])
    
            
            return instance_mapping[v]
        else:
            # a plain python value can just be returned
            return v

    info_to_id = {}
    
    
    for id in toposort(dict(generate_instances_and_references())):
        inst = f[id]
        info = inst.get_info(include_identifier=False, recursive=True, return_type=frozenset)
        if info in info_to_id:
            mapped = instance_mapping[inst] = instance_mapping[f[info_to_id[info]]]

        else:
            info_to_id[info] = id
            instance_mapping[inst] = g.create_entity(
                inst.is_a(),
                *map(map_value, inst)
            )
    return g