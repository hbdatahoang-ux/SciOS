from __future__ import annotations

import pytest

from scios.domain_science.model_comparison.criterion import Criterion


def test_criterion_requires_core_fields():
    criterion = Criterion(
        criterion_id="criterion-001",
        name="Spectral exponent preservation",
        description="Checks whether the observed spectrum preserves the expected exponent.",
    )

    assert criterion.criterion_id == "criterion-001"
    assert criterion.name == "Spectral exponent preservation"
    assert (
        criterion.description
        == "Checks whether the observed spectrum preserves the expected exponent."
    )


def test_criterion_is_model_independent():
    criterion = Criterion(
        criterion_id="criterion-001",
        name="Scaling consistency",
        description="A model-independent scientific criterion.",
    )

    assert not hasattr(criterion, "model")
    assert not hasattr(criterion, "model_id")
    assert not hasattr(criterion, "entity_id")
    assert not hasattr(criterion, "hypothesis")


def test_criterion_does_not_encode_evaluation_state():
    criterion = Criterion(
        criterion_id="criterion-001",
        name="Cross-geometry consistency",
        description="Checks consistency across independent geometries.",
    )

    assert not hasattr(criterion, "evaluation")
    assert not hasattr(criterion, "evaluation_state")
    assert not hasattr(criterion, "supported")
    assert not hasattr(criterion, "disfavored")
    assert not hasattr(criterion, "inconclusive")


def test_criterion_does_not_evaluate_evidence():
    criterion = Criterion(
        criterion_id="criterion-001",
        name="Amplitude consistency",
        description="Checks amplitude behavior.",
    )

    assert not hasattr(criterion, "evaluate")
    assert not hasattr(criterion, "compare")
    assert not hasattr(criterion, "score")


def test_criterion_can_contain_neutral_parameters():
    criterion = Criterion(
        criterion_id="criterion-001",
        name="Statistical consistency",
        description="A generic statistical criterion.",
        parameters={
            "metric": "reduced_chi_squared",
            "threshold": 2.0,
        },
    )

    assert criterion.parameters == {
        "metric": "reduced_chi_squared",
        "threshold": 2.0,
    }


@pytest.mark.parametrize(
    "parameters",
    [
        {},
        {"metric": "reduced_chi_squared"},
        {"threshold": 0.05},
        {"metric": "bic", "direction": "lower_is_better"},
    ],
)
def test_criterion_accepts_neutral_parameters(parameters):
    criterion = Criterion(
        criterion_id="criterion-001",
        name="Generic criterion",
        description="Model-independent criterion.",
        parameters=parameters,
    )

    assert criterion.parameters == parameters


def test_criterion_does_not_require_evidence():
    criterion = Criterion(
        criterion_id="criterion-001",
        name="Universal scaling",
        description="Checks a scaling relation.",
    )

    assert not hasattr(criterion, "evidence")
    assert not hasattr(criterion, "evidence_id")


def test_criterion_does_not_require_claim():
    criterion = Criterion(
        criterion_id="criterion-001",
        name="Robustness",
        description="Checks robustness under perturbation.",
    )

    assert not hasattr(criterion, "claim")
    assert not hasattr(criterion, "claim_id")