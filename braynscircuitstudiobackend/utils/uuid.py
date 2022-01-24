import re

UUID_LENGTH = 36


def extract_uuid_from_text(value: str) -> str:
    return re.match(value, r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}").group()
