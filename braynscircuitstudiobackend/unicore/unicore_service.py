from aiohttp import ClientResponse, ClientSession
from django.conf import settings
from furl import furl
from marshmallow import Schema


async def get_unicore_request_headers(token: str):
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


async def make_unicore_http_request(
    http_method_name: str, endpoint: str, payload=None
) -> ClientResponse:
    url = furl(settings.BBP_UNICORE_URL)
    url /= settings.BBP_UNICORE_CORE_PATH
    url /= endpoint
    token = ""
    async with ClientSession() as session:
        assert http_method_name.lower() in ("post", "get")
        method = getattr(session, http_method_name)
        response = await method(
            url.url,
            headers=await get_unicore_request_headers(token=token),
            data=payload,
        )
    return response


async def http_get_unicore(endpoint: str) -> ClientResponse:
    return await make_unicore_http_request("get", endpoint)


async def http_post_unicore(endpoint: str, payload) -> ClientResponse:
    return await make_unicore_http_request("post", endpoint, payload)


def dump_schema(schema: type(Schema), data: dict):
    schema_instance: Schema = schema()
    return schema_instance.dump(data)
