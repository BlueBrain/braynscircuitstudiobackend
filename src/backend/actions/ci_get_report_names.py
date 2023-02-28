import logging

from bluepy import Simulation, Circuit
from bluepy_configfile import BlueConfigError
from marshmallow import Schema, fields

from backend.jsonrpc.actions import Action
from backend.serialization.fields import FilePathField

logger = logging.getLogger(__name__)


class CIGetReportNamesRequestSchema(Schema):
    path = FilePathField(
        required=True,
    )


class CIGetReportNamesResponseSchema(Schema):
    report_names = fields.List(
        cls_or_instance=fields.String(),
        default=list,
    )


class CIGetReportNames(Action):
    request_schema = CIGetReportNamesRequestSchema
    response_schema = CIGetReportNamesResponseSchema

    async def run(self):
        path = self.request.params["path"]
        logger.debug(f"Loaded circuit from {path}")

        report_names = None

        try:
            simulation = Simulation(path)
            report_names = sorted(simulation.report_names)
        except (BlueConfigError, KeyError):
            pass

        return {
            "report_names": report_names,
        }
