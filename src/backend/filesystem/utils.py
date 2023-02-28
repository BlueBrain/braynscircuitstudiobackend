import os

from backend.config import BASE_DIR_PATH
from backend.jsonrpc.exceptions import PathOutsideBaseDirectory


def get_safe_absolute_path(path: str):
    absolute_path = make_path_end_with_slash(os.path.abspath(path))
    base_dir_path = make_path_end_with_slash(BASE_DIR_PATH)

    if not absolute_path.startswith(base_dir_path):
        raise PathOutsideBaseDirectory

    return absolute_path


def make_path_end_with_slash(path: str):
    return f"{path}/" if not path.endswith("/") else path
