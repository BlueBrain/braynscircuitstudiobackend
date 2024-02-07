from collections.abc import Sequence
from typing import TypeVar

T = TypeVar("T")


def pick(items: Sequence[T], count: int) -> list[T]:
    total = len(items)
    if count >= total:
        return list(items)
    result = list[T]()
    index = 0
    while count > 0:
        step = total // (count + 1)
        index += step
        total -= step
        count -= 1
        if index >= len(items):
            return result
        result.append(items[index])
    return result
