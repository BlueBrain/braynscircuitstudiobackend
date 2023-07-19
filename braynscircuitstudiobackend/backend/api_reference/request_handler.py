from aiohttp.web_request import Request
from aiohttp.web_response import json_response

from .action_docs import get_api_reference_json


def api_reference_view(request: Request):
    return json_response(get_api_reference_json())
