from geoutils import *
import numpy as np

class TestGeocodeUK:

    def test_valid_uk_postcode(self):
        expected = np.array(['CH5 3HJ', '331379', '366865', 'Wales'])
        assert (geocode_uk('CH5 3HJ') == expected).all()

    def test_invalid_uk_postcode(self):
        expected = np.array(['Invalid postcode', 'Invalid postcode',
                             'Invalid postcode', 'Invalid postcode'])
        assert (geocode_uk('CH5 3HJ4') == expected).all()

    def test_passing_int_to_fun(self):
        expected = np.array(['Invalid postcode', 'Invalid postcode',
                             'Invalid postcode', 'Invalid postcode'])
        assert (geocode_uk(12321) == expected).all()

    def test_remove_invalid_character_from_valid_postcode(self):
        expected = np.array(['CH5 3HJ', '331379', '366865', 'Wales'])
        assert (geocode_uk('CH5,3HJ') == expected).all()


class TestRequestUrlToDataframe:

    def test_correct_columns(self):
        expected = [
            'ukgridcode', 'x', 'y'
        ]
        downloaded_data = request_url_to_dataframe('https://uk-air.defra.gov.uk/datastore/pcm/mapbz2017.csv',
                                                   header=5)
        assert (downloaded_data.columns[:3] == expected).all()

    def test_not_csv_file(self):
        expected = None
        assert request_url_to_dataframe('https://uk-air.defra.gov.uk', header=5) == expected