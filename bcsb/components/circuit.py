from dataclasses import dataclass
from logging import Logger
from typing import Any, cast

import bluepy

from ..path import PathValidator
from ..service import Component, EndpointRegistry


@dataclass
class CellIdParams:
    path: str
    targets: list[str]


@dataclass
class CellIdResult:
    gids: list[int]


@dataclass
class ReportInfoParams:
    path: str
    report: str


@dataclass
class ReportInfoResult:
    name: str
    start_time: float
    end_time: float
    time_step: float
    data_unit: str
    time_unit: str
    frame_size: int
    frame_count: int


@dataclass
class ReportNameParams:
    path: str


@dataclass
class ReportNameResult:
    report_names: list[str] | None = None


@dataclass
class TargetParams:
    path: str


@dataclass
class TargetResult:
    targets: list[str]


class Circuit(Component):
    def __init__(self, validator: PathValidator, logger: Logger) -> None:
        self._validator = validator
        self._logger = logger

    def register(self, endpoints: EndpointRegistry) -> None:
        endpoints.add(
            "ci-get-cell-ids",
            self.get_cell_ids,
            "Retreive GIDs of cells in given targets",
        )
        endpoints.add(
            "ci-get-report-info",
            self.get_report_info,
            "Retreive information about a given circuit report",
        )
        endpoints.add(
            "ci-get-report-names",
            self.get_report_names,
            "Retreive available reports for a circuit",
        )
        endpoints.add(
            "ci-get-targets",
            self.get_targets,
            "Retreive available targets for a circuit",
        )

    async def get_cell_ids(self, params: CellIdParams) -> CellIdResult:
        path = self._validator.validate_file(params.path)
        circuit = bluepy.Circuit(path)
        if not params.targets:
            return CellIdResult(sorted(int(value) for value in circuit.cells.ids()))  # type: ignore
        return CellIdResult(
            sorted(set(int(value) for target in params.targets for value in circuit.cells.ids(target)))  # type: ignore
        )

    async def get_report_info(self, params: ReportInfoParams) -> ReportInfoResult:
        path = self._validator.validate_file(params.path)
        simulation = bluepy.Simulation(path)
        report = simulation.report(params.report)
        meta = cast(dict[str, Any], report.meta)
        return ReportInfoResult(
            name=params.report,
            start_time=report.t_start,
            end_time=report.t_end,
            time_step=report.t_step,
            data_unit=meta["data_unit"],
            time_unit=meta["time_unit"],
            frame_size=meta.get("frame_size", 0),
            frame_count=meta.get("frame_count", 0),
        )

    async def get_report_names(self, params: ReportNameParams) -> ReportNameResult:
        path = self._validator.validate_file(params.path)
        names: list[str] | None = None
        try:
            simulation = bluepy.Simulation(path)
            names = sorted(simulation.report_names)
        except Exception as e:
            self._logger.debug("Invalid simulation, assume no reports %s", e)
        return ReportNameResult(names)

    async def get_targets(self, params: TargetParams) -> TargetResult:
        path = self._validator.validate_file(params.path)
        circuit = bluepy.Circuit(path)
        return TargetResult(circuit.cells.targets)  # type: ignore
