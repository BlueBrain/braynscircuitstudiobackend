import logging
from typing import Union

from django.contrib.auth.models import AnonymousUser, User

from common.auth.auth_service import authenticate_user
from common.auth.serializers import AuthenticateRequestSerializer, AuthenticateResponseSerializer
from common.jsonrpc.jsonrpc_consumer import JSONRPCRequest
from common.jsonrpc.jsonrpc_method import JSONRPCMethod
from common.jsonrpc.serializers import JobQueueResponseSerializer
from common.serializers.common import (
    VersionResponseSerializer,
    HelpResponseSerializer,
)
from version import VERSION

logger = logging.getLogger(__name__)


class VersionMethod(JSONRPCMethod):
    """Returns current version of the backend."""

    allow_anonymous_access = True
    response_serializer_class = VersionResponseSerializer

    async def run(self, request: JSONRPCRequest):
        return {
            "version": VERSION,
        }


class HelpMethod(JSONRPCMethod):
    allow_anonymous_access = True
    response_serializer_class = HelpResponseSerializer

    async def run(self, request: JSONRPCRequest):
        return {
            "available_methods": request.consumer.get_available_method_names(),
        }


class AuthenticateMethod(JSONRPCMethod):
    """
    Logs a user in. You can also provide an access token while connecting to the backend.
    Use HTTP "Authorization" header with "Bearer <TOKEN>" as a value.
    """

    allow_anonymous_access = True
    request_serializer_class = AuthenticateRequestSerializer
    response_serializer_class = AuthenticateResponseSerializer

    async def run(self, request: JSONRPCRequest):
        user: Union[User, AnonymousUser] = await authenticate_user(
            request.params["token"],
            request.scope,
        )

        return {
            "user": user,
        }


class GetJobQueueMethod(JSONRPCMethod):
    """
    Returns requests that are currently being processed (jobs).

    Every JSONRPC request to the consumer is processed in a separate thread. These threads are kept record of
    in form of a "job queue". This way we can check whether the server is currently busy i.e.
    processing heavier and or longer tasks.
    """

    allow_anonymous_access = True
    response_serializer_class = JobQueueResponseSerializer

    async def run(self, request: JSONRPCRequest):
        jobs = request.consumer.job_queue
        job_count = len(jobs)

        return {
            "job_count": job_count,
            "job_queue": request.consumer.job_queue,
        }
