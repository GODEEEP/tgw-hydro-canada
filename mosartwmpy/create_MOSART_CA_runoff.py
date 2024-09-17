import os, glob, json
import numpy as np
import pandas as pd
import xarray as xr

xr.set_options(keep_attrs = True)

# set a time period to generate MOSART runoff inputs
timespan = [pd.Timestamp('1979-01-01'), pd.Timestamp('2019-12-31')]
resolution_runoff = 1/16 # runoff resolution
resolution_MOSART = 1/8 # target resolution

# set a path for the MOSART domain
path_domain = 'MOSART_CA_8th_20240104_masked.nc'
ds_domain = xr.open_dataset(path_domain, decode_coords = 'all')

# set a path for runoff netcdf files
# read ./[path_vicout]/[list_groups]/**/mod0_calib/[runoff_filename]
path_vicout = '/vast/projects/godeeep/VIC/calibration/00/'
runoff_filename = 'vic_runoff.1979-01-01.nc'
#path_group = 'grid_ids_ca_group.json'
#with open(path_group) as f:
#    groups = json.load(f)

#list_groups = ['05BA000', '05BB000', '05CA000', '08FB002', '08LD000', '08MA001'] # entire group: list(groups.keys())

#files_runoff = []
#for key in list_groups:
#    files_runoff = files_runoff + glob.glob(os.path.join(path_vicout, key, '**', runoff_filename))
files_runoff = glob.glob(os.path.join(path_vicout, '**', runoff_filename))
files_runoff.sort()

# set a path for outputs
path_output = 'MOSART_CA_8th_runoff_1979_2019.nc'

# create lons and lats (runoff: 1/16th degree, MOSART: 1/8th degree)
west, east = ds_domain['lon'].min().values - resolution_MOSART / 2, ds_domain['lon'].max().values + resolution_MOSART / 2
south, north = ds_domain['lat'].min().values - resolution_MOSART / 2, ds_domain['lat'].max().values + resolution_MOSART / 2
lons_runoff = np.arange(west + resolution_runoff / 2, east + resolution_runoff / 2, resolution_runoff)
lats_runoff = np.arange(south + resolution_runoff / 2, north + resolution_runoff / 2, resolution_runoff)
lons_MOSART = ds_domain['lon'].sortby('lon').values
lats_MOSART = ds_domain['lat'].sortby('lat').values

# load the MOSART domain for area-weighted average of runoffs
da_area = ds_domain['area']
da_area_16th = da_area.interp(lon = lons_runoff, lat = lats_runoff) / 4

# load xarray datasets from simulated runoffs
path_temp = '_VIC_runoff_gridded_16th_kge.nc'
# saving temporary file may take a huge space depending on the number of grid cells
if not os.path.isfile(path_temp):
    print('xr.open_mfdataset...')
    ds_runoff = xr.open_mfdataset(files_runoff, chunks = {'time': -1}, decode_coords = 'all', parallel = True)
    print('ds_runoff.where...')
    ds_runoff = ds_runoff.where(ds_runoff['time'] >= timespan[0], drop = True).where(ds_runoff['time'] <= timespan[1], drop = True).load()
    print('ds_runoff.reindex...')
    ds_runoff = ds_runoff.reindex({'lat': lats_runoff, 'lon': lons_runoff})
    ds_runoff.to_netcdf(path_temp)
else: ds_runoff = xr.load_dataset(path_temp)

# coarsen runoff datasets from 1/16th degree into 1/8th degree (area-weighted)
print('ds_runoff.coarsen...')
ds_runoff_coarsen = (ds_runoff.drop_vars('time_bnds') * da_area_16th).coarsen(lat = 2, lon = 2).sum() / da_area

# check if the upscaling (2 times) creates the desired lon and lat
print("check if the coarsen 'lon' is the same to the expected: {}".format(np.array_equal(ds_runoff_coarsen['lon'], lons_MOSART)))
print("check if the coarsen 'lat' is the same to the expected: {}".format(np.array_equal(ds_runoff_coarsen['lat'], lats_MOSART)))

# select only surface runoff and baseflow
drop_vars = list(ds_runoff_coarsen.data_vars)
for var in ['OUT_RUNOFF', 'OUT_BASEFLOW']:
    drop_vars.remove(var)
    ds_runoff_coarsen[var] = ds_runoff_coarsen[var] / (24 * 60 * 60) # conversion from mm/day into mm/s
    ds_runoff_coarsen[var].attrs['units'] = 'mm/s'
ds_runoff_coarsen = ds_runoff_coarsen.drop_vars(drop_vars)

# rename the variable names and generate the MOSART runoff input
print('ds_runoff.to_netcdf...')
ds_runoff_coarsen = ds_runoff_coarsen.rename({'OUT_RUNOFF': 'QOVER', 'OUT_BASEFLOW': 'QDRAI'})
ds_runoff_coarsen.to_netcdf(path_output)