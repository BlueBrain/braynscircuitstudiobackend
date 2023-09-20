from dataclasses import dataclass
from typing import Any

from .schema import JsonSchema
from .type import JsonType, get_json_type

Path = list[int | str]


def format_path(path: Path) -> str:
    elements = list[str]()
    for item in path:
        if isinstance(item, int):
            elements.append(f"[{item}]")
            continue
        if elements:
            elements.append(f".{item}")
            continue
        elements.append(item)
    return "".join(elements)


@dataclass
class JsonSchemaError(Exception):
    path: Path
    message: str

    def __str__(self) -> str:
        if not self.path:
            return self.message
        path = format_path(self.path)
        return f"{path}: {self.message}"


def validate_schema(value: Any, schema: JsonSchema) -> None:
    path = Path()
    try:
        _check(value, schema, path)
    except ValueError as e:
        raise JsonSchemaError(path, str(e))


def _check(value: Any, schema: JsonSchema, path: Path) -> None:
    _check_type(value, schema.type)
    if schema.type.numeric:
        _check_number(value, schema)
        return
    if schema.oneof:
        _check_oneof(value, schema)
        return
    if schema.enum:
        _check_enum(value, schema)
        return
    if schema.type is JsonType.ARRAY:
        _check_array(value, schema, path)
        return
    if schema.type is not JsonType.OBJECT:
        return
    if schema.items:
        _check_map(value, schema, path)
        return
    if schema.properties:
        _check_object(value, schema, path)
        return


def _check_type(value: Any, expected: JsonType) -> None:
    if expected is JsonType.UNDEFINED:
        return
    t = get_json_type(type(value))
    if t is None:
        raise ValueError(f"Internal error in validation: {t}")
    if t is expected:
        return
    if expected is JsonType.NUMBER and t is JsonType.INTEGER:
        return
    raise ValueError(f"Invalid type: expected {expected.value} got {t.value}")


def _check_number(value: float, schema: JsonSchema) -> None:
    if schema.minimum is not None and value < schema.minimum:
        raise ValueError(f"Out of range: {value} < {schema.minimum}")
    if schema.maximum is not None and value > schema.maximum:
        raise ValueError(f"Out of range: {value} > {schema.maximum}")


def _check_array(value: list[Any], schema: JsonSchema, path: Path) -> None:
    count = len(value)
    if schema.min_items is not None and count < schema.min_items:
        raise ValueError(f"Invalid item count: {count} < {schema.min_items}")
    if schema.max_items is not None and count > schema.max_items:
        raise ValueError(f"Invalid item count: {count} > {schema.max_items}")
    if schema.items is None:
        return
    for index, item in enumerate(value):
        path.append(index)
        _check(item, schema.items, path)
        path.pop()


def _check_map(value: dict[str, Any], schema: JsonSchema, path: Path) -> None:
    if schema.items is None:
        return
    for key, item in value.items():
        path.append(key)
        _check(item, schema.items, path)
        path.pop()


def _check_object(value: dict[str, Any], schema: JsonSchema, path: Path) -> None:
    for key, item in schema.properties.items():
        if item.required and key not in value:
            raise ValueError(f"Missing property: {key}")
    for key, item in value.items():
        child = schema.properties.get(key)
        if child is None:
            raise ValueError(f"Unknown property: {key}")
        path.append(key)
        _check(item, child, path)
        path.pop()


def _check_enum(value: str, schema: JsonSchema) -> None:
    if value not in schema.enum:
        raise ValueError(f"Invalid enum: {value}")


def _check_oneof(value: Any, schema: JsonSchema) -> None:
    for oneof in schema.oneof:
        try:
            return validate_schema(value, oneof)
        except JsonSchemaError:
            pass
    raise ValueError("Invalid oneOf")
