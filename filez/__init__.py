import json
import os
from pathlib import Path
from typing import Union, List
from xml.etree import ElementTree

from .excel_parser import load_xls, load_xlsx
from .json_encoder import datetime_hook, DateTimeEncoder
from .pem_parser import parse_pem_to_dict
from .properties_parser import parse_properties
from .utils import cast_value
from .vcard3_parser import parse_vcard3
from .xml_parser import get_xml_children, parse_xml_node

FILE_TYPES = {
    '.ini': 'ini',
    '.conf': 'ini',
    '.config': 'ini',
    '.properties': 'properties',
    '.json': 'json',
    '.abi': 'json',
    '.har': 'json',
    '.yaml': 'yaml',
    '.yml': 'yaml',
    '.csv': 'csv',
    '.tsv': 'csv',
    '.psv': 'csv',
    '.toml': 'toml',
    '.htm': 'html',
    '.html': 'html',
    '.xml': 'xml',
    '.xls': 'xls',
    '.xlsx': 'xlsx',
    '.xmind': 'xmind',
    '.vcf': 'vcf',
    # '.pem': 'pem',
    # '.cert': 'pem',
    # '.ca': 'pem',
    # '.key': 'pem',
}


class Filez(object):
    def __init__(self):
        self.parse_value = True  # auto cast int, float, bool, list, dict value
        self.parse_env = True
        self.parse_datetime = False
        self.file_types = FILE_TYPES

    @property
    def yaml_loader(self):
        from .yaml_loader import get_yaml_loader
        return get_yaml_loader(self, self.parse_env, self.parse_datetime)

    @property
    def ini_parser(self):
        from .ini_parser import IniParser
        return IniParser

    @property
    def html_parser(self):
        from .html_parser import HtmlParser
        return HtmlParser

    def register(self, ext: str, file_type: str):
        self.file_types[ext] = file_type

    @staticmethod
    def open(file_path: Union[Path, str], **kwargs) -> str:
        encoding = kwargs.pop('encoding', 'utf-8')
        with open(file_path, encoding=encoding) as f:
            raw = f.read()
        return raw

    @staticmethod
    def load_txt(file_path: Union[Path, str], **kwargs) -> List[str]:
        encoding = kwargs.pop('encoding', 'utf-8')
        with open(file_path, encoding=encoding) as f:
            data = [line.strip() for line in f.readlines()]
        return data

    def load_csv(self, file_path: Union[Path, str], **kwargs) -> Union[List[list], List[dict]]:
        import csv
        encoding = kwargs.pop('encoding', 'utf-8')
        header = kwargs.get('header', False)
        skip = kwargs.get('skip', 0)

        with open(file_path, encoding=encoding) as f:
            reader = csv.DictReader(f) if header else csv.reader(f)
            if skip > 0:
                for _ in range(skip):  # 消耗掉前 N 行
                    next(reader, None)
            if self.parse_value:
                if header:
                    return list(map(lambda line:
                                    dict({key: cast_value(value)
                                          for key, value in line.items()}), reader))
                return list(map(lambda line: list(map(lambda value: cast_value(value),
                                                      line)), reader))
            return list(reader)

    def load_json(self, file_path: Union[Path, str], **kwargs) -> Union[dict, list]:
        encoding = kwargs.pop('encoding', 'utf-8')
        parse_env = kwargs.pop('parse_env', self.parse_env) # todo
        parse_datetime = kwargs.pop('parse_datetime', self.parse_datetime)
        with open(file_path, encoding=encoding) as f:
            if parse_datetime:
                return json.load(f, object_hook=datetime_hook, **kwargs)
            return json.load(f, **kwargs)

    def load_yaml(self, file_path, **kwargs) -> Union[dict, list]:
        import yaml
        encoding = kwargs.pop('encoding', 'utf-8')
        if 'parse_env' in kwargs or 'parse_datetime' in kwargs:
            parse_env = kwargs.pop('parse_env', self.parse_env)
            parse_datetime = kwargs.pop('parse_datetime', self.parse_datetime)
            from .yaml_loader import get_yaml_loader
            yaml_loader = get_yaml_loader(self, parse_env, parse_datetime)
        else:
            yaml_loader = self.yaml_loader

        with open(file_path, encoding=encoding) as f:
            data = yaml.load(f, Loader=yaml_loader)
        return data

    def load_ini(self, file_path: Union[Path, str], **kwargs) -> dict:
        encoding = kwargs.pop('encoding', 'utf-8')
        parse_value = kwargs.pop('parse_value', self.parse_value)
        parse_env = kwargs.pop('parse_env', self.parse_env)
        parse_datetime = kwargs.pop('parse_datetime', self.parse_datetime)
        cfg = self.ini_parser(parse_value=parse_value, parse_env=parse_env, parse_datetime=parse_datetime, **kwargs)
        cfg.read(file_path, encoding=encoding)
        data = cfg.items_dict()
        return data

    @staticmethod
    def load_xls(file_path: Union[Path, str], **kwargs) -> dict:
        header = kwargs.get('header', False)
        skip = kwargs.get('skip', 0)
        sheets = kwargs.get('sheets', None)
        data = load_xls(file_path, header=header, skip=skip, sheets=sheets)
        return data

    @staticmethod
    def load_xlsx(file_path, **kwargs) -> list:
        header = kwargs.get('header', False)
        skip = kwargs.get('skip', 0)
        sheets = kwargs.get('sheets', None)
        data = load_xlsx(file_path, header=header, skip=skip, sheets=sheets)
        return data

    def load_xml(self, file_path: Union[Path, str], **kwargs) -> dict:
        raw = self.open(file_path, **kwargs)
        root = ElementTree.fromstring(raw)
        data = parse_xml_node(root, **kwargs)
        return data

    def load_html(self, file_path: Union[Path, str], **kwargs) -> dict:
        raw = self.open(file_path, **kwargs)
        parser = self.html_parser()
        parser.feed(raw)
        root = parser.data['children']
        head, body = {}, {}
        for item in root:
            if item['tag'] == 'head':
                head = item['children']
            elif item['tag']  == 'body':
                body = item['children']
        return {'head': head, 'body': body}

    def load_properties(self, file_path, **kwargs) -> dict:
        raw = self.open(file_path, **kwargs)
        data = parse_properties(raw)
        return data

    @staticmethod
    def load_toml(file_path, **kwargs) -> Union[dict, list]:
        toml = __import__('toml')
        encoding = kwargs.pop('encoding', 'utf-8')
        with open(file_path, encoding=encoding) as f:
            return toml.load(f)

    def load_pem(self, file_path, **kwargs) -> dict:
        raw = self.open(file_path, **kwargs)
        data = parse_pem_to_dict(raw)
        return data

    def load(self, file_path: Union[Path, str], **kwargs) -> Union[dict, list]:  # todo file_type='config'
        file_path = str(file_path)
        _, ext = os.path.splitext(file_path)
        file_type = self.file_types.get(ext, 'txt')
        load_method = getattr(self, f'load_{file_type}')
        return load_method(file_path, **kwargs)

    def load_xmind(self, file_path, **kwargs):
        from xmindparser import xmind_to_dict
        data = xmind_to_dict(file_path)[0]
        return data

    def load_vcf(self, file_path, **kwargs):
        raw = self.open(file_path, **kwargs)
        data = parse_vcard3(raw)
        return data

    @staticmethod
    def save_json(data: Union[dict, list], file_path: Union[Path, str], **kwargs):
        with open(file_path, 'w') as f:
            json.dump(data, f, cls=DateTimeEncoder, **kwargs)

    @staticmethod
    def save_yaml(data: Union[dict, list], file_path: Union[Path, str]):
        yaml = __import__('yaml')
        with open(file_path, 'w') as f:
            yaml.safe_dump(data, f)

    @staticmethod
    def save_toml(data: Union[dict, list], file_path: Union[Path, str]):
        toml = __import__('toml')
        with open(file_path, 'w') as f:
            toml.dump(data, f)

    def convert(self, input_file_path: Union[Path, str], output_file_path: Union[Path, str], **kwargs):
        data = self.load(input_file_path, **kwargs)
        output_file_path = str(output_file_path)
        if output_file_path.endswith('.json'):
            return self.save_json(data, output_file_path)
        if output_file_path.endswith('.yml') or output_file_path.endswith('.yaml'):
            return self.save_yaml(data, output_file_path)
        if output_file_path.endswith('.toml'):
            return self.save_toml(data, output_file_path)
        raise Exception('Output file format not support, only support json,yaml,toml')


file = filez = Filez()
