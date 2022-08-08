from typing import Optional, Union

from django.contrib.auth.models import User, AnonymousUser

from common.jsonrpc.base import BaseJSONRPCConsumer


class JSONRPCRequest:
    method_name: str
    consumer: BaseJSONRPCConsumer

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
    def create_from_channels(
        cls, data, request_id, params, consumer: BaseJSONRPCConsumer
    ) -> "JSONRPCRequest":
        return JSONRPCRequest(
            request_id=request_id,
            method_name=data["method"],
            params=params,
            consumer=consumer,
        )

    @property
    def user(self) -> Union[User, AnonymousUser]:
        return self.scope["user"]

    @property
    def token(self) -> Optional[str]:
        return self.scope.get("token")
