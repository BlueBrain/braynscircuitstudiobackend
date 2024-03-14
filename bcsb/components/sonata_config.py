from dataclasses import dataclass
from logging import Logger

import libsonata

from ..service import Component, EndpointRegistry
from ..utils import PathValidator, parse_sonata_config


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


class SonataConfig(Component):
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
        path = self._validator.file(params.path)
        config = parse_sonata_config(path)
        try:
            nodes = libsonata.NodeSets.from_file(config.node_sets_path)
            names = sorted(nodes.names)
        except Exception as e:
            self._logger.warning("Node sets error (assume empty): %s.", e)
            names = list[str]()
        return NodeSetResult(names)

    async def get_populations(self, params: PopulationParams) -> PopulationResult:
        path = self._validator.file(params.path)
        config = parse_sonata_config(path)
        return PopulationResult(
            populations=self._get_populations(config.circuit),
            reports=self._get_reports(config.simulation) if config.simulation is not None else [],
            edges=self._get_edges(config.circuit),
        )

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
                type=properties.type.name,
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
