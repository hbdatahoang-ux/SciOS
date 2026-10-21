from __future__ import annotations

import pytest

from scios.domain_science.model_comparison.evidence import Evidence


def test_evidence_requires_core_fields():
    evidence = Evidence(
        evidence_id="evidence-001",
        dataset_id="dataset-001",
        observable_id="observable-001",
        value={"measurement": 1.0},
        provenance_id="provenance-001",
    )

    assert evidence.evidence_id == "evidence-001"
    assert evidence.dataset_id == "dataset-001"
    assert evidence.observable_id == "observable-001"
    assert evidence.value == {"measurement": 1.0}
    assert evidence.provenance_id == "provenance-001"


def test_evidence_is_model_independent():
    evidence = Evidence(
        evidence_id="evidence-001",
        dataset_id="dataset-001",
        observable_id="observable-001",
        value={"measurement": 1.0},
        provenance_id="provenance-001",
    )

    assert not hasattr(evidence, "model")
    assert not hasattr(evidence, "model_id")
    assert not hasattr(evidence, "entity_id")
    assert not hasattr(evidence, "hypothesis")


def test_evidence_does_not_encode_evaluation_state():
    evidence = Evidence(
        evidence_id="evidence-001",
        dataset_id="dataset-001",
        observable_id="observable-001",
        value={"measurement": 1.0},
        provenance_id="provenance-001",
    )

    assert not hasattr(evidence, "evaluation")
    assert not hasattr(evidence, "evaluation_state")
    assert not hasattr(evidence, "supported")
    assert not hasattr(evidence, "disfavored")
    assert not hasattr(evidence, "inconclusive")


def test_evidence_can_represent_structured_measurement():
    evidence = Evidence(
        evidence_id="evidence-001",
        dataset_id="dataset-001",
        observable_id="observable-001",
        value={
            "q": [0.1, 0.2, 0.3],
            "spectrum": [10.0, 4.0, 1.5],
        },
        provenance_id="provenance-001",
    )

    assert evidence.value["q"] == [0.1, 0.2, 0.3]
    assert evidence.value["spectrum"] == [10.0, 4.0, 1.5]


def test_evidence_can_represent_derived_measurement():
    evidence = Evidence(
        evidence_id="evidence-002",
        dataset_id="dataset-001",
        observable_id="observable-002",
        value={"effective_value": 2.5},
        provenance_id="provenance-002",
    )

    assert evidence.value == {"effective_value": 2.5}


@pytest.mark.parametrize(
    "value",
    [
        1.0,
        {"measurement": 1.0},
        [1.0, 2.0, 3.0],
        {"q": [0.1, 0.2], "spectrum": [4.0, 2.0]},
    ],
)
def test_evidence_accepts_neutral_value(value):
    evidence = Evidence(
        evidence_id="evidence-001",
        dataset_id="dataset-001",
        observable_id="observable-001",
        value=value,
        provenance_id="provenance-001",
    )

    assert evidence.value == value


def test_evidence_does_not_perform_evaluation():
    evidence = Evidence(
        evidence_id="evidence-001",
        dataset_id="dataset-001",
        observable_id="observable-001",
        value={"measurement": 1.0},
        provenance_id="provenance-001",
    )

    assert not hasattr(evidence, "evaluate")
    assert not hasattr(evidence, "compare")
    assert not hasattr(evidence, "score")


def test_evidence_does_not_encode_claim():
    evidence = Evidence(
        evidence_id="evidence-001",
        dataset_id="dataset-001",
        observable_id="observable-001",
        value={"measurement": 1.0},
        provenance_id="provenance-001",
    )

    assert not hasattr(evidence, "claim")
    assert not hasattr(evidence, "claim_id")


def test_evidence_links_to_dataset_not_execution():
    evidence = Evidence(
        evidence_id="evidence-001",
        dataset_id="dataset-001",
        observable_id="observable-001",
        value={"measurement": 1.0},
        provenance_id="provenance-001",
    )

    assert evidence.dataset_id == "dataset-001"
    assert not hasattr(evidence, "execution_id")
    assert not hasattr(evidence, "pipeline_id")
    assert not hasattr(evidence, "task_id")