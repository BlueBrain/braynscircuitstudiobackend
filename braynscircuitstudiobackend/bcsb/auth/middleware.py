import logging

from bcsb.auth.auth_service import (
    get_user_from_access_token,
    get_access_token_from_headers_as_string,
    authenticate_user,
)

logger = logging.getLogger(__name__)


class KeyCloakAuthMiddleware:
    """
    This middleware provides authentication based on HTTP headers sent when establishing connection.

    Once the authentication is done, a user instance is appended to the scope.

    Please note that anonymous connections are allowed but they may be denied to access most of the methods.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        headers = scope["headers"]
        access_token = get_access_token_from_headers_as_string(headers)
        await authenticate_user(access_token, scope)
        return await self.app(scope, receive, send)
