from aiohttp import ClientResponse, ClientSession
from django.conf import settings
from furl import furl


async def get_unicore_request_headers(token: str):
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def get_unicore_endpoint_furl(endpoint: str) -> furl:
    url = furl(settings.BBP_UNICORE_URL)
    url /= settings.BBP_UNICORE_CORE_PATH
    url /= endpoint
    return url


async def make_unicore_http_request(
    http_method_name: str,
    endpoint: str,
    payload=None,
    token: str = None,
) -> ClientResponse:
    url: furl = get_unicore_endpoint_furl(endpoint)
    async with ClientSession() as session:
        assert http_method_name.lower() in ("post", "get")
        method = getattr(session, http_method_name)
        response = await method(
            url.url,
            headers=await get_unicore_request_headers(token=token),
            data=payload,
        )
    return response


async def http_get_unicore(endpoint: str, token: str = None) -> ClientResponse:
    return await make_unicore_http_request(
        "get",
        endpoint,
        token=token,
    )


async def http_post_unicore(endpoint: str, payload, token: str = None) -> ClientResponse:
    return await make_unicore_http_request(
        "post",
        endpoint,
        payload,
        token=token,
    )
