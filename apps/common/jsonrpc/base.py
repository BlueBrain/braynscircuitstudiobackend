from abc import ABC, abstractmethod
from typing import Dict, Any, Type, Union, Optional
from uuid import UUID

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import User, AnonymousUser
from rest_framework import serializers


class BaseJSONRPCRequest(ABC):
    id: Any
    params: Dict[str, Any]
    method_name: str
    consumer: "BaseJSONRPCConsumer"

    @property
    @abstractmethod
    def user(self) -> Union[User, AnonymousUser]:
        ...

    @property
    @abstractmethod
    def token(self) -> Optional[str]:
        ...

    @property
    @abstractmethod
    def scope(self):
        ...


class BaseJSONRPCResponse(ABC):
    pass


class BaseJSONRPCMethod(ABC):
    request: BaseJSONRPCRequest
    custom_method_name: str
    request_serializer_class: Type[serializers.Serializer]
    response_serializer_class: Type[serializers.Serializer]
    allow_anonymous_access: bool

    @property
    @abstractmethod
    def docstring(self):
        ...

    @abstractmethod
    def prepare(self, request: BaseJSONRPCRequest = None):
        ...

    @abstractmethod
    async def run(self):
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        ...


class BaseJSONRPCConsumer(ABC, AsyncJsonWebsocketConsumer):
    title: str
    methods: Dict[str, Type[BaseJSONRPCMethod]]
    is_authentication_required: bool
    request_queue: Dict[UUID, Any]

    @classmethod
    @abstractmethod
    def autodiscover_methods(cls):
        ...

    @classmethod
    @abstractmethod
    def get_available_method_names(cls):
        ...

    @classmethod
    @abstractmethod
    def get_methods(cls) -> Dict[str, Type[BaseJSONRPCMethod]]:
        ...

    @classmethod
    @abstractmethod
    def get_method(cls, method_name) -> Type[BaseJSONRPCMethod]:
        ...

    @abstractmethod
    async def send_method_response(self, request: BaseJSONRPCRequest, payload):
        ...

    @abstractmethod
    async def send_response(
        self,
        request: BaseJSONRPCRequest,
        result,
        method_name: str = None,
    ):
        ...
