import pytest
import nomiswebAPI

@pytest.fixture
def ci():
    return nomiswebAPI.NomisAPI('census_variables.csv')


# class TestCreateApiUrl:
#
#     def test_something(self, ci):
#         url_2011_1 = 'https://www.nomisweb.co.uk/api/v01/dataset/NM_623_1.data.csv?date=latest&geography=1249902593...1249937345&rural_urban=0&cell=0...12&measures=20100'
#         url_2001_1 = 'https://www.nomisweb.co.uk/api/v01/dataset/NM_1603_1.data.csv?date=latest&geography=1275068417...1275102794&c_larpuk11=0,100,1,2,200,3...7&measures=20100'
#         raise NotImplementedError