"""EntryPoint abstract class and related exception."""
from abc import abstractmethod
from typing import Any, Awaitable, Callable


class EntryPoint:
    """Abstract class to define entry points.

    To create a new entry point, you should inherit this abstract class
    and implement the `name` property and the `exec` method.
    """

    @abstractmethod
    async def exec(self, params: Any) -> Awaitable:
        """Asynchronous execution of this entry point.

        Given some `params`, this function will compute the result.
        It can throw an `EntryPointException` to return an error to the client.
        """

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of this entrypoint."""

    async def callback(
        self,
        query_id: str,
        params: Any,
        success: Callable[[str, Any], Awaitable],
        failure: Callable[[str, int, str], Awaitable],
    ):
        """Send back the result of this entry point given some params."""
        try:
            result = await self.exec(params)
            await success(query_id, result)
        except EntryPointException as ex:
            await failure(query_id, ex.code, ex.message)
        except Exception as ex:  # pylint: disable=broad-except
            await failure(query_id, -9, str(ex))


class EntryPointException(BaseException):
    """Exception for the client."""

    code = 0
    message = ""

    def __init__(self, code: int, message: str) -> None:
        """Entrypoint Exception constructor.

        Args:
            code: error number
            message: error description
        """
        super().__init__(code, message)
        self.code = code
        self.message = message
