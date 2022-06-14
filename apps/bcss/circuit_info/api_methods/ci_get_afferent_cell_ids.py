import logging

from bluepy import Circuit

from bcss.circuit_info.schemas.ci_get_afferent_cell_ids import (
    AfferentCellIdsRequestSchema,
    AfferentCellIdsResponseSchema,
)
from bcss.main.consumers import CircuitServiceConsumer
from common.jsonrpc.consumer import JSONRPCRequest, JSONRPCConsumer

logger = logging.getLogger(__name__)


@CircuitServiceConsumer.register_method(
    request_schema=AfferentCellIdsRequestSchema,
    response_schema=AfferentCellIdsResponseSchema,
)
async def ci_get_afferent_cell_ids(request: JSONRPCRequest, consumer: JSONRPCConsumer):
    path = request.params["path"]
    sources = request.params["sources"]
    circuit = Circuit(path)

    ids = sorted(
        value
        for source_gid in sources
        for value in circuit.connectome.afferent_gids(source_gid).tolist()
    )

    return {
        "ids": ids,
    }
