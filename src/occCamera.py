#!/home/alon/LocalInstalls/miniconda3/envs/pyoccenv741/bin/python
import occGeomtrey
import ifcopenshell, ifcopenshell.geom

from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB
from OCC.Display.OCCViewer import Viewer3d

from OCC.Core import gp
import numpy as np
import math as m

from ctypes import c_double

def getCameraTransform(cam):
    #We define the camera transform such that v_world = T * v_camera
    #that is to say, the cameras position in the world frame is equals to  T * [0 0 0 1]'
    #same way as matlab does hgTransforms basically...

    data = cam.OrientationMatrix().GetData()
    v = list((c_double * 16).from_address(int(data)))
    M = np.array(v).reshape((4,4)).T
    
    #we discovered through trial and error, that M is inv(T)
    R_w2c = M[0:3,0:3]
    R_c2w =  R_w2c.T
    t_c_c2w = M[0:3,3].reshape(3,1)
    t_w_w2c = R_c2w @ (-t_c_c2w)

    #why R_cfix:
    #R_w2c = M[0:3,0:3] is the rotation matrix from world axes to camera axes
    #unfortunatly. the camera is defined with x-right, y-up, z - behind
    #we want the camera to be defined with x-right,y-down, z - front
    R_cfix = np.array([[1, 0, 0],
                        [0, -1, 0],
                        [0, 0,-1]])

    T = occGeomtrey.TfromRt(R_c2w@R_cfix,t_w_w2c)
    return T

def moveCam2Pose(cam,pose):
    t = pose[:3]
    R = occGeomtrey.eul2R_zyx(pose[3],pose[4],pose[5])
    Tto = occGeomtrey.TfromRt(R,t)
    Tin = getCameraTransform(cam)
    gpT = occGeomtrey.T2gpTrsf(Tto @ occGeomtrey.InverseTransform(Tin))
    cam.Transform(gpT)

def getProjectionMatrix(cam):
    data = cam.ProjectionMatrix().GetData()
    v = list((c_double * 16).from_address(int(data)))
    M = np.array(v).reshape((4,4))
    return M

def offlineRenderIFC(ifcPath = '../data/IfcOpenHouse_IFC4.ifc'):
    ifc = ifcopenshell.open(ifcPath)

    settings = ifcopenshell.geom.settings()
    settings.set(settings.USE_PYTHON_OPENCASCADE, True)

    offscreen_renderer = Viewer3d()
    offscreen_renderer.Create()
    offscreen_renderer.SetModeShaded()

    products = ifc.by_type("IfcProduct")
    for product in products:
        if product.is_a("IfcOpeningElement"): continue
        if product.Representation:
            shape = ifcopenshell.geom.create_shape(settings, product)
            r, g, b, a = shape.styles[0] # the shape color
            color = Quantity_Color(abs(r), abs(g), abs(b), Quantity_TOC_RGB)
            offscreen_renderer.DisplayShape(shape.geometry,color=color, transparency=abs(1 -a),update=True)
    return offscreen_renderer
