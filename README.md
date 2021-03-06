
Repository containing python scripts for obtaining geographical variables for a study based in England and Wales.
Includes python packages for scraping DEFRA page of [annual pollution statisics](https://uk-air.defra.gov.uk/data/pcm-data).
Census data was is obtained using [UKCensusAPI](https://github.com/virgesmith/UKCensusAPI).
 

# Table of Contents

**[Set-up](#set-up)**<br>
**[Pre-process and geocode the participants postcode data](#pre-process-and-geocode-the-participants-postcode-data)**<br>
**[Scrape Defra annual pollution statistics page and link with geocoded data](#scrape-defra-annual-pollution-statistics-page-and-link-with-geocoded-data)**<br>
**[Query Nomisweb API and link with geocoded data](#query-nomisweb-api-and-link-with-geocoded-data)**<br>

# Set-up

## Clone github repository

    git clone https://github.com/jmmax/ukepigeo
    cd ukepigeo

## Install requirements (Python 3.7)

    module add devtools/python/3.7.3
    pip install -r requirements.txt

# Pre-process and geocode the participants postcode data

    python preprocess_postcode_data.py --help
    usage: preprocess_postcode_data.py [-h] [--inputfile INPUTFILE]
                                    [--idcol IDCOL] [--outputfile OUTPUTFILE]
                                    [--threads THREADS]

    Python programme for pre-processing and geocoding postcode data (using
    https://postcodes.io/docs). The inputfile is assumed to be a csv file with
    participant ID column (specified by the'idcol' argument) and subsequent
    columns containing postcodes. Multiple columns of postcodes referring to
    different time points may be included in the inputfile where the name of the
    columns specifies the year of data collection i.e. 'Postcodes2008'.
    
    optional arguments:
      -h, --help            show this help message and exit
      --inputfile INPUTFILE, -f INPUTFILE
                            Input file with participant IDs and postcodes.
      --idcol IDCOL, -i IDCOL
                            Column name for participant IDs.
      --outputfile OUTPUTFILE, -o OUTPUTFILE
                            Output filename.
      --threads THREADS, -t THREADS
                            Number of cores for multithreaded functions.


## Example with testing dataset

Testing dataset contains postcode information on 1000 particpants from 1998 and 2008.

    head testing_dataset.csv 
    ID,Postcodes1998,Postcodes2008
    0,TD7 5LG,CB4 2AA
    1,NE12 8WG,DY8 1NJ
    2,IP14 3JH,SA44 4JG
    3,EX15 3HF,NR22 6EG
    4,BS27 3JG,EX10 0RR
    5,DN17 3QA,KY5 0ED
    6,PE21 8PN,SW18 5AL
    7,NP19 0AL,GU21 6LN
    8,BN41 2YD,BS4 1DP
    
    python preprocess_postcode_data.py \
    --inputfile testing_dataset.csv \
    --idcol ID \
    --threads 3 \
    --outputfile testing_geocoded.csv
    Reading and formatting data...
    Columns Postcodes2008 and Postcodes1998, assumed to contain participant postcodes from the years 2008 and 1998, respectively.
    Done.
    Number of cores available:  4
    Geocoding postcodes with 3 core(s)...
    Done.
    
    Frequency table for country of residence:
    
    |      |   Channel Islands |   England |   Isle of Man |   Northern Ireland |   Scotland |   Wales |   All |
    |------+-------------------+-----------+---------------+--------------------+------------+---------+-------|
    | 1998 |                 6 |       822 |             5 |                 31 |         97 |      39 |  1000 |
    | 2008 |                 4 |       817 |             1 |                 30 |         75 |      73 |  1000 |
    | All  |                10 |      1639 |             6 |                 61 |        172 |     112 |  2000 |

## Geocoded data format

    head testing_geocoded.csv
    ID,year,postcode,eastings,northings,country
    0,1998,TD7 5LG,323821.0,623110.0,Scotland
    1,1998,NE12 8WG,425926.0,568533.0,England
    2,1998,IP14 3JH,601576.0,261196.0,England
    3,1998,EX15 3HF,310251.0,113945.0,England
    4,1998,BS27 3JG,346313.0,154057.0,England
    5,1998,DN17 3QA,489783.0,403012.0,England
    6,1998,PE21 8PN,532122.0,344562.0,England
    7,1998,NP19 0AL,331497.0,188472.0,Wales
    8,1998,BN41 2YD,525118.0,107542.0,England

# Scrape Defra annual pollution statistics page and link with geocoded data

    python get_pollution_data.py --help
    usage: get_pollution_data.py [-h] [--geocodedata GEOCODEDATA] [--idcol IDCOL]
                                 [--outputfile OUTPUTFILE]
                                 [--pollutants POLLUTANTS]
    
    Python programme for scraping annual pollution statistics for geocoded UK
    postcodes from https://uk-air.defra.gov.uk/data/pcm-data.
    
    optional arguments:
      -h, --help            show this help message and exit
      --geocodedata GEOCODEDATA, -f GEOCODEDATA
                            Input file with participant IDs, year and geographical
                            co-ordinates.
      --idcol IDCOL, -i IDCOL
                            Column name for participant IDs.
      --outputfile OUTPUTFILE, -o OUTPUTFILE
                            Output filename.
      --pollutants POLLUTANTS, -p POLLUTANTS
                            List of pollutants separated by column.


## Example with testing dataset (link with all available pollutants)
    
    python get_pollution_data.py \
    --geocodedata testing_geocoded.csv \
    --idcol ID \
    --outputfile testing \
    --pollutants PM10,PM2.5,NO2,NOX,SO2,OZONE,BENZENE
    Reading geocoded data...
    Done.
    
    Scraping pollution data...
    
    Information on selected pollutants:
    Pay attention to:
    1) Differences in the postcode data collection year ('Year: postcode')
    and the pollution data collection year ('Year: pollution'). 
    2) Comments (units sometimes differ for different years)
    | Selected pollutants   |   Year: postcode |   Year: pollution | Metric      | Comments                                                                                         |
    |-----------------------+------------------+-------------------+-------------+--------------------------------------------------------------------------------------------------|
    | BENZENE               |             1998 |              2003 | Annual mean | nan                                                                                              |
    | BENZENE               |             2008 |              2008 | Annual mean | nan                                                                                              |
    | NO2                   |             1998 |              2001 | Annual mean | nan                                                                                              |
    | NO2                   |             2008 |              2008 | Annual mean | nan                                                                                              |
    | NOX                   |             1998 |              2001 | Annual mean | µg m-3 (NOX as NO2)                                                                              |
    | NOX                   |             2008 |              2008 | Annual mean | µg m-3 (NOX as NO2)                                                                              |
    | OZONE                 |             1998 |              2003 | DGT120      | metric is number of days on which    the daily max 8-hr concentration is greater than 120 µg m-3 |
    | OZONE                 |             2008 |              2008 | DGT120      | metric is number of days on which    the daily max 8-hr concentration is greater than 120 µg m-3 |
    | PM10                  |             1998 |              2001 | Annual mean | TEOM units                                                                                       |
    | PM10                  |             2008 |              2008 | Annual mean | Gravimetric units                                                                                |
    | PM2.5                 |             1998 |              2002 | Annual mean | nan                                                                                              |
    | PM2.5                 |             2008 |              2008 | Annual mean | nan                                                                                              |
    | SO2                   |             1998 |              2002 | Annual mean | nan                                                                                              |
    | SO2                   |             2008 |              2008 | Annual mean | nan                                                                                              |
    
    
    Linking postcodes to data on selected pollutants: PM10, PM2.5, NO2, NOX, SO2, OZONE, BENZENE...
    Writing results to testing_pollution_data.csv...
    Done.
    
# Query Nomisweb API and link with geocoded data

    Follow instructions on [UKCensusAPI](https://github.com/virgesmith/UKCensusAPI) to get generate scripts for getting data.
    Run the get_census_data.py programme to link with geocoded data.
    
    usage: get_census_data.py [-h] [--geocodedata GEOCODEDATA]
                              [--shapefile SHAPEFILE]
                              [--shapefile_area_id SHAPEFILE_AREA_ID]
                              [--idcol IDCOL] [--out OUT] [--api_dir API_DIR]
                              [--census_table_info CENSUS_TABLE_INFO]
    
    Python program for querying nomisweb API (https://www.nomisweb.co.uk/) for
    census data.Links geocoded data with any data from the nomisweb. A shapefile
    of the census geography must be downloaded and it must match the geography of
    the data downloaded from Nomisweb. Scripts for getting census data from
    Nomisweb arecreated using UKCensusAPI
    (https://github.com/virgesmith/UKCensusAPI) before running this program.
    Nomisweb mostly includes census data for England and Wales only. To find out
    more about census data available go to
    https://www.nomisweb.co.uk/query/select/getdatasetbytheme.asp
    
    optional arguments:
      -h, --help            show this help message and exit
      --geocodedata GEOCODEDATA, -f GEOCODEDATA
                            Input file with participant IDs, year and geographical
                            co-ordinates in eastings/northings (epsg:27700).
      --shapefile SHAPEFILE, -s SHAPEFILE
                            Pathway to shapefile.
      --shapefile_area_id SHAPEFILE_AREA_ID
                            Column name of geographical area ids in shapefile.
      --idcol IDCOL, -i IDCOL
                            Column name for participant IDs.
      --out OUT, -o OUT     Output filename.
      --api_dir API_DIR, -d API_DIR
                            Directory with Nomisweb API scripts generated
                            interactively via UKCensusAPI.
      --census_table_info CENSUS_TABLE_INFO, -c CENSUS_TABLE_INFO
                            CSV file with info on which census tables to
                            download.Must have the format: VARIABLE (name of
                            census table) andCENSUS_VAR_CODE (code for census
                            table - must have a corresponding script in the 'api-
                            dir').


## Example with testing dataset (link with general health variable from 2001 and 2011 census)


### Download shapefiles for linking census data

    mkdir boundary_data/LSOA
    
    python download_boundary_esri_shapefile.py

### Run script

    ls nomis_api_scripts/
    KS101EW.R  KS101EW.py  KS101EW_metadata.json KS102EW.R  KS102EW.py  KS102EW_metadata.json NOMIS_API_KEY  lad_codes.json

    head testing_census_variables.csv
    VARIABLE,CENSUS_YEAR,CENSUS_VAR_CODE
    Usual resident population,2011,KS101EW
    Age structure,2011,KS102EW


    python get_census_data.py \
    --geocodedata testing_geocoded.csv \
    --idcol ID \
    --shapefile boundary_data/LSOA/EW_lsoa_2011.shp \
    --shapefile_area_id zonecode \
    --api_dir nomis_api_scripts \
    --out testing \
    --apikey 'nomis-api-key' \
    --census_table_info 'testing_census_variables.csv'
    Reading geocoded data...
    Done.
    
    Linking geocoded data with shapefile boundary shapefiles from https://census.ukdataservice.ac.uk/get-data/boundary-data.aspx...
    Done.
    
    Writing results to testing.csv.gz...


**Contains National Statistics data © Crown copyright and database right [2020]
Contains OS data © Crown copyright [and database right] (2020)**




