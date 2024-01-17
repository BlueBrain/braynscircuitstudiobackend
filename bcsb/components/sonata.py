from dataclasses import dataclass
from logging import Logger

import libsonata

from ..jsonrpc import InternalError
from ..path import PathValidator
from ..service import Component, EndpointRegistry

REPORT_TYPES = {
    "compartment": "compartment",
    "summation": "simulation",
    "synapse": "synapse",
}


def get_report_type(name: str) -> str:
    result = REPORT_TYPES.get(name)
    if result is not None:
        return result
    raise InternalError(f"Unknown report type {name}")


@dataclass
class NodeSetParams:
    path: str


@dataclass
class NodeSetResult:
    node_sets: list[str]


@dataclass
class PopulationParams:
    path: str


@dataclass
class EdgePopulation:
    name: str
    size: int
    source: str
    target: str


@dataclass
class Population:
    name: str
    type: str
    size: int


@dataclass
class Report:
    type: str
    name: str
    start: int
    end: int
    delta: int
    unit: str
    cells: str


@dataclass
class PopulationResult:
    populations: list[Population]
    reports: list[Report]
    edges: list[EdgePopulation]


class Sonata(Component):
    def __init__(self, validator: PathValidator, logger: Logger) -> None:
        self._validator = validator
        self._logger = logger

    def register(self, endpoints: EndpointRegistry) -> None:
        endpoints.add(
            "sonata-get-node-sets",
            self.get_node_sets,
            "Retreive node sets from sonata circuit",
        )
        endpoints.add(
            "sonata-list-populations",
            self.get_populations,
            "Retreive populations and reports in sonata circuit",
        )

    async def get_node_sets(self, params: NodeSetParams) -> NodeSetResult:
        circuit, simulation = self._parse(params.path)
        node_sets_path = circuit.node_sets_path if simulation is None else simulation.node_sets_file
        try:
            nodes = libsonata.NodeSets.from_file(node_sets_path)
            names = sorted(nodes.names)
        except Exception as e:
            self._logger.warning("Node sets error (assume empty): %s.", e)
            names = list[str]()
        return NodeSetResult(names)

    async def get_populations(self, params: PopulationParams) -> PopulationResult:
        circuit, simulation = self._parse(params.path)
        return PopulationResult(
            populations=self._get_populations(circuit),
            reports=self._get_reports(simulation) if simulation is not None else [],
            edges=self._get_edges(circuit),
        )

    def _parse(self, filename: str) -> tuple[libsonata.CircuitConfig, libsonata.SimulationConfig | None]:
        path = self._validator.validate_file(filename)
        try:
            simulation = libsonata.SimulationConfig.from_file(path)
            circuit = libsonata.CircuitConfig.from_file(simulation.network)
        except Exception as e:
            self._logger.debug("No simulations found for %s: %s", filename, e)
            simulation = None
            circuit = libsonata.CircuitConfig.from_file(path)
        return circuit, simulation

    def _get_populations(self, circuit: libsonata.CircuitConfig) -> list[Population]:
        populations = list[Population]()
        for name in circuit.node_populations:
            properties = circuit.node_population_properties(name)
            kind = properties.type
            self._logger.debug(f"Found population '{name}' of type '{kind}'")
            if kind == "virtual":
                continue
            node = circuit.node_population(name)
            self._logger.debug(f"Attribute names: {node.attribute_names}")
            population = Population(name, kind, node.size)
            populations.append(population)
        return populations

    def _get_reports(self, simulation: libsonata.SimulationConfig) -> list[Report]:
        reports = list[Report]()
        for name in simulation.list_report_names:
            properties = simulation.report(name)
            report = Report(
                type=get_report_type(properties.type.name),
                name=name,
                start=properties.start_time,
                end=properties.end_time,
                delta=properties.dt,
                unit=properties.unit,
                cells=properties.cells,
            )
            reports.append(report)
        return reports

    def _get_edges(self, circuit: libsonata.CircuitConfig) -> list[EdgePopulation]:
        edges = list[EdgePopulation]()
        for name in circuit.edge_populations:
            population = circuit.edge_population(name)
            edge = EdgePopulation(name, population.size, population.source, population.target)
            edges.append(edge)
        return edges
