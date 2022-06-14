from bcss.main.consumers import CircuitServiceConsumer
from common.schemas.common import VersionResponseSchema, HelpResponseSchema
from version import VERSION


@CircuitServiceConsumer.register_method(
    "version",
    allow_anonymous_access=True,
    response_schema=VersionResponseSchema,
)
async def get_version(*_):
    """Returns current version of the backend."""
    return {
        "version": VERSION,
    }


@CircuitServiceConsumer.register_method(
    "help",
    allow_anonymous_access=True,
    response_schema=HelpResponseSchema,
)
async def get_available_methods(*_):
    return {
        "available_methods": CircuitServiceConsumer.get_available_method_names(),
    }
