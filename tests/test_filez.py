from datetime import date, datetime
from pathlib import Path
from pprint import pprint

import pytest

from filez import file


@pytest.fixture
def testdata_dir() -> Path:
    return Path(__file__).parent / 'testdata'


def test_load_txt(testdata_dir):
    data = file.load(testdata_dir / 'data.txt')
    assert data == ['line1', 'line2', 'line3', 'line4']


def test_load_csv(testdata_dir):
    data = file.load(testdata_dir / 'data.csv')
    assert data == [['a', 'b', 'c'], [1, 2.2, True], [4, 5, 6]]

    data = file.load(testdata_dir / 'data.csv', skip=1)
    assert data == [[1, 2.2, True], [4, 5, 6]]

    data = file.load(testdata_dir / 'data.csv', header=True)
    assert data == [{'a': 1, 'b': 2.2, 'c': True}, {'a': 4, 'b': 5, 'c': 6}]


def test_json(testdata_dir):
    data = file.load(testdata_dir / 'data.json', parse_datetime=True)
    assert data == {'birthday': date(1990, 1, 1),
                    'created_at': datetime(2025, 6, 1, 12, 30, 45),
                    'name': 'Alice'}


def test_yaml(testdata_dir, monkeypatch):
    monkeypatch.setenv("PASSWORD", "123456")
    monkeypatch.setenv("PORT", "8888")
    data = file.load(testdata_dir / 'data.yaml', parse_datetime=True)
    assert data == {'a': 1,
                    'b': 2,
                    'birth': date(1990, 1, 1),
                    'birth_ts': date(2024, 6, 1),
                    'created': datetime(2025, 6, 1, 12, 30, 45),
                    'created_ms': datetime(2025, 6, 1, 12, 30, 45, 123456),
                    'debug': 'true',
                    'file_data': {'birthday': date(1990, 1, 1),
                                  'created_at': datetime(2025, 6, 1, 12, 30, 45),
                                  'name': 'Alice'},
                    'list1': [1, 2, 3],
                    'list2': [4, 5],
                    'merged_list': {},
                    'msg': 'port is 8888',
                    'port': '8888',
                    'ts_ms': datetime(2024, 6, 1, 17, 30, 45, 123000),
                    'ts_sec': datetime(2024, 6, 1, 17, 30, 45)}


def test_load_ini(testdata_dir):
    data = file.load_ini(testdata_dir / 'data.ini')

    assert data == {'App': {'Debug': True,
                            'backends': ['127.0.0.1', '192.168.1.2'],
                            'desc': 'This is a multi-line\ndescription.',
                            'message': ['hi', 'superhin'],
                            'params': {'k': 'v', 'n': 1},
                            'release': None,
                            'timeout': 3.5,
                            'version': '1'},
                    'db': {'db_uri': 'mysql://superhin:@localhost:3306/testdb?charset=utf8',
                           'host': 'localhost',
                           'password': '',
                           'port': 3306,
                           'user': 'superhin',
                           'version': '1'}}


def test_load_xls(testdata_dir):
    data1 = file.load(testdata_dir / 'data.xls')
    assert data1 == [['a', 'b', 'c'], [1.0, 2.2, 0], ['hello', 'world', '']]
    data2 = file.load(testdata_dir / 'data.xls', skip=1)
    assert data2 == [[1.0, 2.2, 0], ['hello', 'world', '']]
    data3 = file.load(testdata_dir / 'data.xls', header=True)
    assert data3 == [{'a': 1.0, 'b': 2.2, 'c': 0}, {'a': 'hello', 'b': 'world', 'c': ''}]
    # load all_sheets:
    data = file.load(testdata_dir / 'data.xls', sheets='all')
    assert data == {'Sheet1': [['a', 'b', 'c'], [1.0, 2.2, 0], ['hello', 'world', '']],
                    'Sheet2': [['a', 'b', 'c'], [1.0, 2.2, 0]]}

    # load given_sheets:
    data = file.load(testdata_dir / 'data.xls', skip=1, sheets=[1])
    assert data == {'Sheet2': [[1.0, 2.2, 0]]}


