from asyncio import Future
from http import HTTPStatus
from unittest.mock import AsyncMock, MagicMock

import pytest
from furl import furl

from bcsb.unicore.unicore_service import UnicoreService, ClientResponse


@pytest.mark.asyncio
async def test_get_unicore_request_headers(unicore_service: UnicoreService, TEST_TOKEN: str):
    expected_request_headers = {
        "Authorization": f"Bearer {TEST_TOKEN}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    request_headers = await unicore_service.get_unicore_request_headers()
    assert request_headers == expected_request_headers

    request_headers_with_extra = await unicore_service.get_unicore_request_headers(
        {"Accept": "application/octet-stream", "Connection": "keep-alive"}
    )
    expected_request_headers_with_extra = {
        "Authorization": f"Bearer {TEST_TOKEN}",
        "Accept": "application/octet-stream",
        "Content-Type": "application/json",
        "Connection": "keep-alive",
    }
    assert request_headers_with_extra == expected_request_headers_with_extra


@pytest.mark.asyncio
async def test_get_unicore_endpoint_furl(unicore_service: UnicoreService):
    assert unicore_service.get_unicore_endpoint_furl("jobs") == furl(
        "https://bbpunicore.epfl.ch:8080/BB5-CSCS/rest/core/jobs"
    )


@pytest.mark.asyncio
async def test_make_unicore_http_request(mocker, unicore_service: UnicoreService):
    mock_response_data = {
        "_links": {
            "self": {
                "href": "https://bbpunicore.epfl.ch:8080/BB5-CSCS/rest/core/jobs?offset=0&num=200"
            }
        },
        "jobs": [
            "d9fbc219-0e53-41e1-a518-ea35d9946c5c",
        ],
    }

    mock_response = AsyncMock(ClientResponse)
    mock_response.status = HTTPStatus.OK
    mock_response.json.return_value = mock_response_data

    response_future = Future()
    response_future.set_result(mock_response)

    mocker.patch(
        "bcsb.unicore.unicore_service.ClientSession.get",
        return_value=response_future,
    )

    # Make the actual service call
    response = await unicore_service.make_unicore_http_request("get", "jobs")
    assert response.status == HTTPStatus.OK

    actual_response = await response.json()
    expected_response = {
        "_links": {
            "self": {
                "href": "https://bbpunicore.epfl.ch:8080/BB5-CSCS/rest/core/jobs?offset=0&num=200"
            }
        },
        "jobs": [
            "d9fbc219-0e53-41e1-a518-ea35d9946c5c",
        ],
    }
    assert actual_response == expected_response


@pytest.mark.asyncio
async def test_http_request_unicore(mocker, unicore_service: UnicoreService):
    mock_http_request: MagicMock = mocker.patch(
        "bcsb.unicore.unicore_service.UnicoreService.make_unicore_http_request",
    )

    await unicore_service.http_get_unicore("jobs")
    mock_http_request.assert_called_with("get", "jobs")

    await unicore_service.http_post_unicore("jobs", {})
    mock_http_request.assert_called_with("post", "jobs", {})
