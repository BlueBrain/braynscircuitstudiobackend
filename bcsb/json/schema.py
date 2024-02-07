from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .serialization import add_serializer
from .type import JsonType


@dataclass
class JsonSchema:
    title: str = ""
    description: str = ""
    type: JsonType = JsonType.UNDEFINED
    required: bool = True
    default: Any = None
    minimum: float | None = None
    maximum: float | None = None
    items: JsonSchema | None = None
    min_items: int | None = None
    max_items: int | None = None
    properties: dict[str, JsonSchema] = field(default_factory=dict)
    const: Any = None
    enum: list[str] = field(default_factory=list)
    oneof: list[JsonSchema] = field(default_factory=list)


def serialize_schema(schema: JsonSchema) -> dict[str, Any]:
    result = {}
    _serialize_info(schema, result)
    _serialize_options(schema, result)
    return result


add_serializer(JsonSchema, serialize_schema)


def _serialize_info(schema: JsonSchema, result: dict[str, Any]) -> None:
    if schema.title:
        result["title"] = schema.title
    if schema.description:
        result["description"] = schema.description
    if schema.type is not JsonType.UNDEFINED:
        result["type"] = schema.type.value
    if schema.default is not None:
        result["default"] = schema.default


def _serialize_options(schema: JsonSchema, result: dict[str, Any]) -> None:
    if schema.type.numeric:
        _serialize_number(schema, result)
        return
    if schema.const is not None:
        _serialize_const(schema, result)
    if schema.enum:
        _serialize_enum(schema, result)
        return
    if schema.oneof:
        _serialize_oneof(schema, result)
        return
    if schema.type is JsonType.ARRAY:
        _serialize_array(schema, result)
        return
    if schema.type is JsonType.OBJECT:
        _serialize_object(schema, result)
        return


def _serialize_number(schema: JsonSchema, result: dict[str, Any]) -> None:
    if schema.minimum is not None:
        result["minimum"] = schema.minimum
    if schema.maximum is not None:
        result["maximum"] = schema.maximum


def _serialize_const(schema: JsonSchema, result: dict[str, Any]) -> None:
    result["const"] = schema.const


def _serialize_enum(schema: JsonSchema, result: dict[str, Any]) -> None:
    result["enum"] = schema.enum


def _serialize_oneof(schema: JsonSchema, result: dict[str, Any]) -> None:
    result["oneOf"] = [serialize_schema(oneof) for oneof in schema.oneof]


def _serialize_array(schema: JsonSchema, result: dict[str, Any]) -> None:
    if schema.items is not None:
        result["items"] = serialize_schema(schema.items)
    if schema.min_items is not None:
        result["minItems"] = schema.min_items
    if schema.max_items is not None:
        result["maxItems"] = schema.max_items


def _serialize_object(schema: JsonSchema, result: dict[str, Any]) -> None:
    if schema.items is not None:
        result["additionalProperties"] = serialize_schema(schema.items)
        return
    result["additionalProperties"] = False
    result["properties"] = {key: serialize_schema(value) for key, value in schema.properties.items()}
    result["required"] = [key for key, value in schema.properties.items() if value.required]
