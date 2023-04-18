import os
import unicodedata
from dataclasses import dataclass
from os import DirEntry

from marshmallow import Schema, fields

from backend.filesystem.utils import get_safe_absolute_dir_path
from backend.jsonrpc.actions import Action
from backend.jsonrpc.exceptions import PathIsNotDirectory


class FsListDirRequestSchema(Schema):
    path = fields.String(
        required=True,
        allow_none=False,
    )


class DirectorySchema(Schema):
    name = fields.String()
    path = fields.String()


class FileSchema(Schema):
    name = fields.String()
    path = fields.String()
    size = fields.Integer()


class FsListDirResponseSchema(Schema):
    directories = fields.List(cls_or_instance=fields.Nested(DirectorySchema()))
    files = fields.List(cls_or_instance=fields.Nested(FileSchema()))


@dataclass
class File:
    name: str
    path: str
    size: int


@dataclass
class Directory:
    name: str
    path: str


def name_sort_key(value: str) -> str:
    return unicodedata.normalize("NFD", value.casefold())


class FsListDir(Action):
    request_schema = FsListDirRequestSchema
    response_schema = FsListDirResponseSchema

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.directory_list = []
        self.file_list = []

    async def run(self):
        absolute_path = get_safe_absolute_dir_path(self.request.params["path"])

        if not os.path.isdir(absolute_path):
            raise PathIsNotDirectory

        with os.scandir(absolute_path) as entries:
            for directory_item in entries:
                self.handle_directory_item(directory_item)

        self.directory_list.sort(key=lambda x: name_sort_key(x.name))
        self.file_list.sort(key=lambda x: name_sort_key(x.name))

        return {
            "directories": self.directory_list,
            "files": self.file_list,
        }

    def handle_directory_item(self, directory_item: DirEntry):
        if directory_item.is_dir():
            self.directory_list.append(
                Directory(
                    name=directory_item.name,
                    path=directory_item.path,
                ),
            )
        else:
            stat = directory_item.stat(follow_symlinks=False)
            self.file_list.append(
                File(
                    name=directory_item.name,
                    path=directory_item.path,
                    size=stat.st_size,
                ),
            )
