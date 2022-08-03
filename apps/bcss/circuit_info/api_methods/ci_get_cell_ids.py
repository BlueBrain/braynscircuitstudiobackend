from bluepy import Circuit

from bcss.circuit_info.serializers.ci_get_cell_ids import (
    CellIdsRequestSerializer,
    CellIdsResponseSerializer,
)
from common.jsonrpc.jsonrpc_consumer import JSONRPCRequest
from common.jsonrpc.jsonrpc_method import JSONRPCMethod


class CIGetCellIdsMethod(JSONRPCMethod):
    request_serializer_class = CellIdsRequestSerializer
    response_serializer_class = CellIdsResponseSerializer

    async def run(self, request: JSONRPCRequest):
        circuit = Circuit(request.params["path"])
        targets = request.params["targets"]

        if targets:
            gids = [gid for target in targets for gid in circuit.cells.ids(target).tolist()]
        else:
            gids = circuit.cells.ids().tolist()

        return {
            "ids": gids,
        }
