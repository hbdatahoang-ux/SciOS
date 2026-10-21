# ==============================================================================
# SciOS Runtime Science
# Experiment Model Tests
# ==============================================================================

from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

from scios.runtime.science.experiment.models import (
    Experiment,
    InvalidExperimentError,
    Observation,
    Outcome,
)


# ==============================================================================
# Outcome
# ==============================================================================


def test_outcome_values():
    assert Outcome.PENDING.value == "pending"
    assert Outcome.CONFIRMED.value == "confirmed"
    assert Outcome.REFUTED.value == "refuted"
    assert Outcome.INCONCLUSIVE.value == "inconclusive"
    assert Outcome.SURPRISE.value == "surprise"


def test_outcome_is_string_compatible():
    assert isinstance(Outcome.CONFIRMED, str)
    assert Outcome.CONFIRMED == "confirmed"


# ==============================================================================
# Experiment
# ==============================================================================


def test_experiment_creation():
    experiment = Experiment(
        id="E001",
        hypothesis_id="H001",
    )

    assert experiment.id == "E001"
    assert experiment.hypothesis_id == "H001"
    assert experiment.parameters == {}
    assert experiment.metadata == {}
    assert experiment.created_at.tzinfo is not None


def test_experiment_parameters_are_preserved():
    experiment = Experiment(
        id="E001",
        hypothesis_id="H001",
        parameters={
            "flow_rate": 10.0,
            "temperature": 25.0,
        },
    )

    assert experiment.parameters["flow_rate"] == 10.0
    assert experiment.parameters["temperature"] == 25.0
    assert experiment.parameter_count == 2


def test_experiment_metadata_is_preserved():
    experiment = Experiment(
        id="E001",
        hypothesis_id="H001",
        metadata={
            "source": "synthetic",
            "operator": "human",
        },
    )

    assert experiment.metadata["source"] == "synthetic"
    assert experiment.metadata["operator"] == "human"


def test_experiment_created_at_is_timezone_aware():
    experiment = Experiment(
        id="E001",
        hypothesis_id="H001",
    )

    assert experiment.created_at.utcoffset() is not None


def test_experiment_accepts_explicit_timezone_aware_datetime():
    timestamp = datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    )

    experiment = Experiment(
        id="E001",
        hypothesis_id="H001",
        created_at=timestamp,
    )

    assert experiment.created_at == timestamp


def test_experiment_naive_datetime_is_rejected():
    with pytest.raises(InvalidExperimentError):
        Experiment(
            id="E001",
            hypothesis_id="H001",
            created_at=datetime(2026, 1, 1),
        )


def test_experiment_empty_id_is_rejected():
    with pytest.raises(InvalidExperimentError):
        Experiment(
            id="",
            hypothesis_id="H001",
        )


def test_experiment_whitespace_id_is_rejected():
    with pytest.raises(InvalidExperimentError):
        Experiment(
            id="   ",
            hypothesis_id="H001",
        )


def test_experiment_empty_hypothesis_id_is_rejected():
    with pytest.raises(InvalidExperimentError):
        Experiment(
            id="E001",
            hypothesis_id="",
        )


def test_experiment_whitespace_hypothesis_id_is_rejected():
    with pytest.raises(InvalidExperimentError):
        Experiment(
            id="E001",
            hypothesis_id="   ",
        )


def test_experiment_parameters_must_be_mapping():
    with pytest.raises(InvalidExperimentError):
        Experiment(
            id="E001",
            hypothesis_id="H001",
            parameters=["invalid"],
        )


def test_experiment_metadata_must_be_mapping():
    with pytest.raises(InvalidExperimentError):
        Experiment(
            id="E001",
            hypothesis_id="H001",
            metadata=["invalid"],
        )


def test_experiment_parameters_are_read_only():
    experiment = Experiment(
        id="E001",
        hypothesis_id="H001",
        parameters={"flow_rate": 10.0},
    )

    with pytest.raises(TypeError):
        experiment.parameters["flow_rate"] = 20.0


def test_experiment_metadata_is_read_only():
    experiment = Experiment(
        id="E001",
        hypothesis_id="H001",
        metadata={"source": "human"},
    )

    with pytest.raises(TypeError):
        experiment.metadata["source"] = "ai"


def test_experiment_parameters_are_copied():
    parameters = {
        "flow_rate": 10.0,
    }

    experiment = Experiment(
        id="E001",
        hypothesis_id="H001",
        parameters=parameters,
    )

    parameters["flow_rate"] = 99.0

    assert experiment.parameters["flow_rate"] == 10.0


def test_experiment_metadata_is_copied():
    metadata = {
        "source": "human",
    }

    experiment = Experiment(
        id="E001",
        hypothesis_id="H001",
        metadata=metadata,
    )

    metadata["source"] = "ai"

    assert experiment.metadata["source"] == "human"


