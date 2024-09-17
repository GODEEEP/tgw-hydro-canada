import os
import numpy as np
import xarray as xr

xr.set_options(keep_attrs = True)

# set path for domain netcdf files and load xarray datasets
path_MOSART_sample = os.path.join('ref', 'mosartwmpy_sample_input_data_1980_1985', 'domains', 'mosart_conus_nldas_grid.nc')
path_MOSART_GLOBAL = os.path.join('input', 'MOSART_global_8th_20180211b_elevation.nc')
path_HyMAP_GLOBAL = os.path.join('input', 'HyMAP_parms_bin_GLOBAL.nc')
ds_MOSART_sample = xr.open_dataset(path_MOSART_sample, decode_coords = 'all')
ds_MOSART_GLOBAL = xr.open_dataset(path_MOSART_GLOBAL, decode_coords = 'all')
ds_HyMAP_GLOBAL = xr.open_dataset(path_HyMAP_GLOBAL, decode_coords = 'all')

resolution = 1/8 # target resolution
bounds = [-142, 47, -98, 62] # Canada

# target lon and lat
lons = np.arange(bounds[0] + resolution / 2, bounds[2] + resolution / 2, resolution)
lats = np.arange(bounds[1] + resolution / 2, bounds[3] + resolution / 2, resolution)

# replace redundant dimensions with lon and lat
ds_MOSART_GLOBAL = ds_MOSART_GLOBAL.rename({'ncl2': 'lat', 'ncl3': 'lon', 'ncl4': 'lat', 'ncl5': 'lon', 'ncl6': 'lat', 'ncl7': 'lon'})
# select if the resolusion is 1/8 or interpolate otherwise
ds_MOSART_GLOBAL_sel = ds_MOSART_GLOBAL.sel(lon = lons, lat = lats) # 1/8th degree resolution
ds_HyMAP_GLOBAL_interp = ds_HyMAP_GLOBAL.interp(lon = lons, lat = lats, method = 'linear') # 1/4th degree resolution

# assign dictionary to create a xarray dataset
dict_ds = {
    'area': ds_MOSART_GLOBAL_sel['area'],
    'areaTotal': ds_MOSART_GLOBAL_sel['areaTotal'],
    'areaTotal2': ds_MOSART_GLOBAL_sel['areaTotal2'],
    'dnID': ds_MOSART_GLOBAL_sel['dnID'].fillna(-9999).astype(int),
    'fdir': ds_MOSART_GLOBAL_sel['fdir'].fillna(-9999).astype(int),
    'frac': ds_MOSART_GLOBAL_sel['frac'],
    'gxr': ds_MOSART_GLOBAL_sel['gxr'],
    'hslp': ds_MOSART_GLOBAL_sel['hslp'],
    'ID': ds_MOSART_GLOBAL_sel['ID'].fillna(-9999).astype(int),
    'nh': ds_HyMAP_GLOBAL_interp['fldman'],
    'nr': ds_HyMAP_GLOBAL_interp['rivman'], ### 24 grids <= 0
    'nt': ds_HyMAP_GLOBAL_interp['rivman'], ### 24 grids <= 0
    'rdep': ds_HyMAP_GLOBAL_interp['rivhgt'], ### 24 grids <= 0
    'rwid': ds_HyMAP_GLOBAL_interp['rivwth'], ### 24 grids <= 0
    'rwid0': 5 * ds_HyMAP_GLOBAL_interp['rivwth'], ### 24 grids <= 0
    'rlen': ds_MOSART_GLOBAL_sel['rlen'],
    'rslp': ds_MOSART_GLOBAL_sel['rslp'],
    'tslp': ds_MOSART_GLOBAL_sel['tslp'],
    'twid': 5 * ds_HyMAP_GLOBAL_interp['rivwth'], ### 24 grids <= 0
}

# create a xarray dataset
ds = xr.Dataset(dict_ds, coords = {'lat': lats, 'lon': lons})

# add 'NLDAS_ID' variable, e.g. x1y1 in a string format
x, y = np.meshgrid(np.arange(len(lons)), np.arange(len(lats)))
NLDAS_ID = np.char.add(np.char.add('x', (1 + x).astype(str)), np.char.add('y', (1 + y).astype(str)))
NLDAS_ID = NLDAS_ID.astype('<U8')
ds['NLDAS_ID'] = xr.DataArray(data = NLDAS_ID, dims = ['lat', 'lon'], coords = {'lat': lats, 'lon': lons})

# add 'land_frac' variable, assuming 0.5 for the land-ocean boundaries based on 'fdir' variable
edge = ds['fdir'].values >= 0
rollxp = np.roll(ds['fdir'], 1, axis = 0); rollxp[0, :] = rollxp[1, :] # rolling in +x direction and padding
rollxn = np.roll(ds['fdir'], -1, axis = 0); rollxn[-1, :] = rollxn[-2, :] # rolling in -x direction and padding
rollyp = np.roll(ds['fdir'], 1, axis = 1); rollyp[:, 0] = rollyp[:, 1] # rolling in +y direction and padding
rollyn = np.roll(ds['fdir'], -1, axis = 1); rollyn[:, -1] = rollyn[:, -2] # rolling in -y direction and padding
edge = edge & (np.isnan(rollxp) | np.isnan(rollxn) | np.isnan(rollyp) | np.isnan(rollyn)) # set True if any direction has nan
land_frac = (ds['fdir'].values >= 0) - edge * 0.5
ds['land_frac'] = xr.DataArray(data = land_frac, dims = ['lat', 'lon'], coords = {'lat': lats, 'lon': lons})

