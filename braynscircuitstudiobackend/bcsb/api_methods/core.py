import logging

from bcsb.consumers import CircuitStudioConsumer
from version import VERSION

logger = logging.getLogger(__name__)


@CircuitStudioConsumer.register_method("version", allow_anonymous_access=True)
async def get_version(*_):
    return {
        "version": VERSION,
    }


@CircuitStudioConsumer.register_method("help", allow_anonymous_access=True)
async def get_available_methods(*_):
    return {
        "available_methods": CircuitStudioConsumer.get_available_methods(),
    }
