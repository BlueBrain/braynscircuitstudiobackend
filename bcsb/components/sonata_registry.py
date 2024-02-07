from dataclasses import dataclass, field
from struct import Struct

import libsonata
import numpy
from libsonata._libsonata import Report

from bcsb.jsonrpc.exceptions import InternalError
from bcsb.utils.id_generator import IdGenerator

from ..jsonrpc import InvalidParams
from ..service import Component, EndpointRegistry, Result
from ..utils import PathValidator, parse_sonata_config, pick

ReportPopulation = libsonata.SomaReportPopulation | libsonata.ElementReportPopulation


@dataclass
class Nodes:
    population: libsonata.NodePopulation
    selection: libsonata.Selection
    simulation: libsonata.SimulationConfig | None


@dataclass
class NodeReport:
    node_id: int
    info: Report
    population: ReportPopulation


@dataclass
class NodeParams:
    path: str
    population: str
    count: int
    node_sets: list[str] = field(default_factory=list)


@dataclass
class NodeResult:
    id: int
    count: int


@dataclass
class NodeIdParams:
    id: int


@dataclass
class ReportParams:
    nodes_id: int
    name: str


@dataclass
class ReportResult:
    id: int


@dataclass
class ReportIdParams:
    id: int


@dataclass
class FrameParams:
    report_id: int
    frame: int
    min_value: float
    max_value: float


class SonataRegistry(Component):
    def __init__(self, validator: PathValidator) -> None:
        self._validator = validator
        self._node_ids = IdGenerator()
        self._nodes = dict[int, Nodes]()
        self._report_ids = IdGenerator()
        self._node_reports = dict[int, NodeReport]()

    def register(self, endpoints: EndpointRegistry) -> None:
        endpoints.add(
            "sonata-load-nodes",
            self.load_nodes,
            "Register a selection of nodes and return a unique ID to refer it in further requests",
        )
        endpoints.add(
            "sonata-unload-nodes",
            self.unload_nodes,
            "Remove selection of nodes stored with given ID",
        )
        endpoints.add(
            "sonata-get-node-ids",
            self.get_node_ids,
            "Get IDs of nodes registered with given ID as u64 little endian binary",
        )
        endpoints.add(
            "sonata-get-node-positions",
            self.get_node_positions,
            "Get positions of nodes registered with given ID as f32 binary (XYZXYZ...)",
        )
        endpoints.add(
            "sonata-load-node-report",
            self.load_node_report,
            "Load a report for given nodes and returns an ID to read frames from it",
        )
        endpoints.add(
            "sonata-unload-node-report",
            self.unload_node_report,
            "Remove report stored with given ID",
        )
        endpoints.add(
            "sonata-get-report-frame",
            self.get_report_frame,
            "Read simulation values for given eport at given frame",
        )

    async def load_nodes(self, params: NodeParams) -> NodeResult:
        path = self._validator.file(params.path)
        config = parse_sonata_config(path)
        population = config.circuit.node_population(params.population)
        selection = _select_node_sets(population, config.node_sets_path, params.node_sets)
        selection = _filter_selection(selection, params.count)
        nodes_id = self._node_ids.next()
        self._nodes[nodes_id] = Nodes(population, selection, config.simulation)
        return NodeResult(nodes_id, selection.flat_size)

    async def unload_nodes(self, params: NodeIdParams) -> None:
        self._get_nodes(params.id)
        for report_id, report in self._node_reports.items():
            if report.node_id == params.id:
                self._remove_node_report(report_id)
        self._remove_nodes(params.id)

    async def get_node_ids(self, params: NodeIdParams) -> Result[None]:
        nodes = self._get_nodes(params.id)
        ids: numpy.ndarray = nodes.selection.flatten()
        layout = Struct(f"<{len(ids)}Q")
        data = layout.pack(*ids)
        return Result(None, data)

    async def get_node_positions(self, params: NodeIdParams) -> Result[None]:
        nodes = self._get_nodes(params.id)
        population = nodes.population
        selection = nodes.selection
        xs = population.get_attribute("x", selection).astype(numpy.float32)
        ys = population.get_attribute("y", selection).astype(numpy.float32)
        zs = population.get_attribute("z", selection).astype(numpy.float32)
        data = _pack_positions(xs, ys, zs)
        return Result(None, data)

    async def load_node_report(self, params: ReportParams) -> ReportResult:
        nodes = self._get_nodes(params.nodes_id)
        report = _select_report(nodes.simulation, params.name)
        population = _open_node_population_report(report, nodes.population.name)
        report_id = self._report_ids.next()
        self._node_reports[report_id] = NodeReport(params.nodes_id, report, population)
        return ReportResult(report_id)

    async def unload_node_report(self, params: ReportIdParams) -> None:
        self._remove_node_report(params.id)

    async def get_report_frame(self, params: FrameParams) -> Result[None]:
        report = self._get_node_report(params.report_id)
        time = params.frame * report.info.dt
        nodes = self._nodes[report.node_id]
        selection = nodes.selection
        frame = report.population.get(node_ids=selection, tstart=time, tstop=time)
        data = _rescale(frame.data, params.min_value, params.max_value)
        binary = data.tobytes()
        return Result(None, binary)

    def _get_nodes(self, nodes_id: int) -> Nodes:
        nodes = self._nodes.get(nodes_id)
        if nodes is None:
            raise InvalidParams(f"Cannot find node selection registered with ID {nodes_id}")
        return nodes

    def _remove_nodes(self, nodes_id: int) -> None:
        self._get_nodes(nodes_id)
        del self._nodes[nodes_id]
        self._node_ids.recycle(nodes_id)

    def _get_node_report(self, report_id: int) -> NodeReport:
        node_report = self._node_reports.get(report_id)
        if node_report is None:
            raise InvalidParams(f"Cannot find report registered with ID {report_id}")
        return node_report

    def _remove_node_report(self, report_id: int) -> None:
        self._get_node_report(report_id)
        del self._node_reports[report_id]
        self._report_ids.recycle(report_id)


