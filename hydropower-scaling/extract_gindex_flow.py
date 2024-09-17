import os, glob, functools
import numpy as np
import pandas as pd
import xarray as xr

# select years to extract flow information
#year = 1981
year = np.arange(1981, 2020).tolist()

# set paths for mosartwmpy outputs
if isinstance(year, int):
    path_mosartwmpy = os.path.join('/vast/projects/godeeep/VIC/mosart/canada/WM', f'WM_{year}*.nc')
    files_mosartwmpy = glob.glob(path_mosartwmpy)
    path_mosartwmpy_CRB = os.path.join('/vast/projects/godeeep/VIC/mosart/output/columbia/', f'columbia_{year}*.nc')
    files_mosartwmpy_CRB = glob.glob(path_mosartwmpy_CRB)
elif isinstance(year, list):
    files_mosartwmpy, files_mosartwmpy_CRB = [], []
    for y in year:
        path_mosartwmpy = os.path.join('/vast/projects/godeeep/VIC/mosart/canada/WM', f'WM_{y}*.nc')
        files_mosartwmpy = files_mosartwmpy + glob.glob(path_mosartwmpy)
    for y in year:
        path_mosartwmpy_CRB = os.path.join('/vast/projects/godeeep/VIC/mosart/output/columbia/', f'columbia_{y}*.nc')
        files_mosartwmpy_CRB = files_mosartwmpy_CRB + glob.glob(path_mosartwmpy_CRB)
files_mosartwmpy.sort()
files_mosartwmpy_CRB.sort()

# read hydropower facility list
path_facility = os.path.join('input', 'CAN_hydropower_facilities.csv')
df_facility = pd.read_csv(path_facility, index_col = 0)

# divide facilities by Canada River Basin and Columbia River Basin
list_CAN = np.unique(df_facility.loc[df_facility['Basin_Note'] != 'CRB', 'GINDEX'])
list_CAN = list_CAN[list_CAN > 0].astype(int).tolist()
list_CRB = np.unique(df_facility.loc[df_facility['Basin_Note'] == 'CRB', 'GINDEX_CONUS'])
list_CRB = list_CRB[list_CRB > 0].astype(int).tolist()

# set up GINDEX lists to load
list_CAN_OK, list_CAN_latlon = list_CAN.copy(), []
ds = xr.open_dataset(files_mosartwmpy[0], decode_coords = 'all')
for p in list_CAN:
    if (ds['GINDEX'] == p).sum() > 0:
        loc = ds['GINDEX'].where(ds['GINDEX'] == p, drop = True).squeeze()
        list_CAN_latlon.append([float(loc['lat']), float(loc['lon'])])
    else: list_CAN_OK.remove(p)

list_CRB_OK, list_CRB_latlon = list_CRB.copy(), []
ds = xr.open_dataset(files_mosartwmpy_CRB[0], decode_coords = 'all')
for p in list_CRB:
    if (ds['GINDEX'] == p).sum() > 0:
        loc = ds['GINDEX'].where(ds['GINDEX'] == p, drop = True).squeeze()
        list_CRB_latlon.append([float(loc['lat']), float(loc['lon'])])
    else: list_CRB_OK.remove(p)

# define a function to preprocess when loading mosartwmpy outputs
def _preprocess(ds, gindex, latlons):
    return ds.sel(lat = xr.DataArray(np.array(latlons)[:, 0], dims = 'gindex', coords = {'gindex': gindex}), lon = xr.DataArray(np.array(latlons)[:, 1], dims = 'gindex', coords = {'gindex': gindex}))

# extract flow information for Canada River Basin
partial_func = functools.partial(_preprocess, gindex = list_CAN_OK, latlons = list_CAN_latlon)
ds_CAN = xr.open_mfdataset(files_mosartwmpy, concat_dim = 'time', combine = 'nested', data_vars = 'minimal', preprocess = partial_func, parallel = True)
ds_CAN = ds_CAN[['GINDEX', 'DSIG', 'channel_inflow', 'channel_outflow', 'WRM_STORAGE']]
ds_CAN.to_netcdf('mosartwmpy_flow_CAN.nc')

df = ds_CAN['channel_inflow'].T.to_series()
df_CAN_inflow = pd.concat([df.droplevel(0) for _, df in df.groupby(level = 0)], axis = 1)
df_CAN_inflow.name = 'channel_inflow'
df_CAN_inflow.columns = list_CAN_OK
df_CAN_inflow.to_csv('mosartwmpy_flow_CAN_inflow.csv')
df = ds_CAN['channel_outflow'].T.to_series()
df_CAN_outflow = pd.concat([df.droplevel(0) for _, df in df.groupby(level = 0)], axis = 1)
df_CAN_outflow.name = 'channel_outflow'
df_CAN_outflow.columns = list_CAN_OK
df_CAN_outflow.to_csv('mosartwmpy_flow_CAN_outflow.csv')
df = ds_CAN['WRM_STORAGE'].T.to_series()
df_CAN_storage = pd.concat([df.droplevel(0) for _, df in df.groupby(level = 0)], axis = 1)
df_CAN_storage.name = 'WRM_STORAGE'
df_CAN_storage.columns = list_CAN_OK
df_CAN_storage.to_csv('mosartwmpy_flow_CAN_storage.csv')

# extract flow information for Columbia River Basin
partial_func = functools.partial(_preprocess, gindex = list_CRB_OK, latlons = list_CRB_latlon)
ds_CRB = xr.open_mfdataset(files_mosartwmpy_CRB, concat_dim = 'time', combine = 'nested', data_vars = 'minimal', preprocess = partial_func, parallel = True)
ds_CRB = ds_CRB[['GINDEX', 'DSIG', 'channel_inflow', 'channel_outflow', 'WRM_STORAGE']]
ds_CRB.to_netcdf('mosartwmpy_flow_CRB.nc')

df = ds_CRB['channel_inflow'].T.to_series()
df_CRB_inflow = pd.concat([df.droplevel(0) for _, df in df.groupby(level = 0)], axis = 1)
df_CRB_inflow.name = 'channel_inflow'
df_CRB_inflow.columns = list_CRB_OK
df_CRB_inflow.to_csv('mosartwmpy_flow_CRB_inflow.csv')
df = ds_CRB['channel_outflow'].T.to_series()
df_CRB_outflow = pd.concat([df.droplevel(0) for _, df in df.groupby(level = 0)], axis = 1)
df_CRB_outflow.name = 'channel_outflow'
df_CRB_outflow.columns = list_CRB_OK
df_CRB_outflow.to_csv('mosartwmpy_flow_CRB_outflow.csv')
df = ds_CRB['WRM_STORAGE'].T.to_series()
df_CRB_storage = pd.concat([df.droplevel(0) for _, df in df.groupby(level = 0)], axis = 1)
df_CRB_storage.name = 'WRM_STORAGE'
df_CRB_storage.columns = list_CRB_OK
df_CRB_storage.to_csv('mosartwmpy_flow_CRB_storage.csv')