def test_load_xlsx(testdata_dir):
    data1 = file.load(testdata_dir / 'data.xlsx')
    assert data1 == [['a', 'b', 'c'],
                     [1, 2.2, False],
                     ['hello', 'world', None]], 'single sheet'
    # with skip
    data2 = file.load(testdata_dir / 'data.xlsx', skip=1)
    assert data2 == [[1, 2.2, False], ['hello', 'world', None]], 'single sheet with skip'

    # with header
    data3 = file.load(testdata_dir / 'data.xlsx', header=True)
    assert data3 == [{'a': 1, 'b': 2.2, 'c': False},
                     {'a': 'hello', 'b': 'world', 'c': None}], 'single sheet with header'


def test_load_xml(testdata_dir):
    data1 = file.load(testdata_dir / 'data.xml')
    assert data1 == {
        'bookstore':
            {'book': [
                {':category': 'COOKING',
                 'author': 'Giada De Laurentiis',
                 'price': '30.00',
                 'title': {':lang': 'en', 'text': 'Everyday Italian'},
                 'year': '2005'},
                {':category': 'WEB',
                 'author': 'Erik T. Ray',
                 'price': '39.95',
                 'title': {':lang': 'en', 'text': 'Learning XML'},
                 'year': '2003'}]}
    }
    data2 = file.load(testdata_dir / 'data.xml', ignore_attrs=True)
    assert data2 == {
        'bookstore':
            {'book': [
                {'author': 'Giada De Laurentiis',
                 'price': '30.00',
                 'title': 'Everyday Italian',
                 'year': '2005'},
                {'author': 'Erik T. Ray',
                 'price': '39.95',
                 'title': 'Learning XML',
                 'year': '2003'}
            ]}
    }


def test_load_html(testdata_dir):
    data = file.load(testdata_dir / 'data.html')
    assert data == {
        'head': [
            {'tag': 'meta', 'attrs': {'charset': 'UTF-8'}, 'children': [], 'text': ''},
            {'tag': 'title', 'attrs': {}, 'children': [], 'text': 'Title'}],
        'body': [
            {'tag': 'h1', 'attrs': {}, 'children': [], 'text': '标题'},
            {'tag': 'p', 'attrs': {}, 'children': [], 'text': '内容'},
            {'tag': 'form', 'attrs': {'name': 'form1', 'method': 'post'}, 'children':
                [
                    {'tag': 'input', 'attrs': {'name': 'username', 'type': 'text'}, 'children': [], 'text': ''},
                    {'tag': 'input', 'attrs': {'type': 'submit'}, 'children': [], 'text': ''}
                ], 'text': ''}]}


def test_load_properties(testdata_dir):
    data = file.load(testdata_dir / 'data.properties')
    assert data == {'appId': 'cactus',
                    'publicKey': '-----BEGIN PUBLIC KEY-----\\n'
                                 'MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEP9eQZFl3j5zZX8bmYYEznA0z3/X+\\n'
                                 'TooIQ11rxFcPZsTvJPLCUY7NHasUenXJngmvRXSnP4odegaoe4usLDv/3A==\\n'
                                 '-----END PUBLIC KEY-----',
                    'app': {'config': {'host': '127.0.0.1', 'port': '8080'}}}


def test_load_toml(testdata_dir):
    data = file.load(testdata_dir / 'data.toml')
    assert data == {'vars': {'a': 1, 'b': 2}, 'words': {'Man': True, 'Woman': False}}


