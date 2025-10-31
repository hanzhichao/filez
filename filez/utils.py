import re
from collections import OrderedDict
from typing import Any

import yaml

VAR_PATTERN = re.compile(r'\$\{([A-Z_][A-Z0-9_]*)(:-([^}]*))?\}', re.I)
BOOL_MAP = {'true': True, 'false': False, 'yes': True, 'no': False, 'on': True, 'off': False,
            '~': None, 'null': None, 'none': None}


def cast_value(value: str) -> Any:
    value = value.strip()
    if value.startswith("'") and value.endswith("'") or value.startswith('"') and value.endswith('"'):
        return value.strip("'").strip('"')
    if value.lower() in BOOL_MAP:
        return BOOL_MAP[value.lower()]
    if re.fullmatch(r'-?\d+', value):
        return int(value)
    if re.fullmatch(r'-?\d+\.\d+', value):
        return float(value)
    if (value.startswith('{') and value.endswith('}')) or (value.startswith('[') and value.endswith(']')):
        return yaml.safe_load(value)

    if ',' in value:
        return [cast_value(v) for v in re.split(r'\s*,\s*', value)]
    return value


def cast_dict_value(data, ordered_dict=False):
    data = {key: cast_value(value) for key, value in data.items()}
    if ordered_dict is True:
        data = OrderedDict(data)
    return data
