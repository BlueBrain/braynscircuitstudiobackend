import logging
from http import HTTPStatus
from typing import Tuple, Optional, Union, Dict

import aiohttp
from aiohttp import ClientResponse
from channels.db import database_sync_to_async
from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User

from .serializers import KeycloakUserInfoResponseSerializer

logger = logging.getLogger(__name__)


class AccessTokenResponseValidator:
    def __init__(self, client_response: ClientResponse):
        self._is_valid: Optional[bool] = None
        self.user_info_data: Optional[Dict] = None
        self.client_response = client_response

    @property
    def is_valid(self):
        if self._is_valid is None:
            raise Exception("Validate")
        return self._is_valid

    async def validate(self):
        self._is_valid = self.client_response.status == HTTPStatus.OK

        if self._is_valid:
            user_info_response_serializer = KeycloakUserInfoResponseSerializer(
                await self.client_response.json()
            )
            self.user_info_data = user_info_response_serializer.data
            logger.debug(f"self.user_info_data={self.user_info_data}")


async def validate_access_token(access_token: bytes) -> AccessTokenResponseValidator:
    url = settings.BBP_KEYCLOAK_USER_INFO_URL
    if access_token:
        request_headers = {
            "Host": settings.BBP_KEYCLOAK_HOST,
            "Authorization": f"Bearer {access_token.decode('utf-8')}",
        }
        logger.debug(f"Request headers to `{url}`: {request_headers}")
        async with aiohttp.ClientSession() as session:
            client_response = await session.get(url, headers=request_headers)
            response_validator = AccessTokenResponseValidator(client_response=client_response)
            await response_validator.validate()
        logger.debug(f"Response from auth service: {client_response}")
    return response_validator


def create_user_from_user_info_data(user_info_data: dict) -> User:
    new_user = User.objects.create(
        username=user_info_data["preferred_username"],
        first_name=user_info_data["given_name"],
        last_name=user_info_data["family_name"],
        email=user_info_data["email"],
    )
    return new_user


def update_user_from_user_info_data(user: User, user_info_data: dict) -> User:
    user.username = user_info_data["preferred_username"]
    user.first_name = user_info_data["given_name"]
    user.last_name = user_info_data["family_name"]
    user.email = user_info_data["email"]
    user.save()
    return user


@database_sync_to_async
def get_or_create_user_from_user_info_response(user_info_data: dict) -> User:
    try:
        user = User.objects.get(username=user_info_data["preferred_username"])
        is_new = False
    except User.DoesNotExist:
        user = create_user_from_user_info_data(user_info_data)
        is_new = True
    if not is_new:
        update_user_from_user_info_data(user, user_info_data)
    return user


async def get_user_from_access_token(access_token: Union[bytes, str]) -> Union[User, AnonymousUser]:
    access_token_encoded = None
    if isinstance(access_token, bytes):
        access_token_encoded = access_token
    elif isinstance(access_token, str):
        access_token_encoded = access_token.encode()

    user = AnonymousUser()

    if not settings.CHECK_ACCESS_TOKENS and settings.DEBUG:
        return user

    if access_token_encoded is not None:
        response_validator: AccessTokenResponseValidator = await validate_access_token(
            access_token_encoded
        )
        if response_validator.is_valid:
            user = await get_or_create_user_from_user_info_response(
                response_validator.user_info_data
            )

    return user


def get_access_token_from_headers(headers) -> Optional[bytes]:
    headers_dict = dict(headers)
    if b"authorization" not in dict(headers):
        logger.debug("'Authorization' header is not present within the given scope")
        return None

    authorization_header = headers_dict[b"authorization"]
    authorization_header_parts: Tuple[bytes, bytes] = authorization_header.split(b" ")
    assert (
        authorization_header_parts[0].lower() == b"bearer"
    ), "Authorization header value format seems to be invalid. No 'Bearer' found"
    assert (
        len(authorization_header_parts) == 2
    ), "Authorization header has invalid value. Provide it in 'Bearer <access_token>' format"
    access_token = authorization_header_parts[1]
    return access_token


def get_access_token_from_headers_as_string(headers) -> Optional[str]:
    token = get_access_token_from_headers(headers)
    return token.decode("utf-8") if token is not None else None


async def authenticate_user(access_token, scope) -> Union[User, AnonymousUser]:
    user = await get_user_from_access_token(access_token)
    logger.debug(
        f"Authenticated user = '{user.username}'{' (anonymous)' if user.is_anonymous else ''}"
    )
    scope["user"] = user
    scope["token"] = access_token
    return user