def test_experiment_is_immutable():
    experiment = Experiment(
        id="E001",
        hypothesis_id="H001",
    )

    with pytest.raises(FrozenInstanceError):
        experiment.id = "E002"


# ==============================================================================
# Observation
# ==============================================================================


def test_observation_creation():
    observation = Observation(
        id="O001",
        experiment_id="E001",
        values={
            "oscillation_period": 42.7,
            "amplitude": 0.81,
        },
    )

    assert observation.id == "O001"
    assert observation.experiment_id == "E001"
    assert observation.values["oscillation_period"] == 42.7
    assert observation.values["amplitude"] == 0.81
    assert observation.metadata == {}
    assert observation.observed_at.tzinfo is not None


def test_observation_value_count():
    observation = Observation(
        id="O001",
        experiment_id="E001",
        values={
            "x": 1,
            "y": 2,
            "z": 3,
        },
    )

    assert observation.value_count == 3


def test_observation_observed_at_is_timezone_aware():
    observation = Observation(
        id="O001",
        experiment_id="E001",
        values={},
    )

    assert observation.observed_at.utcoffset() is not None


def test_observation_accepts_explicit_timezone_aware_datetime():
    timestamp = datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    )

    observation = Observation(
        id="O001",
        experiment_id="E001",
        values={},
        observed_at=timestamp,
    )

    assert observation.observed_at == timestamp


def test_observation_naive_datetime_is_rejected():
    with pytest.raises(InvalidExperimentError):
        Observation(
            id="O001",
            experiment_id="E001",
            values={},
            observed_at=datetime(2026, 1, 1),
        )


def test_observation_empty_id_is_rejected():
    with pytest.raises(InvalidExperimentError):
        Observation(
            id="",
            experiment_id="E001",
            values={},
        )


def test_observation_whitespace_id_is_rejected():
    with pytest.raises(InvalidExperimentError):
        Observation(
            id="   ",
            experiment_id="E001",
            values={},
        )


def test_observation_empty_experiment_id_is_rejected():
    with pytest.raises(InvalidExperimentError):
        Observation(
            id="O001",
            experiment_id="",
            values={},
        )


def test_observation_whitespace_experiment_id_is_rejected():
    with pytest.raises(InvalidExperimentError):
        Observation(
            id="O001",
            experiment_id="   ",
            values={},
        )


def test_observation_values_must_be_mapping():
    with pytest.raises(InvalidExperimentError):
        Observation(
            id="O001",
            experiment_id="E001",
            values=["invalid"],
        )


def test_observation_metadata_must_be_mapping():
    with pytest.raises(InvalidExperimentError):
        Observation(
            id="O001",
            experiment_id="E001",
            values={},
            metadata=["invalid"],
        )


def test_observation_values_are_read_only():
    observation = Observation(
        id="O001",
        experiment_id="E001",
        values={
            "temperature": 25.0,
        },
    )

    with pytest.raises(TypeError):
        observation.values["temperature"] = 30.0


def test_observation_metadata_is_read_only():
    observation = Observation(
        id="O001",
        experiment_id="E001",
        values={},
        metadata={
            "instrument": "sensor-01",
        },
    )

    with pytest.raises(TypeError):
        observation.metadata["instrument"] = "sensor-02"


def test_observation_values_are_copied():
    values = {
        "temperature": 25.0,
    }

    observation = Observation(
        id="O001",
        experiment_id="E001",
        values=values,
    )

    values["temperature"] = 99.0

    assert observation.values["temperature"] == 25.0


def test_observation_metadata_is_copied():
    metadata = {
        "instrument": "sensor-01",
    }

    observation = Observation(
        id="O001",
        experiment_id="E001",
        values={},
        metadata=metadata,
    )

    metadata["instrument"] = "sensor-02"

    assert observation.metadata["instrument"] == "sensor-01"


def test_observation_is_immutable():
    observation = Observation(
        id="O001",
        experiment_id="E001",
        values={},
    )

    with pytest.raises(FrozenInstanceError):
        observation.id = "O002"


# ==============================================================================
# Semantic separation
# ==============================================================================


def test_experiment_does_not_contain_observation():
    experiment = Experiment(
        id="E001",
        hypothesis_id="H001",
        parameters={
            "temperature": 25.0,
        },
    )

    assert not hasattr(experiment, "observation")
    assert not hasattr(experiment, "outcome")


def test_observation_does_not_contain_outcome():
    observation = Observation(
        id="O001",
        experiment_id="E001",
        values={
            "result": 42.0,
        },
    )

    assert not hasattr(observation, "outcome")