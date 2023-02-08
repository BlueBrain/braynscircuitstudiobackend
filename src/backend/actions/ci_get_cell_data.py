import logging

from bluepy import Circuit, Cell
from marshmallow import Schema, fields
from scipy.spatial.transform import Rotation

from backend.jsonrpc.actions import Action
from backend.serialization.fields import FilePathField

logger = logging.getLogger(__name__)


class CellDataRequestSchema(Schema):
    path = FilePathField(
        required=True,
    )
    ids = fields.List(
        required=True,
        cls_or_instance=fields.Integer(),
        default=list,
    )
    properties = fields.List(
        required=True,
        cls_or_instance=fields.String(),
        default=list,
    )


class CellDataResponseSchema(Schema):
    mtypes = fields.List(cls_or_instance=fields.String())
    etypes = fields.List(cls_or_instance=fields.String())
    morphology_classes = fields.List(cls_or_instance=fields.String())
    layers = fields.List(cls_or_instance=fields.String())
    positions = fields.List(cls_or_instance=fields.Decimal())
    orientations = fields.List(cls_or_instance=fields.Decimal())


class CIGetCellData(Action):
    request_schema = CellDataRequestSchema
    response_schema = CellDataResponseSchema

    async def run(self):
        circuit = Circuit(self.request.params["path"])
        cell_ids = self.request.params["ids"]
        requested_properties = set(self.request.params["properties"])

        request_positions = (
            Cell.X in requested_properties
            and Cell.Y in requested_properties
            and Cell.Z in requested_properties
        ) or "position" in requested_properties

        if "position" in requested_properties:
            requested_properties.remove("position")
            requested_properties.add(Cell.X)
            requested_properties.add(Cell.Y)
            requested_properties.add(Cell.Z)

        morphology_classes = []
        mtypes = []
        etypes = []
        layers = []
        positions = []
        orientations = []

        for cell_id in cell_ids:
            cell = circuit.cells.get(cell_id, properties=requested_properties)
            orientation = cell.get(Cell.ORIENTATION).tolist()
            rotation = Rotation.from_matrix(orientation)
            x, y, z, w = rotation.as_quat().tolist()
            logger.debug(f"Cell loaded {cell}")

            if Cell.MORPH_CLASS in requested_properties:
                # todo this needs checking because the result differs from what Brayns returns
                morphology_classes.append(cell.get(Cell.MORPH_CLASS))
            if Cell.MTYPE in requested_properties:
                mtypes.append(cell.get(Cell.MTYPE))
            if Cell.ETYPE in requested_properties:
                etypes.append(cell.get(Cell.ETYPE))
            if Cell.LAYER in requested_properties:
                layers.append(cell.get(Cell.LAYER))
            if Cell.ORIENTATION in requested_properties:
                orientations.append([w, x, y, z])
            if request_positions:
                positions.append(cell.get(Cell.X))
                positions.append(cell.get(Cell.Y))
                positions.append(cell.get(Cell.Z))

        return {
            **({"mtypes": mtypes} if mtypes else {}),
            **({"etypes": etypes} if etypes else {}),
            **({"morphology_classes": morphology_classes} if morphology_classes else {}),
            **({"layers": layers} if layers else {}),
            **({"positions": positions} if positions else {}),
            **({"orientations": orientations} if orientations else {}),
        }
