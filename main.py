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
from retrieve_geo_info import *
from scipy_vertical_interp import *
from time_location_of_data import *
from esmf_horizontal_interp import *
from retrieve_data_from_source import *

"""test!!!test"""
# read namelist
date=raw_input("Input Date in YYYYMM format : ")
prefix=raw_input("Input Data Source Prefix : ")
aim_geo_file=raw_input("Input Aim Grid Geo Info : ")
save_name=raw_input("Result File Name : ")
# get number in time series
if int(date[:4])<=2005:
    date_num=relative_timestamp_hist(int(date[:4]),int(date[4:]))
else:
    date_num=relative_timestamp_fcst(int(date[:4]),int(date[4:]))
# vertical interpolation using linear
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
for var in ['PS','P0','PSL','TS','lat','lon']:
    rslt[var]=source_data[var]
# horizontal interploation using bilinear
aim_geo=get_latlon(aim_geo_file)
vars_to_interp=['PS','PSL','TS','U','V','Q','T','Z3']
cpu_count=len(vars_to_interp)
q=mp.Queue(cpu_count)
source_lon,source_lat=np.meshgrid(rslt['lon'],rslt['lat'])
for var_to_interp in vars_to_interp:
    if var_to_interp=='U':
        p=mp.Process(target=horizontal_interp,args=(var_to_interp,3,\
                                                    source_lat,\
                                                    source_lon,\
                                                    rslt[var_to_interp],\
                                                    aim_geo['lat_u'],\
                                                    aim_geo['lon_u'],\
                                                    q,'bilinear'))
    elif var_to_interp=='V':
        p=mp.Process(target=horizontal_interp,args=(var_to_interp,3,\
                                                    source_lat,\
                                                    source_lon,\
                                                    rslt[var_to_interp],\
                                                    aim_geo['lat_v'],\
                                                    aim_geo['lon_v'],\
                                                    q,'bilinear'))
    elif var_to_interp in ['PS','PSL','TS']:
        p=mp.Process(target=horizontal_interp,args=(var_to_interp,2,\
                                                    source_lat,\
                                                    source_lon,\
                                                    rslt[var_to_interp],\
                                                    aim_geo['lat_m'],\
                                                    aim_geo['lon_m'],\
                                                    q,'bilinear'))
    else:
        p=mp.Process(target=horizontal_interp,args=(var_to_interp,3,\
                                                    source_lat,\
                                                    source_lon,\
                                                    rslt[var_to_interp],\
                                                    aim_geo['lat_m'],\
                                                    aim_geo['lon_m'],\
                                                    q,'bilinear'))
    p.start()
rslt_=dict()
for i in range(cpu_count):
    trans=q.get()
    rslt_[trans[0]]=trans[1]
flag_save=open(save_name,'wb')
pickle.dump({'data':rslt,'coord':aim_geo},flag_save)
flag_save.close()

#lon_2d,lat_2d=np.meshgrid(rslt['lon'],rslt['lat'])
#flag=Dataset('../../check_data/grid.nc')
#interp_lat=flag.variables['XLAT_M'][0,:,:]
#interp_lon=flag.variables['XLONG_M'][0,:,:]
#lllat=np.min(interp_lat)
#urlat=np.max(interp_lat)
#lllon=np.min(interp_lon)
#urlon=np.max(interp_lon)
#for i in range(37):
#    tp=rslt_['T'][i,:,:]
#    print np.sum(rslt['T'][i,:,:]-rslt['T'][i+1,:,:])
#    minv=np.mean(tp[np.isnan(tp)==False])*0.9
#    maxv=np.mean(tp[np.isnan(tp)==False])*1.1
#    plot_data(tp,interp_lat,interp_lon,lllat,urlat,lllon,urlon,minv,maxv,'T_'+str(mod_plevs[i])+' Pa')
#    plt.savefig('T_'+str(mod_plevs[i])+'_Pa.png')
#    plt.close()

