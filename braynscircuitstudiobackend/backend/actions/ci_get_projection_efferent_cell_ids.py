from bluepy import Circuit
from marshmallow import Schema, fields

from braynscircuitstudiobackend.backend.jsonrpc.actions import Action
from braynscircuitstudiobackend.backend.serialization.fields import FilePathField


class ProjectionEfferentCellIdsRequestSchema(Schema):
    path = FilePathField(
        required=True,
    )
    sources = fields.List(
        cls_or_instance=fields.Integer(),
        default=list,
        required=True,
    )
    projection = fields.String(
        required=True,
    )


class ProjectionEfferentCellIdsResponseSchema(Schema):
    ids = fields.List(
        cls_or_instance=fields.Integer(),
        default=list,
    )


class CIGetProjectionEfferentCellIds(Action):
    request_schema = ProjectionEfferentCellIdsRequestSchema
    response_schema = ProjectionEfferentCellIdsResponseSchema

    async def run(self):
        path = self.request.params["path"]
        projection_name = self.request.params["projection"]
        sources = self.request.params["sources"]
        circuit = Circuit(path)
        projections = (
            value
            for source_gid in sources
            for value in circuit.projection(projection_name).efferent_gids(source_gid).tolist()
        )

        # Remove any duplicates
        projections = sorted(set(projections))

        return {
            "projections": projections,
        }
