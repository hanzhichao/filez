import configparser
import os
import re
from typing import Any, Dict, Mapping, Optional

from filez.utils import cast_value

VAR_PATTERN = re.compile(r'\$\{([A-Z_][A-Z0-9_]*)(:-([^}]*))?\}', re.I)


def _substitute_env(text: str) -> str:
    def _repl(m: re.Match) -> str:
        var, _, default = m.groups()
        return os.environ.get(var, default if default is not None else '')

    return VAR_PATTERN.sub(_repl, text)


class IniParser(configparser.ConfigParser):
    def __init__(self, *, allow_no_value=True, parse_value=True, parse_env=True, parse_datetime=True, **kw):
        super().__init__(allow_no_value=allow_no_value, interpolation=configparser.BasicInterpolation(), **kw)
        self.optionxform = str
        self._delimiters = ('=', ':')
        self._parse_value = parse_value
        self._parse_env = parse_env
        self._parse_datetime = parse_datetime  # todo

    def _read(self, fp, filename):
        lines = []
        for raw in fp:
            line = re.sub(r'(?<!")(?<!\\)\s+[#;].*$', '', raw).rstrip()
            if line:
                lines.append(line + '\n')
        super()._read(lines, filename)

    def get(self, section: str, option: str, *, raw: bool = False, vars: Optional[Mapping[str, str]] = None,
            fallback: Any = None) -> Any:
        value = super().get(section, option, raw=raw, vars=vars, fallback=fallback)
        if raw or value is None:
            return value
        if self._parse_env:
            value = _substitute_env(value)
        if self._parse_value:
            value = cast_value(value)
        return value

    def items_dict(self) -> Dict[str, Dict[str, Any]]:
        return {sect: {k: self.get(sect, k) for k in self.options(sect)} for sect in self.sections()}
