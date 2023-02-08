import re

from bluepy import Cell
from marshmallow import Schema, fields

from backend.jsonrpc.actions import Action


class CellPropertyNamesRequestSchema(Schema):
    pass


class CellPropertyNamesResponseSchema(Schema):
    property_names = fields.List(cls_or_instance=fields.String())


class CIGetCellPropertyNames(Action):
    request_schema = CellPropertyNamesRequestSchema
    response_schema = CellPropertyNamesResponseSchema

    async def run(self):
        attribute_names = [value for value in dir(Cell) if re.match(r"^(?!_)[A-Z_]+", value)]
        attribute_values = [getattr(Cell, value) for value in attribute_names]
        return {
            "property_names": attribute_values,
        }
