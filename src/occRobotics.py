#!/home/alon/LocalInstalls/miniconda3/envs/pyoccenv741/bin/python


import ifcopenshell, ifcopenshell.geom

from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB

from OCC.Display.OCCViewer import Viewer3d


from OCC.Core import gp
import numpy as np
import math as m

from ctypes import c_double

def eul2R_zyx(roll,pitch,yaw):
    return Rz(yaw) @ Ry(pitch) @ Rx(roll)

def Rx(theta):
    return np.matrix([[ 1, 0           , 0        ],
                   [ 0, m.cos(theta),-m.sin(theta)],
                   [ 0, m.sin(theta), m.cos(theta)]])
  
def Ry(theta):
    return np.matrix([[m.cos(theta), 0, m.sin(theta)],
                   [ 0           , 1, 0           ],
                   [-m.sin(theta), 0, m.cos(theta)]])
  
def Rz(theta):
    return np.matrix([[m.cos(theta), -m.sin(theta), 0 ],
                   [ m.sin(theta), m.cos(theta) , 0 ],
                   [ 0           , 0            , 1 ]])

def gpMat3toNumpy(gpMat3):
    #gp_mat class is a 3x3 matrix class with no method to return values
    #notice how the Row method accepts integers starting 1
    row0 = gpMat3.Row(1).Coord()
    row1 = gpMat3.Row(2).Coord()
    row2 = gpMat3.Row(3).Coord()
    M = np.array([row0,
            row1,
            row2])
    return M

def VAndTheta2Quat(v,theta):
    #builds quaternion for rotation around vector v
    #v - unit direction vector
    #theta - angle in radians
    qx = v[0] * np.sin(theta/2)
    qy = v[1] * np.sin(theta/2)
    qz = v[2] * np.sin(theta/2)
    qw = np.cos(theta/2)
    return (qx,qy,qz,qw)

def makeTrsf(R,t):    
    #X_k+1 = T*X_k
    #This transform was made to move things around in the world space

    #R - numpy matrix 3x3
    #t - numpy array [(x,y,z)]
    
    n1 = R[:,2]
    n2 = R[:,0]
    
    t = t.tolist()
    n1 = n1.squeeze().tolist()[0]
    n2 = n2.squeeze().tolist()[0]

    t = gp.gp_Pnt(t[0],t[1],t[2])
    n1 = gp.gp_Dir(n1[0],n1[1],n1[2])
    n2 = gp.gp_Dir(n2[0],n2[1],n2[2])

    gpTrsf = gp.gp_Trsf()
    gpTrsf.SetTransformation(gp.gp_Ax3(t,n1,n2))

    return gpTrsf

def getCameraTransform(cam):
    #Transform T is an evolving transform, as opposed to coordiante system change.
    #That is to say, v_camera = inv(T) v_world
    #This transform gives the pose of the camera in world coordiantes.

    data = cam.OrientationMatrix().GetData()
    v = list((c_double * 16).from_address(int(data)))
    M = np.array(v).reshape((4,4)).T
    
    #why R_cfix:
    #R_w2c = M[0:3,0:3] is the rotation matrix from world axes to camera axes
    #unfortunatly. the camera is defined with x-right, y-up, z - behind
    #we want the camera to be defined with x-right,y-down, z - front
    R_cfix = np.array([[1, 0, 0],
                        [0, -1, 0],
                        [0, 0,-1]])
    R_w2c = M[0:3,0:3]
    R_c2w =  R_w2c.T
    t_c_c2w = M[0:3,3].reshape(3,1)
    t_w_w2c = R_c2w @ (-t_c_c2w)

    #not exactly sure why this is how its written.. but it does
    T = np.vstack((np.hstack([R_c2w @ R_cfix, t_w_w2c]), [0, 0, 0, 1]))
    return T

def moveCam2Pose(cam,pose):
    t = pose[:3]
    R = eul2R_zyx(pose[3],pose[4],pose[5])
    cam.Transform(makeTrsf(R,t))

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
