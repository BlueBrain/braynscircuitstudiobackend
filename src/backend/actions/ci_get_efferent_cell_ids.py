from bluepy import Circuit
from marshmallow import Schema, fields

from backend.jsonrpc.actions import Action
from backend.serialization.fields import FilePathField


class EfferentCellIdsRequestSchema(Schema):
    path = FilePathField(
        required=True,
    )
    sources = fields.List(
        cls_or_instance=fields.Integer(),
        default=list,
    )


class EfferentCellIdsResponseSchema(Schema):
    ids = fields.List(
        cls_or_instance=fields.Integer(),
        default=list,
        required=True,
    )


class CIGetEfferentCellIds(Action):
    request_schema = EfferentCellIdsRequestSchema
    response_schema = EfferentCellIdsResponseSchema

    async def run(self):
        path = self.request.params["path"]
        sources = self.request.params["sources"]
        circuit = Circuit(path)

        ids = (
            value
            for source_gid in sources
            for value in circuit.connectome.efferent_gids(source_gid).tolist()
        )

        # Remove any duplicates
        ids = sorted(set(ids))

        return {
            "ids": ids,
        }
