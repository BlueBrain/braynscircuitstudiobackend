from dataclasses import dataclass
from enum import Enum
from types import NoneType
from typing import Any, Generic, Literal, TypeVar, get_args

import pytest

from bcsb.json.deserialization import add_deserializer, deserialize

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


@dataclass
class Union1:
    key: Literal["test1"]
    value1: str


@dataclass
class Union2:
    key: Literal["test2"]
    value2: int


def deserialize_custom(value: dict[str, Any], t: type[Custom]) -> Custom:
    arg = get_args(t)[0]
    return t(arg(value["value"]))


add_deserializer(Custom, deserialize_custom)


def test_primitive() -> None:
    assert deserialize(None, NoneType) is None
    assert deserialize(True, bool) is True
    assert deserialize(1, int) == 1
    assert deserialize(1.5, float) == 1.5
    assert deserialize("test", str) == "test"


def test_array() -> None:
    values = [1, "2", True]
    assert deserialize(values, list[int]) == [1, 2, 1]
    assert deserialize(values, list[str]) == ["1", "2", "True"]
    assert deserialize(values, list[bool]) == [True, True, True]


def test_dict() -> None:
    values = {"test1": False, "test2": 2}
    assert deserialize(values, dict[str, str]) == {"test1": "False", "test2": "2"}
    assert deserialize(values, dict[str, int]) == {"test1": 0, "test2": 2}
    assert deserialize(values, dict[str, bool]) == {"test1": False, "test2": True}


def test_enum() -> None:
    value = MockEnum.TEST1
    assert deserialize(value.value, MockEnum) == value


def test_const() -> None:
    assert deserialize(1, Literal[1]) == 1
    with pytest.raises(ValueError, match="Invalid const: expected 1 got 2"):
        deserialize(2, Literal[1])


def test_dataclass() -> None:
    data = {"boolean": True, "integer": 3, "string": "test"}
    assert deserialize(data, MockDataclass) == MockDataclass(True, 3, "test")


def test_custom() -> None:
    data = {"value": 1}
    assert deserialize(data, Custom[int]) == Custom(1)
    assert deserialize(data, Custom[str]) == Custom("1")
    assert deserialize(data, Custom[bool]) == Custom(True)


def test_oneof() -> None:
    data = {"key": "test1", "value1": "test"}
    assert deserialize(data, Union1 | Union2) == Union1("test1", "test")
    data = {"key": "test2", "value2": 1}
    assert deserialize(data, Union1 | Union2) == Union2("test2", 1)
    data = {"key": "test3", "value2": 1}
    with pytest.raises(ValueError):
        deserialize(data, Union1 | Union2)
    data = {"key": "test2", "value3": 1}
    with pytest.raises(ValueError):
        deserialize(data, Union1 | Union2)
