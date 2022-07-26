import logging

from bluepy import Circuit, Simulation
from bluepy.simulation import PathHelpers
from bluepy_configfile import BlueConfigError

from bcss.circuit_info.serializers.ci_get_general_info import (
    CircuitGeneralInfoRequestSerializer,
    CircuitGeneralInfoResponseSerializer,
)
from bcss.main.consumers import CircuitServiceConsumer
from common.jsonrpc.consumer import JSONRPCRequest

logger = logging.getLogger(__name__)


@CircuitServiceConsumer.register_method(
    request_serializer_class=CircuitGeneralInfoRequestSerializer,
    response_serializer_class=CircuitGeneralInfoResponseSerializer,
)
async def ci_get_general_info(request: JSONRPCRequest):
    path = request.params["path"]
    circuit = Circuit(path)
    logger.debug(f"Loaded circuit from {path}")

    try:
        simulation = Simulation(path)
        report_names = sorted(simulation.report_names)
    except BlueConfigError:
        simulation = None
        report_names = None

    logger.debug(f"Loaded simulation from {path}")

    cell_count = circuit.cells.count()
    logger.debug(f"Cell count = {cell_count}")

    cell_properties = sorted([value for value in circuit.cells.available_properties])

    spike_report_path = None

    try:
        if simulation:
            spike_report_path = PathHelpers.spike_report_path(simulation.config)
    except AttributeError:
        pass

    logger.debug(f"Spike report path = {spike_report_path}")

    return {
        "cell_count": cell_count,
        "cell_properties": cell_properties,
        "mtypes": sorted(circuit.cells.mtypes),
        "etypes": sorted(circuit.cells.etypes),
        "targets": sorted(circuit.cells.targets),
        "reports": report_names,
        "spike_report": spike_report_path,
    }
