from collections.abc import Callable
from dataclasses import MISSING, Field, fields, is_dataclass
from enum import Enum
from typing import Any, TypeVar

from .type import JsonType, TypeDict, get_json_type

T = TypeVar("T")

_CUSTOM_TYPES = TypeDict[Callable[[Any], Any]]()


def add_serializer(t: type[T], serializer: Callable[[T], Any]) -> None:
    _CUSTOM_TYPES.add(t, serializer)


def serialize(value: Any) -> Any:
    t = type(value)
    serializer = _CUSTOM_TYPES.get(t)
    if serializer is not None:
        return serializer(value)
    json_type = get_json_type(t)
    if json_type is None:
        return _serialize_advanced(value)
    if json_type.primitive:
        return value
    if json_type is JsonType.ARRAY:
        return [serialize(item) for item in value]
    if json_type is JsonType.OBJECT and isinstance(value, dict):
        return {key: serialize(item) for key, item in value.items()}
    raise ValueError(f"Internal error in serialization: {t}")


def _serialize_advanced(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return _serialize_dataclass(value)
    raise ValueError(f"Unsupported type for serialization: {type(value)}")


def _serialize_dataclass(value: Any) -> dict[str, Any]:
    result = dict[str, Any]()
    for field in fields(value):
        child = getattr(value, field.name)
        if child is not None or _is_required(field):
            result[field.name] = serialize(child)
    return result


def _is_required(field: Field) -> bool:
    return field.default is MISSING and field.default_factory is MISSING
