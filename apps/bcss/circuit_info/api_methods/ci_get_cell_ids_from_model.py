from bcss.circuit_info.serializers.ci_get_cell_ids_from_model import (
    CellIdsFromModelRequestSerializer,
    CellIdsFromModelResponseSerializer,
)
from common.jsonrpc.jsonrpc_method import JSONRPCMethod


class CIGetCellIdsFromModelMethod(JSONRPCMethod):
    request_serializer_class = CellIdsFromModelRequestSerializer
    response_serializer_class = CellIdsFromModelResponseSerializer

    async def run(self):
        gids = None

        return {
            "gids": gids,
        }
