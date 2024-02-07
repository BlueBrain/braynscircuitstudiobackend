from dataclasses import dataclass
from pathlib import Path

import libsonata


@dataclass
class SonataConfig:
    circuit: libsonata.CircuitConfig
    simulation: libsonata.SimulationConfig | None = None

    @property
    def node_sets_path(self) -> str:
        return self.circuit.node_sets_path if self.simulation is None else self.simulation.node_sets_file


def parse_sonata_config(path: Path) -> SonataConfig:
    try:
        return _parse_simulation_config(path)
    except Exception:
        circuit = libsonata.CircuitConfig.from_file(path)
        return SonataConfig(circuit)


def _parse_simulation_config(path: Path) -> SonataConfig:
    simulation = libsonata.SimulationConfig.from_file(path)
    circuit = libsonata.CircuitConfig.from_file(simulation.network)
    return SonataConfig(circuit, simulation)
