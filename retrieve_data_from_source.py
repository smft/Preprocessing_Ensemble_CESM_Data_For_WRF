#!/usr/bin/env python

def get_source(file_prefix,data_number):
    import glob
    import numpy as np
    from netCDF4 import Dataset

    variables=['PS','PSL','TS','U','V','Q','T','Z3']
    constant_variables=['P0','hyai','hybi','lat','lon']
    rslt=dict()
    file_names=list()
    for cell_variable in variables:
        name=glob.glob(file_prefix+'*.'+cell_variable+'.*')[0]
        file_names+=[name]

    for i,cell_variable in enumerate(variables):
        flag=Dataset(file_names[i])
        if i > 2:
            rslt[cell_variable]=flag.variables[cell_variable][data_number,:,:,:]
        else:
            rslt[cell_variable]=flag.variables[cell_variable][data_number,:,:]

    for cell_variable in constant_variables:
        rslt[cell_variable]=flag.variables[cell_variable][:]

    return rslt
