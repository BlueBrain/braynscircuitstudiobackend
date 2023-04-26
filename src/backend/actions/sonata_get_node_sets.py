import os
from pathlib import Path

import libsonata
from marshmallow import Schema, fields

from backend.jsonrpc.actions import Action
from backend.serialization.fields import FilePathField

import logging

logger = logging.getLogger(__name__)


class SonataGetNodeSetsRequestSchema(Schema):
    path = FilePathField()


class SonataGetNodeSetsResponseSchema(Schema):
    node_sets = fields.List(cls_or_instance=fields.String())


class SonataGetNodeSets(Action):
    """Return the names of the available node_sets."""

    request_schema = SonataGetNodeSetsRequestSchema
    response_schema = SonataGetNodeSetsResponseSchema

    async def run(self):
        path = self.request.params["path"]
        path = os.path.abspath(path)
        node_sets = self.get_node_sets(path)

        return {
            "node_sets": node_sets,
        }

    @staticmethod
    def get_node_sets(circuit_path: Path) -> list[str]:
        circuit_config = libsonata.CircuitConfig.from_file(circuit_path)

        try:
            node_sets = libsonata.NodeSets.from_file(circuit_config.node_sets_path)
            node_sets_names = sorted(node_sets.names)
        except (libsonata.SonataError, RuntimeError) as exception:
            # Possible errors:
            # - RuntimeError: Path `` is not a file (if the key "node_sets_file" is missing)
            # - RuntimeError: Path `/path/to/node_sets.json` is not a file (if the file doesn't exist)
            # - RuntimeError: [json.exception.parse_error.101] parse error... (if the file is invalid)
            logger.warning(
                "Error with node_sets for circuit %r: %r, fallback to empty list",
                circuit_path,
                exception,
            )
            node_sets_names = []

        return node_sets_names
