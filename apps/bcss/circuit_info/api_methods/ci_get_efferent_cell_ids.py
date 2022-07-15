from bluepy import Circuit

from bcss.circuit_info.schemas.ci_get_efferent_cell_ids import (
    EfferentCellIdsRequestSchema,
    EfferentCellIdsResponseSchema,
)
from bcss.main.consumers import CircuitServiceConsumer
from common.jsonrpc.consumer import JSONRPCRequest


@CircuitServiceConsumer.register_method(
    request_schema=EfferentCellIdsRequestSchema,
    response_schema=EfferentCellIdsResponseSchema,
)
async def ci_get_efferent_cell_ids(request: JSONRPCRequest):
    path = request.params["path"]
    sources = request.params["sources"]
    circuit = Circuit(path)

    ids = sorted(
        value
        for source_gid in sources
        for value in circuit.connectome.efferent_gids(source_gid).tolist()
    )

    return {
        "ids": ids,
    }
