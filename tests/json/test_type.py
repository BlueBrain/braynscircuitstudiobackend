from types import NoneType
from typing import Any

from bcsb.json.type import JsonType, get_json_type


def test_builtin() -> None:
    assert get_json_type(Any) == JsonType.UNDEFINED
    assert get_json_type(NoneType) == JsonType.NULL
    assert get_json_type(bool) == JsonType.BOOLEAN
    assert get_json_type(int) == JsonType.INTEGER
    assert get_json_type(float) == JsonType.NUMBER
    assert get_json_type(str) == JsonType.STRING
    assert get_json_type(list) == JsonType.ARRAY
    assert get_json_type(tuple) == JsonType.ARRAY
    assert get_json_type(set) == JsonType.ARRAY
    assert get_json_type(dict) == JsonType.OBJECT


def test_generic() -> None:
    assert get_json_type(list[str]) == JsonType.ARRAY
    assert get_json_type(list[int]) == JsonType.ARRAY
    assert get_json_type(tuple[str]) == JsonType.ARRAY
    assert get_json_type(set[str]) == JsonType.ARRAY
    assert get_json_type(dict[str, Any]) == JsonType.OBJECT
    assert get_json_type(dict[str, int]) == JsonType.OBJECT
