from bluepy import Circuit

from bcss.circuit_info.serializers.ci_get_projection_efferent_cell_ids import (
    ProjectionEfferentCellIdsRequestSerializer,
    ProjectionEfferentCellIdsResponseSerializer,
)
from common.jsonrpc.jsonrpc_consumer import JSONRPCRequest
from common.jsonrpc.jsonrpc_method import JSONRPCMethod


class CIGetProjectionEfferentCellIdsMethod(JSONRPCMethod):
    request_serializer_class = ProjectionEfferentCellIdsRequestSerializer
    response_serializer_class = ProjectionEfferentCellIdsResponseSerializer

    async def run(self, request: JSONRPCRequest):
        path = request.params["path"]
        projection_name = request.params["projection"]
        sources = request.params["sources"]
        circuit = Circuit(path)
        projections = sorted(
            value
            for source_gid in sources
            for value in circuit.projection(projection_name).efferent_gids(source_gid).tolist()
        )

        return {
            "projections": projections,
        }
