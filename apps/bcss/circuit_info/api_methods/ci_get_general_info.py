from bluepy import Circuit, Simulation

from bcss.circuit_info.schemas.ci_info import (
    CircuitInfoGeneralInfoRequestSchema,
    CircuitInfoGeneralInfoResponseSchema,
)
from bcss.main.consumers import CircuitServiceConsumer
from common.jsonrpc.consumer import JSONRPCRequest, JSONRPCConsumer


@CircuitServiceConsumer.register_method(
    request_schema=CircuitInfoGeneralInfoRequestSchema,
    response_schema=CircuitInfoGeneralInfoResponseSchema,
)
async def ci_get_general_info(request: JSONRPCRequest, consumer: JSONRPCConsumer):
    circuit = Circuit(request.params["path"])
    simulation = Simulation(request.params["path"])

    return {
        "cell_count": circuit.cells.count(),
        "cell_properties": [value for value in circuit.cells.available_properties],
        "m_types": [*circuit.cells.mtypes],
        "e_types": [*circuit.cells.etypes],
        "targets": [*circuit.cells.targets],
        "reports": [*simulation.report_names],
        "spike_report": "",  # todo where to find the path
    }
