import os, csv
import numpy as np
import xarray as xr
import shapefile
import shapely

'''
Create a list of VIC grids

'''

path_domain = '/vast/projects/godeeep/VIC/params/namerica_domain.nc' # https://zenodo.org/records/5038653
path_shp, path_dbf = os.path.join('input', 'NHN_Subset_Rev2.shp'), os.path.join('input', 'NHN_Subset_Rev2.dbf')
path_csv_conus = os.path.join('input', 'grid_ids_conus.csv')
path_out = os.path.join('input', 'grid_ids_ca_check.csv')

ds_domain = xr.open_dataset(path_domain)
lats, lons = np.meshgrid(ds_domain['lat'], ds_domain['lon'])
lonlats = np.stack([lons.flatten(), lats.flatten()], axis = 1)

### if a boundary shapefile can be provided
path_shp_bounds = os.path.join('input', 'T2_bounds.shp')
if path_shp_bounds is not None:
    with open(path_shp_bounds, 'rb') as f:
        bounds = shapely.geometry.shape(shapefile.Reader(shp = f).shapes()[0])
        lonlats = lonlats[shapely.contains_xy(bounds, lonlats)]

shp, dbf = open(path_shp, 'rb'), open(path_dbf, 'rb')
shpdbf = shapefile.Reader(shp = shp, dbf = dbf)

with open(path_csv_conus, 'r') as f:
    csv_reader = csv.DictReader(f)
    for row in csv_reader: pass # keep the last row to continue with CONUS

with open(path_out, 'w', newline = '') as f:
    csv_writer = csv.writer(f)
    #csv_writer.writerow(['datasetnam', 'id', 'lon', 'lat'])
    csv_writer.writerow(['huc2', 'id', 'lon', 'lat'])
    idx = int(row['id'])
    for iter in shpdbf.iterShapeRecords():
        if iter.shape.shapeTypeName == 'NULL': continue
        feature = shapely.geometry.shape(iter.shape)
        lonlats_feature = lonlats[shapely.contains_xy(feature, lonlats)]
        for ll in lonlats_feature:
            idx += 1
            #csv_writer.writerow([iter.record['DATASETNAM'], idx, ll[0], ll[1]])
            csv_writer.writerow(['00', idx, ll[0], ll[1]])

shp.close(); dbf.close()