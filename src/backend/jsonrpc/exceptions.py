from typing import Optional

from backend.config import BASE_DIR_PATH

JSONRPC_PARSE_ERROR = -32700
JSONRPC_INVALID_REQUEST = -32600
JSONRPC_METHOD_NOT_FOUND = -32601
JSONRPC_INVALID_PARAMS = -32602
JSONRPC_INTERNAL_ERROR = -32603
VALIDATION_ERROR = -10000


class JSONRPCException(Exception):
    code: int = None
    message: Optional[str] = None

    def __init__(self, message=None, *args):
        super().__init__(*args)
        if message is not None:
            self.message = message

    @property
    def name(self):
        return self.__class__.__name__


class JSONRPCParseError(JSONRPCException):
    code = JSONRPC_PARSE_ERROR


class InvalidJSONRPCRequest(JSONRPCException):
    code = JSONRPC_INVALID_REQUEST


class ActionNotFound(JSONRPCException):
    code = JSONRPC_METHOD_NOT_FOUND


class MethodAndErrorNotAllowedTogether(JSONRPCException):
    pass


class ActionAlreadyRegistered(JSONRPCException):
    pass


class MethodNotAsynchronous(JSONRPCException):
    pass


class UnsupportedMessageType(JSONRPCException):
    pass


class PathIsNotDirectory(JSONRPCException):
    pass


class PathOutsideBaseDirectory(JSONRPCException):
    message = f"The requested path is outside the base directory: {BASE_DIR_PATH}"
