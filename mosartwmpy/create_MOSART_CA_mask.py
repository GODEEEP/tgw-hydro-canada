import os
import numpy as np
import pandas as pd
import xarray as xr

xr.set_options(keep_attrs = True)

ds = xr.open_dataset(os.path.join('input', 'runoff_eval_1981-2000.nc')) # daily
da_mask = np.isfinite(ds['KGE'].where(ds['lon'] <= -120).where(ds['lat'] >= 52.5).where(ds['KGE'] < -3)) # remove the unrealistic KGE bands (< -5) along the TGW forcing boundary
# remove one more consistent KGE band (< 0) along the boundary
for lon in da_mask['lon']:
    if np.any(da_mask.sel(lon = lon)):
        lat = da_mask['lat'][da_mask.sel(lon = lon).argmax() - 1]
        if ds['KGE'].sel(lon = lon, lat = lat) < 0: da_mask.loc[{'lon': lon, 'lat': lat}] = True

# remove minor edge grid cells with KGE < -1 along the boundary
#for lon in da_mask['lon']:
#    if np.any(da_mask.sel(lon = lon)):
#        lat = da_mask['lat'][da_mask.sel(lon = lon).argmax() - 1]
#        if ds['KGE'].sel(lon = lon, lat = lat) < -1: da_mask.loc[{'lon': lon, 'lat': lat}] = True

# update mosartwmpy runoff input file
ds_runoff = xr.open_dataset('MOSART_CA_8th_runoff_1979_2019.nc')
da_mask_coarsen = da_mask.coarsen(lat = 2, lon = 2).sum() > 0
da_mask_coarsen = da_mask_coarsen.reindex_like(ds_runoff).fillna(False).astype(bool)
#da_mask_coarsen.to_netcdf('runoff_mask_on_mosartwmpy.nc')

ds_runoff_update = ds_runoff.copy()
for t in ds_runoff['time']:
    ds_runoff_update['QOVER'].loc[{'time': t}] = ds_runoff['QOVER'].sel(time = t) * (1 - da_mask_coarsen.astype(float))
    ds_runoff_update['QDRAI'].loc[{'time': t}] = ds_runoff['QDRAI'].sel(time = t) * (1 - da_mask_coarsen.astype(float))
    print(pd.Timestamp(t.values).strftime('%Y-%m-%d'))
ds_runoff_update.to_netcdf('MOSART_CA_8th_runoff_1979_2019_masked.nc')