def test_load_vcf(testdata_dir):
    data = file.load(testdata_dir / 'data.vcf')
    assert data == [
        {'adr': ['',
                 '',
                 '123 Main St',
                 'Beijing',
                 '',
                 '100000',
                 'China',
                 ['', '', '456 Park Ave', 'Shanghai', '', '200000', 'China']],
         'bday': date(1990, 1, 1),
         'email': [{'types': ['INTERNET,WORK'], 'value': 'alice@example.com'},
                   {'types': ['INTERNET,HOME'], 'value': 'alice.home@example.com'}],
         'fn': 'Alice Smith',
         'n': ['Smith', 'Alice', '', '', ''],
         'nickname': 'Al',
         'nid': 'abc-123',
         'note': 'Test contact for demo',
         'org': ['Example Inc.'],
         'tel': [{'types': ['WORK,VOICE'], 'value': '+86-138-0000-0000'},
                 {'types': ['HOME,VOICE'], 'value': '+86-010-88888888'}],
         'title': 'Software Engineer',
         'url': 'https://alice.example.com',
         'version': '3.0',
         'x-socialprofile': 'https://linkedin.com/in/alicesmith'},
        {'adr': ['', '', '789 Business Rd', 'Shenzhen', '', '518000', 'China'],
         'bday': date(1985, 5, 15),
         'email': {'types': ['INTERNET,WORK'], 'value': 'bob@corp.com'},
         'fn': 'Bob Jones',
         'n': ['Jones', 'Bob', '', '', ''],
         'nickname': 'Bobby',
         'nid': 'def-456',
         'note': 'Bob likes coffee',
         'org': ['Corp Ltd.'],
         'tel': {'types': ['CELL,VOICE'], 'value': '+86-139-1111-1111'},
         'title': 'Product Manager',
         'url': 'https://bob.corp.com',
         'version': '3.0',
         'x-ablabel': 'Favorites'},
        {'adr': ['', '', '321 Campus Ave', 'Hangzhou', '', '310000', 'China'],
         'bday': date(2000, 12, 31),
         'email': {'types': ['INTERNET'], 'value': 'carol@student.com'},
         'fn': 'Carol Lee',
         'n': ['Lee', 'Carol', '', '', ''],
         'note': 'New graduate',
         'org': ['University'],
         'tel': {'types': ['CELL,VOICE'], 'value': '+86-137-2222-2222'},
         'title': 'Student',
         'url': 'https://carol.dev'}
    ]


def test_convert(testdata_dir, monkeypatch, tmpdir):
    monkeypatch.setenv("PASSWORD", "123456")
    monkeypatch.setenv("PORT", "8888")
    input_file_path = testdata_dir / 'data.yaml'
    for file_type in ['json', 'toml', 'yaml']:
        output_file_path = tmpdir / f'data.{file_type}'
        file.convert(input_file_path, output_file_path, parse_datetime=True)
        data = file.load(output_file_path, parse_datetime=True)
        assert data == {'a': 1,
                        'b': 2,
                        'birth': date(1990, 1, 1),
                        'birth_ts': date(2024, 6, 1),
                        'created': datetime(2025, 6, 1, 12, 30, 45),
                        'created_ms': datetime(2025, 6, 1, 12, 30, 45, 123456),
                        'debug': 'true',
                        'file_data': {'birthday': date(1990, 1, 1),
                                      'created_at': datetime(2025, 6, 1, 12, 30, 45),
                                      'name': 'Alice'},
                        'list1': [1, 2, 3],
                        'list2': [4, 5],
                        'merged_list': {},
                        'msg': 'port is 8888',
                        'port': '8888',
                        'ts_ms': datetime(2024, 6, 1, 17, 30, 45, 123000),
                        'ts_sec': datetime(2024, 6, 1, 17, 30, 45)}


@pytest.mark.skip('fixme')
def test_load_pem(testdata_dir):
    # data = file.load(testdata_dir / 'cert.pem')
    # pprint(data)
    # if der[0] != 0x30: raise ValueError("Not a SEQUENCE")
    # E       ValueError: Not a SEQUENCE
    data = file.load(testdata_dir / 'ec_private_key_pkcs8.pem')
    pprint(data)  # fixme {}
    data = file.load(testdata_dir / 'ec_private_key_pkcs13.pem')
    pprint(data)
    assert data == {
        'ec_private_key': '30770201010420b6fd5d544f09a3e0b6604b4dfbac6264c307300258420c3fb1b8eedb544a0719a00a06082a8648ce3d030107a1440342000420be56c478e4ff209ccc43e533170b49262ab0eb38ba11b396ad05427231e2e26bbc3688aba86dfad753d950277c34cd6f286425659f082a5ef667952108fa85'}

    data = file.load(testdata_dir / 'rsa_private_key.pem')
    pprint(data)

    # data = file.load(testdata_dir / 'rsa_public_key.pem')
    # pprint(data) # fixme
    # if rest: raise ValueError("Extra data after RSA pubkey")
    # E       ValueError: Extra data after RSA pubkey

    # data = file.load(testdata_dir / 'x509_public_key.pem')
    # pprint(data) # fixme
    # if rest: raise ValueError("Extra data after RSA pubkey")
    # E       ValueError: Extra data after RSA pubkey

    data = file.load(testdata_dir / 'sm2_private_key.pem')
    pprint(data)  # fixme