# replace 'dnID' if it is not in 'ID'
ds['dnID'] = ds['dnID'].where(np.isin(ds['dnID'], ds['ID']), -9999)

# set the 'frac' variable only for valid grids
for var in ds.data_vars:
    if var in ['dnID', 'ID', 'NLDAS_ID']: continue
    if var in ['fdir', 'hslp', 'rslp', 'tslp']: ds['frac'] = ds['frac'] + ds[var].where(ds[var] >= 0, np.nan) * 0
    else: ds['frac'] = ds['frac'] + ds[var].where(ds[var] > 0, np.nan) * 0

# make nan values consistent throughout the variables
for var in ds.data_vars:
    if var in ['dnID', 'ID', 'NLDAS_ID']: continue
    elif ds[var].dtype == float: ds[var] = ds[var].where(np.isfinite(ds['frac']), np.nan)
    elif ds[var].dtype == int: ds[var] = ds[var].where(np.isfinite(ds['frac']), -9999)
    else: print(var)

# set attributes for each variable
ds['area'].attrs = {
    'long_name': 'local drainage area',
    'units': 'm^2',
    '_FillValue': np.nan,
}
ds['areaTotal'].attrs = {
    'long_name': 'total upstream drainage area, local unit included; using concept of multi flow direction',
    'units': 'm^2',
    '_FillValue': np.nan,
}
ds['areaTotal2'].attrs = {
    'long_name': 'total upstream drainage area, local unit included; using concept of single flow direction',
    'units': 'm^2',
    '_FillValue': np.nan,
}
ds['dnID'].attrs = {
    'long_name': 'downstream ID',
    'units': 'unitless',
}
ds['fdir'].attrs = {
    'long_name': 'flow direction based on D8 algorithm',
    'units': 'unitless',
    '_FillValue': -9999,
}
ds['frac'].attrs = {
    'long_name': 'fraction of the unit draining to the outlet',
    'units': 'unitless',
    '_FillValue': np.nan,
}
ds['gxr'].attrs = {
    'long_name': 'drainage density',
    'units': 'm^-1',
    '_FillValue': np.nan,
}
ds['hslp'].attrs = {
    'long_name': 'topographic slope',
    'units': 'unitless',
    '_FillValue': np.nan,
}
ds['ID'].attrs = {
    'long_name': 'ID',
    'units': 'unitless',
}
ds['land_frac'].attrs = {
    'long_name': 'fraction of grid cell that is active',
    'units': 'unitless',
    '_FillValue': np.nan,
}
ds['lat'].attrs = {
    'long_name': 'latitude',
    'units': 'degrees north',
    '_FillValue': np.nan,
}
ds['lon'].attrs = {
    'long_name': 'longitude',
    'units': 'degrees east',
    '_FillValue': np.nan,
}
ds['nh'].attrs = {
    'long_name': 'Manning\'s roughness coefficient for overland flow',
    'units': 'unitless',
    '_FillValue': np.nan,
}
ds['NLDAS_ID'].attrs = {
    'long_name': 'NLDAS ID',
    'units': 'unitless',
}
ds['nr'].attrs = {
    'long_name': 'Manning\'s roughness coefficient for main channel flow',
    'units': 'unitless',
    '_FillValue': np.nan,
}
ds['nt'].attrs = {
    'long_name': 'Manning\'s roughness coefficient for tributary channel flow',
    'units': 'unitless',
    '_FillValue': np.nan,
}
ds['rdep'].attrs = {
    'long_name': 'bankfull depth of main channel',
    'units': 'm',
    '_FillValue': np.nan,
}
ds['rlen'].attrs = {
    'long_name': 'main channel length',
    'units': 'm',
    '_FillValue': np.nan,
}
ds['rslp'].attrs = {
    'long_name': 'main channel slope',
    'units': 'unitless',
    '_FillValue': np.nan,
}
ds['rwid'].attrs = {
    'long_name': 'bankfull width of main channel',
    'units': 'm',
    '_FillValue': np.nan,
}
ds['rwid0'].attrs = {
    'long_name': 'floodplain width linked to main channel',
    'units': 'm',
    '_FillValue': np.nan,
}
ds['tslp'].attrs = {
    'long_name': 'mean tributary channel slope averaged through the unit',
    'units': 'unitless',
    '_FillValue': np.nan,
}
ds['twid'].attrs = {
    'long_name': 'bankfull width of local tributaries',
    'units': 'm',
    '_FillValue': np.nan,
}

# save to netcdf
ds.to_netcdf('MOSART_CA_8th_20240104.nc')