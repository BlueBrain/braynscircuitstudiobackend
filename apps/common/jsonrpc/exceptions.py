class JSONRPCException(Exception):
    pass


class MethodAndErrorNotAllowedTogether(JSONRPCException):
    pass


class MethodAlreadyRegistered(JSONRPCException):
    pass


class MethodNotAsynchronous(JSONRPCException):
    pass
