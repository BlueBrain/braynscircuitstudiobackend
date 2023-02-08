from bluepy import Circuit
from marshmallow import Schema, fields

from backend.jsonrpc.actions import Action
from backend.serialization.fields import FilePathField


class CellIdsFromModelRequestSchema(Schema):
    path = FilePathField(
        required=True,
    )
    targets = fields.List(
        required=True,
        cls_or_instance=fields.String(),
        default=list,
    )
    model_id = fields.Integer(
        required=True,
    )


class CellIdsFromModelResponseSchema(Schema):
    gids = fields.List(
        cls_or_instance=fields.Integer(),
        default=list,
    )


class CIGetCellIdsFromModel(Action):
    request_schema = CellIdsFromModelRequestSchema
    response_schema = CellIdsFromModelResponseSchema

    async def run(self):
        circuit = Circuit(self.request.params["path"])
        targets = self.request.params["targets"]
        model_id = self.request.params["model_id"]

        if targets:
            gids = [
                gid
                for target in targets
                for gid in set(circuit.cells.get(group=model_id).ids(target).tolist())
            ]
        else:
            gids = circuit.cells.ids().tolist()

        return {
            "gids": gids,
        }
