from bluepy import Circuit

from bcss.circuit_info.schemas.ci_get_cell_ids import (
    CellIdsRequestSchema,
    CellIdsResponseSchema,
)
from bcss.main.consumers import CircuitServiceConsumer
from common.jsonrpc.consumer import JSONRPCRequest


@CircuitServiceConsumer.register_method(
    request_schema=CellIdsRequestSchema,
    response_schema=CellIdsResponseSchema,
)
async def ci_get_cell_ids(request: JSONRPCRequest):
    circuit = Circuit(request.params["path"])
    targets = request.params["targets"]

    if targets:
        gids = [gid for target in targets for gid in circuit.cells.ids(target).tolist()]
    else:
        gids = circuit.cells.ids().tolist()

    return {
        "ids": gids,
    }
