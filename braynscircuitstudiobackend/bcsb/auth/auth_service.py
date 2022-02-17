import logging
from typing import Optional

import aiohttp
from django.conf import settings

logger = logging.getLogger(__name__)


class AccessTokenValidator:
    def __init__(self, response: Optional[dict] = None):
        self.response = response

    def is_valid(self):
        return self.response and "preferred_username" in self.response

    @property
    def username(self):
        return self.response["preferred_username"]

    @property
    def given_name(self):
        return self.response["given_name"]

    @property
    def family_name(self):
        return self.response["family_name"]

    @property
    def email(self):
        return self.response["email"]


async def validate_access_token(access_token: bytes):
    url = settings.BBP_KEYCLOAK_USER_INFO_URL
    json_response = None
    if access_token:
        request_headers = {
            "Host": settings.BBP_KEYCLOAK_HOST,
            "Authorization": f"Bearer {access_token.decode('utf-8')}",
        }
        async with aiohttp.ClientSession() as session:
            json_response = await session.get(url, headers=request_headers)
        logger.debug(f"Request headers: {request_headers}")
        json_response = await json_response.json()
    return AccessTokenValidator(response=json_response)
