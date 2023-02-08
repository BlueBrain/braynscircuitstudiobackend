from typing import Optional

JSONRPC_PARSE_ERROR = -32700
JSONRPC_INVALID_REQUEST = -32600
JSONRPC_METHOD_NOT_FOUND = -32601
JSONRPC_INVALID_PARAMS = -32602
JSONRPC_INTERNAL_ERROR = -32603
VALIDATION_ERROR = -10000


class JSONRPCException(Exception):
    code: int = None
    name: str = None
    message: Optional[str] = None

    def __init__(self, message=None, *args):
        super().__init__(*args)
        self.message = message


class JSONRPCParseError(JSONRPCException):
    code = JSONRPC_PARSE_ERROR
    name = "Parse error"


class InvalidJSONRPCRequest(JSONRPCException):
    code = JSONRPC_INVALID_REQUEST
    name = "Invalid request"


class ActionNotFound(JSONRPCException):
    code = JSONRPC_METHOD_NOT_FOUND
    name = "Method not found"


class MethodAndErrorNotAllowedTogether(JSONRPCException):
    pass


class ActionAlreadyRegistered(JSONRPCException):
    pass


class MethodNotAsynchronous(JSONRPCException):
    pass


class UnsupportedMessageType(JSONRPCException):
    pass
