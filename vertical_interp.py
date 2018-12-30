#!/usr/bin/env python

import numpy as np
import cPickle as pickle
import multiprocessing as mp
import matplotlib.pyplot as plt
from ctypes import *
from verify import *
from hybrid_to_p import *
from netCDF4 import Dataset
from scipy import interpolate
from make_shared_mem import *
from scipy_vertical_interp import *
from time_location_of_data import *
from retrieve_data_from_source import *

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
mod_plevs=np.array([1000,975,950,925,900,875,850,825,800,775,\
                750,700,650,600,550,500,450,400,350,300,\
                250,225,200,175,150,125,100,70,50,30,\
                20,10,7,5,3,2,1])*100
rslt=dict()
nz,ny,nx=np.shape(source_data['T'])
for var in ['T','U','V','Q','Z3']:
    nz,ny,nx=np.shape(source_data['T'])
    source_shared_t=make_shared_array_3D(nz,ny,nx)+source_data[var]
    source_shared_ps=make_shared_array_2D(ny,nx)+source_data['PS']
    source_shared_hyai=make_shared_array_1D(nz-1)+source_data['hyai']
    source_shared_hybi=make_shared_array_1D(nz-1)+source_data['hybi']
    mod_shared_plevs=make_shared_array_1D(37)+mod_plevs
    trans=make_shared_array_3D(37,ny,nx)
    cpu_count=mp.cpu_count()
    processlock=mp.BoundedSemaphore(cpu_count)
    for cell in np.array_split(np.arange(0,nx,1),cpu_count,axis=0):
        processlock.acquire()
        p=mp.Process(target=vertical_interp_module,args=\
                        (source_shared_t,source_shared_ps,source_data['P0'],\
                        source_shared_hyai,source_shared_hybi,mod_shared_plevs,\
                        np.arange(0,ny,1),cell,trans,processlock))
        p.start()
    for i in range(cpu_count):
        p.join()
    rslt[var]=trans

for var in ['PS','P0','TS','lat','lon']:
    rslt[var]=source_data[var]
lon_2d,lat_2d=np.meshgrid(rslt['lon'],rslt['lat'])
flag=Dataset('../../check_data/grid.nc')
interp_lat=flag.variables['XLAT_M'][0,:,:]
interp_lon=flag.variables['XLONG_M'][0,:,:]
lllat=np.min(interp_lat)
urlat=np.max(interp_lat)
lllon=np.min(interp_lon)
urlon=np.max(interp_lon)
for i in range(37):
    tp=rslt['T'][i,:,:]
    print np.sum(rslt['T'][i,:,:]-rslt['T'][i+1,:,:])
    minv=np.mean(tp[np.isnan(tp)==False])*0.9
    maxv=np.mean(tp[np.isnan(tp)==False])*1.1
    plot_data(tp,lat_2d,lon_2d,lllat,urlat,lllon,urlon,minv,maxv,'T_'+str(mod_plevs[i])+' Pa')
    plt.show()
