import re

from bluepy import Cell

from bcss.circuit_info.serializers.ci_get_cell_property_names import (
    CellPropertyNamesRequestSerializer,
    CellPropertyNamesResponseSerializer,
)
from bcss.main.consumers import CircuitServiceConsumer
from common.jsonrpc.jsonrpc_consumer import JSONRPCRequest


@CircuitServiceConsumer.register_method(
    request_serializer_class=CellPropertyNamesRequestSerializer,
    response_serializer_class=CellPropertyNamesResponseSerializer,
)
async def ci_get_cell_property_names(request: JSONRPCRequest):
    attribute_names = [value for value in dir(Cell) if re.match(r"^(?!_)[A-Z_]+", value)]
    attribute_values = [getattr(Cell, value) for value in attribute_names]
    return {
        "property_names": attribute_values,
    }
