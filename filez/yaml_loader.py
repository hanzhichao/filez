import datetime
import os
import re
from pathlib import Path

import yaml

VAR_PATTERN = re.compile(r"""\$\{([A-Z_][A-Z0-9_]*)(:-([^}]*))?\}""", re.IGNORECASE | re.VERBOSE)

# ----------- 正则：ISO-8601 或 时间戳 -----------
ISO_DT_RE = re.compile(r'(?<!\d)(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?)(?!\d)')
ISO_D_RE = re.compile(r'(?<!\d)(\d{4}-\d{2}-\d{2})(?!\d)')
SEC_TS_RE = re.compile(r'(?<!\d)(1[3-9]\d{8})(?!\d)')  # 秒级
MS_TS_RE = re.compile(r'(?<!\d)(1[6-9]\d{11})(?!\d)')  # 毫秒级


class YamlLoader(yaml.SafeLoader):
    def __init__(self, stream):
        super().__init__(stream)
        self.yaml_path = Path(self.name).resolve()


# def env_constructor(loader, node):
#     return os.getenv(loader.construct_scalar(node), '')


def merge_constructor(loader, node):
    seq = loader.construct_sequence(node)
    result = {}
    for d in seq:
        result.update(d)
    return result


def _replace_vars(text: str) -> str:
    def _repl(match: re.Match) -> str:
        var_name, _, default = match.groups()
        return os.environ.get(var_name, default or "")

    return VAR_PATTERN.sub(_repl, text)


def env_var_constructor(loader: yaml.SafeLoader, node: yaml.ScalarNode) -> str:
    value = loader.construct_scalar(node)
    return _replace_vars(value)


# ----------- 构造器 -----------
def _parse_dt(text: str) -> datetime.datetime:
    text = text.strip()
    # 1. ISO-8601 字符串（秒或毫秒）
    if (m := ISO_DT_RE.fullmatch(text)):
        return datetime.datetime.fromisoformat(m.group(1).replace(' ', 'T'))
    # 2. 秒级时间戳
    if (m := SEC_TS_RE.fullmatch(text)):
        return datetime.datetime.fromtimestamp(int(m.group(1)))
    # 3. 毫秒级时间戳
    if (m := MS_TS_RE.fullmatch(text)):
        return datetime.datetime.fromtimestamp(int(m.group(1)) / 1000)
    raise ValueError(f"无法解析为 datetime: {text!r}")


def _parse_date(text: str) -> datetime.date:
    text = text.strip()
    # 1. ISO 日期
    if (m := ISO_D_RE.fullmatch(text)):
        return datetime.date.fromisoformat(m.group(1))
    # 2. 秒级时间戳 → date
    if (m := SEC_TS_RE.fullmatch(text)):
        return datetime.datetime.fromtimestamp(int(m.group(1))).date()
    # 3. 毫秒级时间戳 → date
    if (m := MS_TS_RE.fullmatch(text)):
        return datetime.datetime.fromtimestamp(int(m.group(1)) / 1000).date()
    raise ValueError(f"无法解析为 date: {text!r}")


def datetime_constructor(loader: yaml.SafeLoader, node: yaml.ScalarNode) -> datetime.datetime:
    return _parse_dt(loader.construct_scalar(node))


def date_constructor(loader: yaml.SafeLoader, node: yaml.ScalarNode) -> datetime.date:
    return _parse_date(loader.construct_scalar(node))


def get_yaml_loader(file: "Filez", parse_env=True, parse_datetime=True, **kwargs):
    def file_constructor(loader: YamlLoader, node):
        rel_path = Path(loader.construct_scalar(node))
        abs_path = (loader.yaml_path.parent / rel_path).resolve()
        return file.load(abs_path, parse_env=parse_env, parse_datetime=parse_datetime, **kwargs)

    YamlLoader.add_constructor('!file', file_constructor)
    YamlLoader.add_constructor('!datetime', datetime_constructor)
    YamlLoader.add_constructor('!date', date_constructor)
    YamlLoader.add_constructor('!merge', merge_constructor)


    if parse_env:
        # YamlLoader.add_constructor('!env', env_constructor)
        YamlLoader.add_constructor('tag:yaml.org,2002:str', env_var_constructor)
    return YamlLoader
