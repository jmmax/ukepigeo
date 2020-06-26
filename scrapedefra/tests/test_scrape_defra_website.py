import pytest
import pandas as pd
import numpy as np
import scrapedefra


@pytest.fixture
def data():
    dt = pd.DataFrame([
        [
            "1191", "1998", "YO12 4JR", "503065", "484333", "England"
        ], [
            "10771", "2008", "NG9 1AH", "452432", "337099", "England"
        ],
        [
            "10772", "2018", "GU8 4AR", "498970", "143163", "England"
        ]
    ], columns=[
        "id_twin", "year", "postcode", "eastings", "northings", "country"
    ])
    return dt


@pytest.fixture
def ci(data):
    years = data.year.dropna().unique()
    pollutants = ['PM10', 'PM2.5']
    return scrapedefra.ScrapeDefraPollution(years, pollutants)


class TestGetTables:

    def test_has_website_been_updated(self, ci):
        expected_return_shape_020620 = (138, 6)
        shp = ci.get_tables().shape
        assert shp == expected_return_shape_020620, "Website updated... may cause other functions to fail."


class TestInfo:

    def test_correct_output(self, ci, data):
        expected = pd.DataFrame(
            [
                [
                    "PM10", "1998", "2001", "Annual mean", "pm102001", "TEOM units",
                    "https://uk-air.defra.gov.uk/datastore/pcm/mappm102001.csv"
                ], [
                "PM2.5", "1998", "2002", "Annual mean", "pm252002", np.nan,
                "https://uk-air.defra.gov.uk/datastore/pcm/mappm252002.csv"
            ], [
                "PM10", "2008", "2008", "Annual mean", "pm102008g", "Gravimetric units",
                "https://uk-air.defra.gov.uk/datastore/pcm/mappm102008g.csv"
            ], [
                "PM2.5", "2008", "2008", "Annual mean", "pm252008g", np.nan,
                "https://uk-air.defra.gov.uk/datastore/pcm/mappm252008g.csv"
            ], [
                "PM10", "2018", "2018", "Annual mean", "pm102018g", "Gravimetric units",
                "https://uk-air.defra.gov.uk/datastore/pcm/mappm102018g.csv"
            ], [
                "PM2.5", "2018", "2018", "Annual mean", "pm252018g", np.nan,
                "https://uk-air.defra.gov.uk/datastore/pcm/mappm252018g.csv"
            ]
            ], columns=[
                "pollutant", "year_postcode_data_collected", "year_pollution_data_collected",
                "metric", "header_label", "comments", "download_link"]
        )
        actual = ci.pollution_data
        pd.testing.assert_frame_equal(actual, expected)



class TestGetNearestUkgridcode:

    def test_get_correct_result(self, ci):
        expected = '54979'
        actual = ci.get_nearest_ukgridcode(458500, 1220500)
        assert actual == expected

    def test_str_type(self, ci):
        expected = '54979'
        actual = ci.get_nearest_ukgridcode('458500', '1220500')
        assert actual == expected

    def test_invalid_geocoords(self, ci):
        assert np.isnan(ci.get_nearest_ukgridcode(660510, 1000))

    def test_na_1(self, ci):
        assert np.isnan(ci.get_nearest_ukgridcode(np.nan, 1000))

    def test_na_2(self, ci):
        assert np.isnan(ci.get_nearest_ukgridcode('NaN', np.nan))

    def test_string(self, ci):
        assert np.isnan(ci.get_nearest_ukgridcode('not_coers_to_number', 'not_coers_to_number'))


