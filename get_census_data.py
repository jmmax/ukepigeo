import sys
import argparse
import pandas as pd
import geopandas
import os
import ukcensusapi.Nomisweb as CensusApi
from functools import reduce


def main():
    # Initiate parser and add arguments
    parser = argparse.ArgumentParser(
        description="Python program for querying nomisweb API (https://www.nomisweb.co.uk/) for census data."
                    "Links geocoded data with any data from the nomisweb. A shapefile of the census geography "
                    "must be downloaded and it must match the geography of the data downloaded from Nomisweb. "
                    "Scripts for getting census data from Nomisweb arecreated using UKCensusAPI "
                    "(https://github.com/virgesmith/UKCensusAPI) before running this program. Nomisweb mostly includes"
                    " census data for England and Wales only. To find out more about census data "
                    "available go to https://www.nomisweb.co.uk/query/select/getdatasetbytheme.asp"
    )
    parser.add_argument("--geocodedata", "-f", help="Input file with participant IDs, year and geographical "
                                                    "co-ordinates in eastings/northings (epsg:27700).")
    parser.add_argument("--shapefile", "-s", help="Pathway to shapefile.")
    parser.add_argument("--shapefile_area_id", help="Column name of geographical area ids in shapefile.")
    parser.add_argument("--idcol", "-i", help="Column name for participant IDs.")
    parser.add_argument("--out", "-o", help="Output filename.")
    parser.add_argument("--api_dir", "-d", help="Directory with Nomisweb API scripts generated interactively via"
                                                " UKCensusAPI.")
    parser.add_argument("--census_table_info", "-c", help="CSV file with info on which census tables to download."
                                                          "Must have the format: VARIABLE (name of census table) and"
                                                          "CENSUS_VAR_CODE (code for census table - must have a"
                                                          " corresponding script in the 'api-dir').", default=False)

    # Read arguments from command line
    args = parser.parse_args()

    # Read in geocoded data
    print("Reading geocoded data...")
    typedict = {args.idcol: str}
    data = pd.read_csv(args.geocodedata,
                       na_values=['Postcode not found', 'Invalid postcode'],
                       dtype=typedict)
    print("Done.")

    # Link data with 2001 and 2011 LSOA geography
    print("\nLinking geocoded data with shapefile"
          " boundary shapefiles from https://census.ukdataservice.ac.uk/get-data/boundary-data.aspx...")
    data = link_geocode_with_shapefile(data, args.shapefile)
    data = data[[args.idcol, 'eastings', 'northings', 'year', args.shapefile_area_id]]
    print("Done.\n")

    # Read in info on which census data to download
    variables = pd.read_csv(args.census_table_info)

    # Get all nomisweb data
    data_list = []
    for index, cname, ctable in variables[['VARIABLE', 'CENSUS_VAR_CODE']].itertuples():
        pysc = open(os.path.join(args.api_dir, ctable + ".py")).read()
        exec(pysc)
        cdata = locals()[ctable]
        os.system("rm " + ctable + "*")

        # add context - descriptions of values to the CELL column
        api = CensusApi.Nomisweb(".")
        api.contextify(ctable, "CELL", cdata)

        # reshape data
        cdata.CELL_NAME = cdata.CELL_NAME.str.replace("[(0!?:;,)%*.]+", ".", regex=True)
        cdata.CELL_NAME = cdata.CELL_NAME.str.replace(" ", ".", regex=True)
        cdata.drop("CELL", axis=1, inplace=True)
        cdata = cdata.pivot_table(index="GEOGRAPHY_CODE", columns="CELL_NAME",values="OBS_VALUE").reset_index()
        cdata.index.name = None

        # change column names to include census table
        keys = cdata.columns[1:]
        cols = {key: ctable + "." + key for key in keys}
        cdata.rename(columns=cols, inplace=True)

        # Append to list
        data_list.append(cdata)

    # merge list of nomisweb data
    nomisdata = reduce(lambda df1, df2: pd.merge(df1, df2, on='GEOGRAPHY_CODE'), data_list)

    # merge geocoded data with nomisweb data
    data = pd.merge(data, nomisdata, left_on=args.shapefile_area_id, right_on="GEOGRAPHY_CODE", how="inner")

    # write output
    out = args.out + "_nomisweb.csv.gz"
    print(f"Writing results to {out}...")
    data.to_csv(out, index=False, compression='gzip')

def link_geocode_with_shapefile(data, shpfilename):
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
