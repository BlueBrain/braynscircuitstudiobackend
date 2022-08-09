import re
from typing import Optional
from uuid import UUID

UUID_LENGTH = 36


def extract_uuid_from_text(value: str) -> Optional[UUID]:
    found = re.search(r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}", value)
    if found:
        return UUID(found.group())
    return
