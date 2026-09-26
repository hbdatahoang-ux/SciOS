# ==============================================================================
# SciOS Runtime Science
# Synthetic World Tests
# ==============================================================================

from datetime import datetime, timezone
from types import MappingProxyType

import pytest

from scios.runtime.science.experiment.models import (
    Experiment,
    Observation,
)

from scios.runtime.science.synthetic_world.models import (
    InvalidSyntheticWorldError,
    WorldResult,
    WorldState,
)


# ==============================================================================
# Helpers
# ==============================================================================


def utc_datetime() -> datetime:
    return datetime(2026, 1, 1, tzinfo=timezone.utc)


def make_experiment(
    experiment_id: str = "E001",
    parameters: dict | None = None,
) -> Experiment:
    return Experiment(
        id=experiment_id,
        hypothesis_id="H001",
        parameters=parameters or {},
    )


# ==============================================================================
# WorldState
# ==============================================================================


def test_world_state_creation():
    state = WorldState(
        values={"temperature": 25.0},
        timestamp=utc_datetime(),
    )

    assert state.values["temperature"] == 25.0
    assert state.timestamp == utc_datetime()


def test_world_state_default_values():
    state = WorldState()

    assert state.values == {}
    assert isinstance(state.values, MappingProxyType)
    assert state.timestamp.tzinfo is not None


def test_world_state_timestamp_is_timezone_aware():
    state = WorldState()

    assert state.timestamp.utcoffset() is not None


def test_world_state_naive_timestamp_is_rejected():
    with pytest.raises(InvalidSyntheticWorldError):
        WorldState(
            timestamp=datetime(2026, 1, 1),
        )


def test_world_state_invalid_values_are_rejected():
    with pytest.raises(InvalidSyntheticWorldError):
        WorldState(values=["invalid"])


def test_world_state_invalid_timestamp_type_is_rejected():
    with pytest.raises(InvalidSyntheticWorldError):
        WorldState(timestamp="invalid")


def test_world_state_values_are_read_only():
    state = WorldState(
        values={"temperature": 25.0},
    )

    with pytest.raises(TypeError):
        state.values["temperature"] = 30.0


def test_world_state_is_immutable():
    state = WorldState(
        values={"temperature": 25.0},
    )

    with pytest.raises(AttributeError):
        state.values = {}


def test_world_state_get():
    state = WorldState(
        values={"temperature": 25.0},
    )

    assert state.get("temperature") == 25.0
    assert state.get("missing") is None
    assert state.get("missing", 42) == 42


# ==============================================================================
# WorldResult
# ==============================================================================


def test_world_result_creation():
    state = WorldState(
        values={"x": 1},
        timestamp=utc_datetime(),
    )

    result = WorldResult(
        values={"response": True},
        state=state,
    )

    assert result.values["response"] is True
    assert result.state is state


def test_world_result_values_are_read_only():
    state = WorldState()

    result = WorldResult(
        values={"response": True},
        state=state,
    )

    with pytest.raises(TypeError):
        result.values["response"] = False


def test_world_result_values_are_mapping():
    result = WorldResult(
        values={"response": True},
        state=WorldState(),
    )

    assert isinstance(result.values, MappingProxyType)


def test_world_result_invalid_values_are_rejected():
    with pytest.raises(InvalidSyntheticWorldError):
        WorldResult(
            values=["invalid"],
            state=WorldState(),
        )


def test_world_result_invalid_state_is_rejected():
    with pytest.raises(InvalidSyntheticWorldError):
        WorldResult(
            values={},
            state="invalid",
        )


def test_world_result_is_immutable():
    result = WorldResult(
        values={"response": True},
        state=WorldState(),
    )

    with pytest.raises(AttributeError):
        result.values = {}


# ==============================================================================
# Scientific Boundary
# ==============================================================================


def test_world_state_contains_state_only():
    state = WorldState(
        values={"temperature": 25.0},
    )

    assert "outcome" not in state.values
    assert "knowledge" not in state.values
    assert "surprise" not in state.values


def test_world_result_does_not_define_scientific_outcome():
    result = WorldResult(
        values={"response": True},
        state=WorldState(),
    )

    assert "outcome" not in result.values


def test_world_result_does_not_create_knowledge():
    result = WorldResult(
        values={"response": True},
        state=WorldState(),
    )

    assert "knowledge" not in result.values


def test_world_result_does_not_classify_surprise():
    result = WorldResult(
        values={"response": True},
        state=WorldState(),
    )

    assert "surprise" not in result.values


# ==============================================================================
# Compatibility with Experiment / Observation
# ==============================================================================


def test_experiment_can_be_used_as_world_input():
    experiment = make_experiment(
        parameters={"temperature": 25.0},
    )

    assert isinstance(experiment, Experiment)
    assert experiment.parameters["temperature"] == 25.0


def test_observation_can_represent_world_output():
    experiment = make_experiment()

    observation = Observation(
        id="O001",
        experiment_id=experiment.id,
        values={"response": True},
    )

    assert isinstance(observation, Observation)
    assert observation.experiment_id == experiment.id
    assert observation.values["response"] is True


# ==============================================================================
# Deterministic Semantics
# ==============================================================================


def test_same_world_state_can_produce_same_result():
    state = WorldState(
        values={"x": 10},
        timestamp=utc_datetime(),
    )

    result_a = WorldResult(
        values={"response": 20},
        state=state,
    )

    result_b = WorldResult(
        values={"response": 20},
        state=state,
    )

    assert result_a.values == result_b.values
    assert result_a.state == result_b.state


def test_world_result_preserves_world_state_reference():
    state = WorldState(
        values={"x": 10},
    )

    result = WorldResult(
        values={"response": 20},
        state=state,
    )

    assert result.state is state


# ==============================================================================
# No Hidden Mutation
# ==============================================================================


def test_world_state_copies_input_mapping():
    source = {"temperature": 25.0}

    state = WorldState(values=source)

    source["temperature"] = 100.0

    assert state.values["temperature"] == 25.0


def test_world_result_copies_input_mapping():
    source = {"response": True}

    result = WorldResult(
        values=source,
        state=WorldState(),
    )

    source["response"] = False

    assert result.values["response"] is True