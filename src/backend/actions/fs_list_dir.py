import os
from dataclasses import dataclass

from marshmallow import Schema, fields

from backend.config import BASE_DIR_PATH
from backend.jsonrpc.actions import Action
from backend.jsonrpc.exceptions import PathIsNotDirectory, PathOutsideBaseDirectory


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


class FsListDir(Action):
    request_schema = FsListDirRequestSchema
    response_schema = FsListDirResponseSchema

    async def run(self):
        path: str = self.request.params["path"]
        absolute_path = os.path.abspath(path)

        if not absolute_path.startswith(BASE_DIR_PATH):
            raise PathOutsideBaseDirectory

        if not os.path.isdir(absolute_path):
            raise PathIsNotDirectory

        directory_list = []
        file_list = []

        with os.scandir(absolute_path) as entries:
            for directory_item in entries:
                if directory_item.is_dir():
                    directory_list.append(
                        Directory(
                            name=directory_item.name,
                            path=directory_item.path,
                        ),
                    )
                else:
                    stat = directory_item.stat(follow_symlinks=False)
                    file_list.append(
                        File(
                            name=directory_item.name,
                            path=directory_item.path,
                            size=stat.st_size,
                        ),
                    )

        return {
            "directories": directory_list,
            "files": file_list,
        }
