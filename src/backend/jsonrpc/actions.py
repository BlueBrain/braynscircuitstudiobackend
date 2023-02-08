import logging
from typing import Type

from marshmallow import Schema
from pydash import kebab_case

from .jsonrpc_request import JSONRPCRequest

logger = logging.getLogger(__name__)


class Action:
    response_schema: Type[Schema] = None
    request_schema: Type[Schema] = None

    async def run(self, request: JSONRPCRequest):
        raise NotImplementedError

    def get_method_name(self):
        return None

    @property
    def name(self):
        return self.get_method_name() or kebab_case(self.__class__.__name__).lower()

    def validate_request(self, data):
        if self.request_schema:
            logger.debug(f"Validating request params against {self.request_schema.__name__}")
            logger.debug(f"{data=}")
            schema: Schema = self.request_schema()
            return schema.load(data=data)

        return data

    def validate_response(self, data):
        if self.response_schema is None:
            logger.warning(f"{self.name} has no response schema defined")
            return data

        schema: Schema = self.response_schema()
        clean_data = schema.load(data=data)
        return clean_data
