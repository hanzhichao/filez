import json
import datetime
import re
from typing import Any, Union

ISO_DATETIME_PATTERN = re.compile(
    r'^\d{4}-\d{2}-\d{2}'          # 日期 2025-06-01
    r'[T ]'                        # 分隔符 T 或空格
    r'\d{2}:\d{2}:\d{2}'           # 时分秒 12:30:45
    r'(?:\.\d{1,6})?'              # 可选毫秒 .534
    r'$'
)

ISO_DATE_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}$')
TIMESTAMP_SEC_PATTERN = re.compile(r'(?<!\d)(1[3-9]\d{8})(?!\d)')
TIMESTAMP_MS_PATTERN = re.compile(r'(?<!\d)(1[6-9]\d{11})(?!\d)')


# ========== 自定义编码器 ==========
class DateTimeEncoder(json.JSONEncoder):
    """把 datetime/date 转成 ISO-8601 字符串"""
    def default(self, obj: Any) -> Any:
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        # 如需时间戳版本，打开下面注释
        # if isinstance(obj, datetime.datetime):
        #     return obj.timestamp()        # float
        # if isinstance(obj, datetime.date):
        #     return datetime.datetime.combine(obj, datetime.time.min).timestamp()
        return super().default(obj)

# ========== 自定义解码器 ==========
def datetime_hook(dct: dict) -> dict:
    """把 ISO-8601 字符串还原成 datetime/date"""
    for k, v in dct.items():
        if isinstance(v, str):
            # datetime
            if ISO_DATETIME_PATTERN.fullmatch(v):
                try:
                    dct[k] = datetime.datetime.fromisoformat(v)
                    continue
                except ValueError:
                    pass
            # date
            if ISO_DATE_PATTERN.fullmatch(v):
                try:
                    dct[k] = datetime.date.fromisoformat(v)
                    continue
                except ValueError:
                    pass
            # 时间戳 float → datetime（可选）
            # if isinstance(v, float):
            #     dct[k] = datetime.datetime.fromtimestamp(v)
    return dct
