from bcss.circuit_info.schemas.ci_get_cell_ids_from_model import (
    CellIdsFromModelRequestSchema,
    CellIdsFromModelResponseSchema,
)
from bcss.main.consumers import CircuitServiceConsumer
from common.jsonrpc.consumer import JSONRPCRequest, JSONRPCConsumer


@CircuitServiceConsumer.register_method(
    request_schema=CellIdsFromModelRequestSchema,
    response_schema=CellIdsFromModelResponseSchema,
)
async def ci_get_cell_ids_from_model(request: JSONRPCRequest, consumer: JSONRPCConsumer):
    gids = None
    return {
        "ids": gids,
    }
