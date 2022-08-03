from bluepy import Circuit

from bcss.circuit_info.serializers.ci_get_efferent_cell_ids import (
    EfferentCellIdsRequestSerializer,
    EfferentCellIdsResponseSerializer,
)
from common.jsonrpc.jsonrpc_consumer import JSONRPCRequest
from common.jsonrpc.jsonrpc_method import JSONRPCMethod


class CIGetEfferentCellIdsMethod(JSONRPCMethod):
    request_serializer_class = EfferentCellIdsRequestSerializer
    response_serializer_class = EfferentCellIdsResponseSerializer

    async def run(self, request: JSONRPCRequest):
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
