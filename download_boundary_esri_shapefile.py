import geopandas
import os
from tabulate import tabulate

# See TermsAndConditions_ukdataservice_boundary.html for terms and conditions/lisencing for using these datasets

# 2011 output area

shp_eng_2011 = geopandas.read_file(
        'https://borders.ukdataservice.ac.uk/ukborders/easy_download/prebuilt/shape/England_oa_2011.zip'
)
shp_wales_2011 = geopandas.read_file(
        'https://borders.ukdataservice.ac.uk/ukborders/easy_download/prebuilt/shape/Wales_oa_2011.zip'
)

# Append England and Wales shapefiles
shp_2011 = shp_eng_2011.append(shp_wales_2011, ignore_index=True)

# Print head
print("\n\nOA 2011 data:\n")
shp_2011.to_file(os.path.join("boundary_data", "output_area", "EW_output_area_2011.shp"))
shp_2011.drop('geometry', axis=1, inplace=True)
cols = shp_2011.columns.values.tolist()
print(tabulate(shp_2011.head(),
               headers=cols,
               tablefmt='orgtbl', showindex="never"))