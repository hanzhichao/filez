import re
from collections import OrderedDict
from xml.etree import ElementTree
from html.parser import HTMLParser
from configparser import ConfigParser, NoSectionError, NoOptionError
from typing import Union
from pathlib import Path
from string import Template
import os

SINGLE_TAGS = ['br','hr','img','input','param','meta','link']

def trans_value(value, ensure_number=True, ensure_boolean=True):
    if ensure_boolean is True:
        if value.lower() in ('true', 'on'):
            return True
        elif value.lower() in ('false', 'off'):
            return False
        elif value.lower() in ('null', 'none', '~'):
            return None

    if ensure_number is True:
        if value.isnumeric():
            return int(value)
        else:
            try:
                return float(value)
            except ValueError:
                pass
    return value

def trans_dict_value(data, ensure_number=True, ensure_boolean=True, ordered_dict=False):
    data = {key: trans_value(value, ensure_number, ensure_boolean) for key, value in data.items()}
    if ordered_dict is True:
        data = OrderedDict(data)
    return data


def get_xml_children(node):
    children = node.getchildren()
    if children:
        return [{'tag': node.tag,
                 'attrs': node.attrib,
                 'text': node.text.strip(),
                 'children': get_xml_children(child)
                 } for child in children]
    else:
        return {'tag': node.tag,
                'attrs': node.attrib,
                'text': node.text or None}


class MyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.data = None

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag in SINGLE_TAGS:
            return self.handle_startendtag(tag, attrs)
        self.stack.append(dict(tag=tag, attrs=dict(attrs), children=[], text=''))

    def handle_endtag(self, tag):
        self.data = current = self.stack.pop()
        if self.stack:
            parent = self.stack[-1]
            parent['children'].append(current)

    def handle_startendtag(self, tag, attrs):
        if self.stack:
            parent = self.stack[-1]
            parent['children'].append(dict(tag=tag, attrs=dict(attrs), children=[], text=''))

    def handle_data(self, data):
        if not data.strip():
            return
        if self.stack:
            self.stack[-1]['text'] = data.strip()


class CaseSensitiveiniigParser(ConfigParser):
    def optionxform(self, optionstr):
        return optionstr

    def ensure_value(self, value: str):
        """转为value为各种类型"""
        if value is None:
            return value
        # 转为整形
        if value.isdigit():
            return int(value)

        # 转为True、False或None
        if value.lower() in ['true', 'on']:
            return True

        if value.lower() in ['false', 'off']:
            return False

        if value.lower() in ['~', 'none', 'null']:
            return None

        # 尝试转为浮点型
        try:
            return float(value)
        except:
            pass

        # 尝试解码JSON
        json = __import__('json')
        if value.lstrip().startswith('[') or value.lstrip().startswith('{'):
            try:
                return json.loads(value.replace("'", '"'))
            except Exception as ex:
                # print(ex)
                pass
        # 替换${变量}为系统环境变量值
        if '$' in value:
            return Template(value).safe_substitute(**dict(os.environ))

        return value

    def get(self, section, option, *args, **kwargs):
        try:
            value = super().get(section, option, *args, **kwargs)
        except (NoSectionError, NoOptionError):
            return None
        return self.ensure_value(value)

    def items(self, *args, **kwargs):
        items = super().items(*args, **kwargs)
        return [(item[0], self.ensure_value(item[1])) for item in items]

