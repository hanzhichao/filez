import re


def parse_properties(raw: str):
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
