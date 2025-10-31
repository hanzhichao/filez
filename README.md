# filez 

易用的小型数据及配置文件解析库。

![Languate - Python](https://img.shields.io/badge/language-python-blue.svg)
![PyPI - License](https://img.shields.io/pypi/l/filez)
![PyPI](https://img.shields.io/pypi/v/filez)
![PyPI - Downloads](https://img.shields.io/pypi/dm/filez)

## 特性

- 支持加载 INI /JSON / YAML / TOML / CSV / EXCEL / XML / HTML / CVF / XMIND  / TXT  等文件数据
- 支持自动转换值类型，支持转换 datetime 类型，支持自动解析 环境变量

## 安装方法

```
pip install filez
```

## 使用方法

```python
from filez import file

data = file.load_ini('testdata/data.ini') # 根据文件后缀自动识别类型
print(data)
```


### 加载 INI 文件

> 默认文件后缀名支持 .ini /.conf / .config，如果是其他后缀名，可以使用 file.load_ini('xxx.xxx') 进行加载

特性：

- 支持空值
- 大小写敏感
- 支持`${ENV_KEY}`引用环境变量，支持环境变量默认值，支持字符串中部分插入环境变量
- 支持自动识别变量类型，
    - 支持int, float自动转换
    - 支持true/TRUE/True/on转为True, 支持false/FALSE/False/off转为False
    - 支持null/None/~转为None
    - 支持`{k:v}` / `[a,b]` 自动转为dict和list (支持yaml格式,key,value不加引号)
- 支持`%(option)s`，引用当前section的某个值

例如： 数据文件: testdata/data.conf

```ini
[DEFAULT]
version : '1'

[App]
; App config
Debug = true
backends :  [127.0.0.1, 192.168.1.2] ; backends
desc =
    This is a multi-line
    description.
params = {k: v, n: 1}
message = hi, ${USER}
timeout = 3.5      # seconds
release: null

[db]
# db config
host = ${DB_HOST:-localhost}
port= 3306
user = ${USER}
password =
db_uri = mysql://%(user)s:%(password)s@%(host)s:%(port)s/testdb?charset=utf8
```

加载方法

```python
from filez import file

data = file.load_ini('testdata/data.ini')
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
```

### 加载 JSON 文件

> 默认文件后缀名支持 .json 如果是其他后缀名，可以使用 file.load_json('xxx.xxx') 进行加载

特性：
- 支持自动转换时间日期

例如： 数据文件: testdata/data.json

```json
{  
  "name": "Alice",  
  "created_at": "2025-06-01T12:30:45",  
  "birthday": "1990-01-01"  
}
```

使用方法

```python
from filez import file

data = file.load('testdata/data.json', parse_datetime=True)
assert data == {'birthday': date(1990, 1, 1),  
                'created_at': datetime(2025, 6, 1, 12, 30, 45),  
                'name': 'Alice'}
```

### 加载 YAML 文件

> 默认文件后缀名支持 .yml /.yaml，如果是其他后缀名，可以使用 file.load_yaml('xxx.xxx') 进行加载

特性：

- 文本值中支持包含${ENV_KEY}直接引用环境变量值，支持环境变量带默认值
- 支持构造器`!merge`，合并多个引用锚点列表值
- 支持构造器`!datetime`，将ISO时间日期字符串转为datetime.datetime类型
- 支持构造器`!date`，将ISO日期字符串转为datetime.date类型
- 支持构造器`!file`，加载 json/yaml/toml/csv/ini/...文件数据到当前文件

例如： 数据文件: testdata/data.yaml

```yaml
a: 1  
b: 2  
port: ${PORT}  
debug: ${DEBUG:-true}  
msg: port is ${PORT}  
list1: &list1 [1, 2, 3]  
list2: &list2 [4, 5]  
merged_list: !merge [*list1, *list2]  
file_data: !file ./data.json  
  
created: !datetime 2025-06-01T12:30:45  
created_ms: !datetime 2025-06-01T12:30:45.123456  
ts_sec:  !datetime 1717234245  
ts_ms:   !datetime 1717234245123  
  
birth: !date 1990-01-01  
birth_ts: !date 1717234245
```

设置环境变量

```shell
export PASSWORD=123456
export PORT=8888
```

使用方法

```python
from filez import file

data = file.load('testdata/data.yaml', parse_datetime=True)
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
```

### 加载 TOML 文件

> 默认文件后缀名支持 .json 如果是其他后缀名，可以使用 file.load_json('xxx.xxx') 进行加载

特性：

例如： 数据文件: testdata/data.toml

```json
{
  "a": 1,
  "b": 2
}
```

使用方法

```python
from filez import file

data = file.load('testdata/data.toml')
assert data == {'a': 1, 'b': 2}
```

### 加载 CSV 或 Excel 文件

特性：
- 支持跳过指定行
- 支持带标题行
- Excel支持加载单个表，多个表或所有表数据

例如： 数据文件:
testdata/data.csv 或 testdata/data.xls Sheet1 或 testdata/data.xlsx Sheet1 数据

| a     | b     | c   |
| ----- | ----- | --- |
| 1     | 2.2   | 0   |
| hello | world |     |

使用方法

```python
from filez import file

data1 = file.load('testdata/data.csv')
assert data1 == [['a', 'b', 'c'], [1, 2.2, 0], ['hello', 'world', '']]

data2 = file.load('testdata/data.xls', skip=1)
assert data2 == [[1.0, 2.2, 0], ['hello', 'world', '']]

# load all_sheets:
data3 = file.load('testdata/data.xls', sheets='all')
assert data3 == {'Sheet1': [['a', 'b', 'c'], [1.0, 2.2, 0], ['hello', 'world', '']],
                 'Sheet2': [['a', 'b', 'c'], [1.0, 2.2, 0]]}

# load given_sheets: Sheet2
data4 = file.load('testdata/data.xls', skip=1, sheets=[1])
assert data4 == {'Sheet2': [[1.0, 2.2, 0]]}

data5 = file.load('testdata/data.xlsx', header=True)
assert data5 == [{'a': 1.0, 'b': 2.2, 'c': 0}, {'a': 'hello', 'b': 'world', 'c': ''}]
```

### 加载 XML 文件

特性：

- 支持忽略属性，只保留节点标签及文本数据

例如：数据文件 testdata/data.xml

```xml
<bookstore>
  <book category="COOKING">
    <title lang="en">Everyday Italian</title>
    <author>Giada De Laurentiis</author>
    <year>2005</year>
    <price>30.00</price>
  </book>
  <book category="WEB">
    <title lang="en">Learning XML</title>
    <author>Erik T. Ray</author>
    <year>2003</year>
    <price>39.95</price>
  </book>
</bookstore>
```

使用方法

```python
from filez import file

# default args ：
#   ignore_attrs=False, 忽略节点属性
#   attr_key_prefix=':',  属性key前缀
#   child_tag_key_prefix='', 子节点标签名key前缀
#   default_text_key='text', 叶子节点既有属性又有text时，text值的默认key
#   empty_text=None, 叶子节点text为空时，默认value
data1 = file.load('testdata/data.xml')
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
# 忽略节点属性
data2 = file.load('testdata/data.xml', ignore_attrs=True)
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
```

### 加载 HTML 文件

特性：


例如：数据文件 tests/data.html

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <title>Title</title>
  </head>
  <body>
    <h1>标题</h1>
    <p>内容</p>
    <form name="form1" method="post">
        <input name="username" type="text">
        <input type="submit">
    </form>
  </body>
</html>

```

使用方法

```python
from filez import file

data = file.load('testdata/data.html')
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
```

### 加载 Properties 文件

数据文件 data.properties

```properties
appId=cactus

# key
publicKey=-----BEGIN PUBLIC KEY-----\n\
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEP9eQZFl3j5zZX8bmYYEznA0z3/X+\n\
TooIQ11rxFcPZsTvJPLCUY7NHasUenXJngmvRXSnP4odegaoe4usLDv/3A==\n\
-----END PUBLIC KEY-----

app.config.host=127.0.0.1
app.config.port=8080
```

```python
from filez import file

data = file.load('testdata/data.properties')
assert data == {'appId': 'cactus',  
'publicKey': '-----BEGIN PUBLIC KEY-----\\n'  
			 'MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEP9eQZFl3j5zZX8bmYYEznA0z3/X+\\n'  
			 'TooIQ11rxFcPZsTvJPLCUY7NHasUenXJngmvRXSnP4odegaoe4usLDv/3A==\\n'  
			 '-----END PUBLIC KEY-----',  
'app': {'config': {'host': '127.0.0.1', 'port': '8080'}}}
```
### 加载 vCard3 通讯录文件

数据文件 testdata/data.cvf

```cvf
BEGIN:VCARD  
VERSION:3.0  
FN:Alice Smith  
N:Smith;Alice;;;  
NICKNAME:Al  
NID:abc-123  
BDAY:1990-01-01  
TEL;TYPE=WORK,VOICE:+86-138-0000-0000  
TEL;TYPE=HOME,VOICE:+86-010-88888888  
EMAIL;TYPE=INTERNET,WORK:alice@example.com  
EMAIL;TYPE=INTERNET,HOME:alice.home@example.com  
ORG:Example Inc.  
TITLE:Software Engineer  
URL:https://alice.example.com  
ADR;TYPE=WORK:;;123 Main St;Beijing;;100000;China  
ADR;TYPE=HOME:;;456 Park Ave;Shanghai;;200000;China  
NOTE:Test contact for demo  
X-SOCIALPROFILE;TYPE=linkedin:https://linkedin.com/in/alicesmith  
END:VCARD

...
```



```python
from filez import file

data = file.load('testdata/data.cvf')
print(data)
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
]
```
### 加载 XMind 文件


```python
from filez import file

data = file.load('testdata/data.xmind')
print(data)
```
### 加载其他纯文本文件

特性：

- 自动去除末尾\n

例如：数据文件 tests/data.txt

```text
line1
line2
line3
line4
```

使用方法

```python
from filez import file

data = file.load('tests/data.txt')
assert data == ['line1', 'line2', 'line3', 'line4']
```

