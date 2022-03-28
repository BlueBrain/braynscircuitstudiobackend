import datetime
import json
import logging
from typing import Optional

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from jsonrpc.exceptions import MethodAndErrorNotAllowedTogether, MethodAlreadyRegistered

logger = logging.getLogger(__name__)

JSONRPC_VERSION = "2.0"


class JSONRPCRequest:
    def __init__(self, data, scope):
        self.id = data["id"]
        self.method = data["method"]
        self.params = data.get("params")
        self.scope = scope
        self.raw_data = data

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
        method=None,
    ):
        self._request = request
        self.id = self._request.id if method is None else None
        self.method = method
        assert self.id or self.method, "Response must contain either `id` or `method`"
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
        if self.method:
            payload["method"] = self.method
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
    ):
        def wrap(f):
            method_name = custom_method_name if custom_method_name is not None else f.__name__
            method_name = cls._normalize_method_name(method_name)
            logger.debug(f"Register method `{method_name}`")
            if method_name in cls._methods:
                raise MethodAlreadyRegistered(
                    f"Method `{method_name}` is already registered as {cls._methods[method_name]}"
                )
            cls._methods[method_name] = f
            if allow_anonymous_access:
                cls._anonymous_access_methods.add(method_name)
            return f

        return wrap

    @classmethod
    def get_available_methods(cls):
        return list(cls._methods.keys())

    async def receive_json(self, content, **kwargs):
        request = JSONRPCRequest(content, self.scope)
        logger.debug(f"Received message from: {request.user} => {request.raw_data}")
        if request.method in self._anonymous_access_methods or not self.scope["user"].is_anonymous:
            await self._process_method(request)
        else:
            await self._deny_access_to_method(request)

    async def _process_method(self, request: JSONRPCRequest):
        method_handler = self._methods[request.method]
        method_result = await method_handler(request, self)
        await self.send_response(request, method_result)

    async def send_method_response(self, request: JSONRPCRequest, payload):
        await self.send_response(request, payload, method=request.method)

    async def send_response(
        self,
        request: JSONRPCRequest,
        payload,
        method: str = None,
    ):
        response = JSONRPCResponse(request, payload, method=method)
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
