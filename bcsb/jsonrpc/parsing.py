import json

from ..json import JsonSchemaError, deserialize, get_schema, validate_schema
from .exceptions import InvalidRequest, ParseError
from .messages import JSON_RPC_VERSION, JsonRpcRequest, Request

_SCHEMA = get_schema(JsonRpcRequest)


def parse_request(data: bytes | str) -> Request:
    request = _parse_data(data)
    version = request.message.jsonrpc
    if version and version != JSON_RPC_VERSION:
        raise InvalidRequest(f"Invalid JSON-RPC version {version}")
    return request


def _parse_data(data: bytes | str) -> Request:
    if isinstance(data, bytes):
        return _parse_protobuf(data)
    return _parse_text(data)


def _parse_text(data: str) -> Request:
    json_rpc = _parse_json(data)
    return Request(json_rpc)


def _parse_protobuf(data: bytes) -> Request:
    size = int.from_bytes(data[:4], byteorder="little")
    if size + 4 > len(data):
        raise ParseError(f"Protobuf text size ({size} bytes) bigger than frame size")
    text = data[4 : 4 + size].decode()
    binary = data[4 + size :]
    json_rpc = _parse_json(text)
    return Request(json_rpc, binary)


def _parse_json(data: str) -> JsonRpcRequest:
    try:
        value = json.loads(data)
    except json.JSONDecodeError as e:
        raise ParseError(str(e))
    try:
        validate_schema(value, _SCHEMA)
    except JsonSchemaError as e:
        raise InvalidRequest(str(e))
    return deserialize(value, JsonRpcRequest)
