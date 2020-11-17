import pandas as pd
import numpy as np

# Download data on 'AADF Data - major and minor roads' from https://roadtraffic.dft.gov.uk/downloads

# read traffic data
road_data = pd.read_csv("traffic_data/dft_traffic_counts_aadf.csv")

# select 2008 data and columns in traffic data
road_data = road_data[['year', 'local_authority_name', 'road_name', 'road_category',
                       'road_type', 'easting', 'northing', 'link_length_km', 'estimation_method',
                       'all_motor_vehicles']]
road_data = road_data[road_data.year == 2008]
road_data.road_type.value_counts()

# read in geocoded data
geo_data = pd.read_csv("data/TEDS_geocoded_2008_postcodes.csv")
geo_data = geo_data[(geo_data.eastings != "Postcode not found") & (geo_data.eastings != "Invalid postcode")]
geo_data.dropna(inplace=True)

# find major/minor road nearest to postcode
nearest_road = []
for index, id_twin, easting, northing in geo_data[['id_twin', 'eastings', 'northings']].itertuples():
    east = ((np.array(road_data["easting"]) - int(easting)) ** 2)
    north = ((np.array(road_data["northing"]) - int(northing)) ** 2)
    road_data["distance"] = np.sqrt(east + north) / 1000
    row = road_data[road_data.distance == road_data.distance.min()].values.tolist()[0]
    row = [id_twin] + row
    nearest_road.append(np.array(row))

data = pd.DataFrame(nearest_road)
data.columns = ['id_twin'] + road_data.columns.tolist()
data.drop(['local_authority_name', 'year', 'easting', 'northing'], axis=1, inplace=True)

# write data
data.to_csv("data/TEDS_traffic_data.csv.gz", index=False, compression='gzip')
