def vertical_interp_module(source_data,source_ps,source_p0,\
                            source_hyai,source_hybi,mod_plevs,\
                            nys,nxs,rslt,processlock):
    from hybrid_to_p import cal_plev
    from scipy import interpolate
    import numpy as np
    import warnings
    warnings.simplefilter("ignore")
    for i in nys:
        for j in nxs:
            source_plev=(cal_plev(source_hyai,source_hybi,source_p0,source_ps[i,j]))
            f=interpolate.interp1d(source_plev,source_data[:,i,j],kind='linear',\
                                    bounds_error=False,fill_value="extrapolate")
            trans=f(mod_plevs[::-1])
            rslt[:,i,j]+=trans
    processlock.release()
