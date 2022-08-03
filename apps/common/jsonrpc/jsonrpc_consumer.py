import inspect
import json
import logging
from importlib import import_module
from json import JSONDecodeError
from typing import Optional, Type, Dict
from uuid import UUID

from django.apps import apps
from django.conf import settings
from pydash import get
from rest_framework import serializers

from common.jsonrpc.base_jsonrpc_consumer import BaseJSONRPCConsumer
from common.jsonrpc.exceptions import (
    MethodAlreadyRegistered,
    MethodNotAsynchronous,
    MethodNotFound,
    JSONRPCException,
    JSONRPCParseError,
)
from common.jsonrpc.jsonrpc_request import JSONRPCRequest
from common.jsonrpc.jsonrpc_response import JSONRPCResponse
from common.jsonrpc.jsonrpc_method import JSONRPCMethod
from common.jsonrpc.running_method import RunningMethod
from common.jsonrpc.serializers import JSONRPCResponseSerializer, JSONRPCRequestSerializer
from common.utils.serializers import load_via_serializer

logger = logging.getLogger(__name__)


class JSONRPCConsumer(BaseJSONRPCConsumer):
    methods = {}
    is_authentication_required = True
    job_queue: Dict[UUID, RunningMethod] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.job_queue = {}

    @classmethod
    def autodiscover_methods(cls):
        for app in apps.get_app_configs():
            package_name = f"{app.module.__package__}.{settings.API_METHODS_PACKAGE_NAME}"
            logger.debug(f"Loading package: {package_name}")
            try:
                module = import_module(package_name)
                logger.debug(f"Loaded consumer methods module: {module.__package__}")
            except ModuleNotFoundError:
                # Having API methods package/module is not compulsory, so we can ignore it
                continue
            except ImportError:
                # We want to be notified of any import errors here (at the app startup)
                raise

            method_classes = [
                action_class
                for name, action_class in module.__dict__.items()
                if isinstance(action_class, type)
                and issubclass(action_class, JSONRPCMethod)
                and action_class != JSONRPCMethod
            ]

            # Register encountered actions in the consumer
            for action_class in method_classes:
                cls.add_method_to_register(action_class)

        registered_methods = []
        for method_name in cls.get_available_method_names():
            registered_methods.append(method_name)
        registered_methods.sort()
        logger.debug(
            f"Registered methods:\n"
            + "\n".join([f"{i + 1}. {name}" for i, name in enumerate(registered_methods)])
        )

    @classmethod
    def normalize_method_name(cls, name: str):
        normalized_name = name.replace("_", "-")
        return normalized_name

    @classmethod
    def add_method_to_register(cls, method_class: Type[JSONRPCMethod]):
        method_name = method_class.get_method_name()

        if method_name in cls.methods:
            raise MethodAlreadyRegistered(
                f"Method `{method_name}` is already registered as {cls.methods[method_name]}"
            )

        if not inspect.iscoroutinefunction(method_class.run):
            raise MethodNotAsynchronous(
                f"The run() method must be a coroutine function in {cls.__name__}. "
                f"Try using `async def run(...)` instead."
            )

        logger.debug(f"Registering {method_class=} as {method_name=}")
        cls.methods[method_name] = method_class

    @classmethod
    def get_available_method_names(cls):
        return list(cls.methods.keys())

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        try:
            return await self.handle_receive(
                text_data=text_data,
                bytes_data=bytes_data,
                **kwargs,
            )
        except JSONRPCParseError as exception:
            # We can't pass `content` here because we are not sure whether the data was valid JSON
            # See .receive_json() method
            await self.handle_jsonrpc_exception(exception=exception)

    async def handle_receive(self, text_data=None, bytes_data=None, **kwargs):
        try:
            return await super().receive(text_data=text_data, bytes_data=bytes_data, **kwargs)
        except JSONDecodeError as exception:
            raise JSONRPCParseError(exception.msg) from exception

    async def receive_json(self, content: Dict, **kwargs):
        method: Optional[JSONRPCMethod] = None
        request: Optional[JSONRPCRequest] = None

        try:
            request_serializer_data = load_via_serializer(
                content,
                JSONRPCRequestSerializer,
            )
            method = self.get_method(request_serializer_data["method"])
            params = load_via_serializer(
                request_serializer_data.get("params", {}),
                method.request_serializer_class,
            )
            request = JSONRPCRequest.create_from_channels(
                data=request_serializer_data,
                request_id=request_serializer_data["id"],
                params=params,
                consumer=self,
            )
        except JSONRPCException as exception:
            await self.handle_jsonrpc_exception(exception=exception, content=content)
        except serializers.ValidationError as exception:
            await self.handle_validation_error(exception=exception, content=content)

        if request is None:
            return

        allowed_to_process_method = (
            not settings.CHECK_ACCESS_TOKENS
            or not self.scope["user"].is_anonymous
            or method.allow_anonymous_access
            or not self.is_authentication_required
        )

        if allowed_to_process_method:
            running_method = RunningMethod(
                consumer=self,
                request=request,
            )
            running_method.start()
        else:
            await self.deny_access_to_method(request)

    def queue_job(self, job: RunningMethod):
        self.job_queue[job.id] = job

    def dequeue_job(self, job_id: UUID):
        del self.job_queue[job_id]

    async def handle_jsonrpc_exception(self, exception: JSONRPCException, content: Dict = None):
        logger.exception("JSONRPCException raised", exc_info=exception)
        exception_response = {
            "id": get(content, "id"),
            "error": {
                "name": exception.__class__.__name__,
                "code": exception.code,
                "message": exception.message,
            },
        }
        response_serializer = JSONRPCResponseSerializer(exception_response)
        await self.send_data(response_serializer.data)

    async def handle_validation_error(
        self, exception: serializers.ValidationError, content: Dict = None
    ):
        logger.exception("serializers.ValidationError raised", exc_info=exception)
        exception_response = {
            "id": get(content, "id"),
            "error": {
                "name": "ValidationError",
                "code": exception.status_code,
                "data": {
                    "problems": exception.get_full_details(),
                },
            },
        }
        response_serializer = JSONRPCResponseSerializer(exception_response)
        await self.send_data(response_serializer.data)

    async def send_data(self, data):
        return await self.send(
            text_data=json.dumps(data),
            close=False,
        )

    async def process_method_handler(self, request: JSONRPCRequest):
        method_class: Type[JSONRPCMethod] = self.methods[request.method_name]
        method = method_class()
        result_data = await method.run(request)
        response_serializer = method.response_serializer_class(result_data)
        await self.send_response(
            request,
            result=response_serializer.data,
        )

    async def send_method_response(self, request: JSONRPCRequest, payload):
        await self.send_response(
            request,
            payload,
            method_name=request.method_name,
        )

    async def send_response(
        self,
        request: JSONRPCRequest,
        result,
        method_name: str = None,
    ):
        response = JSONRPCResponse(
            request,
            result=result,
            method_name=method_name,
        )
        await self.send(
            text_data=await response.get_serialized_result(),
            close=False,
        )

    async def deny_access_to_method(self, request):
        response = JSONRPCResponse(
            request,
            error={
                "message": "This method is not accessible for anonymous users - please authenticate first"
            },
        )
        await self.send(text_data=await response.get_serialized_result())

    @classmethod
    def get_method(cls, method_name) -> Type[JSONRPCMethod]:
        try:
            return cls.methods[method_name]
        except KeyError:
            logger.debug(f"Get method {method_name=}")
            raise MethodNotFound(f"Method `{method_name}` could not be found")