class Filez(object):

    @staticmethod
    def open(file_path: Union[Path, str], **kwargs):
        encoding = kwargs.get('encoding', 'utf-8')
        with open(file_path, encoding=encoding) as f:
            raw = f.read()
        return raw

    @staticmethod
    def load_txt(file_path: Union[Path, str], **kwargs):
        encoding = kwargs.get('encoding', 'utf-8')
        with open(file_path, encoding=encoding) as f:
            data = [line.strip() for line in f.readlines()]
        return data

    @staticmethod
    def load_csv(file_path: Union[Path, str], **kwargs):
        csv = __import__('csv')
        encoding = kwargs.get('encoding', 'utf-8')
        header = kwargs.get('header', False)
        ensure_number = kwargs.get('ensure_number', True)
        ensure_boolean = kwargs.get('ensure_boolean', True)

        with open(file_path, encoding=encoding) as f:
            reader = csv.DictReader(f) if header else csv.reader(f)
            data = list(reader)

        if ensure_number or ensure_boolean:
            if header:
                collections = __import__('collections')
                data = list(map(lambda line:
                                dict({key: trans_value(value, ensure_number, ensure_boolean)
                                                         for key,value in line.items()}), data))
            else:
                data = list(map(lambda line: list(map(lambda value: trans_value(value, ensure_number, ensure_boolean),
                                                      line)), data))
        return data

    @staticmethod
    def load_json(file_path: Union[Path, str], **kwargs):
        json = __import__('json')
        encoding = kwargs.get('encoding', 'utf-8')
        with open(file_path, encoding=encoding) as f:
            data = json.load(f)
        return data

    @staticmethod
    def load_yaml(file_path, **kwargs):
        yaml = __import__('yaml')
        encoding = kwargs.get('encoding', 'utf-8')
        with open(file_path, encoding=encoding) as f:
            data = yaml.safe_load(f)
        return data

    @staticmethod
    def load_ini(file_path: Union[Path, str], **kwargs):  # todo case sensitive, sub section insure_boolean
        configparser = __import__('configparser')
        encoding = kwargs.get('encoding', 'utf-8')

        conf = CaseSensitiveiniigParser(allow_no_value=True)
        conf.read(file_path, encoding=encoding)

        data = {section: dict(conf.items(section)) for section in conf.sections()}
        return data

    @staticmethod
    def load_xls(file_path: Union[Path, str], **kwargs):  # todo float->int ->str, FALSE -> False, '' -> None
        xlrd = __import__('xlrd')  # todo change to openpyxl
        header = kwargs.get('header', False)
        sheets = kwargs.get('sheets')
        wb = xlrd.open_workbook(file_path)
        all_sheets = wb.sheets()
        if not all_sheets:
            return
        def get_sh_data(sh, header):
            sh_data = [sh.row_values(i) for i in range(sh.nrows)]
            if header and sh_data:  # todo column name as header
                headers = sh_data[0]
                sh_data = [dict(zip(headers, line)) for line in sh_data[1:]]
            return sh_data

        if sheets:
            if isinstance(sheets, (list, tuple)):
                keep_sheets = [wb.sheet_by_index(i) if isinstance(i, int) else wb.sheet_by_name(i)
                               for i in sheets] # todo try
            elif sheets == 'all':
                keep_sheets = all_sheets
            else:
                return  # todo
            data = {}
            for sh in keep_sheets:
                data[sh.name] = get_sh_data(sh, header)
        else:
            sh = all_sheets[0]
            data = get_sh_data(sh, header)
        return data

    @staticmethod
    def load_xlsx(file_path, **kwargs) -> list:
        openpyxl = __import__('openpyxl')
        header = kwargs.get('header', False)
        excel = openpyxl.load_workbook(file_path)  # 有路径应带上路径
        # 使用指定工作表
        sheet = excel.active
        result = []
        # 读取标题行
        for row in sheet.iter_rows(max_row=1):
            title_row = [cell.value for cell in row]
            if header is False:
                result.append(title_row)
        # 读取标题行以外数据
        for row in sheet.iter_rows(min_row=2):
            row_data = [cell.value for cell in row]
            if header is False:
                result.append(row_data)
            else:
                result.append(dict(zip(title_row, row_data)))
        return result

    @staticmethod
    def load_xml(file_path: Union[Path, str], **kwargs):
        encoding = kwargs.get('encoding', 'utf-8')
        with open(file_path, encoding=encoding) as f:
            raw = f.read().strip()
        root = ElementTree.fromstring(raw)
        data = get_xml_children(root)
        return data

    @staticmethod
    def load_html(file_path: Union[Path, str], **kwargs):
        parser = MyHTMLParser()
        encoding = kwargs.get('encoding', 'utf-8')
        with open(file_path, encoding=encoding) as f:
            raw = f.read().strip()
        parser.feed(raw)
        return parser.data

    @staticmethod
    def load_properties(filepath, **kwargs):
        with open(filepath) as f:
            raw = f.read()
        # 去掉注释和处理换行
        body = re.sub(r'#.*|\\\n', '', raw)
        data = {}
        for line in body.split('\n'):
            # 如果非空
            if line:
                key, value = line.split('=', 1)
                # 处理多级属性，例如 a.b.c = 1
                if '.' in key:
                    nodes = key.split(".")
                    cur = data
                    for node in nodes[:-1]:
                        if cur.get(node) is None:
                            cur[node] = {}
                        else:
                            assert isinstance(cur.get(node), dict), "data format error"
                        cur = cur[node]
                    cur[nodes[-1]] = value
                else:
                    data.update({key: value})
        return data

    @staticmethod
    def load_toml(file_path, **kwargs):
        toml = __import__('toml')
        import toml
        encoding = kwargs.get('encoding', 'utf-8')
        with open(file_path, encoding=encoding) as f:
            return toml.load(f)

    def load(self, file_path: Union[Path, str], **kwargs):  # todo file_type='config'
        file_path = str(file_path)
        if file_path.endswith('.csv'):
            return self.load_csv(file_path, **kwargs)
        elif file_path.endswith('.json'):
            return self.load_json(file_path, **kwargs)
        elif file_path.endswith('.yml') or file_path.endswith('.yaml'):
            return self.load_yaml(file_path, **kwargs)
        elif file_path.endswith('.conf') or file_path.endswith('.ini') or file_path.endswith('.config'):
            return self.load_ini(file_path, **kwargs)
        elif file_path.endswith('.xlsx'):
            return self.load_xlsx(file_path, **kwargs)
        elif file_path.endswith('.xls'):
            return self.load_xls(file_path, **kwargs)
        elif file_path.endswith('.xml'):
            return self.load_xml(file_path, **kwargs)
        elif file_path.endswith('.html') or file_path.endswith('.htm'):
            return self.load_html(file_path, **kwargs)
        elif file_path.endswith('.properties'):
            return self.load_properties(file_path, **kwargs)
        elif file_path.endswith('.toml'):
            return self.load_toml(file_path, **kwargs)
        else:
            return self.load_txt(file_path, **kwargs)


file = filez = Filez()
