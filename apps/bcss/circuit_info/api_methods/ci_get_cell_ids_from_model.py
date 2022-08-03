from bcss.circuit_info.serializers.ci_get_cell_ids_from_model import (
    CellIdsFromModelRequestSerializer,
    CellIdsFromModelResponseSerializer,
)
from bcss.main.consumers import CircuitServiceConsumer
from common.jsonrpc.jsonrpc_consumer import JSONRPCRequest


@CircuitServiceConsumer.register_method(
    request_serializer_class=CellIdsFromModelRequestSerializer,
    response_serializer_class=CellIdsFromModelResponseSerializer,
)
async def ci_get_cell_ids_from_model(request: JSONRPCRequest):
    gids = None
    return {
        "ids": gids,
    }
