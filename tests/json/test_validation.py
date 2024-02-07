import re
from types import NoneType
from typing import Any

import pytest

from bcsb.json.reflection import get_schema
from bcsb.json.schema import JsonSchema
from bcsb.json.type import JsonType
from bcsb.json.validation import JsonSchemaError, validate_schema


def test_undefined() -> None:
    schema = get_schema(Any)
    validate_schema(1, schema)
    validate_schema(1.5, schema)
    validate_schema("test", schema)
    validate_schema({}, schema)
    validate_schema([], schema)


def test_null() -> None:
    schema = get_schema(NoneType)
    validate_schema(None, schema)
    with pytest.raises(JsonSchemaError, match="Invalid type: expected null got boolean"):
        validate_schema(False, schema)
    with pytest.raises(JsonSchemaError, match="Invalid type: expected null got integer"):
        validate_schema(1, schema)
    with pytest.raises(JsonSchemaError, match="Invalid type: expected null got string"):
        validate_schema("test", schema)


def test_number() -> None:
    schema = get_schema(int)
    validate_schema(1, schema)
    with pytest.raises(JsonSchemaError, match="Invalid type: expected integer got number"):
        validate_schema(1.5, schema)
    validate_schema(1, schema)
    schema = get_schema(float)
    validate_schema(1.5, schema)
    validate_schema(1, schema)


def test_range() -> None:
    schema = get_schema(float)
    schema.minimum = 2
    schema.maximum = 3
    validate_schema(2, schema)
    validate_schema(3, schema)
    with pytest.raises(JsonSchemaError, match="Out of range: 1 < 2"):
        validate_schema(1, schema)
    with pytest.raises(JsonSchemaError, match="Out of range: 4 > 3"):
        validate_schema(4, schema)


def test_const() -> None:
    schema = JsonSchema(const=1)
    validate_schema(1, schema)
    with pytest.raises(JsonSchemaError, match="Invalid const: 2"):
        validate_schema(2, schema)


def test_enum() -> None:
    schema = JsonSchema(type=JsonType.STRING, enum=["1", "2"])
    validate_schema("1", schema)
    validate_schema("2", schema)
    with pytest.raises(JsonSchemaError, match="Invalid enum: 3"):
        validate_schema("3", schema)


def test_oneof() -> None:
    schema = get_schema(int | str)
    validate_schema(1, schema)
    validate_schema("test", schema)
    with pytest.raises(JsonSchemaError, match="Invalid oneOf"):
        validate_schema(False, schema)


def test_array() -> None:
    schema = get_schema(list[str])
    validate_schema(["1", "2"], schema)
    with pytest.raises(
        JsonSchemaError,
        match=re.escape("[1]: Invalid type: expected string got integer"),
    ):
        validate_schema(["1", 2], schema)


def test_count() -> None:
    schema = get_schema(list[int])
    schema.min_items = 2
    schema.max_items = 3
    validate_schema([1, 2], schema)
    validate_schema([1, 2, 3], schema)
    with pytest.raises(JsonSchemaError, match="Invalid item count: 1 < 2"):
        validate_schema([1], schema)
    with pytest.raises(JsonSchemaError, match="Invalid item count: 4 > 3"):
        validate_schema([1, 2, 3, 4], schema)


def test_map() -> None:
    schema = get_schema(dict[str, dict[str, int]])
    validate_schema({}, schema)
    validate_schema({"test": {}}, schema)
    validate_schema({"test": {"internal": 1}}, schema)
    with pytest.raises(
        JsonSchemaError,
        match="test.internal: Invalid type: expected integer got string",
    ):
        validate_schema({"test": {"internal": "1"}}, schema)


def test_object() -> None:
    schema = JsonSchema(
        type=JsonType.OBJECT,
        properties={
            "required": JsonSchema(type=JsonType.INTEGER),
            "optional": JsonSchema(type=JsonType.INTEGER, required=False),
        },
    )
    validate_schema({"required": 1, "optional": 2}, schema)
    validate_schema({"required": 1}, schema)
    with pytest.raises(JsonSchemaError, match="Missing property: required"):
        validate_schema({}, schema)
    with pytest.raises(JsonSchemaError, match="Unknown property: invalid"):
        validate_schema({"required": 1, "invalid": 3}, schema)


def test_composition() -> None:
    schema = get_schema(dict[str, list[dict[str, int]]])
    validate_schema({"test": []}, schema)
    validate_schema({"test": [{"internal": 1}]}, schema)
    with pytest.raises(
        JsonSchemaError,
        match=re.escape("test[1].internal: Invalid type: expected integer got string"),
    ):
        validate_schema({"test": [{}, {"internal": "invalid"}]}, schema)
