import os

import libsonata
from marshmallow import Schema, fields

from backend.jsonrpc.actions import Action
from backend.jsonrpc.exceptions import JSONRPCException
from backend.serialization.fields import FilePathField


class UnknownReportType(JSONRPCException):
    pass


class SonataListPopulationsRequestSchema(Schema):
    path = FilePathField


class ReportSchema(Schema):
    # {
    #                     "type": stringify_report_type(report.type),
    #                     "name": report_name,
    #                     "start": report.start_time,
    #                     "end": report.end_time,
    #                     "delta": report.dt,
    #                     "unit": report.unit,
    #                     "cells": report.cells,
    #                 }
    pass  # todo


class PopulationsSchema(Schema):
    pass  # todo


class SonataListPopulationsResponseSchema(Schema):
    # todo
    populations = fields.Nested(PopulationsSchema())
    reports = fields.Nested(ReportSchema())


class SonataListPopulations(Action):
    """Return the list of available populations in a SONATA file."""

    request_schema = SonataListPopulationsRequestSchema
    response_schema = SonataListPopulationsResponseSchema

    async def run(self):
        path = self.request_schema.params["path"]
        path = os.path.abspath(path)
        simulation = None
        circuit_path = path

        try:
            simulation = libsonata.SimulationConfig.from_file(path)
            circuit_path = simulation.network
        except:  # todo narrow down the exception
            # This is not a Simulation.
            print("This circuit has no simulation:", path)
            pass

        circuit = libsonata.CircuitConfig.from_file(circuit_path)  # todo missing arg0 ?
        populations_before_filtering = list(circuit.node_populations)
        populations = []

        for population in populations_before_filtering:
            props = circuit.node_population_properties(population)
            print("Found population", population, "of type", props.type)
            if props.type != "virtual":
                node = circuit.node_population(population)
                print("    Attribute names:", node.attribute_names)
                populations.append(
                    {
                        "name": population,
                        "type": props.type,
                        "size": node.size,
                    }
                )

        reports = []
        report_names = []

        if simulation is not None:
            report_names = simulation.list_report_names

        for report_name in list(report_names):
            report = simulation.report(report_name)
            reports.append(
                {
                    "type": stringify_report_type(report.type),
                    "name": report_name,
                    "start": report.start_time,
                    "end": report.end_time,
                    "delta": report.dt,
                    "unit": report.unit,
                    "cells": report.cells,
                }
            )

        return {
            "populations": populations,
            "reports": reports,
        }


ReportType = libsonata._libsonata.Report.Type

REPORT_TYPE_STR_MAPPING = {
    ReportType.compartment: "compartment",
    ReportType.summation: "simulation",
    ReportType.synapse: "synapse",
}


def stringify_report_type(value) -> str:
    try:
        return REPORT_TYPE_STR_MAPPING[value]
    except KeyError:
        raise UnknownReportType
