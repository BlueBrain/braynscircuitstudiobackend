from bluepy import Circuit

from bcss.circuit_info.serializers.ci_get_projections import (
    ProjectionsRequestSerializer,
    ProjectionsResponseSerializer,
)
from bcss.main.consumers import CircuitServiceConsumer
from common.jsonrpc.consumer import JSONRPCRequest


@CircuitServiceConsumer.register_method(
    request_serializer_class=ProjectionsRequestSerializer,
    response_serializer_class=ProjectionsResponseSerializer,
)
async def ci_get_projections(request: JSONRPCRequest):
    path = request.params["path"]
    circuit = Circuit(path)
    projections = circuit.config.get("projections")

    return {
        "projections": projections,
    }
