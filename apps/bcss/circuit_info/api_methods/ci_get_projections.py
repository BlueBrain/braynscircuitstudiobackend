from bluepy import Circuit

from bcss.circuit_info.schemas.ci_get_projections import (
    ProjectionsRequestSchema,
    ProjectionsResponseSchema,
)
from bcss.main.consumers import CircuitServiceConsumer
from common.jsonrpc.consumer import JSONRPCRequest, JSONRPCConsumer


@CircuitServiceConsumer.register_method(
    request_schema=ProjectionsRequestSchema,
    response_schema=ProjectionsResponseSchema,
)
async def ci_get_projections(request: JSONRPCRequest, consumer: JSONRPCConsumer):
    path = request.params["path"]
    circuit = Circuit(path)
    projections = circuit.config.get("projections")

    return {
        "projections": projections,
    }
