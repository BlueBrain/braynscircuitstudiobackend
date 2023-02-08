from bluepy import Simulation
from marshmallow import Schema, fields

from backend.jsonrpc.actions import Action
from backend.serialization.fields import FilePathField


class ReportInfoRequestSchema(Schema):
    path = FilePathField(
        required=True,
    )
    report = fields.String(
        required=True,
    )


class ReportInfoResponseSchema(Schema):
    start_time = fields.Decimal()
    end_time = fields.Decimal()
    time_step = fields.Decimal()
    data_unit = fields.String()
    time_unit = fields.String()
    frame_count = fields.Integer()
    frame_size = fields.Integer()


class CIGetReportInfo(Action):
    request_schema = ReportInfoRequestSchema
    response_schema = ReportInfoResponseSchema

    async def run(self):
        path = self.request.params["path"]
        report_name = self.request.params["report"]

        simulation = Simulation(path)
        report = simulation.report(report_name)

        return {
            "start_time": report.t_start,
            "end_time": report.t_end,
            "time_step": report.t_step,
            "data_unit": report.meta["data_unit"],
            "time_unit": report.meta["time_unit"],
            "frame_size": report.meta.get("frame_size"),
            "frame_count": report.meta["frame_count"],
        }
