from types import FunctionType


class Method:
    name: str
    handler: FunctionType

    def __init__(self, name: str, handler: FunctionType, allow_anonymous_access: bool = False):
        self.name = name
        self.handler = handler
        self.allow_anonymous_access = allow_anonymous_access

    @property
    def docstring(self):
        return self.handler.__doc__
