from dataclasses import dataclass
from enum import Enum
from typing import Generic, TypeVar

from bcsb.json.serialization import add_serializer, serialize

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


def serialize_custom(value: Custom) -> str:
    return str(value.value)


add_serializer(Custom, serialize_custom)


def test_primitive() -> None:
    assert serialize(None) is None
    assert serialize(True) is True
    assert serialize(1) == 1
    assert serialize(1.5) == 1.5
    assert serialize("test") == "test"


def test_array() -> None:
    values = [1, "test", False]
    assert serialize(values) == values
    assert serialize(tuple(values)) == values
    assert set(serialize(set(values))) == set(values)


def test_dict() -> None:
    values = {"test1": 1, "test2": 2}
    assert serialize(values) == values


def test_enum() -> None:
    value = MockEnum.TEST1
    assert serialize(value) == value.value


def test_dataclass() -> None:
    value = MockDataclass(True, 2, "test")
    ref = {"boolean": True, "integer": 2, "string": "test"}
    assert serialize(value) == ref


def test_custom() -> None:
    assert serialize(Custom[int](3)) == "3"
    assert serialize(Custom[float](1.5)) == "1.5"
    assert serialize(Custom[str]("test")) == "test"
