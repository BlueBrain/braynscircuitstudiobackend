import json
from typing import Any

from ..json import serialize
from .exceptions import JsonRpcException
from .messages import JsonRpcError, JsonRpcErrorInfo, JsonRpcId, JsonRpcReply, Reply


def compose_reply(reply: Reply) -> bytes | str:
    if reply.binary:
        return _compose_protobuf(reply)
    return _compose_json(reply.message)


def compose_result(result: Any, id: JsonRpcId = None, binary: bytes = b"") -> bytes | str:
    return compose_reply(Reply(JsonRpcReply(result, id), binary))


def compose_error(error: JsonRpcError) -> str:
    return _compose_json(error)


def compose_exception(e: JsonRpcException, id: JsonRpcId = None) -> str:
    message = error(e, id)
    return compose_error(message)


def error(e: JsonRpcException, id: JsonRpcId = None) -> JsonRpcError:
    return JsonRpcError(JsonRpcErrorInfo(e.code, e.message, e.data), id)


def _compose_json(value: Any) -> str:
    message = serialize(value)
    return json.dumps(message)


def _compose_protobuf(reply: Reply) -> bytes:
    text = _compose_json(reply.message)
    binary = reply.binary
    size = len(text).to_bytes(4, byteorder="little")
    return size + text.encode() + binary
