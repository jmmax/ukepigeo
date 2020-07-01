import argparse
import pandas as pd
import multiprocessing as mp
import geoutils
import re
import sys
from tabulate import tabulate

def main():
    # Initiate parser and add arguments
    parser = argparse.ArgumentParser(
        description="Python programme for pre-processing and geocoding postcode data (using "
                    "https://postcodes.io/docs). The inputfile is assumed to be a csv file "
                    "with participant ID column (specified by the'id_col' argument) and subsequent"
                    " columns containing postcodes. Multiple columns of postcodes referring to "
                    "different time points may be included in the inputfile where the name of the"
                    " columns specifies the year of data collection i.e. 'Postcodes2008'."
    )
    parser.add_argument("--inputfile", "-f", help="Input file with participant IDs and postcodes.")
    parser.add_argument("--idcol", "-i", help="Column name for participant IDs.")
    parser.add_argument("--outputfile", "-o", help="Output filename.")
    parser.add_argument("--threads", "-t", help="Number of cores for multithreaded functions.", default=1)

    # Read arguments from command line
    args = parser.parse_args()

    # Read data, check file format and drop NAs
    print("Reading and formatting data...")
    data = read_and_format_data(
        args.inputfile, args.idcol
    ).dropna()
    print("Done.")


    # Clean and geocode postcodes
    print("Number of cores available: ", mp.cpu_count())
    print(f"Geocoding postcodes with {args.threads} core(s)...")
    pool = mp.Pool(int(args.threads))
    dt = pool.map(
        apply_geo_fun,
        [
            (pid, year, postcode) for pid, orig_col, postcode, year in data.itertuples(index=False)
        ]
    )
    pool.close()

    data = pd.DataFrame(dt)
    data.columns = [args.idcol, "year", "postcode", "eastings", "northings", "country"]
    print("Done.")

    # Print sample size of participants in countries at different time points
    print("\nFrequency table for country of residence:\n")
    ct = pd.crosstab(data["year"], data["country"], margins=True)
    print(tabulate(
        ct, ct.columns.values.tolist(), tablefmt='orgtbl'
    ))
    print("\n")

    # Write
    data.to_csv(args.outputfile, index=False)


def read_and_format_data(inputfile, idcol):
    """
    Read and format data on the pariticpants postcodes. Postcodes may refer to data collected at multiple time points.
    File assumed to be a CSV containing participant ID's and postcodes for different time points in seperate columns.
    Postcode columm name(s) must specify the data collection year e.g. 'Postcodes2005'

    :param inputfile: csv file with participant ID column and subsequent columns containing postcodes.
    :param idcol: name of the column containing the participant ID's.
    :return: pd.DataFrame with ID, year and postcode column.
    """
    # Read in data with pandas
    data = pd.read_csv(inputfile)

    # Check that the columns containing postcodes are correctly formatted
    if idcol not in data.columns:
        sys.exit(print(f"Error: '{idcol}', column not found in {inputfile}."
                       f"\nCheck the column names of your inputfile:\n {data.head()}"))
    postcode_cols_list = data.columns[1:].tolist()
    years = re.findall(r"[12][0-9]{3}", ' '.join(postcode_cols_list))
    if len(years) != len(postcode_cols_list):
        sys.exit(print(f"Error: name of postcode column(s) must include the year of data collection."
                       f"\nColumn names of inputfile:"
                       f"{','.join(postcode_cols_list[1:])} and {postcode_cols_list[0]}"))
    else:
        print(f"Columns {','.join(postcode_cols_list[1:])} and {postcode_cols_list[0]}, "
              f"assumed to contain participant postcodes from the years {','.join(years[1:])} "
              f"and {years[0]}, respectively.")

    # Change DataFrame to long format and create year column
    data = data.melt(id_vars=idcol)
    yr_dict = {key: var for key, var in zip(postcode_cols_list, years)}
    data['year'] = data['variable'].map(yr_dict)

    # Return pd.DataFrame
    return data

def apply_geo_fun(tup):
    """
    Function to add ID and year variables to list returned from geocode_uk function.
    :param tup: tuple of (pid, year, postcode).
    :return: list of ID, year and data from geocode_uk function.
    """
    return list(tup[:2]) + geoutils.geocode_uk(tup[2])




if __name__ == "__main__":
    main()