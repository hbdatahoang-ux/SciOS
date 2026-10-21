import pytest

_inference = pytest.importorskip("scios.cognitive_core.inference")
Evidence = _inference.Evidence


def make_evidence() -> Evidence:
    return Evidence(
        id="E17",
        observation="microfluidic flow/pressure anomaly",
        value={
            "flow_rate": 1.5,
            "pressure": 16.0,
        },
        context={
            "baseline_flow_rate": 2.5,
            "baseline_pressure": 14.2,
        },
        source="pressure_sensor_01+flow_sensor_01",
        uncertainty={
            "flow_rate": 0.05,
            "pressure": 0.1,
        },
        quality=0.95,
    )


def test_evidence_has_stable_identity():
    evidence = make_evidence()
    assert evidence.id == "E17"


def test_evidence_contains_observation_and_measurement():
    evidence = make_evidence()

    assert evidence.observation == "microfluidic flow/pressure anomaly"
    assert evidence.value["flow_rate"] == 1.5
    assert evidence.value["pressure"] == 16.0


def test_evidence_contains_context_and_provenance():
    evidence = make_evidence()

    assert evidence.context["baseline_flow_rate"] == 2.5
    assert evidence.context["baseline_pressure"] == 14.2
    assert evidence.source == "pressure_sensor_01+flow_sensor_01"


def test_evidence_contains_uncertainty():
    evidence = make_evidence()

    assert evidence.uncertainty["flow_rate"] == 0.05
    assert evidence.uncertainty["pressure"] == 0.1


def test_evidence_quality_is_bounded():
    evidence = make_evidence()
    assert 0.0 <= evidence.quality <= 1.0


def test_evidence_does_not_own_hypothesis_confidence():
    evidence = make_evidence()
    assert not hasattr(evidence, "confidence")


def test_evidence_does_not_own_amplitude_or_phase():
    evidence = make_evidence()

    assert not hasattr(evidence, "amplitude")
    assert not hasattr(evidence, "phase")
