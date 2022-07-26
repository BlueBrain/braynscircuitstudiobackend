from bluepy import Circuit

from bcss.circuit_info.serializers.ci_get_efferent_cell_ids import (
    EfferentCellIdsRequestSerializer,
    EfferentCellIdsResponseSerializer,
)
from bcss.main.consumers import CircuitServiceConsumer
from common.jsonrpc.consumer import JSONRPCRequest


@CircuitServiceConsumer.register_method(
    request_serializer_class=EfferentCellIdsRequestSerializer,
    response_serializer_class=EfferentCellIdsResponseSerializer,
)
async def ci_get_efferent_cell_ids(request: JSONRPCRequest):
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
