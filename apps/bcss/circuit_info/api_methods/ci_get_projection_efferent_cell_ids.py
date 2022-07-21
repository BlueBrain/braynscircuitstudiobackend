from bluepy import Circuit

from bcss.circuit_info.serializers.ci_get_projection_efferent_cell_ids import (
    ProjectionEfferentCellIdsRequestSerializer,
    ProjectionEfferentCellIdsResponseSerializer,
)
from bcss.main.consumers import CircuitServiceConsumer
from common.jsonrpc.consumer import JSONRPCRequest


@CircuitServiceConsumer.register_method(
    request_serializer=ProjectionEfferentCellIdsRequestSerializer,
    response_serializer=ProjectionEfferentCellIdsResponseSerializer,
)
async def ci_get_projection_efferent_cell_ids(request: JSONRPCRequest):
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
