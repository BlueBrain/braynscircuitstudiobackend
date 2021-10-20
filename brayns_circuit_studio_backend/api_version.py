"""Entrypoint: version() -> str."""
from entrypoint import EntryPoint


class VersionEntryPoint(EntryPoint):
    """Entrypoint: version() -> str.

    No input. Return the current version.
    """

    def __init__(self, version):
        """Set version number."""
        self.version = version

    @property
    def name(self):
        """Name of this entrypoint."""
        return "version"

    async def exec(self, params):
        """Return version of Brayns Circuit Studio Backend."""
        del params  # Unused
        return self.version
