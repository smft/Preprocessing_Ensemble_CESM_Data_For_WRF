def get_latlon(aim_file):
    import numpy as np
    from netCDF4 import Dataset

    flag_aim=Dataset(aim_file)
    aim_lat=flag_aim.variables['XLAT_M'][0,:,:]
    aim_lon=flag_aim.variables['XLONG_M'][0,:,:]
    aim_lat_u=flag_aim.variables['XLAT_U'][0,:,:]
    aim_lon_u=flag_aim.variables['XLONG_U'][0,:,:]
    aim_lat_v=flag_aim.variables['XLAT_V'][0,:,:]
    aim_lon_v=flag_aim.variables['XLONG_V'][0,:,:]
    return {'lat_m':aim_lat,'lat_u':aim_lat_u,'lat_v':aim_lat_v,\
            'lon_m':aim_lon,'lon_u':aim_lon_u,'lon_v':aim_lon_v}
