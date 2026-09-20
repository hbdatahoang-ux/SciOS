import pytest

_inference = pytest.importorskip("scios.cognitive_core.inference")
Hypothesis = _inference.Hypothesis


def make_hypothesis() -> Hypothesis:
    return Hypothesis(
        id="H1",
        variables=["flow_rate", "pressure"],
        mechanism="partial channel obstruction",
        causal_structure={
            "obstruction": ["hydraulic_resistance"],
            "hydraulic_resistance": ["flow_rate", "pressure"],
        },
        parameters={
            "obstruction_fraction": 0.2,
        },
    )


def test_hypothesis_has_stable_identity():
    h = make_hypothesis()
    assert h.id == "H1"


def test_hypothesis_contains_scientific_explanation():
    h = make_hypothesis()

    assert h.variables == ["flow_rate", "pressure"]
    assert h.mechanism == "partial channel obstruction"
    assert "obstruction" in h.causal_structure
    assert h.parameters["obstruction_fraction"] == 0.2


def test_hypothesis_does_not_own_inference_amplitude():
    h = make_hypothesis()
    assert not hasattr(h, "amplitude")


def test_hypothesis_does_not_own_inference_phase():
    h = make_hypothesis()
    assert not hasattr(h, "phase")


def test_hypothesis_is_not_an_inference_state():
    h = make_hypothesis()

    assert not hasattr(h, "interference")
    assert not hasattr(h, "probability")
    assert not hasattr(h, "confidence")
