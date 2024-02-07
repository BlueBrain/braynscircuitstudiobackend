from bcsb.utils.picking import pick


def test_empty() -> None:
    assert pick([], 1) == []
    assert pick([1, 2], 0) == []


def test_too_much() -> None:
    assert pick([1, 2], 3) == [1, 2]
    assert pick([1, 2], 2) == [1, 2]


def test_samples() -> None:
    assert pick([1, 2, 3, 4], 3) == [2, 3, 4]
    assert pick([1, 2, 3, 4], 2) == [2, 3]
    assert pick([1, 2, 3, 4], 1) == [3]
    assert pick([i + 1 for i in range(10)], 5) == [2, 3, 5, 7, 9]
