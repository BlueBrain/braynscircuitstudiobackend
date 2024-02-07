from bcsb.json.schema import JsonSchema
from bcsb.json.serialization import serialize
from bcsb.json.type import JsonType


def test_minimal() -> None:
    assert serialize(JsonSchema()) == {}


def test_type_only() -> None:
    assert serialize(JsonSchema(type=JsonType.NULL)) == {"type": "null"}


def test_number() -> None:
    schema = JsonSchema(
        title="Test",
        description="Description",
        type=JsonType.NUMBER,
        required=False,
        default=3,
        minimum=2,
        maximum=10,
    )
    data = {
        "title": "Test",
        "description": "Description",
        "type": "number",
        "default": 3,
        "minimum": 2,
        "maximum": 10,
    }
    assert serialize(schema) == data


def test_array() -> None:
    schema = JsonSchema(
        type=JsonType.ARRAY,
        items=JsonSchema(type=JsonType.INTEGER),
        min_items=2,
        max_items=3,
    )
    data = {
        "type": "array",
        "items": {"type": "integer"},
        "minItems": 2,
        "maxItems": 3,
    }
    assert serialize(schema) == data


def test_map() -> None:
    schema = JsonSchema(type=JsonType.OBJECT, items=JsonSchema(type=JsonType.NUMBER))
    data = {"type": "object", "additionalProperties": {"type": "number"}}
    assert serialize(schema) == data


def test_object() -> None:
    schema = JsonSchema(
        type=JsonType.OBJECT,
        properties={
            "required": JsonSchema(type=JsonType.INTEGER),
            "not": JsonSchema(type=JsonType.STRING, required=False),
        },
    )
    data = {
        "type": "object",
        "additionalProperties": False,
        "properties": {"required": {"type": "integer"}, "not": {"type": "string"}},
        "required": ["required"],
    }
    assert serialize(schema) == data


def test_const() -> None:
    schema = JsonSchema(const=1)
    data = {"const": 1}
    assert serialize(schema) == data


def test_enum() -> None:
    schema = JsonSchema(type=JsonType.STRING, enum=["1", "2"])
    data = {"type": "string", "enum": ["1", "2"]}

    assert serialize(schema) == data


def test_oneof() -> None:
    schema = JsonSchema(
        oneof=[JsonSchema(type=JsonType.STRING), JsonSchema(type=JsonType.NUMBER)],
    )
    data = {
        "oneOf": [{"type": "string"}, {"type": "number"}],
    }
    assert serialize(schema) == data
