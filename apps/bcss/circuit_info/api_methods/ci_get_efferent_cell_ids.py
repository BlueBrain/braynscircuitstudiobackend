from bluepy import Circuit

from bcss.circuit_info.serializers.ci_get_efferent_cell_ids import (
    EfferentCellIdsRequestSerializer,
    EfferentCellIdsResponseSerializer,
)
from common.jsonrpc.jsonrpc_method import JSONRPCMethod


class CIGetEfferentCellIdsMethod(JSONRPCMethod):
    request_serializer_class = EfferentCellIdsRequestSerializer
    response_serializer_class = EfferentCellIdsResponseSerializer

    async def run(self):
        path = self.request.params["path"]
        sources = self.request.params["sources"]
        circuit = Circuit(path)

        ids = (
            value
            for source_gid in sources
            for value in circuit.connectome.efferent_gids(source_gid).tolist()
        )

        # Remove any duplicates
        ids = sorted(set(ids))

        return {
            "ids": ids,
        }
