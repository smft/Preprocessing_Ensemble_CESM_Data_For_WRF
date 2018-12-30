def horizontal_interp(var,dim,source_lat,source_lon,source_data,\
                        aim_lat,aim_lon,q,method):
    import ESMF
    import numpy as np
    import matplotlib.pyplot as plt

    ESMF.Manager(debug=False)
    trans_source_lat=source_lat[:,:].copy()
    trans_source_lon=source_lon[:,:].copy()
    trans_aim_lat=aim_lat[:,:].copy()
    trans_aim_lon=aim_lon[:,:].copy()

    source_grid=ESMF.Grid(np.asarray(trans_source_lat.shape),\
                                coord_sys=ESMF.CoordSys.SPH_DEG,\
                                staggerloc=ESMF.StaggerLoc.CENTER)
    source_lat_local=source_grid.get_coords(1)
    source_lon_local=source_grid.get_coords(0)
    source_lat_local[...]=trans_source_lat
    source_lon_local[...]=trans_source_lon
    source_field=ESMF.Field(source_grid,name='source_value')

    aim_grid=ESMF.Grid(np.asarray(trans_aim_lat.shape),\
                                coord_sys=ESMF.CoordSys.SPH_DEG,\
                                staggerloc=ESMF.StaggerLoc.CENTER)
    aim_lat_local=aim_grid.get_coords(1)
    aim_lon_local=aim_grid.get_coords(0)
    aim_lat_local[...]=trans_aim_lat
    aim_lon_local[...]=trans_aim_lon
    aim_field=ESMF.Field(aim_grid,name='aim_value')
    if method=="bilinear":
        regrid=ESMF.Regrid(source_field,aim_field,\
                            regrid_method=ESMF.RegridMethod.BILINEAR,
                            unmapped_action=ESMF.UnmappedAction.IGNORE)
    elif method=="nearest":
        regrid=ESMF.Regrid(source_field,aim_field,\
                            regrid_method=ESMF.RegridMethod.NEAREST_STOD,
                            unmapped_action=ESMF.UnmappedAction.IGNORE)
    
    if dim==3:
        nz,ny,nx=np.shape(source_data)
        ny,nx=np.shape(aim_lon_local)
        target_data=np.zeros([nz,ny,nx])
        for i,cell in enumerate(source_data):
            source_field.data[...]=source_data[i].copy()
            target_data[i,:,:]+=regrid(source_field,aim_field).data
    else:
        ny,nx=np.shape(aim_lon_local)
        target_data=np.zeros([ny,nx])
        source_field.data[...]=source_data.copy()
        target_data[:,:]+=regrid(source_field,aim_field).data
    q.put([var,target_data])

