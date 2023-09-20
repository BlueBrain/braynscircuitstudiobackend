import asyncio
from dataclasses import dataclass
from logging import Logger
from types import NoneType

import pytest

from bcsb.json import get_schema
from bcsb.jsonrpc import (
    Endpoint,
    EndpointParams,
    EndpointResult,
    EndpointSchema,
    InternalError,
)
from bcsb.service import EndpointRegistry, Params, Result


@dataclass
class SomeParams:
    value: int


@dataclass
class SomeResult:
    value: str


async def mock_raise() -> None:
    raise InternalError("This is a test")


async def mock_empty() -> None:
    pass


async def mock_dataclass(params: SomeParams) -> SomeResult:
    return SomeResult(str(params.value))


async def mock_binary(params: Params[int]) -> Result[str]:
    return Result(str(params.value), params.binary)


def register_endpoints() -> dict[str, Endpoint]:
    endpoints = dict[str, Endpoint]()
    registry = EndpointRegistry(endpoints, Logger("Test"))
    registry.add("test1", mock_raise, "Raise")
    registry.add("test2", mock_empty, "Empty")
    registry.add("test3", mock_dataclass)
    registry.add("test4", mock_binary, "Binary")
    return endpoints


def expected_schemas() -> list[EndpointSchema]:
    return [
        EndpointSchema("test1", "Raise", get_schema(NoneType), get_schema(NoneType)),
        EndpointSchema("test2", "Empty", get_schema(NoneType), get_schema(NoneType)),
        EndpointSchema("test3", "", get_schema(SomeParams), get_schema(SomeResult)),
        EndpointSchema("test4", "Binary", get_schema(int), get_schema(str)),
    ]


def mock_params() -> dict[str, EndpointParams]:
    return {
        "test1": EndpointParams(None, b""),
        "test2": EndpointParams(None, b""),
        "test3": EndpointParams({"value": 1}, b""),
        "test4": EndpointParams(1, b"123"),
    }


def expected_results() -> dict[str, EndpointResult]:
    return {
        "test2": EndpointResult(None, b""),
        "test3": EndpointResult({"value": "1"}, b""),
        "test4": EndpointResult("1", b"123"),
    }


def run(endpoint: Endpoint, params: EndpointParams) -> EndpointResult:
    return asyncio.run(endpoint.handler.handle(params))


def test_schemas() -> None:
    endpoints = register_endpoints()
    test = {key: endpoint.schema for key, endpoint in endpoints.items()}
    ref = {schema.method: schema for schema in expected_schemas()}
    assert test == ref


def test_request() -> None:
    endpoints = register_endpoints()
    params = mock_params()
    results = expected_results()
    with pytest.raises(InternalError) as e:
        run(endpoints["test1"], params["test1"])
    assert e.value.message == "Internal error: This is a test"
    assert run(endpoints["test2"], params["test2"]) == results["test2"]
    assert run(endpoints["test3"], params["test3"]) == results["test3"]
    assert run(endpoints["test4"], params["test4"]) == results["test4"]
