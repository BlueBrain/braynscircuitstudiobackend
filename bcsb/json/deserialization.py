from collections.abc import Callable
from dataclasses import fields, is_dataclass
from enum import Enum
from types import UnionType
from typing import Any, Literal, TypeVar, get_args, get_origin

from .type import JsonType, TypeDict, get_json_type

T = TypeVar("T")

_CUSTOM_TYPES = TypeDict[Callable[[Any, type], Any]]()


def add_deserializer(t: type[T], deserializer: Callable[[Any, type], T]) -> None:
    _CUSTOM_TYPES.add(t, deserializer)


def deserialize(data: Any, t: type[T]) -> T:
    deserializer = _CUSTOM_TYPES.get(t)
    if deserializer is not None:
        return deserializer(data, t)
    json_type = get_json_type(t)
    if json_type is None:
        return _deserialize_advanced(data, t)
    if json_type is JsonType.UNDEFINED:
        return data
    if json_type is JsonType.NULL:
        return t()
    if json_type.primitive:
        return t(data)
    if json_type is JsonType.ARRAY:
        return _deserialize_array(data, t)
    if json_type is JsonType.OBJECT:
        return _deserialize_dict(data, t)
    raise ValueError(f"Internal error in deserialize: {t}")


def _deserialize_advanced(data: Any, t: type[T]) -> T:
    origin = get_origin(t)
    if origin is Literal:
        return _deserialize_const(data, t)
    if origin is UnionType:
        return _deserialize_oneof(data, t)
    if issubclass(t, Enum):
        return t(data)
    if is_dataclass(t):
        return _deserialize_dataclass(data, t)
    raise ValueError(f"Unsupported type for deserialization: {t}")


def _deserialize_array(data: Any, t: type[T]) -> T:
    args = get_args(t)
    if len(args) != 1:
        raise ValueError("Trying to deserialize array of unknown type")
    return t(deserialize(item, args[0]) for item in data)


def _deserialize_dict(data: dict[str, Any], t: type[T]) -> T:
    args = get_args(t)
    if len(args) != 2:
        raise ValueError("Trying to deserialize dict of unknown type")
    return t((key, deserialize(item, args[1])) for key, item in data.items())


def _deserialize_const(data: dict[str, Any], t: type) -> Any:
    (value,) = get_args(t)
    if data != value:
        raise ValueError(f"Invalid const: expected {value} got {data}")
    return data


def _deserialize_oneof(data: Any, t: type[T]) -> T:
    args = get_args(t)
    for arg in args:
        if isinstance(data, arg):
            return data
    for arg in args:
        try:
            return deserialize(data, arg)
        except Exception:
            pass
    raise ValueError(f"Cannot deserialize union type {t}")


def _deserialize_dataclass(data: dict[str, Any], t: type) -> Any:
    properties = dict[str, Any]()
    for field in fields(t):
        child = data.get(field.name)
        if child is None:
            continue
        properties[field.name] = deserialize(child, field.type)
    return t(**properties)
