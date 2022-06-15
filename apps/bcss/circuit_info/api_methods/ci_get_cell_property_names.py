import re

from bluepy import Cell

from bcss.circuit_info.schemas.ci_get_cell_property_names import (
    CellPropertyNamesResponseSchema,
    CellPropertyNamesRequestSchema,
)
from bcss.main.consumers import CircuitServiceConsumer
from common.jsonrpc.consumer import JSONRPCRequest, JSONRPCConsumer


@CircuitServiceConsumer.register_method(
    request_schema=CellPropertyNamesRequestSchema,
    response_schema=CellPropertyNamesResponseSchema,
)
async def ci_get_cell_property_names(request: JSONRPCRequest, consumer: JSONRPCConsumer):
    attribute_names = [value for value in dir(Cell) if re.match(r"^(?!_)[A-Z_]+", value)]
    attribute_values = [getattr(Cell, value) for value in attribute_names]
    return {
        "property_names": attribute_values,
    }
