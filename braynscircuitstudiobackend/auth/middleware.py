import logging
from typing import Tuple

from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser, User

from auth import auth_service
from auth.auth_service import AccessTokenValidator

logger = logging.getLogger(__name__)


def create_user_from_token(token_validator: AccessTokenValidator):
    new_user = User.objects.create(
        username=token_validator.username,
        first_name=token_validator.given_name,
        last_name=token_validator.family_name,
        email=token_validator.email,
    )
    return new_user


def update_user_from_token(user: User, token_validator: AccessTokenValidator):
    user.first_name = token_validator.given_name
    user.last_name = token_validator.family_name
    user.email = token_validator.email
    user.save()
    return user


@database_sync_to_async
def get_or_create_user_from_token_validator(token_validator: AccessTokenValidator):
    try:
        user = User.objects.get(username=token_validator.username)
        is_new = False
    except User.DoesNotExist:
        user = create_user_from_token(token_validator)
        is_new = True
    if not is_new:
        update_user_from_token(user, token_validator)
    return user


async def get_user_from_access_token(access_token):
    token_validator: AccessTokenValidator = await auth_service.validate_access_token(access_token)
    if token_validator.is_valid():
        user = await get_or_create_user_from_token_validator(token_validator)
    else:
        user = AnonymousUser()
    return user


def get_access_token_from_headers(headers):
    headers_dict = dict(headers)
    logger.debug(f"Headers = {headers}")
    assert b"authorization" in dict(
        headers
    ), "'Authorization' header is not present within the given scope"
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


class KeyCloakAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        headers = scope["headers"]
        try:
            access_token = get_access_token_from_headers(headers)
            user = await get_user_from_access_token(access_token)
        except AssertionError:
            await send({"type": "websocket.close"})
            return
        logger.debug(f"Authenticated user = {user.username}")
        scope["user"] = user
        return await self.app(scope, receive, send)
