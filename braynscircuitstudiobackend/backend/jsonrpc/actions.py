import logging

from marshmallow import Schema
from pydash import kebab_case

from braynscircuitstudiobackend.backend.decorators.classproperty import classproperty

from .jsonrpc_request import JSONRPCRequest

logger = logging.getLogger(__name__)


class Action:
    request: JSONRPCRequest = None
    request_schema: type[Schema] = None
    response_schema: type[Schema] = None

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

        # This will serialize the object into JSON data (defined in the response_schema of the action class)
        schema: Schema = self.response_schema()

        try:
            clean_data = schema.dump(data)
        except ValueError:
            logger.error(f"Got error during data dump. Original input was: {data=}")
            raise

        return clean_data
