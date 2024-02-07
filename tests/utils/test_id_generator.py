from bcsb.utils.id_generator import IdGenerator


def test_next() -> None:
    generator = IdGenerator()
    assert generator.next() == 0
    assert generator.next() == 1
    assert generator.next() == 2
    assert generator.next() == 3
    assert generator.next() == 4


def test_recycle() -> None:
    generator = IdGenerator()
    assert generator.next() == 0
    assert generator.next() == 1
    assert generator.next() == 2
    generator.recycle(1)
    assert generator.next() == 1
    generator.recycle(2)
    generator.recycle(1)
    generator.recycle(0)
    assert generator.next() == 0
