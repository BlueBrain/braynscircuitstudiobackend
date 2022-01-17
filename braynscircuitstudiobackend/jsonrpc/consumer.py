import datetime
import json
import logging

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from jsonrpc.exceptions import MethodAndErrorNotAllowedTogether

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


class JSONRPCResponse:
    def __init__(self, request: JSONRPCRequest, result=None, error=None):
        self.id = request.id
        if result and error:
            raise MethodAndErrorNotAllowedTogether
        self.result = result
        self.error = error

    async def get_serialized_result(self):
        return json.dumps(await self.get_response_payload(), default=self.__serializer)

    async def get_response_payload(self) -> dict:
        payload = {
            "jsonrpc": JSONRPC_VERSION,
            "id": self.id,
        }
        if self.error:
            payload["error"] = self.error
        if self.result:
            payload["result"] = self.result
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
    def register_method(cls, method_name: str, allow_anonymous_access=False):
        def wrap(f):
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
        method_result = await method_handler(request)
        response = JSONRPCResponse(request, method_result)
        await self.send(text_data=await response.get_serialized_result(), close=False)

    async def _deny_access_to_method(self, request):
        response = JSONRPCResponse(
            request,
            error={
                "message": "This method is not accessible for anonymous users - please authenticate first"
            },
        )
        await self.send(text_data=await response.get_serialized_result())
