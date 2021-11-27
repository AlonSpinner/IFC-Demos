#!/home/alon/LocalInstalls/miniconda3/envs/pyoccenv741/bin/python

import ifcopenshell, ifcopenshell.geom
from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB
from OCC.Display.SimpleGui import init_display
import time
import occCamera

occ_display, start_display, add_menu, add_function_to_menu = init_display()
cam = occ_display.View.Camera()

def loadIFC(ifcPath = '../data/IfcOpenHouse_IFC4.ifc'):
    # Open the IFC file using IfcOpenShell
    ifc = ifcopenshell.open(ifcPath)
    settings = ifcopenshell.geom.settings()
    settings.set(settings.USE_PYTHON_OPENCASCADE, True)
    products = ifc.by_type("IfcProduct")
    for product in products:
        if product.is_a("IfcOpeningElement"): continue
        if product.Representation:
            shape = ifcopenshell.geom.create_shape(settings, product)
            r, g, b, a = shape.styles[0] # the shape color
            color = Quantity_Color(abs(r), abs(g), abs(b), Quantity_TOC_RGB)
            display_shape = occ_display.DisplayShape(shape.geometry,color=color, transparency=abs(1 -a),update=True)

def loadMenus():
    add_menu('camera projection')
    def perspective(event=None):
        occ_display.SetPerspectiveProjection()
        occ_display.Repaint()
    def orthographic(event=None):
        occ_display.SetOrthographicProjection()
        occ_display.Repaint()
    add_function_to_menu('camera projection', perspective)
    add_function_to_menu('camera projection', orthographic)

    add_menu('camera view')
    def viewTop(event=None):
        occ_display.View_Top()
    def viewBottom(event=None):
        occ_display.View_Bottom()
    def viewLeft(event=None):
        occ_display.View_Left()
    def viewRight(event=None):
        occ_display.View_Right()
    def viewFront(event=None):
        occ_display.View_Front()
    def viewRear(event=None):
        occ_display.View_Rear()
    def viewIso(event=None):
        occ_display.View_Iso()
    add_function_to_menu('camera view', viewTop)
    add_function_to_menu('camera view', viewBottom)
    add_function_to_menu('camera view', viewLeft)
    add_function_to_menu('camera view', viewRight)
    add_function_to_menu('camera view', viewFront)
    add_function_to_menu('camera view', viewRear)
    add_function_to_menu('camera view', viewIso)
    
    add_menu('print')
    def printCameraTransform():
        print("%s[s]:" % (time.time() - start_time))
        print(occCamera.getCameraTransform(cam))
    add_function_to_menu('print', printCameraTransform)

if __name__ == '__main__':
    loadIFC()
    loadMenus()
    start_time = time.time()
    start_display() #must be used or kernel crashes