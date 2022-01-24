import re
from typing import Optional

UUID_LENGTH = 36


def extract_uuid_from_text(value: str) -> Optional[str]:
    found = re.search(r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}", value)
    if found:
        return found.group()
    return
