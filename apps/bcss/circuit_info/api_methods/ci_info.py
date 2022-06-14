from bluepy import Circuit, Simulation

from bcsb.consumers import CircuitStudioConsumer
from bcss.circuit_info.schemas.ci_info import (
    CircuitInfoGeneralInfoRequestSchema,
    CircuitInfoGeneralInfoResponseSchema,
)
from bcss.main.consumers import CircuitServiceConsumer
from common.jsonrpc.consumer import JSONRPCRequest
from common.utils.schemas import load_schema


@CircuitServiceConsumer.register_method(
    request_schema=CircuitInfoGeneralInfoRequestSchema,
    response_schema=CircuitInfoGeneralInfoResponseSchema,
)
async def ci_get_general_info(request: JSONRPCRequest, consumer: CircuitStudioConsumer):
    params = load_schema(CircuitInfoGeneralInfoRequestSchema, request.params)
    circuit = Circuit(params["path"])
    simulation = Simulation(params["path"])

    return {
        "cell_count": circuit.cells.count(),
        "cell_properties": [value for value in circuit.cells.available_properties],
        "m_types": [value for value in circuit.cells.mtypes],
        "e_types": [value for value in circuit.cells.etypes],
        "targets": [value for value in circuit.cells.targets],
        "reports": [value for value in simulation.report_names],
        "spike_report": "",  # todo where to find the path
    }
