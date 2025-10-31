from collections import OrderedDict

from filez.utils import cast_value, cast_dict_value


def test_auto_cast():
    assert cast_value('1') == 1
    assert cast_value('1.1') == 1.1
    assert cast_value('true') is True
    assert cast_value('off') is False
    assert cast_value('~') is None


def test_cast_dict_value():
    assert cast_dict_value({'a': '1', 'b': 'null'}) == {'a': 1, 'b': None}
    assert cast_dict_value({'a': '1', 'b': 'null'}, ordered_dict=True) == OrderedDict([('a', 1), ('b', None)])
