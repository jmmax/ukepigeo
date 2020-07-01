import sys
import argparse
import pandas as pd
import nomiswebAPI
from geoutils import request_url_to_dataframe
import geopandas
import os
import re


def main():

    # Initiate parser and add arguments
    parser = argparse.ArgumentParser(
        description="Python program for querying nomisweb API (https://www.nomisweb.co.uk/) for census data."
                    "Links geocoded data with any data from the 2010 and 2011 census in LSOA geographic level."
                    "Only includes census data for England and Wales. To find out more about census data available for"
                    " 2010 and 2011 go to https://www.nomisweb.co.uk/query/select/getdatasetbytheme.asp"
    )
    parser.add_argument("--geocodedata", "-f", help="Input file with participant IDs, year and geographical "
                                                    "co-ordinates in eastings/northings (epsg:27700).")
    parser.add_argument("--idcol", "-i", help="Column name for participant IDs.")
    parser.add_argument("--outputfile", "-o", help="Output filename.")
    parser.add_argument("--variables_csv", "-c", help="CSV file with info on census data to download."
                                                      "Must have the format: VARIABLE (name of census variable),"
                                                      "CENSUS_YEAR (2001 or 2011) and CENSUS_VAR_CODE "
                                                      "(code selected from "
                                                      "https://www.nomisweb.co.uk/query/select/getdatasetbytheme.asp)",
                        default=False)
    parser.add_argument("--apikey", "-k", help="API key obtained after registering on https://www.nomisweb.co.uk/.",
                        default=None)

    # Read arguments from command line
    args = parser.parse_args()

    if not args.apikey:
        sys.exit("Error: must include '--apikey':"
                 " API key obtained when registering at https://www.nomisweb.co.uk,\n"
                 "and then navigating to https://www.nomisweb.co.uk/myaccount/webservice.asp.")

    NOMIS_API_KEY = args.apikey

    # Read in geocoded data
    print("Reading geocoded data...")
    typedict = {args.idcol: str}
    data = pd.read_csv(args.geocodedata,
                       na_values=['Postcode not found', 'Invalid postcode'],
                       dtype=typedict)
    print("Done.")


    # Link data with 2001 and 2011 LSOA geography
    print("\nLinking geocoded data with 2001 and 2011 LSOA"
          " boundary shapefiles from https://census.ukdataservice.ac.uk/get-data/boundary-data.aspx...")
    data = link_geocode_with_LSOA(data, os.path.join("boundary_data", "LSOA", "EW_LSOA_2001.shp"))
    data = data[[args.idcol, 'eastings', 'northings', 'year', 'zonecode']]
    data.rename(columns={'zonecode': 'LSOA_2001'}, inplace=True)
    data = link_geocode_with_LSOA(data, os.path.join("boundary_data", "LSOA", "EW_LSOA_2011.shp"))
    data = data[[args.idcol, 'year', 'LSOA_2001', 'code']]
    data.rename(columns={'code': 'LSOA_2011'}, inplace=True)
    print("Done.\n")

    # Read in info on which census data to download
    variables = pd.read_csv(args.variables_csv)

    # Initalise nomisAPI class
    nom = nomiswebAPI.NomisAPI(args.apikey)

    # Loop through variables and write
    for index, year, code in variables[['CENSUS_YEAR', 'CENSUS_VAR_CODE']].itertuples():
        mergecol = "LSOA_" + str(year)
        # Download census data
        print(f"Downloading and formating data on {code}...")
        name, cell_info, url = nom.get_url(code)
        census_data = request_url_to_dataframe(url, header=0)

        # Check if data larger than 1m cell limit - if so download remaining!
        offset = 1000000
        while census_data.shape[0] >= offset:
            url = url + "&" + "recordoffset=" + str(offset)
            extra_census_data = request_url_to_dataframe(url, header=0)
            census_data = census_data.append(extra_census_data)
            offset += 1000000

        # Change the column values to to names based on metadata
        for key, value in cell_info.items():
            census_data[key] = census_data[key].astype('str').map(value)

        # Merging with geocoded data
        print(f"Merging {code} data with geocoded data...")
        dt = pd.merge(data, census_data, left_on=mergecol, right_on="GEOGRAPHY_CODE", how="inner")
        dt.drop(["LSOA_2001", "LSOA_2011", "RECORD_COUNT"], axis=1, inplace=True)

        # Write data
        name = re.sub(r"[-!?@/(),]", " ", name)
        name = re.sub(r'\s+', '_', name)
        out = args.outputfile + "_" + name + "_" + str(year) + "_census.csv.gz"
        print(f"Writing results to {out}...")
        dt.to_csv(out, index=False, compression='gzip')
        print("Done.\n")


def link_geocode_with_LSOA(data, shpfilename):
    """
    Download boundary shapefiles for LSOA geography from 2001 or 2001 and spatial join with geocoded data.
    Data with eastings and northings column (BNG co-ordinate reference system).
    :param data: Geocoded data
    :param shpfilename: Boundary shapefile for reading.
    :return:
    """
    # Brittish national grid (BNG) co-ordinate reference system (CRS)
    bng = {'init': 'epsg:27700'}

    # Read in england and wales shapefiles from web
    shp = geopandas.read_file(shpfilename)

    # Change CRS if necessary
    if shp.crs != bng:
        shp = shp.to_crs(bng)

    # Create GeoDataFrame from co-ordinates in data
    data = data.dropna()
    data = geopandas.GeoDataFrame(
        data, geometry=geopandas.points_from_xy(data.eastings.astype(int), data.northings.astype(int)),
        crs=bng
    )

    # Spatial join data with shapefile
    data = geopandas.sjoin(data, shp, how="inner", op='within')

    # Return joined data
    return data




if __name__ == "__main__":
    main()