def _select_node_sets(
    population: libsonata.NodePopulation, node_sets_path: str, names: list[str]
) -> libsonata.Selection:
    if not node_sets_path or not names:
        return population.select_all()
    if names and not node_sets_path:
        raise InvalidParams("No node sets in circuit")
    node_sets = libsonata.NodeSets.from_file(node_sets_path)
    _check_invalid_names(names, node_sets.names)
    selection = libsonata.Selection([])
    for name in names:
        selection |= node_sets.materialize(name, population)
    return selection


def _check_invalid_names(names: list[str], ref: set[str]) -> None:
    invalid = set(names) - ref
    if not invalid:
        return
    message = ", ".join(f"'{name}'" for name in invalid)
    raise InvalidParams(f"Invalid node sets: {message}")


def _filter_selection(selection: libsonata.Selection, count: int) -> libsonata.Selection:
    indices = selection.flatten()
    indices = pick(indices, count)
    return libsonata.Selection(indices)


def _pack_positions(xs: numpy.ndarray, ys: numpy.ndarray, zs: numpy.ndarray) -> bytes:
    size = len(xs)
    if len(ys) != size or len(zs) != size:
        raise InternalError("Corrupted file with different node count in x, y or z")
    layout = Struct(f"{3 * size}f")
    positions = (i for position in zip(xs, ys, zs) for i in position)
    return layout.pack(*positions)


def _select_report(simulation: libsonata.SimulationConfig | None, name: str) -> Report:
    if simulation is None:
        raise InvalidParams("Selected nodes have no simulations")
    if name not in simulation.list_report_names:
        raise InvalidParams(f"Invalid report name: '{name}'")
    return simulation.report(name)


def _open_node_population_report(report: Report, population: str) -> ReportPopulation:
    filename = report.file_name
    if report.type == Report.Type.compartment and report.sections == Report.Sections.soma:
        reader = libsonata.SomaReportReader(filename)
        return reader[population]
    reader = libsonata.ElementReportReader(filename)
    return reader[population]


def _rescale(values: numpy.ndarray, min_value: float, max_value: float) -> numpy.ndarray:
    if min_value >= max_value:
        raise InvalidParams(f"Invalid range [{min_value}, {max_value}]")
    clamped = numpy.clip(values, min_value, max_value)
    rescaled = (clamped - min_value) / (max_value - min_value)
    return (255 * rescaled).astype(numpy.uint8)
