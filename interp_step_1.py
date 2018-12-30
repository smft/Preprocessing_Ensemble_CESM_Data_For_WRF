#!/usr/bin/env python

import numpy as np
import cPickle as pickle
import multiprocessing as mp
import matplotlib.pyplot as plt
from time_location_of_data import *
from retrieve_data_from_source import *
from retrieve_geo_info import *
from esmf_horizontal_interp import *

"""test!!!test"""
date=raw_input("Input Date in YYYYMM format : ")
prefix=raw_input("Input Data Source Prefix : ")
aim_geo_file=raw_input("Input Aim Grid Geo Info : ")
save_name=raw_input("Result File Name : ")

if int(date[:4])<=2005:
    date_num=relative_timestamp_hist(int(date[:4]),int(date[4:]))
else:
    date_num=relative_timestamp_fcst(int(date[:4]),int(date[4:]))
source_data=get_source(prefix,date_num)
aim_geo=get_latlon(aim_geo_file)

vars_to_interp=['PS','PSL','TS','U','V','Q','T','Z3']
cpu_count=len(vars_to_interp)
q=mp.Queue(cpu_count)
source_lon,source_lat=np.meshgrid(source_data['lon'],source_data['lat'])
for var_to_interp in vars_to_interp:
    if var_to_interp=='U':
        p=mp.Process(target=horizontal_interp,args=(var_to_interp,3,\
                                                    source_lat,\
                                                    source_lon,\
                                                    source_data[var_to_interp],\
                                                    aim_geo['lat_u'],\
                                                    aim_geo['lon_u'],\
                                                    q,'bilinear'))
    elif var_to_interp=='V':
        p=mp.Process(target=horizontal_interp,args=(var_to_interp,3,\
                                                    source_lat,\
                                                    source_lon,\
                                                    source_data[var_to_interp],\
                                                    aim_geo['lat_v'],\
                                                    aim_geo['lon_v'],\
                                                    q,'bilinear'))
    elif var_to_interp in ['PS','PSL','TS']:
        p=mp.Process(target=horizontal_interp,args=(var_to_interp,2,\
                                                    source_lat,\
                                                    source_lon,\
                                                    source_data[var_to_interp],\
                                                    aim_geo['lat_m'],\
                                                    aim_geo['lon_m'],\
                                                    q,'bilinear'))
    else:
        p=mp.Process(target=horizontal_interp,args=(var_to_interp,3,\
                                                    source_lat,\
                                                    source_lon,\
                                                    source_data[var_to_interp],\
                                                    aim_geo['lat_m'],\
                                                    aim_geo['lon_m'],\
                                                    q,'bilinear'))
    p.start()
rslt=dict()
for i in range(cpu_count):
    trans=q.get()
    rslt[trans[0]]=trans[1]
flag_save=open(save_name,'wb')
pickle.dump({'data':rslt,'coord':aim_geo},flag_save)
flag_save.close()

