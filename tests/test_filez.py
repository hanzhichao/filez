from filez import file, trans_value, trans_dict_value
from collections import OrderedDict


def test_load_txt():
    data = file.load_txt('tests/data.txt')
    assert data == ['line1', 'line2', 'line3', 'line4']


def test_load_no_header_csv():
    data = file.load_csv('tests/no_header.csv', ensure_number=False, ensure_boolean=False)
    assert data == [['1', '2', '3'], ['4', '5', '6'], ['7', '8', '9']]


def test_load_no_header_csv_ensure_number():
    data = file.load_csv('tests/no_header.csv')
    assert data == [[1, 2, 3], [4, 5, 6], [7, 8, 9]]


def test_load_with_header_csv():
    data = file.load_csv('tests/with_header.csv', header=True, ensure_boolean=False, ensure_number=False)
    assert data == [OrderedDict([('a', '1'), ('b', '2.2'), ('c', 'true')]), OrderedDict([('a', '4'), ('b', '5'), ('c', '6')])]


def test_load_with_header_csv_ensure_number():
    data = file.load_csv('tests/with_header.csv', header=True, ensure_boolean=False)
    assert data == [OrderedDict([('a', 1), ('b', 2.2), ('c', 'true')]), OrderedDict([('a', 4), ('b', 5), ('c', 6)])]


def test_load_with_header_csv_ensure_boolean():
    data = file.load_csv('tests/with_header.csv', header=True, ensure_number=False)
    assert data == [OrderedDict([('a', '1'), ('b', '2.2'), ('c', True)]), OrderedDict([('a', '4'), ('b', '5'), ('c', '6')])]


def test_json():
    data = file.load_json('tests/data.json')
    assert data == {'a': 1, 'b': 2}


def test_yaml():
    data = file.load_yaml('tests/data.yaml')
    assert data == {'a': 1, 'b': 2}


def test_config():
    data = file.load_config('tests/data.conf', ensure_number=False, ensure_boolean=False)
    print(data)
    assert data == {'vars': {'a': '1', 'b': '2'}, 'words': {'man': 'true', 'woman': 'off'}}


def test_config_ensure_num():
    data = file.load_config('tests/data.conf', ensure_boolean=False)
    print(data)
    assert data == {'vars': {'a': 1.0, 'b': 2.0}, 'words': {'man': 'true', 'woman': 'off'}}


def test_config_ensure_boolean():
    data = file.load_config('tests/data.conf')
    assert data == {'vars': {'a': 1, 'b': 2}, 'words': {'man': True, 'woman': False}}


def test_trans_value():
    assert trans_value('1') == 1
    assert trans_value('1.1') == 1.1
    assert trans_value('true') is True
    assert trans_value('off') is False
    assert trans_value('~') is None


def test_trans_dict_value():
    assert trans_dict_value({'a': '1', 'b': 'null'}) == {'a': 1, 'b': None}
    assert trans_dict_value({'a': '1', 'b': 'null'}, ordered_dict=True) == OrderedDict([('a',1),('b',None)])


def test_load_excel():
    data = file.load_excel('tests/data.xlsx')
    assert data == [['a', 'b', 'c'], [1.0, 2.2, 0], ['hello', 'world', '']]


def test_load_excel_with_header():
    data = file.load_excel('tests/data.xlsx', header=True)
    assert data == [OrderedDict([('a', 1.0), ('b', 2.2), ('c', 0)]),
                    OrderedDict([('a', 'hello'), ('b', 'world'), ('c', '')])]
    print(data)


def test_load_excel_all_sheets():
    data = file.load_excel('tests/data.xlsx', sheets='all')
    assert data == {'Sheet1': [['a', 'b', 'c'], [1.0, 2.2, 0], ['hello', 'world', '']],
                    'Sheet2': [['a', 'b', 'c'], [1.0, 2.2, 0]]}

def test_load_excel_given_sheets():
    data = file.load_excel('tests/data.xlsx', sheets=[1])
    assert data == {'Sheet2': [['a', 'b', 'c'], [1.0, 2.2, 0]]}
