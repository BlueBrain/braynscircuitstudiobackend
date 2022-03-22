from utils.strings import equals_ignoring_case


def test_equals_ignoring_case():
    assert equals_ignoring_case("", "")
    assert equals_ignoring_case("a", "A")
    assert equals_ignoring_case("B", "b")
    assert equals_ignoring_case("c", "c")
    assert equals_ignoring_case("D", "D")
    assert equals_ignoring_case("EeEe", "eeEe")
    assert not equals_ignoring_case("EeEe", "ee")
    assert not equals_ignoring_case("x", "")
