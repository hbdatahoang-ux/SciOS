# ==============================================================================
# SciOS Runtime Science
# Evaluation Tests
# ==============================================================================

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

from scios.runtime.science.evaluation.models import (
    EvaluationError,
    EvaluationOutcome,
    EvaluationResult,
    InvalidEvaluationError,
)
from scios.runtime.science.evaluation.evaluator import Evaluator


# ==============================================================================
# Helpers
# ==============================================================================


class DummyHypothesis:
    """Minimal hypothesis compatible with the evaluator contract."""

    def __init__(
        self,
        id: str = "H001",
        expected: object = True,
    ) -> None:
        self.id = id
        self.expected = expected


class DummyObservation:
    """Minimal observation compatible with the evaluator contract."""

    def __init__(
        self,
        id: str = "O001",
        value: object = True,
    ) -> None:
        self.id = id
        self.value = value


# ==============================================================================
# Exceptions
# ==============================================================================


def test_evaluation_error_is_runtime_error():
    assert issubclass(EvaluationError, RuntimeError)


def test_invalid_evaluation_error_is_evaluation_error():
    assert issubclass(
        InvalidEvaluationError,
        EvaluationError,
    )


def test_invalid_evaluation_error_is_value_error():
    assert issubclass(
        InvalidEvaluationError,
        ValueError,
    )


# ==============================================================================
# EvaluationOutcome
# ==============================================================================


def test_evaluation_outcome_values():
    assert EvaluationOutcome.CONFIRMED.value == "confirmed"
    assert EvaluationOutcome.REFUTED.value == "refuted"
    assert EvaluationOutcome.INCONCLUSIVE.value == "inconclusive"
    assert EvaluationOutcome.SURPRISE.value == "surprise"


def test_evaluation_outcome_is_string_enum():
    assert isinstance(
        EvaluationOutcome.CONFIRMED,
        str,
    )


# ==============================================================================
# EvaluationResult construction
# ==============================================================================


def test_evaluation_result_creation():
    result = EvaluationResult(
        hypothesis_id="H001",
        observation_id="O001",
        outcome=EvaluationOutcome.CONFIRMED,
        score=1.0,
        reason="observation matches hypothesis",
    )

    assert result.hypothesis_id == "H001"
    assert result.observation_id == "O001"
    assert result.outcome is EvaluationOutcome.CONFIRMED
    assert result.score == 1.0
    assert result.reason == "observation matches hypothesis"
    assert result.metadata == {}
    assert result.created_at.tzinfo is not None


def test_evaluation_result_timestamp_is_timezone_aware():
    result = EvaluationResult(
        hypothesis_id="H001",
        observation_id="O001",
        outcome=EvaluationOutcome.CONFIRMED,
        score=1.0,
        reason="confirmed",
    )

    assert result.created_at.utcoffset() is not None


def test_explicit_timezone_aware_timestamp_is_preserved():
    timestamp = datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    )

    result = EvaluationResult(
        hypothesis_id="H001",
        observation_id="O001",
        outcome=EvaluationOutcome.CONFIRMED,
        score=1.0,
        reason="confirmed",
        created_at=timestamp,
    )

    assert result.created_at is timestamp


# ==============================================================================
# EvaluationResult validation
# ==============================================================================


def test_empty_hypothesis_id_is_rejected():
    with pytest.raises(
        InvalidEvaluationError,
        match="hypothesis_id must be a non-empty string",
    ):
        EvaluationResult(
            hypothesis_id="",
            observation_id="O001",
            outcome=EvaluationOutcome.CONFIRMED,
            score=1.0,
            reason="confirmed",
        )


def test_empty_observation_id_is_rejected():
    with pytest.raises(
        InvalidEvaluationError,
        match="observation_id must be a non-empty string",
    ):
        EvaluationResult(
            hypothesis_id="H001",
            observation_id="",
            outcome=EvaluationOutcome.CONFIRMED,
            score=1.0,
            reason="confirmed",
        )


