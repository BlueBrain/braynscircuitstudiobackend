class JSONRPCException(Exception):
    pass


class MethodAndErrorNotAllowedTogether(JSONRPCException):
    pass
