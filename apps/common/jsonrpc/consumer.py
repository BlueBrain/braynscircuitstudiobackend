import inspect
import json
import logging
from json import JSONDecodeError
from typing import Optional, Type, Dict

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.conf import settings
from pydash import get
from rest_framework import serializers


from common.jsonrpc.exceptions import (
    MethodAndErrorNotAllowedTogether,
    MethodAlreadyRegistered,
    MethodNotAsynchronous,
    MethodNotFound,
    JSONRPCException,
    JSONRPCParseError,
    InvalidJSONRPCRequest,
)
from common.jsonrpc.methods import Method
from common.jsonrpc.serializers import JSONRPCResponseSerializer
from common.utils.serializers import load_via_serializer

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
    def create_from_channels(cls, data, method: Method, consumer: "JSONRPCConsumer"):
        try:
            request_id = data["id"]
        except KeyError:
            raise InvalidJSONRPCRequest("Missing `id` in the request body")

        try:
            params = load_via_serializer(
                serializer_class=method.request_serializer,
                data=data.get("params", {}),
            )
        except serializers.ValidationError as error:
            logger.debug(f"create_from_channels errors: {error.detail}")
            raise

        return JSONRPCRequest(
            request_id=request_id,
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
        request_serializer: Type[serializers.Serializer] = None,
        response_serializer: Type[serializers.Serializer] = None,
    ):
        def wrap(handler_function):
            method_name = (
                custom_method_name if custom_method_name is not None else handler_function.__name__
            )
            method_name = cls._normalize_method_name(method_name)

            logger.debug(f"Registering method `{method_name}`")

            if not inspect.iscoroutinefunction(handler_function):
                raise MethodNotAsynchronous(
                    f"Method {handler_function} must be a coroutine function. "
                    f"Try using `async def {handler_function.__name__}(...)` instead."
                )

            if method_name in cls._methods:
                raise MethodAlreadyRegistered(
                    f"Method `{method_name}` is already registered as {cls._methods[method_name]}"
                )

            cls._methods[method_name] = Method(
                name=method_name,
                handler=handler_function,
                allow_anonymous_access=allow_anonymous_access,
                request_serializer=request_serializer,
                response_serializer=response_serializer,
            )

            if allow_anonymous_access:
                cls._anonymous_access_methods.add(method_name)
            return handler_function

        return wrap

    @classmethod
    def get_available_method_names(cls):
        return list(cls._methods.keys())

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        try:
            return await self._handle_receive(text_data=text_data, bytes_data=bytes_data, **kwargs)
        except JSONRPCParseError as exception:
            await self._handle_jsonrpc_exception(exception=exception)

    async def _handle_receive(self, text_data=None, bytes_data=None, **kwargs):
        try:
            return await super().receive(text_data=text_data, bytes_data=bytes_data, **kwargs)
        except JSONDecodeError as exception:
            raise JSONRPCParseError(exception.msg) from exception

    async def receive_json(self, content: Dict, **kwargs):
        try:
            return await self._handle_incoming_json(content=content, **kwargs)
        except JSONRPCException as exception:
            await self._handle_jsonrpc_exception(content=content, exception=exception)

    async def _handle_incoming_json(self, content: Dict, **kwargs):
        """
        When receiving a JSON message, we create a JSONRPCRequest
        in order to imitate more a request-response cycle.

        :param content:
        :param kwargs:
        :return:
        """
        try:
            method_name = content["method"]
        except KeyError:
            raise InvalidJSONRPCRequest("Missing `method` key in the request object")

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

    async def _handle_jsonrpc_exception(self, exception: JSONRPCException, content: Dict = None):
        logger.exception("JSONRPCException raised", exc_info=exception)
        exception_response = {
            "id": get(content, "id"),
            "error": exception,
        }
        response_serializer = JSONRPCResponseSerializer(exception_response)
        await self.send(
            text_data=json.dumps(response_serializer.data),
            close=False,
        )

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
        response = JSONRPCResponse(
            request,
            result=payload,
            method_name=method_name,
        )
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
        try:
            return cls._methods[method_name]
        except KeyError:
            raise MethodNotFound(f"Method `{method_name}` could not be found")
