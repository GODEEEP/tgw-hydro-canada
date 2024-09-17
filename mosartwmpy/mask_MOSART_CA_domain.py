import os
import numpy as np
import pandas as pd
import xarray as xr

xr.set_options(keep_attrs = True)

path_csv = os.path.join('input', 'grids_ca_attr_basinmasked.csv')
path_domain = 'MOSART_CA_8th_20240104.nc'

df = pd.read_csv(os.path.join('..', '..', 'QGIS', path_csv))
df_lonlat = np.stack([df['lon'], df['lat']], axis = 1)

ds = xr.open_dataset(path_domain, decode_coords = 'all')
ds_lon, ds_lat = np.meshgrid(ds['lon'], ds['lat'])
ds_lonlat_flat = np.stack([ds_lon.flatten(), ds_lat.flatten()], axis = 1)

mask = np.full(ds_lonlat_flat.shape[0], False)
for i, ll in enumerate(ds_lonlat_flat):
    if not (ll == df_lonlat[:, None]).all(axis = -1).any(): mask[i] = True

da = xr.DataArray(mask.reshape(ds_lon.shape), coords = {'lat': ds['lat'], 'lon': ds['lon']})

ds['frac'] = ds['frac'].where(~da)
ds['land_frac'] = ds['land_frac'].where(~da)

ds.to_netcdf(path_domain.replace('.nc', '_masked.nc'))