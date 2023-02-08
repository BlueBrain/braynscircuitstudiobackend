import logging
from typing import Type

from marshmallow import Schema
from pydash import kebab_case

from .jsonrpc_request import JSONRPCRequest
from ..decorators.classproperty import classproperty

logger = logging.getLogger(__name__)


class Action:
    request: JSONRPCRequest = None
    request_schema: Type[Schema] = None
    response_schema: Type[Schema] = None

    def __init__(self, request: JSONRPCRequest):
        self.request = request

    async def run(self):
        raise NotImplementedError

    @classproperty
    def name(cls) -> str:
        return kebab_case(cls.__name__).lower()

    def validate_request(self, data):
        if self.request_schema:
            logger.debug(f"Validating request params against {self.request_schema.__name__}")
            logger.debug(f"{data=}")
            schema: Schema = self.request_schema()
            return schema.load(data=data)
        logger.warning(f"No request schema for {self.name}")
        return data

    def validate_response(self, data):
        if self.response_schema is None:
            logger.warning(f"{self.name} has no response schema defined")
            return data

        schema: Schema = self.response_schema()
        clean_data = schema.load(data=data)
        return clean_data
