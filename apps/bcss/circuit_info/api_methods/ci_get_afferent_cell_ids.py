import logging

from bluepy import Circuit

from bcss.circuit_info.serializers.ci_get_afferent_cell_ids import (
    AfferentCellIdsRequestSerializer,
    AfferentCellIdsResponseSerializer,
)
from common.jsonrpc.jsonrpc_method import JSONRPCMethod

logger = logging.getLogger(__name__)


class CIGetAfferentCellIdsMethod(JSONRPCMethod):
    request_serializer_class = AfferentCellIdsRequestSerializer
    response_serializer_class = AfferentCellIdsResponseSerializer

    async def run(self):
        path = self.request.params["path"]
        sources = self.request.params["sources"]
        circuit = Circuit(path)

        ids = sorted(
            value
            for source_gid in sources
            for value in circuit.connectome.afferent_gids(source_gid).tolist()
        )

        return {
            "ids": ids,
        }
