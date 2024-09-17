import os
import numpy as np
import pandas as pd
import xarray as xr

# set reference year
year_ref = 2008

# read hydropower facility list
path_facility = os.path.join('input', 'CAN_hydropower_facilities.csv')
df_facility = pd.read_csv(path_facility, index_col = 0)

# read WECC ADS 2032 reference generation
path_WECC = os.path.join('input', 'WECC_ADS_2032_CAN.csv')
df_WECC = pd.read_csv(path_WECC, index_col = 0)

# read flow information for Canada River Basin and Columbia River Basin
ds_CAN = xr.open_dataset('mosartwmpy_flow_CAN.nc', decode_coords = True)
df_CAN_inflow = pd.read_csv('mosartwmpy_flow_CAN_inflow.csv', index_col = 0, parse_dates = True)
df_CAN_outflow = pd.read_csv('mosartwmpy_flow_CAN_outflow.csv', index_col = 0, parse_dates = True)
df_CAN_storage = pd.read_csv('mosartwmpy_flow_CAN_storage.csv', index_col = 0, parse_dates = True)
ds_CRB = xr.open_dataset('mosartwmpy_flow_CRB.nc', decode_coords = True)
df_CRB_inflow = pd.read_csv('mosartwmpy_flow_CRB_inflow.csv', index_col = 0, parse_dates = True)
df_CRB_outflow = pd.read_csv('mosartwmpy_flow_CRB_outflow.csv', index_col = 0, parse_dates = True)
df_CRB_storage = pd.read_csv('mosartwmpy_flow_CRB_storage.csv', index_col = 0, parse_dates = True)

df_CAN_inflow.columns = df_CAN_inflow.columns.astype(int)
df_CAN_outflow.columns = df_CAN_outflow.columns.astype(int)
df_CAN_storage.columns = df_CAN_storage.columns.astype(int)
df_CRB_inflow.columns = df_CRB_inflow.columns.astype(int)
df_CRB_outflow.columns = df_CRB_outflow.columns.astype(int)
df_CRB_storage.columns = df_CRB_storage.columns.astype(int)

# only for reference year
year_dates = pd.date_range(start = pd.Timestamp(year = year_ref, month = 1, day = 1), end = pd.Timestamp(year = year_ref, month = 12, day = 31))
df_CAN_inflow_year = df_CAN_inflow.loc[year_dates]
df_CAN_outflow_year = df_CAN_outflow.loc[year_dates]
df_CRB_inflow_year = df_CRB_inflow.loc[year_dates]
df_CRB_outflow_year = df_CRB_outflow.loc[year_dates]

# assign available streamflow [m^3/s]
df_facility['FlowRef'], df_facility['FlowRef_Cap'] = np.nan, np.nan
for idx, df in df_facility.iterrows():
    if df['Basin_Note'] == 'X': continue    # skip facilities outside of TGW
    if df['WECC_ADS_2032'] == 'X': continue # skip facilities with no reference generation
    
    if df['Basin_Note'] != 'CRB':
        gindex = int(df['GINDEX'])
        dsig = int(ds_CAN['DSIG'].sel(gindex = gindex))
        df_flowref = (df_CAN_outflow_year.loc[:, gindex] * (dsig > -1) + df_CAN_inflow_year.loc[:, gindex] * (dsig == -1)) # outlet cells do not have outflows while headwater cells do not have inflows
    else:
        gindex = int(df['GINDEX_CONUS'])
        dsig = int(ds_CRB['DSIG'].sel(gindex = gindex))
        df_flowref = (df_CRB_outflow_year.loc[:, gindex] * (dsig > -1) + df_CRB_inflow_year.loc[:, gindex] * (dsig == -1)) # outlet cells do not have outflows while headwater cells do not have inflows
    df_facility.loc[idx, 'FlowRef'] = df_flowref.sum(skipna = False) # annual sum

    # constraint due to intake flow rate
    if np.isfinite(df['Intake_Flow_Rate']): df_flowref.loc[df_flowref > df['Intake_Flow_Rate']] = df['Intake_Flow_Rate']
    else: df_flowref.loc[:] = np.nan
    df_facility.loc[idx, 'FlowRef_Cap'] = df_flowref.sum(skipna = False) # annual sum

# calculate scaling factors
df_facility['Flow2Gen'] = df_WECC.loc[df_facility.index, 'SUM_GWh'] * 1000 / df_facility['FlowRef'] # scaling factor [MWh / CMS]
df_facility['Flow2Gen'] = df_facility['Flow2Gen'].replace([np.inf, -np.inf], np.nan)
df_facility['Flow2Gen_Cap'] = df_WECC.loc[df_facility.index, 'SUM_GWh'] * 1000 / df_facility['FlowRef_Cap'] # scaling factor [MWh / CMS]
df_facility['Flow2Gen_Cap'] = df_facility['Flow2Gen_Cap'].replace([np.inf, -np.inf], np.nan)
df_facility.to_csv('CAN_hydropower_facilities_SF.csv')