def test_invalid_outcome_is_rejected():
    with pytest.raises(
        InvalidEvaluationError,
        match="outcome must be an EvaluationOutcome",
    ):
        EvaluationResult(
            hypothesis_id="H001",
            observation_id="O001",
            outcome="confirmed",
            score=1.0,
            reason="confirmed",
        )


@pytest.mark.parametrize(
    "score",
    [
        -1.0,
        -0.001,
        1.001,
        2.0,
    ],
)
def test_score_outside_range_is_rejected(score):
    with pytest.raises(
        InvalidEvaluationError,
        match="score must be between 0.0 and 1.0",
    ):
        EvaluationResult(
            hypothesis_id="H001",
            observation_id="O001",
            outcome=EvaluationOutcome.CONFIRMED,
            score=score,
            reason="invalid score",
        )


@pytest.mark.parametrize(
    "score",
    [
        True,
        False,
    ],
)
def test_boolean_score_is_rejected(score):
    with pytest.raises(
        InvalidEvaluationError,
        match="score must be numeric",
    ):
        EvaluationResult(
            hypothesis_id="H001",
            observation_id="O001",
            outcome=EvaluationOutcome.CONFIRMED,
            score=score,
            reason="invalid score",
        )


@pytest.mark.parametrize(
    "score",
    [
        0,
        0.0,
        0.5,
        1,
        1.0,
    ],
)
def test_valid_score_boundaries(score):
    result = EvaluationResult(
        hypothesis_id="H001",
        observation_id="O001",
        outcome=EvaluationOutcome.CONFIRMED,
        score=score,
        reason="valid score",
    )

    assert 0.0 <= result.score <= 1.0
    assert isinstance(result.score, float)


@pytest.mark.parametrize(
    "reason",
    [
        "",
        "   ",
    ],
)
def test_empty_reason_is_rejected(reason):
    with pytest.raises(
        InvalidEvaluationError,
        match="reason must be a non-empty string",
    ):
        EvaluationResult(
            hypothesis_id="H001",
            observation_id="O001",
            outcome=EvaluationOutcome.CONFIRMED,
            score=1.0,
            reason=reason,
        )


def test_naive_datetime_is_rejected():
    with pytest.raises(
        InvalidEvaluationError,
        match="created_at must be timezone-aware",
    ):
        EvaluationResult(
            hypothesis_id="H001",
            observation_id="O001",
            outcome=EvaluationOutcome.CONFIRMED,
            score=1.0,
            reason="confirmed",
            created_at=datetime(2026, 1, 1),
        )


def test_invalid_datetime_is_rejected():
    with pytest.raises(
        InvalidEvaluationError,
        match="created_at must be a datetime",
    ):
        EvaluationResult(
            hypothesis_id="H001",
            observation_id="O001",
            outcome=EvaluationOutcome.CONFIRMED,
            score=1.0,
            reason="confirmed",
            created_at="2026-01-01",
        )


def test_invalid_metadata_is_rejected():
    with pytest.raises(
        InvalidEvaluationError,
        match="metadata must be a mapping",
    ):
        EvaluationResult(
            hypothesis_id="H001",
            observation_id="O001",
            outcome=EvaluationOutcome.CONFIRMED,
            score=1.0,
            reason="confirmed",
            metadata=["invalid"],
        )


# ==============================================================================
# Immutability
# ==============================================================================


def test_metadata_is_read_only():
    result = EvaluationResult(
        hypothesis_id="H001",
        observation_id="O001",
        outcome=EvaluationOutcome.CONFIRMED,
        score=1.0,
        reason="confirmed",
        metadata={"source": "synthetic"},
    )

    with pytest.raises(TypeError):
        result.metadata["source"] = "human"


def test_metadata_is_copied():
    metadata = {
        "source": "synthetic",
    }

    result = EvaluationResult(
        hypothesis_id="H001",
        observation_id="O001",
        outcome=EvaluationOutcome.CONFIRMED,
        score=1.0,
        reason="confirmed",
        metadata=metadata,
    )

    metadata["source"] = "changed"

    assert result.metadata["source"] == "synthetic"


