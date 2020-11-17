import rasterio
import pandas as pd
import geopandas

# Download data on land cover 2007 from centre of ecology and hydrology (CEH)

# read in geocoded data
geo_data = pd.read_csv("data/TEDS_geocoded_2008_postcodes.csv")
geo_data = geo_data[(geo_data.eastings != "Postcode not found") & (geo_data.eastings != "Invalid postcode")]
geo_data.dropna(inplace=True)

# Get coords
coords = [(x, y) for x, y in zip(geo_data.eastings.astype(int), geo_data.northings.astype(int))]

# read in each raster image and get values for target classes
for n in range(1, 24):
    src = rasterio.open("land_cover_data/lcm-2007-1km_3755987/percentage_target_class/LCM2007_GB_1K_PC_TargetClass_" +
                        str(n) + ".tif")
    geo_data['LCM_TargetClass_' + str(n)] = [x[0] for x in src.sample(coords)]

# read in each raster image and get values for aggregate classes
for n in range(1, 11):
    src = rasterio.open("land_cover_data/lcm-2007-1km_3755987/percentage_aggregate_class/LCM2007_GB_1K_PC_AggregateClass_"
                        + str(n) + ".tif")
    geo_data['LCM_AggregateClass_' + str(n)] = [x[0] for x in src.sample(coords)]

# write data
geo_data.drop(['year', 'postcode', 'eastings', 'northings', 'country'], axis=1, inplace=True)
geo_data.to_csv("data/TEDS_land_cover_data.csv.gz", index=False, compression='gzip')
