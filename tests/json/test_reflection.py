from dataclasses import dataclass
from enum import Enum
from types import NoneType
from typing import Any, Generic, Literal, TypeVar, get_args

from bcsb.json.reflection import add_reflector, get_schema
from bcsb.json.schema import JsonSchema
from bcsb.json.type import JsonType, get_json_type

T = TypeVar("T")


class MockEnum(Enum):
    TEST1 = "test1"
    TEST2 = "test2"


@dataclass
class MockDataclass:
    boolean: bool
    integer: int
    string: str


@dataclass
class Custom(Generic[T]):
    value: T


def get_custom_schema(t: type[Custom]) -> JsonSchema:
    arg = get_args(t)[0]
    json_type = get_json_type(arg)
    if json_type is None:
        return JsonSchema(type=JsonType.UNDEFINED)
    return JsonSchema(title="Custom", type=json_type)


add_reflector(Custom, get_custom_schema)


def test_primitive() -> None:
    assert get_schema(NoneType) == JsonSchema(type=JsonType.NULL)
    assert get_schema(bool) == JsonSchema(type=JsonType.BOOLEAN)
    assert get_schema(int) == JsonSchema(type=JsonType.INTEGER)
    assert get_schema(float) == JsonSchema(type=JsonType.NUMBER)
    assert get_schema(str) == JsonSchema(type=JsonType.STRING)


def test_array() -> None:
    assert get_schema(list[str]) == JsonSchema(type=JsonType.ARRAY, items=JsonSchema(type=JsonType.STRING))
    assert get_schema(set[int]) == JsonSchema(type=JsonType.ARRAY, items=JsonSchema(type=JsonType.INTEGER))


def test_dict() -> None:
    assert get_schema(dict[str, Any]) == JsonSchema(type=JsonType.OBJECT, items=JsonSchema())
    assert get_schema(dict[str, str]) == JsonSchema(type=JsonType.OBJECT, items=JsonSchema(type=JsonType.STRING))


def test_const() -> None:
    assert get_schema(Literal[1]) == JsonSchema(const=1)


def test_enum() -> None:
    assert get_schema(MockEnum) == JsonSchema(title="MockEnum", type=JsonType.STRING, enum=["test1", "test2"])


def test_oneof() -> None:
    assert get_schema(int | str) == JsonSchema(
        oneof=[JsonSchema(type=JsonType.INTEGER), JsonSchema(type=JsonType.STRING)]
    )


def test_dataclass() -> None:
    assert get_schema(MockDataclass) == JsonSchema(
        title="MockDataclass",
        type=JsonType.OBJECT,
        properties={
            "boolean": JsonSchema(type=JsonType.BOOLEAN),
            "integer": JsonSchema(type=JsonType.INTEGER),
            "string": JsonSchema(type=JsonType.STRING),
        },
    )


def test_custom() -> None:
    assert get_schema(Custom[int]) == JsonSchema(title="Custom", type=JsonType.INTEGER)
    assert get_schema(Custom[str]) == JsonSchema(title="Custom", type=JsonType.STRING)
