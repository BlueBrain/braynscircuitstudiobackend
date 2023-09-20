import unicodedata
from base64 import b64decode
from dataclasses import dataclass, field
from enum import Enum

from ..jsonrpc import InternalError
from ..path import PathValidator
from ..service import Component, EndpointRegistry


class PathType(Enum):
    FILE = "file"
    DIRECTORY = "directory"


@dataclass
class ExistsParams:
    path: str


@dataclass
class ExistsResult:
    exists: bool
    type: PathType | None = None


@dataclass
class ListDirParams:
    path: str


@dataclass
class File:
    name: str
    path: str
    size: int


@dataclass
class Directory:
    name: str
    path: str


@dataclass
class ListDirResult:
    directories: list[Directory] = field(default_factory=list)
    files: list[File] = field(default_factory=list)


@dataclass
class UploadParams:
    path: str
    content: str
    base64: bool


def sort_key(value: File | Directory) -> str:
    return unicodedata.normalize("NFD", value.name.casefold())


class Filesystem(Component):
    def __init__(self, validator: PathValidator) -> None:
        self._validator = validator

    def register(self, endpoints: EndpointRegistry) -> None:
        endpoints.add("fs-exists", self.exists, "Inspect given path")
        endpoints.add("fs-get-root", self.get_root, "Base directory")
        endpoints.add("fs-list-dir", self.list_dir, "List directory content")
        endpoints.add("fs-upload-content", self.upload, "Upload file")

    async def exists(self, params: ExistsParams) -> ExistsResult:
        path = self._validator.validate(params.path)
        if path.is_dir():
            return ExistsResult(exists=True, type=PathType.DIRECTORY)
        if path.is_file():
            return ExistsResult(exists=True, type=PathType.FILE)
        return ExistsResult(exists=False)

    async def get_root(self) -> str:
        return str(self._validator.base_directory)

    async def list_dir(self, params: ListDirParams) -> ListDirResult:
        path = self._validator.validate_directory(params.path)
        result = ListDirResult()
        for child in path.glob("*"):
            if child.is_dir():
                directory = Directory(child.name, str(child))
                result.directories.append(directory)
            if child.is_file():
                size = child.stat().st_size
                file = File(child.name, str(child), size)
                result.files.append(file)
        result.directories.sort(key=sort_key)
        result.files.sort(key=sort_key)
        return result

    async def upload(self, params: UploadParams) -> None:
        path = self._validator.validate(params.path)
        mode = "w"
        content = params.content
        try:
            if params.base64:
                mode = "wb"
                content = b64decode(content)
            with path.open(mode) as file:
                file.write(content)
        except Exception as e:
            raise InternalError(str(e))
