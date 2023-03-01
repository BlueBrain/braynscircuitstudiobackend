from bluepy import Circuit
from marshmallow import Schema, fields

from backend.jsonrpc.actions import Action
from backend.serialization.fields import FilePathField


class ProjectionsRequestSchema(Schema):
    path = FilePathField(
        required=True,
    )


class ProjectionsResponseSchema(Schema):
    projections = fields.List(
        cls_or_instance=fields.String(),
        default=list,
    )


class CIGetProjections(Action):
    request_schema = ProjectionsRequestSchema
    response_schema = ProjectionsResponseSchema

    async def run(self):
        path = self.request.params["path"]
        circuit = Circuit(path)
        projections = list(circuit.config.get("projections"))

        return {
            "projections": projections,
        }
