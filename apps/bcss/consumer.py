import logging
import re
from typing import Type

from aiohttp import WSMessage, WSMsgType
from aiohttp.web_request import Request
from aiohttp.web_ws import WebSocketResponse
from marshmallow import Schema

from common.jsonrpc.exceptions import MethodAlreadyRegistered
from common.jsonrpc.methods import Method

logger = logging.getLogger(__name__)


class BCSSConsumer:
    ws: WebSocketResponse = None

    _methods = {}
    _anonymous_access_methods = set()

    @classmethod
    def _normalize_method_name(cls, name: str):
        normalized_name = name.replace("_", "-")
        return normalized_name

    @classmethod
    def register_method(
        cls,
        custom_method_name: str = None,
        allow_anonymous_access: bool = False,
        request_schema: Type[Schema] = None,
        response_schema: Type[Schema] = None,
    ):
        def wrap(handler_function):
            method_name = (
                custom_method_name if custom_method_name is not None else handler_function.__name__
            )
            method_name = cls._normalize_method_name(method_name)
            logger.debug(f"Register method `{method_name}`")
            if method_name in cls._methods:
                raise MethodAlreadyRegistered(
                    f"Method `{method_name}` is already registered as {cls._methods[method_name]}"
                )

            cls._methods[method_name] = Method(
                name=method_name,
                handler=handler_function,
                allow_anonymous_access=allow_anonymous_access,
                request_schema=request_schema,
                response_schema=response_schema,
            )

            if allow_anonymous_access:
                cls._anonymous_access_methods.add(method_name)
            return handler_function

        return wrap

    @classmethod
    def get_available_method_names(cls):
        return list(cls._methods.keys())

    async def get_handler(self, request: Request):
        self.ws = ws = WebSocketResponse()
        await ws.prepare(request)

        logger.info(f"New connection established: {ws.status} from {request.remote}")
        last_message = None

        async for message in ws:
            message: WSMessage
            if message.type == WSMsgType.TEXT:
                last_message = message.json()
                await self.handle_request(request, last_message)

        logger.info(f"Connection closed with code: {ws.close_code}")
        await self.after_connection_close(last_message)
        return ws

    async def after_connection_close(self, last_message):
        return

    async def handle_request(self, request, payload):
        original_method_name = payload["method"]
        normalized_method_name = (
            "handle_" + re.sub(r"(?<!^)(?=[A-Z])", "_", original_method_name).lower()
        )
        handler_function = getattr(self, normalized_method_name)
        request_id = payload["id"]
        logger.debug(f"Got request:{request_id} {original_method_name}")
        response = await handler_function(
            request_id=request_id,
            params=payload["params"],
        )
        if response is not None:
            logger.debug(f"Send response to request:{request_id}")
            await self.ws.send_json(
                {
                    "id": request_id,
                    "method": original_method_name,
                    "result": response,
                }
            )
