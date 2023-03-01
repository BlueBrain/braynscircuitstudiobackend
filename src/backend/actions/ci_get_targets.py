import logging

from bluepy import Circuit, Simulation
from bluepy.simulation import PathHelpers
from bluepy_configfile import BlueConfigError
from marshmallow import Schema, fields

from backend.jsonrpc.actions import Action
from backend.serialization.fields import FilePathField

logger = logging.getLogger(__name__)


class CIGetTargetsRequestSchema(Schema):
    path = FilePathField(
        required=True,
    )


class CIGetTargetsResponseSchema(Schema):
    targets = fields.List(
        cls_or_instance=fields.String(),
        default=list,
    )


class CIGetTargets(Action):
    request_schema = CIGetTargetsRequestSchema
    response_schema = CIGetTargetsResponseSchema

    async def run(self):
        path = self.request.params["path"]
        circuit = Circuit(path)

        return {
            "targets": sorted(circuit.cells.targets),
        }
