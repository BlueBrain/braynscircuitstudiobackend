"""Version entrypoint test file."""
import pytest
import brayns_circuit_studio_backend
from brayns_circuit_studio_backend.api_version import VersionEntryPoint


@pytest.mark.asyncio
async def test_entrypoint_version():
    """Should return the current version."""
    entrypoint = VersionEntryPoint(brayns_circuit_studio_backend.version.__version__)
    version = await entrypoint.exec(None)
    assert version == brayns_circuit_studio_backend.version.__version__
