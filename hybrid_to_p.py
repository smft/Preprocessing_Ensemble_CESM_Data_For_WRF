def cal_plev(hyam,hybm,p0,ps):
    import numpy as np
    plev=[]
    for i in range(len(hyam)):
        plev+=[hyam[i]*p0+hybm[i]*ps]
    plev+=[ps]
    return np.asarray(plev)
