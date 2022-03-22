from marshmallow import Schema, fields

from bcsb.consumers import CircuitStudioConsumer
from jsonrpc.consumer import JSONRPCRequest


@CircuitStudioConsumer.register_method()
async def get_allocations(request: JSONRPCRequest):
    return {
        "allocations": [],
    }


class MethodSchema(Schema):
    pass


class AllocateNodeSchema(MethodSchema):
    project = fields.String(required=True)


@CircuitStudioConsumer.register_method()
async def allocate(request: JSONRPCRequest):
    return {}
