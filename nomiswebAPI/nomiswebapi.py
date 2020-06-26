import requests
from bs4 import BeautifulSoup
import re

class NomisAPI:

    def __init__(self, apikey):
        self.agent = {
            "User-Agent":
                'Mozilla/5.0 (Windows NT 6.3; WOW64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/59.0.3071.115 Safari/537.36'
        }
        self.apikey = apikey
        self.root = 'https://www.nomisweb.co.uk/api/v01/dataset/'
        self.datasets = self.datasets_info()

    def datasets_info(self):
        """

        :return:
        """
        # get table html from url
        url = "https://www.nomisweb.co.uk/api/v01/dataset/def.htm"
        request = requests.get(url, headers=self.agent).content
        soup = BeautifulSoup(request, features="lxml")
        tables = soup.find_all('table')

        # Loop through tables and create dictionary for each
        info = {}
        for table in tables:
            keyfamily = table.find_all('tr')[0].find('td').text

            # Only include keyfamily tables
            if keyfamily != 'KeyFamily':
                continue

            # Select id, name and dimensions
            trs = table.find_all('tr')
            elems = [
                list(filter(None, [td.text for td in tr.find_all('td')]))
                for tr in trs if len(tr) in [2, 3]
            ]
            elems_dict = {item[0]: item[1] for item in elems}
            elems_dict.pop('Parent link')
            elems_dict.pop('conceptRef')
            elems_dict.pop('Child link')
            name = elems_dict.pop('Name')

            # Append to dictionary
            info[name] = elems_dict

        # Return info dictionary
        return info


    def get_metadata(self, code):
        """

        :param code:
        :return:
        """
        # Select code from datasets
        name = [name for name in self.datasets.keys() if re.match(code, name)][0]
        info = self.datasets[name]

        # Get link to metadata
        start = "https://www.nomisweb.co.uk/api/v01/dataset/"
        end = ".def.htm"
        key_id = info['id']
        metadata = {key: start + key_id + '/' + key + end for key in info.keys() if key != 'id'}

        # Loop through metadata links and get all options
        for key, link in metadata.items():
            request = requests.get(link, headers=self.agent).content
            soup = BeautifulSoup(request, features="lxml")
            tables = soup.find_all('table')

            # Loop through tables on html page
            for table in tables:
                codelist = table.find_all('tr')[0].find('td').text

                # Only include codelist tables
                if codelist != 'Codelist':
                    continue

                # Get values and descriptions from table
                trs = table.find_all('tr')
                elems = [
                    list(filter(None, [td.text for td in tr.find_all('td')]))
                    for tr in trs if len(tr) in [2, 3]
                ]
                elems_dict = {item[0]: item[1] for item in elems}
                elems_dict.pop('id')
                elems_dict.pop('value')

                metadata[key] = elems_dict

        # Return name and metadata
        return name, key_id, metadata


    def get_url(self, code):
        """

        :param code:
        :return:
        """
        # Get code info
        name, key_id, metadata = self.get_metadata(code)

        # GEOGRAPHY and MEASURE and RURAL_URBAN as seperate objects
        geog = metadata.pop("GEOGRAPHY", None)
        measure = metadata.pop("MEASURES", None)
        rural_urban = metadata.pop("RURAL_URBAN", None)

        # Create empty dictionary for params
        params = []

        if not geog:
            raise ValueError(f"Error: {code} doesn't have associated"
                             f" geography and is not supported by the program.")

        # Always select value for the measures variable
        if measure:
            params.append("measures=20100")

        # Always select 0 for the rural urban variable
        if rural_urban:
            params.append('rural_urban=0')

        # Loop through remaining metadata and select all.
        for key, subdict in metadata.items():
            params.append(key.lower() + "=" + ','.join(subdict.keys()))


        # Set geographu type as LSOA for 2001 and 2011
        if 2001 in metadata["TIME"].keys():
            params.append('geography=1275068417...1275102794')
        if 2011 in metadata["TIME"].keys():
            params.append('geography=1249902593...124993734')

        # Set date to latest
        params.append('date=latest')

        # Set columns to select from data
        metadata.pop("FREQ")
        metadata.pop("TIME")
        params.append('select=geography_name,geography_code,obs_value'
                      + ',' + ','.join(metadata.keys()).lower())

        # Include unique ID
        params.append('uid=' + self.apikey)

        # URL
        url = self.root + key_id + ".data.csv?" + '&'.join(params)

        # Return name of variable and download url
        return name, metadata, url










