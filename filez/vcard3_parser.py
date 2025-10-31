import re
from datetime import date
from typing import Dict, Any

# ---------- 读 ----------
VCARD_BLOCK_RE = re.compile(r'BEGIN:VCARD\s*\n(.*?)\nEND:VCARD', re.MULTILINE | re.DOTALL)


def parse_vcard3_item(text: str) -> Dict[str, Any]:
    """
    解析 vCard 3.0 文本 → 统一小写 key 的字典
    支持字段：n, nid, fn, nickname, bday, tel, email, org, title, url, addr, note, version 及任意扩展
    """
    match = VCARD_BLOCK_RE.search(text.strip())
    if not match:
        raise ValueError("Not a valid vCard 3.0 block")
    lines = [ln.strip() for ln in match.group(1).splitlines() if ln.strip()]
    data: Dict[str, Any] = {}

    def _split_left_right(line: str):
        """返回 (field, attrs_list, value)"""
        if ':' not in line:
            return None, [], ''
        left, right = line.split(':', 1)
        parts = left.split(';')
        field = parts[0].upper()
        attrs = parts[1:] if len(parts) > 1 else []
        return field, attrs, right.strip()

    for line in lines:
        field, attrs, val = _split_left_right(line)
        if field is None:
            continue
        key = field.lower()  # 统一小写

        # ---- 值转换 ----
        if key == 'bday':
            try:
                val = date.fromisoformat(val)
            except ValueError:
                pass  # 保留原字符串
        elif key in ('tel', 'email'):
            # 电话/邮箱：{value, types}
            types = [a.split('=', 1)[1] for a in attrs if a.startswith('TYPE=')]
            val = {"value": val, "types": types}
        elif key == 'adr':
            # ADR: pobox; ext; street; city; region; code; country
            val = [v.strip() for v in val.split(';')]
        elif key in ('org', 'n'):
            # N: 姓; 名; 附加; 前缀; 后缀
            val = [v.strip() for v in val.split(';')]
        elif key in ('org', 'nickname', 'title', 'url', 'note', 'fn', 'nid', 'version'):
            # 字符串字段，保持原样
            pass
        # 任意扩展字段也保持字符串

        # ---- 多值处理 ----
        if key in data:
            # 同字段出现多次 → 转列表
            old = data[key]
            data[key] = [old, val] if not isinstance(old, list) else old + [val]
        else:
            data[key] = val

    return data


# ---------- 写 ----------
def build_vcard3_item(data: Dict[str, Any]) -> str:
    """
    把小写 key 的字典 → vCard 3.0 文本
    字段顺序：VERSION + 常用字段 + 任意扩展
    """
    lines = ["BEGIN:VCARD", "VERSION:3.0"]
    # 预定义常用字段顺序（可扩展）
    field_order = ['fn', 'n', 'nickname', 'bday', 'tel', 'email', 'org', 'title', 'url', 'adr', 'note', 'nid']
    # 先输出顺序字段
    for key in field_order:
        if key not in data:
            continue
        val = data[key]
        # 统一大写字段名
        field = key.upper()
        # ---- 值格式化 ----
        if key == 'bday' and isinstance(val, date):
            val = val.isoformat()
        elif key == 'tel' or key == 'email':
            # 列表或单 dict
            items = val if isinstance(val, list) else [val]
            for item in items:
                if isinstance(item, dict) and 'value' in item:
                    types = ','.join(item.get('types', []))
                    field_w_type = f"{field};TYPE={types}" if types else field
                    lines.append(f"{field_w_type}:{item['value']}")
                else:
                    lines.append(f"{field}:{item}")
            continue
        elif key == 'adr' or key == 'n' or key == 'org':
            # 分号拼接
            val = ';'.join(str(v) for v in val) if isinstance(val, list) else str(val)
        elif isinstance(val, list):
            # 其他多值 → 分号拼接（或逐行输出）
            val = ';'.join(str(v) for v in val)
        else:
            val = str(val)
        lines.append(f"{field}:{val}")

    # 任意扩展字段（不在预定义列表里）
    for key, val in data.items():
        if key in field_order or key == 'version':
            continue
        field = key.upper()
        if isinstance(val, list):
            val = ';'.join(str(v) for v in val)
        else:
            val = str(val)
        lines.append(f"{field}:{val}")

    lines.append("END:VCARD")
    return "\n".join(lines) + "\n"


def parse_vcard3(text: str):
    vcard_blocks = re.findall(r'BEGIN:VCARD.*?END:VCARD', text, flags=re.S)
    contacts = [parse_vcard3_item(b) for b in vcard_blocks]
    return contacts
