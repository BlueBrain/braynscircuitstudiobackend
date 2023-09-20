from logging import Logger

from ..json import JsonSchemaError, validate_schema
from ..websocket import Connection, ConnectionClosed, ConnectionHandler
from .composing import compose_exception, compose_result
from .endpoint import Endpoint, EndpointParams, EndpointResult
from .exceptions import InvalidParams, JsonRpcException, MethodNotFound, unexpected
from .messages import Request
from .parsing import parse_request


class JsonRpcHandler(ConnectionHandler):
    def __init__(self, endpoints: dict[str, Endpoint], logger: Logger) -> None:
        self._endpoints = endpoints
        self._logger = logger

    async def handle(self, connection: Connection) -> None:
        self._logger.info("Handling messages from %s.", connection)
        while True:
            try:
                await self._handle_next_request(connection)
            except ConnectionClosed:
                self._logger.info("Stop handling messages from %s.", connection)
                return
            except Exception as e:
                self._logger.error("Unexpected handler error: %s", e)
                self._logger.info("Forcing disconnection from %s.", connection)
                return

    async def _handle_next_request(self, connection: Connection) -> None:
        self._logger.info("Waiting for next request.")
        data = await connection.receive()
        self._logger.info("Handling request.")
        try:
            self._logger.info("Parsing request.")
            request = parse_request(data)
        except JsonRpcException as e:
            self._logger.warning("Request parsing failed: %s.", e)
            return await self._parsing_error(connection, e)
        except Exception as e:
            self._logger.error("Unexpected parsing error: %s.", e)
            return await self._parsing_error(connection, unexpected(e))
        self._logger.info("Request parsed.")
        self._logger.debug("Parsed request: %s.", request)
        await self._handle(connection, request)

    async def _handle(self, connection: Connection, request: Request) -> None:
        self._logger.info("Processing request.")
        try:
            params = EndpointParams(request.params, request.binary)
            result = await self._dispatch(request.method, params)
        except JsonRpcException as e:
            self._logger.warning("Request failed with error: %s.", e)
            return await self._error(connection, request, e)
        except Exception as e:
            self._logger.error("Unexpected request failure: %s.", e)
            return await self._error(connection, request, unexpected(e))
        self._logger.info("Request successfully processed.")
        await self._reply(connection, request, result)

    async def _dispatch(self, method: str, params: EndpointParams) -> EndpointResult:
        self._logger.info("Dispatching request '%s' to endpoints.", method)
        endpoint = self._endpoints.get(method)
        if endpoint is None:
            self._logger.warning("Method '%s' not found.", method)
            raise MethodNotFound(method)
        self._logger.info("Endpoint found for method '%s'.", method)
        self._logger.info("Validating params schema.")
        try:
            validate_schema(params.message, endpoint.schema.params)
        except JsonSchemaError as e:
            self._logger.warning("Invalid params schema: %s.", e)
            raise InvalidParams(str(e))
        self._logger.info("Params schema is valid.")
        return await endpoint.handler.handle(params)

    async def _reply(
        self, connection: Connection, request: Request, result: EndpointResult
    ) -> None:
        if request.id is None:
            self._logger.info("Skip reply message (no ID).")
            return
        self._logger.info("Sending reply message.")
        data = compose_result(result.message, request.id, result.binary)
        await connection.send(data)
        self._logger.info("Reply message sent.")

    async def _parsing_error(self, connection: Connection, e: JsonRpcException) -> None:
        data = compose_exception(e)
        self._logger.info("Notifying parsing error.")
        await connection.send(data)
        self._logger.info("Parsing error notified.")

    async def _error(
        self, connection: Connection, request: Request, e: JsonRpcException
    ) -> None:
        if request.id is None:
            self._logger.info("Skip error message (no ID).")
            return
        self._logger.info("Sending error message.")
        data = compose_exception(e, request.id)
        await connection.send(data)
        self._logger.info("Error message sent.")
