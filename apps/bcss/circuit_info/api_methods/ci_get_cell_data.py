import logging

from bluepy import Circuit, Cell
from scipy.spatial.transform import Rotation

from bcss.circuit_info.serializers.ci_get_cell_data import (
    CellDataRequestSerializer,
    CellDataResponseSerializer,
)
from bcss.main.consumers import CircuitServiceConsumer
from common.jsonrpc.consumer import JSONRPCRequest

logger = logging.getLogger(__name__)


@CircuitServiceConsumer.register_method(
    request_serializer_class=CellDataRequestSerializer,
    response_serializer_class=CellDataResponseSerializer,
)
async def ci_get_cell_data(request: JSONRPCRequest):
    circuit = Circuit(request.params["path"])
    cell_ids = request.params["ids"]
    requested_properties = set(request.params["properties"])

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
            # todo thix needs checking because the result differs from what Brayns returns
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
