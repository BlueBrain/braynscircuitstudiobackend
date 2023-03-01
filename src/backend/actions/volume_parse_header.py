import os
import re

from marshmallow import Schema

from backend.jsonrpc.actions import Action
from backend.serialization.fields import FilePathField

# todo needs checking/testing

RX_END_OF_HEADER = re.compile(r"(\n\n)|(\r\n\r\n)|(\r\r)")
RX_END_OF_LINE = re.compile(r"[\n\r]+")


class VolumeParseHeaderRequestSchema(Schema):
    path = FilePathField(required=True)


class VolumeParseHeader(Action):
    request_schema = VolumeParseHeaderRequestSchema

    async def run(self):
        path = self.request.params["path"]
        path = os.path.abspath(path)

        with open(path, "rb") as fd:
            chunk = fd.read(1024)
            text = convert_into_string(chunk)
            print(text)
            match = RX_END_OF_HEADER.search(text)
            header = text[: match.start] if match is not None else text

        data = {}
        lines = RX_END_OF_LINE.split(header)

        for line in lines:
            if is_comment(line):
                continue
            if line[:4] == "NRRD":
                data["NRRD version"] = line[4:]
                continue
            key, value = parse_field(line)
            data[key] = value.strip()

        return data


def is_comment(line):
    return line[0] == "#"


def parse_field(line):
    index = line.find(":")
    return line[:index], line[index + 1 :]


def convert_into_string(chunk):
    mode = ""
    i = 0
    carriage_return_ord = ord("\r")
    new_line_ord = ord("\n")
    for i in range(len(chunk)):
        v = chunk[i]
        if mode == "":
            if v == carriage_return_ord:
                mode = "r"
            elif v == new_line_ord:
                mode = "n"
        elif mode == "r":
            if v == carriage_return_ord:
                i -= 2
                break
            if v == new_line_ord:
                mode = "rn"
            else:
                mode = ""
        elif mode == "n":
            if v == new_line_ord:
                i -= 2
                break
            mode = ""
        elif mode == "rn":
            if v == carriage_return_ord:
                mode = "rnr"
            else:
                mode = ""
        elif mode == "rnr":
            if mode == new_line_ord:
                i -= 4
                break
            mode = ""
    return chunk[: i + 1].decode("utf-8")