def test_result_is_immutable():
    result = EvaluationResult(
        hypothesis_id="H001",
        observation_id="O001",
        outcome=EvaluationOutcome.CONFIRMED,
        score=1.0,
        reason="confirmed",
    )

    with pytest.raises(FrozenInstanceError):
        result.outcome = EvaluationOutcome.REFUTED


# ==============================================================================
# EvaluationResult query API
# ==============================================================================


def test_confirmed_is_positive():
    result = EvaluationResult(
        hypothesis_id="H001",
        observation_id="O001",
        outcome=EvaluationOutcome.CONFIRMED,
        score=1.0,
        reason="confirmed",
    )

    assert result.is_positive is True
    assert result.is_negative is False
    assert result.is_conclusive is True
    assert result.is_surprise is False


def test_refuted_is_negative():
    result = EvaluationResult(
        hypothesis_id="H001",
        observation_id="O001",
        outcome=EvaluationOutcome.REFUTED,
        score=0.0,
        reason="refuted",
    )

    assert result.is_positive is False
    assert result.is_negative is True
    assert result.is_conclusive is True
    assert result.is_surprise is False


def test_inconclusive_is_not_conclusive():
    result = EvaluationResult(
        hypothesis_id="H001",
        observation_id="O001",
        outcome=EvaluationOutcome.INCONCLUSIVE,
        score=0.5,
        reason="insufficient evidence",
    )

    assert result.is_positive is False
    assert result.is_negative is False
    assert result.is_conclusive is False
    assert result.is_surprise is False


def test_surprise_is_detected():
    result = EvaluationResult(
        hypothesis_id="H001",
        observation_id="O001",
        outcome=EvaluationOutcome.SURPRISE,
        score=0.0,
        reason="unexpected observation",
    )

    assert result.is_positive is False
    assert result.is_negative is False
    assert result.is_conclusive is False
    assert result.is_surprise is True


# ==============================================================================
# Evaluator construction
# ==============================================================================


def test_evaluator_creation():
    evaluator = Evaluator()

    assert isinstance(evaluator, Evaluator)


# ==============================================================================
# Evaluator behavior
# ==============================================================================


def test_evaluator_confirms_matching_values():
    evaluator = Evaluator()

    hypothesis = DummyHypothesis(
        id="H001",
        expected=True,
    )

    observation = DummyObservation(
        id="O001",
        value=True,
    )

    result = evaluator.evaluate(
        hypothesis,
        observation,
    )

    assert isinstance(result, EvaluationResult)
    assert result.hypothesis_id == "H001"
    assert result.observation_id == "O001"
    assert result.outcome is EvaluationOutcome.CONFIRMED
    assert result.score == 1.0


def test_evaluator_refutes_different_boolean_values():
    evaluator = Evaluator()

    hypothesis = DummyHypothesis(
        id="H001",
        expected=True,
    )

    observation = DummyObservation(
        id="O001",
        value=False,
    )

    result = evaluator.evaluate(
        hypothesis,
        observation,
    )

    assert result.outcome is EvaluationOutcome.REFUTED
    assert result.score == 0.0


def test_evaluator_refutes_different_numeric_values():
    evaluator = Evaluator()

    hypothesis = DummyHypothesis(
        id="H001",
        expected=10,
    )

    observation = DummyObservation(
        id="O001",
        value=11,
    )

    result = evaluator.evaluate(
        hypothesis,
        observation,
    )

    assert result.outcome is EvaluationOutcome.REFUTED
    assert result.score == 0.0


def test_evaluator_reports_surprise_for_different_types():
    evaluator = Evaluator()

    hypothesis = DummyHypothesis(
        id="H001",
        expected={"phase": "stable"},
    )

    observation = DummyObservation(
        id="O001",
        value=["unexpected"],
    )

    result = evaluator.evaluate(
        hypothesis,
        observation,
    )

    assert result.outcome is EvaluationOutcome.SURPRISE
    assert result.score == 0.0


# ==============================================================================
# Evaluator validation
# ==============================================================================


def test_evaluator_rejects_hypothesis_without_id():
    evaluator = Evaluator()

    hypothesis = DummyHypothesis()
    hypothesis.id = ""

    observation = DummyObservation()

    with pytest.raises(
        InvalidEvaluationError,
        match="hypothesis must provide a non-empty string id",
    ):
        evaluator.evaluate(
            hypothesis,
            observation,
        )


