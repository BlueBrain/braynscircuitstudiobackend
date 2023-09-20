import json

from bcsb.jsonrpc import JsonRpcException
from bcsb.jsonrpc.composing import (
    compose_error,
    compose_exception,
    compose_reply,
    compose_result,
)
from bcsb.jsonrpc.messages import (
    JSON_RPC_VERSION,
    JsonRpcError,
    JsonRpcErrorInfo,
    JsonRpcReply,
    Reply,
)


def test_compose_error() -> None:
    e = JsonRpcError(JsonRpcErrorInfo(1, "test", [1, 2, 3]), 4)
    ref = {
        "jsonrpc": JSON_RPC_VERSION,
        "id": 4,
        "error": {"code": 1, "message": "test", "data": [1, 2, 3]},
    }
    data = compose_error(e)
    assert json.loads(data) == ref


def test_compose_exception() -> None:
    e = JsonRpcException("test", 1, [1, 2, 3])
    data = compose_exception(e, 4)
    ref = {
        "jsonrpc": JSON_RPC_VERSION,
        "id": 4,
        "error": {"code": 1, "message": "test", "data": [1, 2, 3]},
    }
    assert json.loads(data) == ref


def test_error_notification() -> None:
    e = JsonRpcException("test", 1)
    ref = {
        "jsonrpc": JSON_RPC_VERSION,
        "error": {"code": 1, "message": "test"},
    }
    data = compose_exception(e)
    assert json.loads(data) == ref


def test_compose_reply() -> None:
    reply = Reply(JsonRpcReply(3, 1), b"123")
    data = compose_reply(reply)
    assert isinstance(data, bytes)
    size = int.from_bytes(data[:4], "little")
    text = data[4 : size + 4]
    assert json.loads(text) == {"id": 1, "result": 3, "jsonrpc": JSON_RPC_VERSION}
    assert data[size + 4 :] == reply.binary


def test_compose_result() -> None:
    reply = Reply(JsonRpcReply(3, 1), b"123")
    data = compose_result(reply.result)
    assert json.loads(data) == {"result": 3, "jsonrpc": JSON_RPC_VERSION}
    data = compose_result(reply.result, reply.id, reply.binary)
    assert data == compose_reply(reply)
