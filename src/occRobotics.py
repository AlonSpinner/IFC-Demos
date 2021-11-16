import ifcopenshell, ifcopenshell.geom

from OCC.Core import gp
import numpy as np
import math as m


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
