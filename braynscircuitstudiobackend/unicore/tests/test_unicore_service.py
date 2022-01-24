from asyncio import Future
from http import HTTPStatus
from unittest.mock import patch, MagicMock, AsyncMock
import pytest_mock
import pytest

from unicore import unicore_service


@pytest.mark.asyncio
async def test_get_unicore_request_headers():
    test_token = "eyJhbGciOiJSUzI1N...iIsInR5cCIgOiAiSldUIiwia"
    expected_request_headers = {
        "Authorization": "Bearer eyJhbGciOiJSUzI1N...iIsInR5cCIgOiAiSldUIiwia",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    request_headers = await unicore_service.get_unicore_request_headers(token=test_token)
    assert request_headers == expected_request_headers


@pytest.mark.asyncio
# @patch("unicore.unicore_service.ClientSession")
async def test_make_unicore_http_request(mocker):
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

    mock_response = AsyncMock(unicore_service.ClientResponse)
    mock_response.status = HTTPStatus.OK
    mock_response.json.return_value = mock_response_data

    response_future = Future()
    response_future.set_result(mock_response)

    mocker.patch(
        "unicore.unicore_service.ClientSession.get",
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