def test_evaluator_rejects_observation_without_id():
    evaluator = Evaluator()

    hypothesis = DummyHypothesis()

    observation = DummyObservation()
    observation.id = ""

    with pytest.raises(
        InvalidEvaluationError,
        match="observation must provide a non-empty string id",
    ):
        evaluator.evaluate(
            hypothesis,
            observation,
        )


def test_evaluator_rejects_hypothesis_without_expected_value():
    evaluator = Evaluator()

    class InvalidHypothesis:
        id = "H001"

    observation = DummyObservation()

    with pytest.raises(
        InvalidEvaluationError,
        match="hypothesis must provide expected value",
    ):
        evaluator.evaluate(
            InvalidHypothesis(),
            observation,
        )


def test_evaluator_rejects_observation_without_value():
    evaluator = Evaluator()

    hypothesis = DummyHypothesis()

    class InvalidObservation:
        id = "O001"

    with pytest.raises(
        InvalidEvaluationError,
        match="observation must provide observed value",
    ):
        evaluator.evaluate(
            hypothesis,
            InvalidObservation(),
        )


# ==============================================================================
# Mapping compatibility
# ==============================================================================


def test_evaluator_accepts_mapping_hypothesis():
    evaluator = Evaluator()

    hypothesis = {
        "id": "H001",
        "expected": True,
    }

    observation = DummyObservation(
        id="O001",
        value=True,
    )

    result = evaluator.evaluate(
        hypothesis,
        observation,
    )

    assert result.outcome is EvaluationOutcome.CONFIRMED


def test_evaluator_accepts_mapping_observation():
    evaluator = Evaluator()

    hypothesis = DummyHypothesis(
        id="H001",
        expected=True,
    )

    observation = {
        "id": "O001",
        "value": True,
    }

    result = evaluator.evaluate(
        hypothesis,
        observation,
    )

    assert result.outcome is EvaluationOutcome.CONFIRMED


def test_evaluator_accepts_world_result_style_values():
    evaluator = Evaluator()

    hypothesis = DummyHypothesis(
        id="H001",
        expected=True,
    )

    observation = {
        "id": "O001",
        "values": {
            "response": True,
        },
    }

    result = evaluator.evaluate(
        hypothesis,
        observation,
    )

    assert result.outcome is EvaluationOutcome.CONFIRMED


# ==============================================================================
# Determinism
# ==============================================================================


def test_evaluator_is_deterministic():
    evaluator = Evaluator()

    hypothesis = DummyHypothesis(
        id="H001",
        expected=True,
    )

    observation = DummyObservation(
        id="O001",
        value=True,
    )

    result_1 = evaluator.evaluate(
        hypothesis,
        observation,
    )

    result_2 = evaluator.evaluate(
        hypothesis,
        observation,
    )

    assert result_1.hypothesis_id == result_2.hypothesis_id
    assert result_1.observation_id == result_2.observation_id
    assert result_1.outcome is result_2.outcome
    assert result_1.score == result_2.score
    assert result_1.reason == result_2.reason


# ==============================================================================
# Input immutability
# ==============================================================================


def test_evaluator_does_not_mutate_hypothesis():
    evaluator = Evaluator()

    hypothesis = DummyHypothesis(
        id="H001",
        expected=True,
    )

    observation = DummyObservation(
        id="O001",
        value=True,
    )

    before = (
        hypothesis.id,
        hypothesis.expected,
    )

    evaluator.evaluate(
        hypothesis,
        observation,
    )

    after = (
        hypothesis.id,
        hypothesis.expected,
    )

    assert after == before


def test_evaluator_does_not_mutate_observation():
    evaluator = Evaluator()

    hypothesis = DummyHypothesis(
        id="H001",
        expected=True,
    )

    observation = DummyObservation(
        id="O001",
        value=True,
    )

    before = (
        observation.id,
        observation.value,
    )

    evaluator.evaluate(
        hypothesis,
        observation,
    )

    after = (
        observation.id,
        observation.value,
    )

    assert after == before