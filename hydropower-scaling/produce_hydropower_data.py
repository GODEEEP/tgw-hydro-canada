import os
import numpy as np
import pandas as pd
import xarray as xr

# facility to apply monthly generation profiles directly
facility_profile = [
    'Arrow Lakes',
    'Mica',
    'Revelstoke',
]
os.chdir('hydropower-scaling')
# read hydropower facility list with scaling factors
path_facility = 'CAN_hydropower_facilities&scaling.csv'
df_facility = pd.read_csv(path_facility, index_col = 0)

# read WECC ADS 2032 reference generation
path_WECC = os.path.join('input', 'WECC_ADS_2032_CAN.csv')
df_WECC = pd.read_csv(path_WECC, index_col = 0)

col_months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

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

# read PNW parameters to derive p_avg, p_max, p_min, p_ador
df_mma_params_mode = pd.read_csv(os.path.join('input', 'PNW_28_max_min_ador_parameters_mode.csv'), index_col = 0)
df_mma_params_general = df_mma_params_mode.groupby('mode').mean().drop(columns = 'EIA_ID')

# scale monthly hydropower generation
date_min, date_max = df_CAN_inflow.index[0], df_CAN_inflow.index[-1]
arr_gen_cap_mprf = []
arr_p_avg, arr_p_max, arr_p_min, arr_p_ador = [], [], [], []
for idx, df in df_facility.iterrows():
    if df['Basin_Note'] == 'X': continue    # skip facilities outside of TGW
    if df['WECC_ADS_2032'] == 'X': continue # skip facilities with no reference generation

    if df['Basin_Note'] != 'CRB':
        gindex = int(df['GINDEX'])
        dsig = int(ds_CAN['DSIG'].sel(gindex = gindex))
        df_flowref = df_CAN_outflow.loc[date_min:date_max, gindex] * (dsig > -1) + df_CAN_inflow.loc[date_min:date_max, gindex] * (dsig == -1) # outlet cells do not have outflows while headwater cells do not have inflows
    else:
        gindex = int(df['GINDEX_CONUS'])
        dsig = int(ds_CRB['DSIG'].sel(gindex = gindex))
        df_flowref = df_CRB_outflow.loc[date_min:date_max, gindex] * (dsig > -1) + df_CRB_inflow.loc[date_min:date_max, gindex] * (dsig == -1) # outlet cells do not have outflows while headwater cells do not have inflows
    
    df_gen = df_flowref.resample('MS').sum() * df['Scaling'] # generation [MWh]
    df_gen.name = df['Facility']

    # calculate maximum generation by nameplate capacity
    df_maxgen = df_gen.copy()
    #df_maxgen.loc[:] = df['Hydro_MW'] * 24 * df_maxgen.index.days_in_month.values
    df_maxgen.loc[:] = df_WECC.loc[idx, 'MaxCap'] * 24 * df_maxgen.index.days_in_month.values # based on WECC ADS 2032
    
    # constraint due to intake flow rate
    df_flowref_cap = df_flowref.copy()
    if np.isfinite(df['Intake_Flow_Rate']):
        df_flowref_cap.loc[df_flowref_cap > df['Intake_Flow_Rate']] = df['Intake_Flow_Rate']
        df_gen_cap = df_flowref_cap.resample('MS').sum() * df['Scaling_IntakeCap'] # Generation [MWh]
    #else: df_gen_cap = df_gen * np.nan
    else: df_gen_cap = df_gen.copy()
    df_gen_cap.name = df['Facility']

    # apply monthly generation profile directly
    if df['Facility'] in facility_profile:
        df_mprf = df_WECC.loc[idx, col_months].astype(float)
        df_mprf = df_mprf / df_mprf.sum()
        df_gen_cap_mprf = df_gen_cap.resample('YS').agg(pd.Series.sum, skipna = False).reindex(df_gen_cap.index, method = 'ffill') * df_mprf.iloc[df_gen_cap.index.month - 1].to_numpy()
    else: df_gen_cap_mprf = df_gen_cap.copy()
    
    # constraint due to nameplate capacity
    df_gen_cap_mprf = df_gen_cap_mprf.where(df_gen_cap_mprf < df_maxgen, df_maxgen)
    arr_gen_cap_mprf.append(df_gen_cap_mprf)

    # derive p_avg, p_max, p_min, p_ador
    if np.isfinite(df['Intake_Flow_Rate']): df_p_avg = df_flowref_cap.resample('MS').mean() * df['Scaling_IntakeCap'] / 24 # power [MW]
    else: df_p_avg = df_flowref_cap.resample('MS').mean() * df['Scaling'] / 24 # power [MW]
    df_p_avg = df_p_avg.where(df_p_avg < df_WECC.loc[idx, 'MaxCap'], df_WECC.loc[idx, 'MaxCap'])
    df_p_avg.name = df['Facility']

    if 'run-of-river' in df['Type']: mode = 'RoR'
    else: mode = 'Storage'

    df_p_max = df_p_avg + df_mma_params_general.loc[mode, 'max_param'] * (df_WECC.loc[idx, 'MaxCap'] - df_p_avg)
    df_p_min = df_mma_params_general.loc[mode, 'min_param'] * df_p_avg
    df_p_ador = df_mma_params_general.loc[mode, 'ador_param'] * (df_p_max - df_p_min)
    df_p_max.name, df_p_min.name, df_p_ador.name = df['Facility'], df['Facility'], df['Facility']

    arr_p_avg.append(df_p_avg)
    arr_p_max.append(df_p_max)
    arr_p_min.append(df_p_min)
    arr_p_ador.append(df_p_ador)

