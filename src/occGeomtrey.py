#!/home/alon/LocalInstalls/miniconda3/envs/pyoccenv741/bin/python
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

def TfromRt(R, t):
    #copied from programcreek
    R = R.reshape(3, 3)
    t = t.reshape(3, 1)
    return np.vstack((np.hstack([R, t]), [0, 0, 0, 1])) 

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

def gpMattoNumpy(gpMat):
    #gp_mat class is a 2x3 matrix class with no method to return values
    #notice how the Row method accepts integers starting 1
    row0 = gpMat.Row(1).Coord()
    row1 = gpMat.Row(2).Coord()
    M = np.array([row0,
            row1])
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

def gpTrsf2T(gpT):
    T=np.zeros((4,4))
    for ii in range(3): #gpTrsf defines are 3x4 matrix
        for jj in range(4):
            T[ii,jj] = gpT.Value(ii+1,jj+1)
    T[3,3] = 1 #add the 1 for the [4th,4th place]
    return T

def T2gpTrsf(T):
    gpTrsf = gp.gp_Trsf()
    gpTrsf.SetValues(float(T[0,0]),float(T[0,1]),float(T[0,2]),float(T[0,3]),
    float(T[1,0]),float(T[1,1]),float(T[1,2]),float(T[1,3]),
    float(T[2,0]),float(T[2,1]),float(T[2,2]),float(T[2,3]))
    return gpTrsf