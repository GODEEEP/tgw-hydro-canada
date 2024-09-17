import os, glob
import numpy as np
import pandas as pd
import xarray as xr

domain_path = 'MOSART_CA_8th_20240104_masked.nc'
ds_domain = xr.open_dataset(domain_path)
df_domain = ds_domain['ID'].to_dataframe().reset_index() # GINDEX, lat, lon, ID

flow_path = '/vast/projects/godeeep/VIC/mosart/canada/noWM_*.nc'
flow_glob = glob.glob(flow_path); flow_glob.sort()
da_flow = xr.open_mfdataset(flow_glob[:3], combine = 'nested', concat_dim = 'time', parallel = True)['RIVER_DISCHARGE_OVER_LAND_LIQ']

res_file = pd.read_csv('mapped_GRanD_on_grids.csv')

# rename grid cell index column
res_file = res_file.rename(columns={'GINDEX': 'GRID_CELL_INDEX'})

da_flow_mean = da_flow.resample(time = 'MS').mean()

# remove months if not complete
check_month_first = da_flow['time'].resample(time = 'MS').nearest().isel(time = 0)
check_month_last = da_flow['time'].resample(time = 'ME').nearest().isel(time = -1)
if check_month_first != check_month_first['time']: da_flow_mean = da_flow_mean.sel(time = da_flow_mean['time'][1:])
if check_month_last != check_month_last['time']: da_flow_mean = da_flow_mean.sel(time = da_flow_mean['time'][:-1])

arr_flow_mean = []
for i in res_file['GRAND_ID']:
    gci = int(res_file.loc[res_file['GRAND_ID'] == i, 'GRID_CELL_INDEX'].iloc[0])
    arr_flow_mean = arr_flow_mean + da_flow_mean.sel(lon = df_domain.loc[gci, 'lon'], lat = df_domain.loc[gci, 'lat']).groupby('time.month').mean().values.tolist()

# create actual monthly flow file
flow_mon = pd.DataFrame(columns=['GRAND_ID', 'MONTH_INDEX', 'MEAN_FLOW'])
flow_mon.GRAND_ID = np.repeat(res_file['GRAND_ID'], 12)
flow_mon.MONTH_INDEX = np.tile(np.arange(0, 12), len(res_file))
flow_mon.MEAN_FLOW = arr_flow_mean
flow_mon.to_parquet('MOSART_CA_8th_reservoir_flow_monthly_mean.parquet')