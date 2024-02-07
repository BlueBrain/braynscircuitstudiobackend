import re
from dataclasses import dataclass
from logging import Logger
from pathlib import Path

from ..service import Component, EndpointRegistry
from ..utils import PathValidator

HEADER_END = re.compile(r"(\n\n)|(\r\n\r\n)|(\r\r)")
ENDLINE = re.compile(r"[\n\r]+")


def chunk_to_string(chunk: bytes) -> str:
    mode = ""
    i = 0
    carriage_return = ord("\r")
    new_line = ord("\n")
    for i in range(len(chunk)):
        v = chunk[i]
        if mode == "":
            if v == carriage_return:
                mode = "r"
            elif v == new_line:
                mode = "n"
        elif mode == "r":
            if v == carriage_return:
                i -= 2
                break
            if v == new_line:
                mode = "rn"
            else:
                mode = ""
        elif mode == "n":
            if v == new_line:
                i -= 2
                break
            mode = ""
        elif mode == "rn":
            if v == carriage_return:
                mode = "rnr"
            else:
                mode = ""
        elif mode == "rnr":
            if mode == new_line:
                i -= 4
                break
            mode = ""
    return chunk[: i + 1].decode()


def read_header(path: Path) -> str:
    with path.open("rb") as file:
        chunk = file.read(1024)
    header = chunk_to_string(chunk)
    match = HEADER_END.search(header)
    if match is None:
        return header
    return header[: match.start()]


@dataclass
class VolumeHeaderParams:
    path: str


class Volume(Component):
    def __init__(self, validator: PathValidator, logger: Logger) -> None:
        self._validator = validator
        self._logger = logger

    def register(self, endpoints: EndpointRegistry) -> None:
        endpoints.add("volume-parse-header", self.parse_header, "Parse volume header")

    async def parse_header(self, params: VolumeHeaderParams) -> dict[str, str]:
        path = self._validator.validate_file(params.path)
        header = read_header(path)
        self._logger.debug("Header: %s", header)
        data = dict[str, str]()
        for line in ENDLINE.split(header):
            if line.startswith("#"):
                continue
            if line[:4] == "NRRD":
                data["NRRD version"] = line[4:]
                continue
            key, value = line.split(":", maxsplit=1)
            data[key] = value.strip()
        return data
