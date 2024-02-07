class IdGenerator:
    def __init__(self) -> None:
        self._counter = 0
        self._recycled_ids = list[int]()

    def next(self) -> int:
        if self._recycled_ids:
            return self._recycled_ids.pop()
        id = self._counter
        self._counter += 1
        return id

    def recycle(self, id: int) -> None:
        self._recycled_ids.append(id)
