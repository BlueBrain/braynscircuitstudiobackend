from bluepy import Circuit

from bcss.circuit_info.serializers.ci_get_projections import (
    ProjectionsRequestSerializer,
    ProjectionsResponseSerializer,
)
from common.jsonrpc.jsonrpc_method import JSONRPCMethod


class CIGetProjectionsMethod(JSONRPCMethod):
    request_serializer_class = ProjectionsRequestSerializer
    response_serializer_class = ProjectionsResponseSerializer

    async def run(self):
        path = self.request.params["path"]
        circuit = Circuit(path)
        projections = circuit.config.get("projections")

        return {
            "projections": projections,
        }
