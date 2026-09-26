import pytest

_inference = pytest.importorskip("scios.cognitive_core.inference")
Compatibility = _inference.Compatibility
Coupling = _inference.Coupling


def test_compatibility_accepts_full_domain():
    assert Compatibility(1.0).value == 1.0
    assert Compatibility(0.0).value == 0.0
    assert Compatibility(-1.0).value == -1.0


@pytest.mark.parametrize("value", [-1.1, 1.1, 2.0, -2.0])
def test_compatibility_rejects_values_outside_domain(value):
    with pytest.raises(ValueError):
        Compatibility(value)


def test_compatibility_zero_means_independent_or_orthogonal():
    compatibility = Compatibility(0.0)
    assert compatibility.value == 0.0


def test_coupling_accepts_zero():
    assert Coupling(0.0).value == 0.0


@pytest.mark.parametrize("value", [-0.1, -1.0, -10.0])
def test_coupling_rejects_negative_values(value):
    with pytest.raises(ValueError):
        Coupling(value)


def test_coupling_is_non_negative():
    coupling = Coupling(0.75)
    assert coupling.value >= 0.0


def test_compatibility_and_coupling_are_distinct_quantities():
    compatibility = Compatibility(-0.8)
    coupling = Coupling(0.7)

    assert compatibility.value == -0.8
    assert coupling.value == 0.7


def test_compatibility_does_not_encode_phase():
    compatibility = Compatibility(-1.0)

    assert not hasattr(compatibility, "phase")
    assert not hasattr(compatibility, "phase_difference")


def test_coupling_does_not_encode_compatibility():
    coupling = Coupling(0.7)
    assert not hasattr(coupling, "compatibility")
