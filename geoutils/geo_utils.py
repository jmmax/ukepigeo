import requests
import re
import pandas as pd
import numpy as np
import io

def geocode_uk(postcode):
    """
    Convert UK postcode into geographical co-ordinates by querying https://postcodes.io/.
    Co-ordinate reference system (CRS):
    - Brittish National Grid for English, Scottish and Welsh postcodes
    - Irish National Grid for Northern Irish postcodes.
    :param postcode: postcode.
    :return: 1 dimensional numpy array of postcode, easting, northing, country.
    """
    url = 'http://api.postcodes.io/postcodes/' + re.sub(r"\s+|\W+", '', str(postcode))
    response = requests.get(url)

    if response.status_code == 200:
        info = response.json()["result"]
        return [info['postcode'], info['eastings'], info['northings'],
                info['country']]
    else:
        info = response.json()["error"]
        return [info, info, info, info]


def geocode(postcode):
    """
    Convert worldwide postcode to latitude and longitude by scraping worldpostalcode.com.
    :param postcode: postcode
    :return: 1 dimensional numpy array of postcode, latitude, longitude, country.
    """
    raise NotImplementedError


def random_postcode(n):
    """
    Generate list of random postcodes of length n.
    :param n: length.
    :return: list of random postcodes of length n.
    """
    N = 0
    plist = []
    while N < n:
        url = 'https://api.postcodes.io/random/postcodes'
        response = requests.get(url)
        if response.status_code == 200:
            plist.append(response.json()["result"]["postcode"])
            N += 1
        else:
            continue
    return plist


def find_nearest_idx(array, value):
    """
    Returns indicies of an column that are closest to a value (includes all occurances).
    :param array: array
    :param value: value
    :return: list of indicies of the array.
    """
    try:
        value = float(value)
        if np.isnan(value):
            return np.nan
        array = np.asarray(array).astype(float)
        difference = np.abs(array - value)
        idx = np.argwhere(difference == min(difference))
        return idx.flatten().tolist()
    except ValueError:
        return np.nan


def request_url_to_dataframe(link, header):
    """
    Read in pollution data.
    :param header: Header line in the file.
    :param link: url to csv file with pollution data.
    :return: pandas dataframe with pollutaion data with the following columns: unique code for 1x1km grid
    square (ukgridcode), easting (x), northing (y), and header label referring to the pollutant and
    the year (i.e 'pm102008g' for PM10 pollution data from the year 2008).
    """
    agent = {
        "User-Agent":
            'Mozilla/5.0 (Windows NT 6.3; WOW64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/59.0.3071.115 Safari/537.36'
    }
    if 'csv' not in link:
        print("Error: expected a http connection to a csv file.")
    else:
        f = requests.get(link, headers=agent)
        if f.status_code == 200:
            df = pd.read_csv(io.StringIO(f.text),
                             low_memory=False, na_values=['NA', 'NaN', 'MISSING'],
                             header=header)
            return df
        elif f.status_code == 404:
            print("Error: Not Found.")


