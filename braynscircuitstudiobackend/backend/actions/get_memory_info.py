import psutil
from marshmallow import Schema, fields

from braynscircuitstudiobackend.backend.config import BASE_DIR_PATH
from braynscircuitstudiobackend.backend.jsonrpc.actions import Action


class VirtualMemorySchema(Schema):
    total = fields.Integer()
    available = fields.Integer()
    percent = fields.Float()
    used = fields.Integer()
    free = fields.Integer()
    active = fields.Integer()
    inactive = fields.Integer()
    cached = fields.Integer()
    shared = fields.Integer()


class SwapMemorySchema(Schema):
    total = fields.Integer()
    used = fields.Integer()
    free = fields.Integer()
    percent = fields.Float()
    sin = fields.Integer()
    sout = fields.Integer()


class GetMemoryInfoResponseSchema(Schema):
    virtual_memory = fields.Nested(VirtualMemorySchema())
    swap_memory = fields.Nested(SwapMemorySchema())


class GetMemoryInfo(Action):
    """Statistics about system memory and swap memory"""

    response_schema = GetMemoryInfoResponseSchema

    async def run(self):
        # See for reference https://psutil.readthedocs.io/en/latest/#memory
        virtual_memory = psutil.virtual_memory()
        swap_memory = psutil.swap_memory()

        return {
            "virtual_memory": virtual_memory,
            "swap_memory": swap_memory,
        }
