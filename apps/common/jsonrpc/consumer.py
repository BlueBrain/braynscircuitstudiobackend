import asyncio
import inspect
import json
import logging
from json import JSONDecodeError
from threading import Thread
from typing import Optional, Type, Dict, Union
from uuid import uuid4, UUID

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.conf import settings
from django.contrib.auth.models import User, AnonymousUser
from django.utils.timezone import now
from pydash import get
from rest_framework import serializers

from common.jsonrpc.exceptions import (
    MethodAndErrorNotAllowedTogether,
    MethodAlreadyRegistered,
    MethodNotAsynchronous,
    MethodNotFound,
    JSONRPCException,
    JSONRPCParseError,
)
from common.jsonrpc.methods import Method
from common.jsonrpc.serializers import JSONRPCResponseSerializer, JSONRPCRequestSerializer
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
    def create_from_channels(
        cls, data, request_id, params, consumer: "JSONRPCConsumer"
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


class RunningMethod:
    id: UUID
    request: JSONRPCRequest
    thread: Thread
    started_at = None
    consumer: "JSONRPCConsumer"

    def __init__(
        self,
        consumer: "JSONRPCConsumer",
        request: JSONRPCRequest,
    ):
        self.id = uuid4()
        self.consumer = consumer
        self.request = request
        self.thread = Thread(
            target=asyncio.run,
            args=(self.run_method(),),
        )

    async def run_method(self):
        await self.consumer.process_method_handler(self.request)
        # Let the consumer know that the method has finished
        self.consumer.dequeue_job(self.id)

    def start(self):
        self.consumer.queue_job(self)
        self.started_at = now()
        return self.thread.start()

    def is_alive(self):
        return self.thread.is_alive()

    @property
    def request_id(self):
        return self.request.id

    @property
    def method_name(self):
        return self.request.method_name

    @property
    def uptime(self):
        if self.started_at is None:
            return 0
        return (now() - self.started_at).total_seconds()


class JSONRPCConsumer(AsyncJsonWebsocketConsumer):
    methods = {}
    anonymous_access_methods = set()
    is_authentication_required = True
    job_queue: Dict[UUID, RunningMethod] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.job_queue = {}

    @classmethod
    def normalize_method_name(cls, name: str):
        normalized_name = name.replace("_", "-")
        return normalized_name

    @classmethod
    def register_method(
        cls,
        custom_method_name: str = None,
        allow_anonymous_access: bool = False,
        request_serializer_class: Type[serializers.Serializer] = None,
        response_serializer_class: Type[serializers.Serializer] = None,
    ):
        def wrap(handler_function):
            method_name = (
                custom_method_name if custom_method_name is not None else handler_function.__name__
            )
            method_name = cls.normalize_method_name(method_name)

            logger.debug(f"Registering method `{method_name}`")

            if not inspect.iscoroutinefunction(handler_function):
                raise MethodNotAsynchronous(
                    f"Method {handler_function} must be a coroutine function. "
                    f"Try using `async def {handler_function.__name__}(...)` instead."
                )

            if method_name in cls.methods:
                raise MethodAlreadyRegistered(
                    f"Method `{method_name}` is already registered as {cls.methods[method_name]}"
                )

            cls.methods[method_name] = Method(
                name=method_name,
                handler=handler_function,
                allow_anonymous_access=allow_anonymous_access,
                request_serializer_class=request_serializer_class,
                response_serializer_class=response_serializer_class,
            )

            if allow_anonymous_access:
                cls.anonymous_access_methods.add(method_name)
            return handler_function

        return wrap

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
        method: Optional[Method] = None
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
        method: Method = self.methods[request.method_name]
        result_data = await method.handler(request)
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
    def get_method(cls, method_name) -> Method:
        try:
            return cls.methods[method_name]
        except KeyError:
            raise MethodNotFound(f"Method `{method_name}` could not be found")
