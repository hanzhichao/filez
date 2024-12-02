from pathlib import Path

import pytest

from filez import file, trans_value, trans_dict_value
from collections import OrderedDict


@pytest.fixture
def testdata() -> Path:
    return Path(__file__).parent / 'testdata'


def test_load_txt(testdata):
    data = file.load(testdata / 'data.txt')
    assert data == ['line1', 'line2', 'line3', 'line4']


def test_load_no_header_csv(testdata):
    data = file.load(testdata / 'data.csv', ensure_number=False, ensure_boolean=False)
    assert data == [['a', 'b', 'c'], ['1', '2.2', 'true'], ['4', '5', '6']]


def test_load_no_header_csv_ensure_number(testdata):
    data = file.load(testdata / 'data.csv')
    assert data == [['a', 'b', 'c'], [1, 2.2, True], [4, 5, 6]]


def test_load_with_header_csv(testdata):
    data = file.load(testdata / 'data.csv', header=True, ensure_boolean=False, ensure_number=False)
    assert data == [dict([('a', '1'), ('b', '2.2'), ('c', 'true')]),
                    dict([('a', '4'), ('b', '5'), ('c', '6')])]


def test_load_with_header_csv_ensure_number(testdata):
    data = file.load(testdata / 'data.csv', header=True, ensure_boolean=False)
    assert data == [dict([('a', 1), ('b', 2.2), ('c', 'true')]),
                    dict([('a', 4), ('b', 5), ('c', 6)])]


def test_load_with_header_csv_ensure_boolean(testdata):
    data = file.load(testdata / 'data.csv', header=True, ensure_number=False)
    assert data == [dict([('a', '1'), ('b', '2.2'), ('c', True)]),
                    dict([('a', '4'), ('b', '5'), ('c', '6')])]


def test_json(testdata):
    data = file.load(testdata / 'data.json')
    assert data == {'a': 1, 'b': 2}


def test_yaml(testdata):
    data = file.load(testdata / 'data.yaml')
    assert data == {'a': 1, 'b': 2}


def test_config(testdata):
    data = file.load(testdata / 'data.conf')
    assert data == {'vars': {'a': 1, 'b': 2}, 'words': {'Man': True, 'Woman': False}}


def test_trans_value(testdata):
    assert trans_value('1') == 1
    assert trans_value('1.1') == 1.1
    assert trans_value('true') is True
    assert trans_value('off') is False
    assert trans_value('~') is None


def test_trans_dict_value(testdata):
    assert trans_dict_value({'a': '1', 'b': 'null'}) == {'a': 1, 'b': None}
    assert trans_dict_value({'a': '1', 'b': 'null'}, ordered_dict=True) == OrderedDict([('a', 1), ('b', None)])


def test_load_xls(testdata):
    data = file.load(testdata / 'data.xls')
    assert data == [['a', 'b', 'c'], [1.0, 2.2, 0], ['hello', 'world', '']]


def test_load_xlsx(testdata):
    data = file.load(testdata / 'data.xlsx')
    assert data == [['a', 'b', 'c'], [1, 2.2, False], ['hello', 'world', None]]


def test_load_xlsx_with_header(testdata):
    data = file.load(testdata / 'data.xlsx', header=True)
    assert data == [{'a': 1, 'b': 2.2, 'c': False},
                    {'a': 'hello', 'b': 'world', 'c': None}]
    print(data)


def test_load_excel_all_sheets(testdata):
    data = file.load(testdata / 'data.xls', sheets='all')
    assert data == {'Sheet1': [['a', 'b', 'c'], [1.0, 2.2, 0], ['hello', 'world', '']],
                    'Sheet2': [['a', 'b', 'c'], [1.0, 2.2, 0]]}


def test_load_excel_given_sheets(testdata):
    data = file.load(testdata / 'data.xls', sheets=[1])
    assert data == {'Sheet2': [['a', 'b', 'c'], [1.0, 2.2, 0]]}


def test_load_properties(testdata):
    data = file.load(testdata / 'data.properties')
    assert data == {'appId': 'cactus', 'publicKey': '-----BEGIN PUBLIC KEY-----\\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEP9eQZFl3j5zZX8bmYYEznA0z3/X+\\nTooIQ11rxFcPZsTvJPLCUY7NHasUenXJngmvRXSnP4odegaoe4usLDv/3A==\\n-----END PUBLIC KEY-----', 'app': {'config': {'host': '127.0.0.1', 'port': '8080'}}}



def test_load_toml(testdata):
    data = file.load(testdata / 'data.toml')
    assert data == {'vars': {'a': 1, 'b': 2}, 'words': {'Man': True, 'Woman': False}}
