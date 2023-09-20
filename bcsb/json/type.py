from enum import Enum
from types import NoneType
from typing import Any, Generic, TypeVar, get_origin

T = TypeVar("T")


class TypeDict(Generic[T]):
    def __init__(self, values: dict[type, T] | None = None) -> None:
        self._values = {} if values is None else values

    def get(self, t: type) -> T | None:
        origin = get_origin(t)
        if origin is not None:
            t = origin
        return self._values.get(t)

    def add(self, t: type, value: T) -> None:
        self._values[t] = value


class JsonType(Enum):
    UNDEFINED = "undefined"
    NULL = "null"
    BOOLEAN = "boolean"
    INTEGER = "integer"
    NUMBER = "number"
    STRING = "string"
    ARRAY = "array"
    OBJECT = "object"

    @property
    def numeric(self) -> bool:
        return self in (JsonType.INTEGER, JsonType.NUMBER)

    @property
    def primitive(self) -> bool:
        return self not in (JsonType.ARRAY, JsonType.OBJECT)


def get_json_type(t: type) -> JsonType | None:
    return _JSON_TYPES.get(t)


_JSON_TYPES = TypeDict[JsonType](
    {
        Any: JsonType.UNDEFINED,
        NoneType: JsonType.NULL,
        bool: JsonType.BOOLEAN,
        int: JsonType.INTEGER,
        float: JsonType.NUMBER,
        str: JsonType.STRING,
        list: JsonType.ARRAY,
        tuple: JsonType.ARRAY,
        set: JsonType.ARRAY,
        dict: JsonType.OBJECT,
    }
)
