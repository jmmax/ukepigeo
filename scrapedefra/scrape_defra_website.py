import pandas as pd
import requests
import numpy as np
from bs4 import BeautifulSoup
from geoutils import find_nearest_idx
from geoutils import request_url_to_dataframe

class ScrapeDefraPollution:

    def __init__(self, years, pollutants):
        url = 'https://uk-air.defra.gov.uk/data/pcm-data'
        self.agent = {
            "User-Agent":
                'Mozilla/5.0 (Windows NT 6.3; WOW64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/59.0.3071.115 Safari/537.36'
        }
        self.request = requests.get(url, headers=self.agent).content
        self.soup = BeautifulSoup(self.request, features="lxml")
        self.pollutants = pollutants
        self.years = years
        self.pollution_data = self.info()
        self.reference = request_url_to_dataframe(
            'https://uk-air.defra.gov.uk/datastore/pcm/mappm102001.csv', header=5).iloc[:, :3]

    def get_tables(self):
        """
        Scrape tables from https://uk-air.defra.gov.uk/data/pcm-data.
        :return: pandas DataFrame with columns: pollutant, year_pollution_data_collected, metric, header_label,
        comments, download_link.
        """
        table_elem = self.soup.find_all('table', {"class": "data"})
        data_list = list()
        for tab in table_elem:
            rows = [[elem.text for elem in row.find_all('td')] for row in tab.find_all('tr')]
            refs = tab.find_all('a', href=True)
            refcol = [
                'https://uk-air.defra.gov.uk' + ref.attrs['href'].replace('..', '') for ref in refs
            ]
            dt = pd.DataFrame([x for x in rows if x]).iloc[:, :-1]
            dt['download_link'] = np.asarray(refcol)
            try:
                dt.columns = [
                    'pollutant', 'year_pollution_data_collected', 'metric', 'header_label', 'comments', 'download_link'
                ]
            except:
                continue
            dt['pollutant'] = dt['pollutant'].str.upper()
            data_list.append(dt)
        data = pd.concat(data_list)
        return data

    def info(self):
        """
        Get data on the pollutants from years specified on the class initialisation. (i.e.
        'year_postcode_data_collected') If year not available then the closest year will be selected.
        :return: pandas DataFrame with columns: pollutant, year_postcode_data_collected, year_pollution_data_collected,
        metric,header_label, comments, download_link.
        """
        if type(self.years) == str or type(self.years) == int or type(self.years) == float:
            self.years = [str(self.years)]
        if type(self.pollutants) == str or type(self.years) == int or type(self.years) == float:
            self.pollutants = [str(self.pollutants)]

        ptab = self.get_tables()

        dt = []
        for year in self.years:
            for p in self.pollutants:
                pollution_dt = ptab[ptab['pollutant'] == p].copy()
                indexes = find_nearest_idx(pollution_dt['year_pollution_data_collected'], year)
                pollution_dt = pollution_dt.iloc[indexes, :]
                pollution_dt.insert(1, 'year_postcode_data_collected', year, allow_duplicates=True)
                pollution_dt = pollution_dt[
                    (pollution_dt['metric'] == 'Annual mean')
                    | (pollution_dt['metric'] == 'DGT120')]
                dt.append(pollution_dt)
        df = pd.concat(dt).replace(r'^\s+$', np.NaN, regex=True)
        df = df.reset_index(drop=True)
        return df


    def get_nearest_ukgridcode(self, easting, northing):
        """
        Returns grid code of the nearest km square in the British National Grid.
        :param northing: north co-ordinate in metres.
        :param easting: east co-cordinate in metres.
        :return: grid code (str).
        """
        try:
            easting = float(easting)
            northing = float(northing)
        except ValueError:
            return np.nan
        else:
            xindex = find_nearest_idx(self.reference.x, easting)
            if np.isnan(xindex).any():
                return np.nan
            else:
                update_reference = self.reference.iloc[xindex, :]
                yindex = find_nearest_idx(update_reference.y, northing)
                if np.isnan(yindex).any():
                    return np.nan
                else:
                    nearest = update_reference.iloc[yindex[0], :]
                    if abs(nearest['x'] - easting) > 1000:
                        return np.nan
                    elif abs(nearest['y'] - northing) > 1000:
                        return np.nan
                    else:
                        return str(nearest['ukgridcode'])

    def linking_func(self, data, idcol):
        """
        Function for linking the geocoded participant data with the pollution data.
        :param idcol: column name for participant ids
        :param data: DataFrame with columns: idcol, year, postcode, easting, northing, country.
        :return: DataFrame with columns: id_col, year, pollutant,
        """
        data['ukgridcode'] = [self.get_nearest_ukgridcode(east, north)
                              for iid, year, poll, east, north, count in data.itertuples(index=False)]
        dfs = []
        for year in self.years:
            df = data[data['year'] == year].copy()
            df['ukgridcode'] = df['ukgridcode'].astype(str)
            for pollutant in self.pollutants:
                linksdf = self.pollution_data[
                    (self.pollution_data['pollutant'] == pollutant)
                    & (self.pollution_data['year_postcode_data_collected'] == year)]
                link = linksdf.iloc[0, 6]
                pollution_df = request_url_to_dataframe(link, header=5)
                pollution_df['ukgridcode'] = pollution_df['ukgridcode'].astype(str)
                df = df.merge(pollution_df, 'left', 'ukgridcode')
                df = df.drop(['x', 'y'], axis=1)
                df = df.rename(columns={df.columns[-1]: pollutant})
            dfs.append(df)
        rdata = pd.concat(dfs)
        rdata = rdata.drop('ukgridcode', axis=1)
        return rdata

