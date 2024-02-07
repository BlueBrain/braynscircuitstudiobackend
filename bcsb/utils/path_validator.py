from pathlib import Path

from ..jsonrpc import InvalidParams


class PathValidator:
    def __init__(self, base_directory: Path) -> None:
        self._base_directory = base_directory

    @property
    def base_directory(self) -> Path:
        return self._base_directory

    def validate(self, path: Path | str) -> Path:
        path = Path(path)
        if not path.is_relative_to(self._base_directory):
            raise InvalidParams(f"'{path}' is outside '{self.base_directory}'")
        return path.absolute()

    def file(self, path: Path | str) -> Path:
        path = Path(path)
        if not path.is_file():
            raise InvalidParams(f"'{path}' is not a regular file")
        return path

    def directory(self, path: Path | str) -> Path:
        path = Path(path)
        if not path.is_dir():
            raise InvalidParams(f"'{path}' is not a directory")
        return path

    def validate_file(self, path: Path | str) -> Path:
        path = self.validate(path)
        return self.file(path)

    def validate_directory(self, path: Path | str) -> Path:
        path = self.validate(path)
        return self.directory(path)
