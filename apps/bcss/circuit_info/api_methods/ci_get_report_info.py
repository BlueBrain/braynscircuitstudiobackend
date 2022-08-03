from bluepy import Simulation

from bcss.circuit_info.serializers.ci_get_report_info import (
    ReportInfoRequestSerializer,
    ReportInfoResponseSerializer,
)
from common.jsonrpc.jsonrpc_consumer import JSONRPCRequest
from common.jsonrpc.jsonrpc_method import JSONRPCMethod


class CIGetReportInfoMethod(JSONRPCMethod):
    request_serializer_class = ReportInfoRequestSerializer
    response_serializer_class = ReportInfoResponseSerializer

    async def run(self, request: JSONRPCRequest):
        path = request.params["path"]
        report_name = request.params["report"]

        simulation = Simulation(path)
        report = simulation.report(report_name)

        return {
            "start_time": report.t_start,
            "end_time": report.t_end,
            "time_step": report.t_step,
            "data_unit": "",
            "time_unit": "",
            "frame_size": -1,
            "frame_count": -1,
        }
