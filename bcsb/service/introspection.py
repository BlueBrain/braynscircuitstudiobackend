import inspect
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from logging import Logger
from types import NoneType
from typing import Any, Generic, TypeVar, get_args, get_origin

from ..json import JsonSchema, deserialize, get_schema, serialize
from ..jsonrpc import (
    Endpoint,
    EndpointHandler,
    EndpointParams,
    EndpointResult,
    EndpointSchema,
)

T = TypeVar("T")

Handler = Callable[[], Awaitable[Any]] | Callable[[Any], Awaitable[Any]]


@dataclass
class Params(Generic[T]):
    value: T
    binary: bytes


@dataclass
class Result(Generic[T]):
    value: T
    binary: bytes


class HandlerWrapper(EndpointHandler):
    def __init__(self, params_type: type, handler: Callable[..., Awaitable[Any]], logger: Logger) -> None:
        self._params_type = params_type
        self._handler = handler
        self._logger = logger

    async def handle(self, params: EndpointParams) -> EndpointResult:
        self._logger.info("Processing request from endpoint.")
        result = await self._call_handler(params)
        self._logger.info("Request processing done.")
        self._logger.debug("Request result: %s.", result)
        self._logger.info("Serializing result.")
        message = self._serialize_result(result)
        self._logger.info("Result serialized.")
        self._logger.debug("Serialized result: %s.", message)
        return message

    async def _call_handler(self, params: EndpointParams) -> Any:
        if self._params_type is NoneType:
            self._logger.info("No request params.")
            return await self._handler()
        self._logger.info("Parsing request params.")
        arg = self._deserialize_params(params)
        self._logger.info("Request params parsed.")
        self._logger.debug("Parsed request params: %s.", arg)
        return await self._handler(arg)

    def _deserialize_params(self, params: EndpointParams) -> Any:
        if get_origin(self._params_type) is not Params:
            return deserialize(params.message, self._params_type)
        args = get_args(self._params_type)
        message = deserialize(params.message, args[0])
        return Params(message, params.binary)

    def _serialize_result(self, result: Any) -> EndpointResult:
        if isinstance(result, Result):
            message = serialize(result.value)
            return EndpointResult(message, result.binary)
        message = serialize(result)
        return EndpointResult(message, b"")


def create_endpoint(method: str, description: str, handler: Handler, logger: Logger) -> Endpoint:
    params_type = _get_params_type(handler)
    result_type = _get_result_type(handler)
    return Endpoint(
        EndpointSchema(
            method=method,
            description=description,
            params=_get_params_schema(params_type),
            result=_get_result_schema(result_type),
        ),
        HandlerWrapper(params_type, handler, logger),
    )


def _get_params_schema(params_type: type) -> JsonSchema:
    if get_origin(params_type) is not Params:
        return get_schema(params_type)
    args = get_args(params_type)
    return get_schema(args[0])


def _get_result_schema(result_type: type) -> JsonSchema:
    if get_origin(result_type) is not Result:
        return get_schema(result_type)
    args = get_args(result_type)
    return get_schema(args[0])


def _get_params_type(handler: Handler) -> type:
    signature = inspect.signature(handler)
    params = list(signature.parameters.values())
    if len(params) == 0:
        return NoneType
    if len(params) > 1:
        raise ValueError("Handler cannot have more than 1 parameter")
    params_type = params[0].annotation
    if params_type is None:
        return NoneType
    if params_type is signature.empty:
        raise ValueError("Handler params must have a type hint")
    return params_type


def _get_result_type(handler: Handler) -> type:
    signature = inspect.signature(handler)
    result_type = signature.return_annotation
    if result_type is signature.empty:
        raise ValueError("No return type in handler")
    if result_type is None:
        return NoneType
    return result_type
