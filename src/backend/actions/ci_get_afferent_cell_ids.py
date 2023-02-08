import logging

from bluepy import Circuit
from marshmallow import Schema, fields

from backend.jsonrpc.actions import Action
from backend.serialization.fields import FilePathField

logger = logging.getLogger(__name__)


class AfferentCellIdsRequestSchema(Schema):
    path = FilePathField(
        required=True,
    )
    sources = fields.List(
        required=True,
        cls_or_instance=fields.Integer(),
        default=list,
    )


class AfferentCellIdsResponseSchema(Schema):
    ids = fields.List(
        cls_or_instance=fields.Integer(),
    )


class CIGetAfferentCellIds(Action):
    request_schema = AfferentCellIdsRequestSchema
    response_schema = AfferentCellIdsResponseSchema

    async def run(self):
        path = self.request.params["path"]
        sources = self.request.params["sources"]
        circuit = Circuit(path)

        ids = sorted(
            value
            for source_gid in sources
            for value in circuit.connectome.afferent_gids(source_gid).tolist()
        )

        return {
            "ids": ids,
        }
