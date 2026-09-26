import pytest

_inference = pytest.importorskip("scios.cognitive_core.inference")
Compatibility = _inference.Compatibility
Coupling = _inference.Coupling


def test_compatibility_domain_is_closed():
    for value in (-1.0, -0.5, 0.0, 0.5, 1.0):
        assert Compatibility(value).value == value


def test_coupling_domain_is_non_negative():
    for value in (0.0, 0.1, 1.0, 10.0):
        assert Coupling(value).value == value


def test_compatibility_does_not_imply_phase():
    negative = Compatibility(-1.0)
    positive = Compatibility(1.0)

    assert negative.value != positive.value
    assert not hasattr(negative, "phase")
    assert not hasattr(positive, "phase")


@pytest.mark.parametrize(
    "invalid",
    [-float("inf"), float("inf"), float("nan")],
)
def test_compatibility_rejects_non_finite_values(invalid):
    with pytest.raises(ValueError):
        Compatibility(invalid)


@pytest.mark.parametrize(
    "invalid",
    [-float("inf"), -1.0, float("inf"), float("nan")],
)
def test_coupling_rejects_invalid_values(invalid):
    with pytest.raises(ValueError):
        Coupling(invalid)
