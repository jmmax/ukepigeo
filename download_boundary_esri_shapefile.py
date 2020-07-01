import geopandas
import os
from tabulate import tabulate

# See TermsAndConditions_ukdataservice_boundary.html for terms and conditions/lisencing for using these datasets

# 2001 LSOA

shp_eng_2001 = geopandas.read_file(
        'https://borders.ukdataservice.ac.uk/ukborders/easy_download/prebuilt/shape/England_low_soa_2001.zip'
)
shp_wales_2001 = geopandas.read_file(
        'https://borders.ukdataservice.ac.uk/ukborders/easy_download/prebuilt/shape/Wales_low_soa_2001.zip'
)

# Append England and Wales shapefiles
shp_2001 = shp_eng_2001.append(shp_wales_2001, ignore_index=True)

# Print head
shp_2001.to_file(os.path.join("boundary_data", "LSOA", "EW_LSOA_2001.shp"))
print("\n\nLSOA 2001:\n")
shp_2001.drop('geometry', axis=1, inplace=True)
cols = shp_2001.columns.values.tolist()
print(tabulate(shp_2001.head(),
               headers=cols,
               tablefmt='orgtbl', showindex="never"))


# 2011 LSOA

shp_eng_2011 = geopandas.read_file(
        'https://borders.ukdataservice.ac.uk/ukborders/easy_download/prebuilt/shape/England_lsoa_2011.zip'
)
shp_wales_2011 = geopandas.read_file(
        'https://borders.ukdataservice.ac.uk/ukborders/easy_download/prebuilt/shape/Wales_lsoa_2011.zip'
)

# Append England and Wales shapefiles
shp_2011 = shp_eng_2011.append(shp_wales_2011, ignore_index=True)

# Print head
print("\n\nLSOA 2011 data:\n")
shp_2011.to_file(os.path.join("boundary_data", "LSOA", "EW_LSOA_2011.shp"))
shp_2011.drop('geometry', axis=1, inplace=True)
cols = shp_2011.columns.values.tolist()
print(tabulate(shp_2011.head(),
               headers=cols,
               tablefmt='orgtbl', showindex="never"))