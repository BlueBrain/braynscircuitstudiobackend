from aiohttp import ClientResponse, ClientSession
from django.conf import settings
from furl import furl


class UnicoreService:
    _token: str = None

    def __init__(self, token: str = None):
        self.set_token(token)

    def set_token(self, token: str):
        self._token = token

    async def get_unicore_request_headers(self, extra_headers: dict = None):
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if extra_headers:
            headers.update(extra_headers)
        return headers

    def get_unicore_furl(self) -> furl:
        url = furl(settings.BBP_UNICORE_URL)
        url /= settings.BBP_UNICORE_CORE_PATH
        return url

    def get_unicore_endpoint_furl(self, endpoint: str) -> furl:
        return self.get_unicore_furl() / endpoint

    async def make_unicore_http_request(
        self,
        http_method_name: str,
        path: str,
        payload=None,
        extra_headers: dict = None,
    ) -> ClientResponse:
        url: furl = self.get_unicore_endpoint_furl(path)
        request_headers = await self.get_unicore_request_headers(extra_headers)
        async with ClientSession() as session:
            assert http_method_name.lower() in ("post", "get", "put")
            method = getattr(session, http_method_name)
            response = await method(
                url.url,
                headers=request_headers,
                data=payload,
            )
        return response

    async def http_get_unicore(self, endpoint: str) -> ClientResponse:
        return await self.make_unicore_http_request(
            "get",
            endpoint,
        )

    async def http_post_unicore(self, endpoint: str, payload) -> ClientResponse:
        return await self.make_unicore_http_request(
            "post",
            endpoint,
            payload,
        )
