import datetime
import json
import logging

from channels.generic.websocket import AsyncJsonWebsocketConsumer

from jsonrpc.exceptions import MethodAndErrorNotAllowedTogether

logger = logging.getLogger(__name__)

JSONRPC_VERSION = "2.0"


class JSONRPCRequest:
    def __init__(self, data):
        self.id = data["id"]
        self.method = data["method"]
        self.params = data.get("params")


class JSONRPCResponse:
    def __init__(self, request: JSONRPCRequest, result, error=None):
        self.id = request.id
        if result and error:
            raise MethodAndErrorNotAllowedTogether
        self.result = result
        self.error = error

    async def get_serialized_result(self):
        return json.dumps(await self.get_response_payload(), default=self.__serializer)

    async def get_response_payload(self):
        return {
            "jsonrpc": JSONRPC_VERSION,
            "id": self.id,
            "result": self.result,
        }

    @staticmethod
    def __serializer(obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return str(obj)


class JSONRPCConsumer(AsyncJsonWebsocketConsumer):
    methods = {}

    @classmethod
    def register_method(cls, method_name: str):
        def wrap(f):
            cls.methods[method_name] = f
            return f

        return wrap

    @classmethod
    def get_available_methods(cls):
        return list(cls.methods.keys())

    async def receive_json(self, content, **kwargs):
        request = JSONRPCRequest(content)
        method_handler = self.methods[request.method]
        method_result = await method_handler(request)
        response = JSONRPCResponse(request, method_result)
        await self.send(text_data=await response.get_serialized_result(), close=False)
