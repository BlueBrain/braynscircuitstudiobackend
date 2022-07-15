import datetime
import json
import logging
from typing import Optional, Type, Dict

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.conf import settings
from marshmallow import Schema, ValidationError

from common.jsonrpc.exceptions import MethodAndErrorNotAllowedTogether, MethodAlreadyRegistered
from common.jsonrpc.methods import Method

logger = logging.getLogger(__name__)

JSONRPC_VERSION = "2.0"


class JSONRPCRequest:
    method_name: str
    consumer: "JSONRPCConsumer"

    def __init__(self, request_id, method_name, params, raw_data=None, consumer=None):
        self.id = request_id
        self.method_name = method_name
        self.params = params
        self.raw_data = raw_data
        self.consumer = consumer

    @property
    def scope(self):
        return self.consumer.scope

    @classmethod
    def create_from_channels(cls, data, method, consumer: "JSONRPCConsumer"):
        try:
            params = method.request_schema().load(data.get("params", {}))
        except ValidationError as error:
            logger.debug(f"create_from_channels errors: {error.messages}")
            raise
        return JSONRPCRequest(
            request_id=data["id"],
            method_name=data["method"],
            params=params,
            consumer=consumer,
        )

    @property
    def user(self):
        return self.scope["user"]

    @property
    def token(self) -> Optional[str]:
        return self.scope.get("token")


class JSONRPCResponse:
    def __init__(
        self,
        request: JSONRPCRequest,
        result=None,
        error=None,
        method_name: str = None,
    ):
        self._request = request
        self.id = self._request.id if method_name is None else None
        self.method_name = method_name
        assert self.id or self.method_name, "Response must contain either `id` or `method`"
        if result and error:
            raise MethodAndErrorNotAllowedTogether
        self.result = result
        self.error = error

    async def get_serialized_result(self):
        return json.dumps(
            await self.get_response_payload(),
            default=self.__serializer,
        )

    async def get_response_payload(self) -> dict:
        payload = {
            "jsonrpc": JSONRPC_VERSION,
        }
        if self.id is not None:
            payload["id"] = self.id
        if self.error:
            payload["error"] = self.error
        if self.result:
            payload["result"] = self.result
        if self.method_name:
            payload["method"] = self.method_name
        return payload

    @staticmethod
    def __serializer(obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return str(obj)


class JSONRPCConsumer(AsyncJsonWebsocketConsumer):
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

    async def receive_json(self, content: Dict, **kwargs):
        """
        When receiving a JSON message, we create a JSONRPCRequest
        in order to imitate more a request-response cycle.

        :param content:
        :param kwargs:
        :return:
        """
        method_name = content["method"]
        method = self.get_method(method_name)
        request = JSONRPCRequest.create_from_channels(content, method, consumer=self)
        logger.debug(f"Received message from: {request.user} => {request.raw_data}")
        if (
            not settings.CHECK_ACCESS_TOKENS
            or not self.scope["user"].is_anonymous
            or method.allow_anonymous_access
        ):
            await self._process_method(request)
        else:
            await self._deny_access_to_method(request)

    async def _process_method(self, request: JSONRPCRequest):
        method_instance: Method = self._methods[request.method_name]
        method_result = await method_instance.handler(request)
        await self.send_response(request, method_result)

    async def send_method_response(self, request: JSONRPCRequest, payload):
        await self.send_response(request, payload, method_name=request.method_name)

    async def send_response(
        self,
        request: JSONRPCRequest,
        payload,
        method_name: str = None,
    ):
        response = JSONRPCResponse(request, payload, method_name=method_name)
        await self.send(
            text_data=await response.get_serialized_result(),
            close=False,
        )

    async def _deny_access_to_method(self, request):
        response = JSONRPCResponse(
            request,
            error={
                "message": "This method is not accessible for anonymous users - please authenticate first"
            },
        )
        await self.send(text_data=await response.get_serialized_result())

    @classmethod
    def get_method(cls, method_name) -> Method:
        return cls._methods[method_name]
