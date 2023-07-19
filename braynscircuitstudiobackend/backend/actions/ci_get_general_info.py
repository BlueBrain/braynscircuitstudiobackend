import logging

from bluepy import Circuit, Simulation
from bluepy.simulation import PathHelpers
from bluepy_configfile import BlueConfigError
from marshmallow import Schema, fields

from braynscircuitstudiobackend.backend.jsonrpc.actions import Action
from braynscircuitstudiobackend.backend.serialization.fields import FilePathField

logger = logging.getLogger(__name__)


class CircuitGeneralInfoRequestSchema(Schema):
    path = FilePathField(
        required=True,
    )


class CircuitGeneralInfoResponseSchema(Schema):
    cell_count = fields.Integer()
    cell_properties = fields.List(
        cls_or_instance=fields.String(),
        default=list,
    )
    mtypes = fields.List(
        cls_or_instance=fields.String(),
        default=list,
    )
    etypes = fields.List(
        cls_or_instance=fields.String(),
        default=list,
    )
    targets = fields.List(
        cls_or_instance=fields.String(),
        default=list,
    )
    reports = fields.List(
        cls_or_instance=fields.String(),
        default=list,
    )
    spike_report = fields.String()


class CIGetGeneralInfo(Action):
    request_schema = CircuitGeneralInfoRequestSchema
    response_schema = CircuitGeneralInfoResponseSchema

    async def run(self):
        path = self.request.params["path"]
        circuit = Circuit(path)
        logger.debug(f"Loaded circuit from {path}")

        try:
            simulation = Simulation(path)
            report_names = sorted(simulation.report_names)
        except (BlueConfigError, KeyError):
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
