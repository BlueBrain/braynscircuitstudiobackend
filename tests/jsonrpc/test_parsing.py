import json

from bcsb.jsonrpc.messages import JSON_RPC_VERSION
from bcsb.jsonrpc.parsing import parse_request

REQUEST = {"id": 1, "method": "test", "params": 3}


def test_parse_text() -> None:
    data = json.dumps(REQUEST)
    request = parse_request(data)
    assert request.id == 1
    assert request.method == "test"
    assert request.params == 3
    assert request.binary == b""


def test_parse_protobuf() -> None:
    message = json.dumps(REQUEST).encode()
    header = len(message).to_bytes(4, "little")
    binary = b"123"
    data = header + message + binary
    request = parse_request(data)
    assert request.version == JSON_RPC_VERSION
    assert request.id == 1
    assert request.method == "test"
    assert request.params == 3
    assert request.binary == binary
