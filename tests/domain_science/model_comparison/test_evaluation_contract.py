from __future__ import annotations

import pytest

from scios.domain_science.model_comparison.evaluation import (
    Evaluation,
    EvaluationState,
)


def test_evaluation_requires_core_fields():
    evaluation = Evaluation(
        evaluation_id="evaluation-001",
        entity_id="entity-001",
        evidence_id="evidence-001",
        criterion_id="criterion-001",
        state=EvaluationState.SUPPORTED,
    )

    assert evaluation.evaluation_id == "evaluation-001"
    assert evaluation.entity_id == "entity-001"
    assert evaluation.evidence_id == "evidence-001"
    assert evaluation.criterion_id == "criterion-001"
    assert evaluation.state is EvaluationState.SUPPORTED


@pytest.mark.parametrize(
    "state",
    [
        EvaluationState.SUPPORTED,
        EvaluationState.DISFAVORED,
        EvaluationState.INCONCLUSIVE,
    ],
)
def test_evaluation_accepts_canonical_states(state):
    evaluation = Evaluation(
        evaluation_id="evaluation-001",
        entity_id="entity-001",
        evidence_id="evidence-001",
        criterion_id="criterion-001",
        state=state,
    )

    assert evaluation.state is state


def test_evaluation_state_is_not_a_boolean():
    assert EvaluationState.SUPPORTED is not True
    assert EvaluationState.DISFAVORED is not False


@pytest.mark.parametrize(
    "invalid_state",
    [
        "confirmed",
        "refuted",
        "surprise",
        "winner",
        "supported_by_default",
    ],
)
def test_evaluation_rejects_noncanonical_states(invalid_state):
    with pytest.raises(ValueError):
        Evaluation(
            evaluation_id="evaluation-001",
            entity_id="entity-001",
            evidence_id="evidence-001",
            criterion_id="criterion-001",
            state=invalid_state,
        )


def test_evaluation_links_entity_evidence_and_criterion():
    evaluation = Evaluation(
        evaluation_id="evaluation-001",
        entity_id="entity-001",
        evidence_id="evidence-001",
        criterion_id="criterion-001",
        state=EvaluationState.INCONCLUSIVE,
    )

    assert evaluation.entity_id == "entity-001"
    assert evaluation.evidence_id == "evidence-001"
    assert evaluation.criterion_id == "criterion-001"


def test_evaluation_does_not_encode_probability_or_confidence():
    evaluation = Evaluation(
        evaluation_id="evaluation-001",
        entity_id="entity-001",
        evidence_id="evidence-001",
        criterion_id="criterion-001",
        state=EvaluationState.SUPPORTED,
    )

    assert not hasattr(evaluation, "probability")
    assert not hasattr(evaluation, "confidence")
    assert not hasattr(evaluation, "posterior")
    assert not hasattr(evaluation, "likelihood")


def test_evaluation_does_not_encode_model_selection():
    evaluation = Evaluation(
        evaluation_id="evaluation-001",
        entity_id="entity-001",
        evidence_id="evidence-001",
        criterion_id="criterion-001",
        state=EvaluationState.SUPPORTED,
    )

    assert not hasattr(evaluation, "winner")
    assert not hasattr(evaluation, "rank")
    assert not hasattr(evaluation, "selected")
    assert not hasattr(evaluation, "best_model")


def test_evaluation_does_not_execute_inference():
    evaluation = Evaluation(
        evaluation_id="evaluation-001",
        entity_id="entity-001",
        evidence_id="evidence-001",
        criterion_id="criterion-001",
        state=EvaluationState.SUPPORTED,
    )

    assert not hasattr(evaluation, "infer")
    assert not hasattr(evaluation, "fit")
    assert not hasattr(evaluation, "predict")
    assert not hasattr(evaluation, "score")


def test_evaluation_can_contain_neutral_details():
    evaluation = Evaluation(
        evaluation_id="evaluation-001",
        entity_id="entity-001",
        evidence_id="evidence-001",
        criterion_id="criterion-001",
        state=EvaluationState.INCONCLUSIVE,
        details={"reason": "insufficient evidence"},
    )

    assert evaluation.details == {"reason": "insufficient evidence"}


def test_evaluation_does_not_depend_on_runtime_or_cognitive_core():
    evaluation = Evaluation(
        evaluation_id="evaluation-001",
        entity_id="entity-001",
        evidence_id="evidence-001",
        criterion_id="criterion-001",
        state=EvaluationState.SUPPORTED,
    )

    assert not hasattr(evaluation, "execution_id")
    assert not hasattr(evaluation, "task_id")
    assert not hasattr(evaluation, "agent_id")
    assert not hasattr(evaluation, "reasoning_engine")