# export
df_mosartwmpy_gen_cap_mprf = pd.concat(arr_gen_cap_mprf, axis = 1)
df_mosartwmpy_gen_cap_mprf.index = df_mosartwmpy_gen_cap_mprf.index.strftime('%Y-%m')
df_mosartwmpy_gen_cap_mprf.index.name = 'Year-Month'
df_mosartwmpy_gen_cap_mprf.to_csv('CAN_hydropower_monthly_generation_MWh.csv')

df_mosartwmpy_p_avg_cap_mprf = pd.concat(arr_p_avg, axis = 1)
df_mosartwmpy_p_max_cap_mprf = pd.concat(arr_p_max, axis = 1)
df_mosartwmpy_p_min_cap_mprf = pd.concat(arr_p_min, axis = 1)
df_mosartwmpy_p_ador_cap_mprf = pd.concat(arr_p_ador, axis = 1)
#df_mosartwmpy_p_avg_cap_mprf.index = df_mosartwmpy_p_avg_cap_mprf.index.strftime('%Y-%m')
df_mosartwmpy_p_max_cap_mprf.index = df_mosartwmpy_p_max_cap_mprf.index.strftime('%Y-%m')
df_mosartwmpy_p_min_cap_mprf.index = df_mosartwmpy_p_min_cap_mprf.index.strftime('%Y-%m')
df_mosartwmpy_p_ador_cap_mprf.index = df_mosartwmpy_p_ador_cap_mprf.index.strftime('%Y-%m')
#df_mosartwmpy_p_avg_cap_mprf.index.name = 'Year-Month'
df_mosartwmpy_p_max_cap_mprf.index.name = 'Year-Month'
df_mosartwmpy_p_min_cap_mprf.index.name = 'Year-Month'
df_mosartwmpy_p_ador_cap_mprf.index.name = 'Year-Month'
#df_mosartwmpy_p_avg_cap_mprf.to_csv('CAN_hydropower_monthly_p_avg_MW.csv')
df_mosartwmpy_p_max_cap_mprf.to_csv('CAN_hydropower_monthly_p_max_MW.csv')
df_mosartwmpy_p_min_cap_mprf.to_csv('CAN_hydropower_monthly_p_min_MW.csv')
df_mosartwmpy_p_ador_cap_mprf.to_csv('CAN_hydropower_monthly_p_ador_MW.csv')