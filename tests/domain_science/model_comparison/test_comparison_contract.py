from __future__ import annotations

import pytest

from scios.domain_science.model_comparison.comparison import ModelComparison


def test_comparison_requires_core_fields():
    comparison = ModelComparison(
        comparison_id="comparison-001",
        entity_ids=("entity-001", "entity-002"),
        evaluation_ids=("evaluation-001", "evaluation-002"),
    )

    assert comparison.comparison_id == "comparison-001"
    assert comparison.entity_ids == ("entity-001", "entity-002")
    assert comparison.evaluation_ids == (
        "evaluation-001",
        "evaluation-002",
    )


def test_comparison_supports_multiple_entities():
    comparison = ModelComparison(
        comparison_id="comparison-001",
        entity_ids=(
            "entity-001",
            "entity-002",
            "entity-003",
            "entity-004",
        ),
        evaluation_ids=(
            "evaluation-001",
            "evaluation-002",
            "evaluation-003",
        ),
    )

    assert len(comparison.entity_ids) == 4
    assert len(comparison.evaluation_ids) == 3


def test_comparison_does_not_select_a_winner():
    comparison = ModelComparison(
        comparison_id="comparison-001",
        entity_ids=("entity-001", "entity-002"),
        evaluation_ids=("evaluation-001", "evaluation-002"),
    )

    assert not hasattr(comparison, "winner")
    assert not hasattr(comparison, "best_model")
    assert not hasattr(comparison, "selected_model")
    assert not hasattr(comparison, "rank")


def test_comparison_does_not_score_entities():
    comparison = ModelComparison(
        comparison_id="comparison-001",
        entity_ids=("entity-001", "entity-002"),
        evaluation_ids=("evaluation-001", "evaluation-002"),
    )

    assert not hasattr(comparison, "score")
    assert not hasattr(comparison, "scores")
    assert not hasattr(comparison, "model_score")


def test_comparison_does_not_encode_probability_or_confidence():
    comparison = ModelComparison(
        comparison_id="comparison-001",
        entity_ids=("entity-001", "entity-002"),
        evaluation_ids=("evaluation-001", "evaluation-002"),
    )

    assert not hasattr(comparison, "probability")
    assert not hasattr(comparison, "confidence")
    assert not hasattr(comparison, "posterior")
    assert not hasattr(comparison, "likelihood")


def test_comparison_is_model_name_neutral():
    comparison = ModelComparison(
        comparison_id="comparison-001",
        entity_ids=("entity-001", "entity-002"),
        evaluation_ids=("evaluation-001", "evaluation-002"),
    )

    assert not hasattr(comparison, "ceit")
    assert not hasattr(comparison, "uniform_wlc")
    assert not hasattr(comparison, "heterogeneous_elasticity")
    assert not hasattr(comparison, "viscoelastic_gradient")
    assert not hasattr(comparison, "boundary_artifact")


def test_comparison_does_not_execute_model_fitting():
    comparison = ModelComparison(
        comparison_id="comparison-001",
        entity_ids=("entity-001", "entity-002"),
        evaluation_ids=("evaluation-001", "evaluation-002"),
    )

    assert not hasattr(comparison, "fit")
    assert not hasattr(comparison, "infer")
    assert not hasattr(comparison, "predict")
    assert not hasattr(comparison, "evaluate")


def test_comparison_is_not_an_execution_pipeline():
    comparison = ModelComparison(
        comparison_id="comparison-001",
        entity_ids=("entity-001", "entity-002"),
        evaluation_ids=("evaluation-001", "evaluation-002"),
    )

    assert not hasattr(comparison, "pipeline")
    assert not hasattr(comparison, "executor")
    assert not hasattr(comparison, "run")
    assert not hasattr(comparison, "execution_id")


@pytest.mark.parametrize(
    "entity_ids",
    [
        ("entity-001", "entity-002"),
        ("entity-001", "entity-002", "entity-003"),
    ],
)
def test_comparison_accepts_neutral_entity_collections(entity_ids):
    comparison = ModelComparison(
        comparison_id="comparison-001",
        entity_ids=entity_ids,
        evaluation_ids=("evaluation-001",),
    )

    assert comparison.entity_ids == entity_ids
