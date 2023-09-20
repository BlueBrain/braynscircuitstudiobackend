import asyncio
import json
from dataclasses import dataclass, field
from logging import Logger
from typing import Any

from bcsb.json import JsonSchema
from bcsb.jsonrpc import (
    Endpoint,
    EndpointHandler,
    EndpointParams,
    EndpointResult,
    EndpointSchema,
    InternalError,
    JsonRpcHandler,
)
from bcsb.jsonrpc.exceptions import INTERNAL_ERROR, PARSE_ERROR
from bcsb.jsonrpc.messages import JSON_RPC_VERSION
from bcsb.websocket.interface import Connection, ConnectionClosed

RAISE = "raise"


@dataclass
class MockConnection(Connection):
    requests: list[bytes | str]
    replies: list[dict[str, Any]] = field(default_factory=list)

    @property
    def host(self) -> str:
        return ""

    @property
    def port(self) -> int:
        return 0

    async def send(self, data: bytes | str) -> None:
        self.replies.append(json.loads(data))

    async def receive(self) -> bytes | str:
        if not self.requests:
            raise ConnectionClosed()
        return self.requests.pop(0)


@dataclass
class MockHandler(EndpointHandler):
    results: list[EndpointResult]
    params: list[EndpointParams] = field(default_factory=list)

    async def handle(self, params: EndpointParams) -> EndpointResult:
        self.params.append(params)
        return self.results.pop(0)


@dataclass
class RaiseHandler(EndpointHandler):
    async def handle(self, _: EndpointParams) -> EndpointResult:
        raise InternalError("This is a test")


def mock_connection() -> MockConnection:
    return MockConnection(
        requests=[
            "{Invalid JSON",
            json.dumps({"id": 1, "method": "ok", "params": "123"}),
            json.dumps({"id": 2, "method": RAISE}),
        ]
    )


def expected_params() -> list[EndpointParams]:
    return [EndpointParams("123", b"")]


def expected_replies() -> list[dict[str, Any]]:
    return [
        {
            "error": {
                "code": PARSE_ERROR,
                "message": "Failed to parse JSON: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)",
            },
            "jsonrpc": JSON_RPC_VERSION,
        },
        {
            "id": 1,
            "result": "Some result",
            "jsonrpc": JSON_RPC_VERSION,
        },
        {
            "id": 2,
            "error": {
                "code": INTERNAL_ERROR,
                "message": "Internal error: This is a test",
            },
            "jsonrpc": JSON_RPC_VERSION,
        },
    ]


def mock_schema() -> EndpointSchema:
    return EndpointSchema("", "", JsonSchema(), JsonSchema())


def mock_endpoints(handler: EndpointHandler) -> dict[str, Endpoint]:
    return {
        "ok": Endpoint(mock_schema(), handler),
        RAISE: Endpoint(mock_schema(), RaiseHandler()),
    }


def test_handle() -> None:
    connection = mock_connection()
    result = EndpointResult("Some result", b"")
    handler = MockHandler([result])
    endpoints = mock_endpoints(handler)
    test = JsonRpcHandler(endpoints, Logger("Test"))
    asyncio.run(test.handle(connection))
    assert handler.params == expected_params()
    assert connection.replies == expected_replies()
