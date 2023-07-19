import logging

from bluepy import Simulation
from marshmallow import Schema, fields
from pydash import get

from braynscircuitstudiobackend.backend.jsonrpc.actions import Action
from braynscircuitstudiobackend.backend.serialization.fields import FilePathField

logger = logging.getLogger(__name__)


class CIGetReportInfoRequestSchema(Schema):
    path = FilePathField(
        required=True,
    )
    report = fields.String(
        required=True,
    )


class CIGetReportInfoResponseSchema(Schema):
    name: fields.String()
    data_unit = fields.String()
    start_time = fields.Float()
    end_time = fields.Float()
    frame_size = fields.Integer()
    frame_count = fields.Integer()
    time_step = fields.Float()
    time_unit = fields.String()


class CIGetReportInfo(Action):
    request_schema = CIGetReportInfoRequestSchema
    response_schema = CIGetReportInfoResponseSchema

    async def run(self):
        path = self.request.params["path"]
        report_name = self.request.params["report"]

        simulation = Simulation(path)
        report = simulation.report(report_name)

        result = {
            "name": report_name,
            "start_time": report.t_start,
            "end_time": report.t_end,
            "time_step": report.t_step,
            "data_unit": report.meta["data_unit"],
            "time_unit": report.meta["time_unit"],
            "frame_size": get(report, "meta.frame_size", 0),
            "frame_count": get(report, "meta.frame_count"),
        }
        logger.debug(f"{result=}")
        return result
