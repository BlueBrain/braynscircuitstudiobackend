import pytest

from backend.actions.version import Version
from backend.jsonrpc.jsonrpc_request import JSONRPCRequest
from version import VERSION


@pytest.mark.asyncio
async def test_something():
    payload = {"id": 1, "method": "version"}
    request = JSONRPCRequest.create(
        payload,
        ws_handler=None,
    )
    action = Version(request)
    assert action.name == "version"
    result = await action.run()
    assert result == {"version": VERSION}
