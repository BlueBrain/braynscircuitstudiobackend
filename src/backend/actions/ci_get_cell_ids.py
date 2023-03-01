from bluepy import Circuit
from marshmallow import Schema, fields

from backend.jsonrpc.actions import Action
from backend.serialization.fields import FilePathField


class CellIdsRequestSchema(Schema):
    path = FilePathField(
        required=True,
    )
    targets = fields.List(
        required=True,
        cls_or_instance=fields.String(),
        default=list,
    )


class CellIdsResponseSchema(Schema):
    gids = fields.List(
        cls_or_instance=fields.Integer(),
        default=list,
    )


class CIGetCellIds(Action):
    request_schema = CellIdsRequestSchema
    response_schema = CellIdsResponseSchema

    async def run(self):
        circuit = Circuit(self.request.params["path"])
        targets = self.request.params["targets"]

        if targets:
            gids = [gid for target in targets for gid in circuit.cells.ids(target).tolist()]
        else:
            gids = circuit.cells.ids().tolist()

        # Remove any duplicates
        gids = sorted(set(gids))

        return {
            "gids": gids,
        }
