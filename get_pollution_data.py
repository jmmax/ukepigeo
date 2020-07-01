import sys
import argparse
import pandas as pd
from datetime import date
from tabulate import tabulate
import scrapedefra

POLLUTANTS = {'PM10', 'PM2.5', 'NO2', 'NOX', 'CO', 'SO2', 'OZONE', 'BENZENE'}

def main():
    # Initiate parser and add arguments
    parser = argparse.ArgumentParser(
        description="Python programme for scraping annual pollution statistics for geocoded UK postcodes"
                    " from https://uk-air.defra.gov.uk/data/pcm-data. "
    )
    parser.add_argument("--geocodedata", "-f", help="Input file with participant IDs, year and geographical "
                                                    "co-ordinates.")
    parser.add_argument("--idcol", "-i", help="Column name for participant IDs.")
    parser.add_argument("--outputfile", "-o", help="Output filename.")
    parser.add_argument("--pollutants", "-p", help="List of pollutants separated by column.",
                        default='PM10,PM2.5,NO2,NOX,SO2,OZONE,BENZENE')

    # Read arguments from command line
    args = parser.parse_args()

    # Read in geocoded data
    print("Reading geocoded data...")
    data = pd.read_csv(args.geocodedata)
    print("Done.")

    print("\nScraping pollution data...")

    # Check user selected pollutants are valid
    pollutants = args.pollutants.split(',')
    for p in pollutants:
        if p not in POLLUTANTS:
            sys.exit(f"Error: {p} is not a valid pollutant.\n"
                     f"Valid pollutants: {', '.join(POLLUTANTS)}.")

    # Years of postcode data collection
    years = data.year.dropna().unique()

    # Intialise class to scrape pollution data
    sc = scrapedefra.ScrapeDefraPollution(years, pollutants)

    # Print info df
    print("\nInformation on selected pollutants:")
    print("Pay attention to:"
          "\n1) Differences in the postcode data collection year ('Year: postcode')"
          "\nand the pollution data collection year ('Year: pollution'). "
          "\n2) Comments (units sometimes differ for different years)")
    print_info = sc.pollution_data.iloc[:, [0, 1, 2, 3, 5]].sort_values(by='pollutant')
    newcols = [
        "Selected pollutants", "Year: postcode", "Year: pollution", "Metric", "Comments"
    ]
    print_info.columns = newcols
    print_info.reset_index(drop=True)
    print(tabulate(print_info, headers=newcols, tablefmt='orgtbl', showindex="never"))

    # Link postcode data with the pollution data
    print(f"\n\nLinking postcodes to data on selected pollutants: {', '.join(pollutants)}...")
    p_data = sc.linking_func(data, args.idcol)

    # Write data

    out = args.outputfile + "_pollution_data" + ".csv"
    print(f"Writing results to {out}...")
    p_data.to_csv(out, index=False)
    print("Done.")



if __name__ == "__main__":
    main()