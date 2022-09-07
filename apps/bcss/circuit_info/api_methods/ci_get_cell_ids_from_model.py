from bluepy import Circuit

from bcss.circuit_info.serializers.ci_get_cell_ids_from_model import (
    CellIdsFromModelRequestSerializer,
    CellIdsFromModelResponseSerializer,
)
from common.jsonrpc.jsonrpc_method import JSONRPCMethod


class CIGetCellIdsFromModelMethod(JSONRPCMethod):
    request_serializer_class = CellIdsFromModelRequestSerializer
    response_serializer_class = CellIdsFromModelResponseSerializer

    async def run(self):
        circuit = Circuit(self.request.params["path"])
        targets = self.request.params["targets"]
        model_id = self.request.params["model_id"]

        if targets:
            gids = [
                gid
                for target in targets
                for gid in set(circuit.cells.get(group=model_id).ids(target).tolist())
            ]
        else:
            gids = circuit.cells.ids().tolist()

        return {
            "gids": gids,
        }
