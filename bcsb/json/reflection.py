from collections.abc import Callable
from dataclasses import MISSING, fields, is_dataclass
from enum import Enum
from types import UnionType
from typing import get_args, get_origin

from .schema import JsonSchema
from .serialization import serialize
from .type import JsonType, TypeDict, get_json_type

_CUSTOM_TYPES = TypeDict[Callable[[type], JsonSchema]]()


def add_reflector(t: type, reflector: Callable[[type], JsonSchema]) -> None:
    _CUSTOM_TYPES.add(t, reflector)


def get_schema(t: type) -> JsonSchema:
    reflector = _CUSTOM_TYPES.get(t)
    if reflector is not None:
        return reflector(t)
    json_type = get_json_type(t)
    if json_type is not None:
        return _get_builtin_schema(t, json_type)
    if get_origin(t) is UnionType:
        return _get_oneof_schema(t)
    if issubclass(t, Enum):
        return _get_enum_schema(t)
    if is_dataclass(t):
        return _get_dataclass_schema(t)
    raise ValueError(f"Unsupported type for reflection: {t}")


def _reflect_schema(_: type[JsonSchema]) -> JsonSchema:
    return JsonSchema(title="JsonSchema", type=JsonType.OBJECT)


add_reflector(JsonSchema, _reflect_schema)


def _get_builtin_schema(t: type, json_type: JsonType) -> JsonSchema:
    schema = JsonSchema(type=json_type)
    if json_type.primitive:
        return schema
    args = get_args(t)
    if json_type is JsonType.ARRAY:
        schema.items = get_schema(args[0])
    if json_type is JsonType.OBJECT:
        schema.items = get_schema(args[1])
    return schema


def _get_enum_schema(t: type[Enum]) -> JsonSchema:
    return JsonSchema(
        title=t.__name__,
        type=JsonType.STRING,
        enum=list(str(item.value) for item in t),
    )


def _get_oneof_schema(t: type) -> JsonSchema:
    return JsonSchema(oneof=[get_schema(child) for child in get_args(t)])


def _get_dataclass_schema(t: type) -> JsonSchema:
    properties = dict[str, JsonSchema]()
    for field in fields(t):
        if field.name.startswith("_"):
            continue
        schema = get_schema(field.type)
        if field.default is not MISSING:
            schema.required = False
            schema.default = serialize(field.default)
        if field.default_factory is not MISSING:
            schema.required = False
            schema.default = serialize(field.default_factory())
        properties[field.name] = schema
    return JsonSchema(
        title=t.__name__,
        type=JsonType.OBJECT,
        properties=properties,
    )
