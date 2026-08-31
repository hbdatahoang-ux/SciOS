# ==============================================================================
# SciOS Runtime Science
# Synthetic World Rules Tests
# ==============================================================================

from __future__ import annotations

import pytest

from scios.runtime.science.synthetic_world.models import (
    WorldResult,
    WorldState,
)
from scios.runtime.science.synthetic_world.rules import (
    ThresholdRule,
    WorldRule,
)


# ==============================================================================
# Helpers
# ==============================================================================


class DummyState(WorldState):
    """Minimal state used for rule tests."""


# ==============================================================================
# WorldRule contract
# ==============================================================================


def test_world_rule_is_abstract():
    assert WorldRule.__abstractmethods__ == {"apply"}


def test_world_rule_cannot_be_instantiated():
    with pytest.raises(TypeError):
        WorldRule()


# ==============================================================================
# ThresholdRule construction
# ==============================================================================


def test_threshold_rule_creation():
    rule = ThresholdRule(
        parameter="temperature",
        threshold=25.0,
    )

    assert rule.parameter == "temperature"
    assert rule.threshold == 25.0
    assert rule.output == "response"


def test_threshold_rule_custom_output():
    rule = ThresholdRule(
        parameter="temperature",
        threshold=25.0,
        output="phase_transition",
    )

    assert rule.output == "phase_transition"


# ==============================================================================
# Threshold behavior
# ==============================================================================


def test_threshold_rule_returns_true_above_threshold():
    rule = ThresholdRule(
        parameter="x",
        threshold=10.0,
    )

    state = WorldState()
    result = rule.apply(
        state,
        {"x": 11.0},
    )

    assert isinstance(result, WorldResult)
    assert result.values["response"] is True
    assert result.values["input"] == 11.0
    assert result.values["threshold"] == 10.0


def test_threshold_rule_returns_true_at_threshold():
    rule = ThresholdRule(
        parameter="x",
        threshold=10.0,
    )

    state = WorldState()
    result = rule.apply(
        state,
        {"x": 10.0},
    )

    assert result.values["response"] is True


def test_threshold_rule_returns_false_below_threshold():
    rule = ThresholdRule(
        parameter="x",
        threshold=10.0,
    )

    state = WorldState()
    result = rule.apply(
        state,
        {"x": 9.99},
    )

    assert result.values["response"] is False


# ==============================================================================
# Custom output
# ==============================================================================


def test_threshold_rule_uses_custom_output_key():
    rule = ThresholdRule(
        parameter="temperature",
        threshold=25.0,
        output="hot",
    )

    result = rule.apply(
        WorldState(),
        {"temperature": 30.0},
    )

    assert result.values["hot"] is True
    assert "response" not in result.values


def test_threshold_rule_custom_output_below_threshold():
    rule = ThresholdRule(
        parameter="temperature",
        threshold=25.0,
        output="hot",
    )

    result = rule.apply(
        WorldState(),
        {"temperature": 20.0},
    )

    assert result.values["hot"] is False
    assert "response" not in result.values


# ==============================================================================
# State preservation
# ==============================================================================


def test_threshold_rule_preserves_state():
    state = WorldState()

    rule = ThresholdRule(
        parameter="x",
        threshold=1.0,
    )

    result = rule.apply(
        state,
        {"x": 2.0},
    )

    assert result.state is state


# ==============================================================================
# Parameter validation
# ==============================================================================


def test_missing_parameter_is_rejected():
    rule = ThresholdRule(
        parameter="x",
        threshold=1.0,
    )

    with pytest.raises(
        ValueError,
        match="parameter 'x' must be numeric",
    ):
        rule.apply(
            WorldState(),
            {},
        )


@pytest.mark.parametrize(
    "value",
    [
        None,
        "10",
        [],
        {},
        object(),
    ],
)
def test_non_numeric_parameter_is_rejected(value):
    rule = ThresholdRule(
        parameter="x",
        threshold=1.0,
    )

    with pytest.raises(
        ValueError,
        match="parameter 'x' must be numeric",
    ):
        rule.apply(
            WorldState(),
            {"x": value},
        )


# ==============================================================================
# Numeric semantics
# ==============================================================================


@pytest.mark.parametrize(
    "value, expected",
    [
        (-1, False),
        (0, False),
        (1, False),
        (9.999, False),
        (10, True),
        (10.0, True),
        (11, True),
    ],
)
def test_threshold_rule_numeric_semantics(value, expected):
    rule = ThresholdRule(
        parameter="x",
        threshold=10.0,
    )

    result = rule.apply(
        WorldState(),
        {"x": value},
    )

    assert result.values["response"] is expected


# ==============================================================================
# Result contract
# ==============================================================================


def test_threshold_rule_result_contains_input():
    rule = ThresholdRule(
        parameter="q",
        threshold=5.0,
    )

    result = rule.apply(
        WorldState(),
        {"q": 7.0},
    )

    assert result.values["input"] == 7.0


def test_threshold_rule_result_contains_threshold():
    rule = ThresholdRule(
        parameter="q",
        threshold=5.0,
    )

    result = rule.apply(
        WorldState(),
        {"q": 7.0},
    )

    assert result.values["threshold"] == 5.0


def test_threshold_rule_result_contains_only_expected_keys():
    rule = ThresholdRule(
        parameter="q",
        threshold=5.0,
    )

    result = rule.apply(
        WorldState(),
        {"q": 7.0},
    )

    assert set(result.values) == {
        "response",
        "input",
        "threshold",
    }


def test_threshold_rule_result_is_world_result():
    rule = ThresholdRule(
        parameter="q",
        threshold=5.0,
    )

    result = rule.apply(
        WorldState(),
        {"q": 7.0},
    )

    assert isinstance(result, WorldResult)


# ==============================================================================
# Determinism
# ==============================================================================


def test_threshold_rule_is_deterministic():
    rule = ThresholdRule(
        parameter="x",
        threshold=5.0,
    )

    state = WorldState()
    parameters = {"x": 7.5}

    result_1 = rule.apply(
        state,
        parameters,
    )

    result_2 = rule.apply(
        state,
        parameters,
    )

    assert result_1.values == result_2.values
    assert result_1.state is result_2.state