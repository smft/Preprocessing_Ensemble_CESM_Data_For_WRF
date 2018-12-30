#!/usr/bin/env python
import multiprocessing as mp
import numpy as np
from ctypes import *

def make_shared_array_3D(nz,ny,nx):
    shared_array_input_base=mp.Array(c_double,nz*ny*nx)
    data=np.ctypeslib.as_array(shared_array_input_base.get_obj())
    data=data.reshape(nz,ny,nx)
    return data

def make_shared_array_2D(ny,nx):
    shared_array_input_base=mp.Array(c_double,ny*nx)
    data=np.ctypeslib.as_array(shared_array_input_base.get_obj())
    data=data.reshape(ny,nx)
    return data

def make_shared_array_1D(nx):
    shared_array_input_base=mp.Array(c_double,nx)
    data=np.ctypeslib.as_array(shared_array_input_base.get_obj())
    data=data.reshape(nx)
    return data
