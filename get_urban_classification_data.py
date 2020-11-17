import geopandas
import pandas as pd

# Read in shapefiles

url = 'https://borders.ukdataservice.ac.uk/ukborders/easy_download/prebuilt/shape/England_oa_ru_classn_2011.zip'
england = geopandas.read_file(url)

url = 'https://borders.ukdataservice.ac.uk/ukborders/easy_download/prebuilt/shape/Wales_oa_ru_classn_2011.zip'
wales = geopandas.read_file(url)

shpdata = pd.concat([england, wales], axis=0)
shpdata.drop(["assign_chr", "assign_chg", "bound_chgi", "ruc11cd", "name", "label"], axis=1, inplace=True)

# read in geocoded data
geo_data = pd.read_csv("data/TEDS_geocoded_2008_postcodes.csv")
geo_data = geo_data[(geo_data.eastings != "Postcode not found") & (geo_data.eastings != "Invalid postcode")]
geo_data.dropna(inplace=True)

# Brittish national grid (BNG) co-ordinate reference system (CRS)
bng = {'init': 'epsg:27700'}

# Change CRS if necessary
if shpdata.crs != bng:
    shp = shpdata.to_crs(bng)

# Create GeoDataFrame from co-ordinates in data
data = geopandas.GeoDataFrame(
    geo_data, geometry=geopandas.points_from_xy(geo_data.eastings.astype(int), geo_data.northings.astype(int)),
    crs=bng
)

# Spatial join data with shapefile
data = geopandas.sjoin(data, shpdata, how="inner", op='within')
data.drop(['code', 'index_right', 'geometry', 'country', 'northings', 'eastings', 'postcode', 'year'],
          axis=1, inplace=True)

# Write data
data.to_csv("data/TEDS_OA_urban_classification_data.csv.gz", index=False, compression='gzip')
