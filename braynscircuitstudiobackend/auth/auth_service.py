import aiohttp
from django.conf import settings


class AccessTokenValidator:
    def __init__(self, response: dict):
        self.response = response
        assert "preferred_username" in self.response

    def is_valid(self):
        return self.username

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
    request_headers = {
        "Host": settings.BBP_KEYCLOAK_HOST,
        "Authorization": f"Bearer {access_token.decode('utf-8')}",
    }
    async with aiohttp.ClientSession() as session:
        response = await session.get(url, headers=request_headers)
    print("Request headers:", request_headers)
    print(await response.json())
    return AccessTokenValidator(await response.json())
