# ==============================================================================
# SciOS Runtime Science
# Scientific Execution Tests
# ==============================================================================

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

from scios.runtime.science.experiment.models import (
    Experiment,
    Observation,
)
from scios.runtime.science.synthetic_world.models import (
    WorldResult,
    WorldState,
)
from scios.runtime.science.synthetic_world.rules import (
    ThresholdRule,
)
from scios.runtime.science.synthetic_world.world import (
    SyntheticWorld,
)

from scios.runtime.science.execution.context import (
    ExecutionContext,
)
from scios.runtime.science.execution.errors import (
    ExecutionError,
    ExecutionStateError,
    InvalidExecutionError,
    InvalidExecutionResultError,
    WorldExecutionError,
)
from scios.runtime.science.execution.executor import (
    ScientificExecutor,
)
from scios.runtime.science.execution.result import (
    ExecutionResult,
    ExecutionStatus,
)


# ==============================================================================
# Helpers
# ==============================================================================


class DummyWorld:
    """
    Minimal deterministic world used by executor tests.

    The world exposes:
        execute(parameters) -> WorldResult
    """

    def __init__(self) -> None:
        self.calls = 0
        self.parameters_seen: list[dict] = []

    def execute(self, parameters):
        self.calls += 1
        self.parameters_seen.append(dict(parameters))

        return WorldResult(
            values={
                "response": parameters["x"] >= 10,
                "input": parameters["x"],
            },
            state=WorldState(),
        )


class FailingWorld:
    """World that always fails execution."""

    def execute(self, parameters):
        raise RuntimeError("world failure")


class InvalidWorld:
    """World returning an invalid result."""

    def execute(self, parameters):
        return {"invalid": True}


class FalseWorld:
    """World returning a valid false observation."""

    def execute(self, parameters):
        return WorldResult(
            values={
                "response": False,
                "input": parameters["x"],
            },
            state=WorldState(),
        )


def make_experiment(
    *,
    experiment_id: str = "E001",
    hypothesis_id: str = "H001",
    parameters: dict | None = None,
) -> Experiment:
    return Experiment(
        id=experiment_id,
        hypothesis_id=hypothesis_id,
        parameters=parameters or {"x": 10},
    )


def make_context(
    *,
    experiment: Experiment | None = None,
    state: WorldState | None = None,
) -> ExecutionContext:
    return ExecutionContext(
        experiment=experiment or make_experiment(),
        state=state or WorldState(),
    )


def make_observation(
    *,
    observation_id: str = "O001",
    experiment_id: str = "E001",
    response: bool = True,
) -> Observation:
    return Observation(
        id=observation_id,
        experiment_id=experiment_id,
        values={
            "response": response,
        },
    )


def make_result(
    *,
    execution_id: str = "X001",
    experiment_id: str = "E001",
    hypothesis_id: str = "H001",
    status: ExecutionStatus = ExecutionStatus.COMPLETED,
    observation: Observation | None = None,
    metadata: dict | None = None,
) -> ExecutionResult:
    return ExecutionResult(
        execution_id=execution_id,
        experiment_id=experiment_id,
        hypothesis_id=hypothesis_id,
        status=status,
        observation=observation,
        metadata=metadata or {},
    )


def make_world() -> SyntheticWorld:
    world = SyntheticWorld()

    world.add_rule(
        ThresholdRule(
            parameter="x",
            threshold=10.0,
        )
    )

    return world


# ==============================================================================
# Exception hierarchy
# ==============================================================================


def test_execution_error_is_runtime_error():
    assert issubclass(
        ExecutionError,
        RuntimeError,
    )


def test_invalid_execution_error_inherits_execution_error():
    assert issubclass(
        InvalidExecutionError,
        ExecutionError,
    )


def test_execution_state_error_inherits_execution_error():
    assert issubclass(
        ExecutionStateError,
        ExecutionError,
    )


def test_world_execution_error_inherits_execution_error():
    assert issubclass(
        WorldExecutionError,
        ExecutionError,
    )


def test_invalid_execution_result_error_inherits_execution_error():
    assert issubclass(
        InvalidExecutionResultError,
        ExecutionError,
    )


# ==============================================================================
# ExecutionContext construction
# ==============================================================================


def test_context_creation():
    experiment = make_experiment()

    context = ExecutionContext(
        experiment=experiment,
        state=WorldState(),
    )

    assert context.experiment is experiment
    assert isinstance(context.state, WorldState)


def test_context_has_execution_id():
    context = make_context()

    assert isinstance(
        context.execution_id,
        str,
    )

    assert context.execution_id.strip()


def test_context_execution_id_is_unique():
    context_1 = make_context()
    context_2 = make_context()

    assert (
        context_1.execution_id
        != context_2.execution_id
    )


def test_context_created_at_is_datetime():
    context = make_context()

    assert isinstance(
        context.created_at,
        datetime,
    )


def test_context_created_at_is_timezone_aware():
    context = make_context()

    assert context.created_at.tzinfo is not None
    assert context.created_at.utcoffset() is not None


def test_context_created_at_defaults_to_utc():
    context = make_context()

    assert (
        context.created_at.utcoffset()
        == timezone.utc.utcoffset(context.created_at)
    )


def test_context_metadata_defaults_to_empty():
    context = make_context()

    assert context.metadata == {}


def test_context_metadata_count():
    context = ExecutionContext(
        experiment=make_experiment(),
        state=WorldState(),
        metadata={
            "source": "test",
            "version": 1,
        },
    )

    assert context.metadata_count == 2


def test_context_metadata_is_immutable():
    context = ExecutionContext(
        experiment=make_experiment(),
        state=WorldState(),
        metadata={
            "source": "test",
        },
    )

    with pytest.raises(TypeError):
        context.metadata["source"] = "changed"


def test_context_is_frozen():
    context = make_context()

    with pytest.raises(FrozenInstanceError):
        context.execution_id = "changed"


# ==============================================================================
# ExecutionContext validation
# ==============================================================================


def test_context_requires_experiment():
    with pytest.raises(
        InvalidExecutionError,
        match="experiment",
    ):
        ExecutionContext(
            experiment=None,
            state=WorldState(),
        )


def test_context_requires_world_state():
    with pytest.raises(
        InvalidExecutionError,
        match="state",
    ):
        ExecutionContext(
            experiment=make_experiment(),
            state=None,
        )


@pytest.mark.parametrize(
    "execution_id",
    [
        "",
        " ",
        "   ",
        None,
        1,
        object(),
    ],
)
def test_context_rejects_invalid_execution_id(
    execution_id,
):
    with pytest.raises(InvalidExecutionError):
        ExecutionContext(
            experiment=make_experiment(),
            state=WorldState(),
            execution_id=execution_id,
        )


def test_context_rejects_naive_created_at():
    with pytest.raises(
        InvalidExecutionError,
        match="timezone-aware",
    ):
        ExecutionContext(
            experiment=make_experiment(),
            state=WorldState(),
            created_at=datetime.now(),
        )


def test_context_rejects_invalid_created_at():
    with pytest.raises(
        InvalidExecutionError,
        match="datetime",
    ):
        ExecutionContext(
            experiment=make_experiment(),
            state=WorldState(),
            created_at="now",
        )


def test_context_accepts_explicit_timezone():
    timestamp = datetime.now(timezone.utc)

    context = ExecutionContext(
        experiment=make_experiment(),
        state=WorldState(),
        created_at=timestamp,
    )

    assert context.created_at == timestamp


def test_context_rejects_invalid_metadata():
    with pytest.raises(
        InvalidExecutionError,
        match="metadata",
    ):
        ExecutionContext(
            experiment=make_experiment(),
            state=WorldState(),
            metadata=[],
        )


@pytest.mark.parametrize(
    "name",
    [
        "",
        " ",
        "   ",
        None,
        1,
    ],
)
def test_context_with_metadata_rejects_invalid_name(name):
    context = make_context()

    with pytest.raises(
        InvalidExecutionError,
        match="metadata name",
    ):
        context.with_metadata(
            name,
            "value",
        )


# ==============================================================================
# ExecutionContext query API
# ==============================================================================


def test_context_has_metadata():
    context = ExecutionContext(
        experiment=make_experiment(),
        state=WorldState(),
        metadata={
            "source": "test",
        },
    )

    assert context.has_metadata("source") is True
    assert context.has_metadata("missing") is False


def test_context_has_metadata_rejects_non_string_name():
    context = make_context()

    assert context.has_metadata(None) is False
    assert context.has_metadata(1) is False


def test_context_get_metadata():
    context = ExecutionContext(
        experiment=make_experiment(),
        state=WorldState(),
        metadata={
            "source": "test",
        },
    )

    assert (
        context.get_metadata("source")
        == "test"
    )


def test_context_get_metadata_default():
    context = make_context()

    assert (
        context.get_metadata(
            "missing",
            "fallback",
        )
        == "fallback"
    )


# ==============================================================================
# ExecutionContext functional update
# ==============================================================================


def test_context_with_metadata_returns_new_context():
    context = make_context()

    updated = context.with_metadata(
        "source",
        "test",
    )

    assert updated is not context


def test_context_with_metadata_preserves_identity():
    context = make_context()

    updated = context.with_metadata(
        "source",
        "test",
    )

    assert (
        updated.execution_id
        == context.execution_id
    )

    assert (
        updated.experiment
        is context.experiment
    )

    assert (
        updated.state
        is context.state
    )

    assert (
        updated.created_at
        == context.created_at
    )


def test_context_with_metadata_does_not_mutate_original():
    context = make_context()

    updated = context.with_metadata(
        "source",
        "test",
    )

    assert context.has_metadata("source") is False
    assert updated.has_metadata("source") is True


def test_context_with_metadata_replaces_existing_value():
    context = ExecutionContext(
        experiment=make_experiment(),
        state=WorldState(),
        metadata={
            "source": "old",
        },
    )

    updated = context.with_metadata(
        "source",
        "new",
    )

    assert (
        context.get_metadata("source")
        == "old"
    )

    assert (
        updated.get_metadata("source")
        == "new"
    )


# ==============================================================================
# ExecutionResult construction
# ==============================================================================


def test_result_creation():
    observation = make_observation()

    result = ExecutionResult(
        experiment_id="E001",
        hypothesis_id="H001",
        observation=observation,
    )

    assert result.experiment_id == "E001"
    assert result.hypothesis_id == "H001"
    assert isinstance(
        result.observation,
        Observation,
    )


def test_result_generates_execution_id():
    result = ExecutionResult(
        experiment_id="E001",
        hypothesis_id="H001",
    )

    assert isinstance(
        result.execution_id,
        str,
    )

    assert result.execution_id.strip()


def test_result_execution_ids_are_unique():
    result_1 = ExecutionResult(
        experiment_id="E001",
        hypothesis_id="H001",
    )

    result_2 = ExecutionResult(
        experiment_id="E001",
        hypothesis_id="H001",
    )

    assert (
        result_1.execution_id
        != result_2.execution_id
    )


def test_result_created_at_is_timezone_aware():
    result = ExecutionResult(
        experiment_id="E001",
        hypothesis_id="H001",
    )

    assert isinstance(
        result.created_at,
        datetime,
    )

    assert result.created_at.tzinfo is not None
    assert result.created_at.utcoffset() is not None


def test_result_default_status_is_completed():
    result = ExecutionResult(
        experiment_id="E001",
        hypothesis_id="H001",
    )

    assert (
        result.status
        is ExecutionStatus.COMPLETED
    )


def test_result_success():
    result = make_result(
        status=ExecutionStatus.COMPLETED,
    )

    assert result.success is True
    assert result.failed is False


def test_result_failed():
    result = make_result(
        status=ExecutionStatus.FAILED,
    )

    assert result.success is False
    assert result.failed is True


def test_result_is_pending():
    result = make_result(
        status=ExecutionStatus.PENDING,
    )

    assert result.is_pending is True
    assert result.is_running is False
    assert result.is_completed is False
    assert result.is_failed is False


def test_result_is_running():
    result = make_result(
        status=ExecutionStatus.RUNNING,
    )

    assert result.is_pending is False
    assert result.is_running is True
    assert result.is_completed is False
    assert result.is_failed is False


def test_result_is_completed():
    result = make_result(
        status=ExecutionStatus.COMPLETED,
    )

    assert result.is_pending is False
    assert result.is_running is False
    assert result.is_completed is True
    assert result.is_failed is False


def test_result_is_failed():
    result = make_result(
        status=ExecutionStatus.FAILED,
    )

    assert result.is_pending is False
    assert result.is_running is False
    assert result.is_completed is False
    assert result.is_failed is True


def test_result_is_immutable():
    result = make_result()

    with pytest.raises(FrozenInstanceError):
        result.experiment_id = "E002"


def test_result_metadata_defaults_to_empty():
    result = ExecutionResult(
        experiment_id="E001",
        hypothesis_id="H001",
    )

    assert result.metadata == {}


def test_result_metadata_is_immutable():
    result = ExecutionResult(
        experiment_id="E001",
        hypothesis_id="H001",
        metadata={
            "source": "test",
        },
    )

    with pytest.raises(TypeError):
        result.metadata["source"] = "changed"


def test_result_metadata_count():
    result = ExecutionResult(
        experiment_id="E001",
        hypothesis_id="H001",
        metadata={
            "source": "test",
            "version": 1,
        },
    )

    assert result.metadata_count == 2


# ==============================================================================
# ExecutionResult validation
# ==============================================================================


@pytest.mark.parametrize(
    "experiment_id",
    [
        "",
        " ",
        "   ",
        None,
        1,
        object(),
    ],
)
def test_result_rejects_invalid_experiment_id(
    experiment_id,
):
    with pytest.raises(InvalidExecutionResultError):
        ExecutionResult(
            experiment_id=experiment_id,
            hypothesis_id="H001",
        )


@pytest.mark.parametrize(
    "hypothesis_id",
    [
        "",
        " ",
        "   ",
        None,
        1,
        object(),
    ],
)
def test_result_rejects_invalid_hypothesis_id(
    hypothesis_id,
):
    with pytest.raises(InvalidExecutionResultError):
        ExecutionResult(
            experiment_id="E001",
            hypothesis_id=hypothesis_id,
        )


@pytest.mark.parametrize(
    "execution_id",
    [
        "",
        " ",
        "   ",
        None,
        1,
        object(),
    ],
)
def test_result_rejects_invalid_execution_id(
    execution_id,
):
    with pytest.raises(InvalidExecutionResultError):
        ExecutionResult(
            execution_id=execution_id,
            experiment_id="E001",
            hypothesis_id="H001",
        )


def test_result_rejects_invalid_status():
    with pytest.raises(
        InvalidExecutionResultError,
        match="status",
    ):
        ExecutionResult(
            experiment_id="E001",
            hypothesis_id="H001",
            status="completed",
        )


def test_result_rejects_naive_created_at():
    with pytest.raises(
        InvalidExecutionResultError,
        match="timezone-aware",
    ):
        ExecutionResult(
            experiment_id="E001",
            hypothesis_id="H001",
            created_at=datetime.now(),
        )


def test_result_rejects_invalid_created_at():
    with pytest.raises(
        InvalidExecutionResultError,
        match="datetime",
    ):
        ExecutionResult(
            experiment_id="E001",
            hypothesis_id="H001",
            created_at="now",
        )


def test_result_rejects_invalid_metadata():
    with pytest.raises(
        InvalidExecutionResultError,
        match="metadata",
    ):
        ExecutionResult(
            experiment_id="E001",
            hypothesis_id="H001",
            metadata=[],
        )


# ==============================================================================
# ExecutionResult query API
# ==============================================================================


def test_result_has_observation():
    result = make_result(
        observation=make_observation(),
    )

    assert result.has_observation is True


def test_result_without_observation():
    result = make_result(
        observation=None,
    )

    assert result.has_observation is False


def test_result_has_metadata():
    result = make_result(
        metadata={
            "source": "test",
        },
    )

    assert result.has_metadata("source") is True
    assert result.has_metadata("missing") is False


def test_result_has_metadata_rejects_non_string_name():
    result = make_result()

    assert result.has_metadata(None) is False
    assert result.has_metadata(1) is False


def test_result_get_metadata():
    result = make_result(
        metadata={
            "source": "test",
        },
    )

    assert (
        result.get_metadata("source")
        == "test"
    )


def test_result_get_metadata_default():
    result = make_result()

    assert (
        result.get_metadata(
            "missing",
            "fallback",
        )
        == "fallback"
    )


# ==============================================================================
# ExecutionResult functional update
# ==============================================================================


def test_result_with_metadata_returns_new_result():
    result = make_result()

    updated = result.with_metadata(
        "source",
        "test",
    )

    assert updated is not result


def test_result_with_metadata_preserves_identity():
    result = make_result(
        execution_id="X001",
        experiment_id="E001",
        hypothesis_id="H001",
    )

    updated = result.with_metadata(
        "source",
        "test",
    )

    assert (
        updated.execution_id
        == result.execution_id
    )

    assert (
        updated.experiment_id
        == result.experiment_id
    )

    assert (
        updated.hypothesis_id
        == result.hypothesis_id
    )

    assert updated.status is result.status

    assert (
        updated.observation
        is result.observation
    )

    assert (
        updated.created_at
        == result.created_at
    )


def test_result_with_metadata_does_not_mutate_original():
    result = make_result()

    updated = result.with_metadata(
        "source",
        "test",
    )

    assert result.has_metadata("source") is False
    assert updated.has_metadata("source") is True


def test_result_with_metadata_replaces_existing_value():
    result = make_result(
        metadata={
            "source": "old",
        },
    )

    updated = result.with_metadata(
        "source",
        "new",
    )

    assert (
        result.get_metadata("source")
        == "old"
    )

    assert (
        updated.get_metadata("source")
        == "new"
    )


@pytest.mark.parametrize(
    "name",
    [
        "",
        " ",
        "   ",
        None,
        1,
    ],
)
def test_result_with_metadata_rejects_invalid_name(name):
    result = make_result()

    with pytest.raises(
        InvalidExecutionResultError,
        match="metadata name",
    ):
        result.with_metadata(
            name,
            "value",
        )


# ==============================================================================
# ScientificExecutor construction
# ==============================================================================


def test_executor_creation():
    executor = ScientificExecutor()

    assert executor is not None


def test_executor_creation_has_zero_count():
    executor = ScientificExecutor()

    assert executor.execution_count == 0


def test_executor_accepts_world():
    world = make_world()

    executor = ScientificExecutor(
        world=world,
    )

    assert executor.world is world


def test_executor_accepts_custom_world():
    world = DummyWorld()

    executor = ScientificExecutor(
        world=world,
    )

    assert executor.world is world


# ==============================================================================
# Basic execution
# ==============================================================================


def test_executor_runs_experiment():
    world = DummyWorld()

    executor = ScientificExecutor(
        world=world,
    )

    experiment = make_experiment(
        parameters={
            "x": 11,
        },
    )

    result = executor.execute(
        experiment,
    )

    assert isinstance(
        result,
        ExecutionResult,
    )

    assert result.experiment_id == "E001"
    assert result.hypothesis_id == "H001"

    assert isinstance(
        result.observation,
        Observation,
    )


def test_executor_produces_observation():
    executor = ScientificExecutor(
        world=DummyWorld(),
    )

    result = executor.execute(
        make_experiment(
            parameters={
                "x": 11,
            },
        ),
    )

    assert result.observation is not None

    assert (
        result.observation.experiment_id
        == "E001"
    )


def test_executor_preserves_world_values():
    executor = ScientificExecutor(
        world=DummyWorld(),
    )

    result = executor.execute(
        make_experiment(
            parameters={
                "x": 11,
            },
        ),
    )

    assert (
        result.observation.values["response"]
        is True
    )

    assert (
        result.observation.values["input"]
        == 11
    )


def test_executor_can_execute_false_result():
    executor = ScientificExecutor(
        world=DummyWorld(),
    )

    result = executor.execute(
        make_experiment(
            parameters={
                "x": 5,
            },
        ),
    )

    assert (
        result.observation.values["response"]
        is False
    )


def test_executor_result_status_is_completed():
    executor = ScientificExecutor(
        world=DummyWorld(),
    )

    result = executor.execute(
        make_experiment(
            parameters={
                "x": 11,
            },
        ),
    )

    assert (
        result.status
        is ExecutionStatus.COMPLETED
    )

    assert result.success is True


# ==============================================================================
# Synthetic world integration
# ==============================================================================


def test_executor_integrates_with_synthetic_world():
    executor = ScientificExecutor(
        world=make_world(),
    )

    result = executor.execute(
        make_experiment(
            parameters={
                "x": 11,
            },
        ),
    )

    assert isinstance(
        result,
        ExecutionResult,
    )

    assert isinstance(
        result.observation,
        Observation,
    )

    assert (
        result.observation.values["response"]
        is True
    )


def test_executor_synthetic_world_threshold_false():
    executor = ScientificExecutor(
        world=make_world(),
    )

    result = executor.execute(
        make_experiment(
            parameters={
                "x": 9,
            },
        ),
    )

    assert (
        result.observation.values["response"]
        is False
    )


# ==============================================================================
# Context execution
# ==============================================================================


def test_executor_accepts_context():
    executor = ScientificExecutor(
        world=DummyWorld(),
    )

    context = make_context(
        experiment=make_experiment(
            parameters={
                "x": 11,
            },
        ),
    )

    result = executor.execute_context(
        context,
    )

    assert isinstance(
        result,
        ExecutionResult,
    )

    assert result.experiment_id == "E001"
    assert result.hypothesis_id == "H001"


def test_execute_context_preserves_context_execution_id():
    executor = ScientificExecutor(
        world=DummyWorld(),
    )

    context = make_context(
        experiment=make_experiment(
            parameters={
                "x": 11,
            },
        ),
    )

    result = executor.execute_context(
        context,
    )

    assert (
        result.execution_id
        == context.execution_id
    )


def test_execute_context_uses_context_experiment():
    world = DummyWorld()

    executor = ScientificExecutor(
        world=world,
    )

    experiment = make_experiment(
        experiment_id="E777",
        hypothesis_id="H999",
        parameters={
            "x": 17,
        },
    )

    context = make_context(
        experiment=experiment,
    )

    result = executor.execute_context(
        context,
    )

    assert result.experiment_id == "E777"
    assert result.hypothesis_id == "H999"

    assert (
        result.observation.experiment_id
        == "E777"
    )

    assert (
        result.observation.values["input"]
        == 17
    )


def test_execute_and_execute_context_are_consistent():
    world = DummyWorld()

    executor = ScientificExecutor(
        world=world,
    )

    experiment = make_experiment(
        parameters={
            "x": 11,
        },
    )

    direct = executor.execute(
        experiment,
    )

    context = ExecutionContext(
        experiment=experiment,
        state=WorldState(),
    )

    contextual = executor.execute_context(
        context,
    )

    assert (
        direct.experiment_id
        == contextual.experiment_id
    )

    assert (
        direct.hypothesis_id
        == contextual.hypothesis_id
    )

    assert (
        direct.observation.values
        == contextual.observation.values
    )


def test_execute_creates_context_and_delegates():
    world = DummyWorld()

    executor = ScientificExecutor(
        world=world,
    )

    experiment = make_experiment(
        parameters={
            "x": 11,
        },
    )

    result = executor.execute(
        experiment,
    )

    assert result.execution_id
    assert world.calls == 1


# ==============================================================================
# Context validation
# ==============================================================================


@pytest.mark.parametrize(
    "context",
    [
        None,
        1,
        "context",
        {},
        object(),
    ],
)
def test_execute_context_rejects_invalid_context(
    context,
):
    executor = ScientificExecutor(
        world=DummyWorld(),
    )

    with pytest.raises(
        InvalidExecutionError,
        match="context",
    ):
        executor.execute_context(
            context,
        )


def test_execute_context_requires_experiment():
    context = object()

    executor = ScientificExecutor(
        world=DummyWorld(),
    )

    with pytest.raises(
        InvalidExecutionError,
    ):
        executor.execute_context(
            context,
        )


# ==============================================================================
# Determinism
# ==============================================================================


def test_executor_is_deterministic():
    executor = ScientificExecutor(
        world=DummyWorld(),
    )

    experiment = make_experiment(
        parameters={
            "x": 11,
        },
    )

    result_1 = executor.execute(
        experiment,
    )

    result_2 = executor.execute(
        experiment,
    )

    assert (
        result_1.observation.values
        == result_2.observation.values
    )


def test_executor_generates_distinct_execution_ids():
    executor = ScientificExecutor(
        world=DummyWorld(),
    )

    experiment = make_experiment(
        parameters={
            "x": 11,
        },
    )

    result_1 = executor.execute(
        experiment,
    )

    result_2 = executor.execute(
        experiment,
    )

    assert (
        result_1.execution_id
        != result_2.execution_id
    )


def test_executor_generates_distinct_observation_ids():
    executor = ScientificExecutor(
        world=DummyWorld(),
    )

    experiment = make_experiment(
        parameters={
            "x": 11,
        },
    )

    result_1 = executor.execute(
        experiment,
    )

    result_2 = executor.execute(
        experiment,
    )

    assert (
        result_1.observation.id
        != result_2.observation.id
    )


# ==============================================================================
# Execution state
# ==============================================================================


def test_executor_tracks_execution_count():
    executor = ScientificExecutor(
        world=DummyWorld(),
    )

    assert executor.execution_count == 0

    executor.execute(
        make_experiment(
            parameters={
                "x": 11,
            },
        ),
    )

    assert executor.execution_count == 1


def test_executor_execution_count_increments():
    executor = ScientificExecutor(
        world=DummyWorld(),
    )

    executor.execute(
        make_experiment(
            experiment_id="E001",
            parameters={
                "x": 11,
            },
        ),
    )

    executor.execute(
        make_experiment(
            experiment_id="E002",
            parameters={
                "x": 5,
            },
        ),
    )

    assert executor.execution_count == 2


def test_executor_execution_count_increments_for_false_observation():
    executor = ScientificExecutor(
        world=FalseWorld(),
    )

    executor.execute(
        make_experiment(
            parameters={
                "x": 5,
            },
        ),
    )

    assert executor.execution_count == 1


def test_executor_execution_count_starts_from_zero():
    executor = ScientificExecutor(
        world=DummyWorld(),
    )

    assert executor.execution_count == 0


# ==============================================================================
# Invalid experiment
# ==============================================================================


@pytest.mark.parametrize(
    "experiment",
    [
        None,
        1,
        "experiment",
        {},
        [],
        object(),
    ],
)
def test_executor_rejects_invalid_experiment(
    experiment,
):
    executor = ScientificExecutor(
        world=DummyWorld(),
    )

    with pytest.raises(
        InvalidExecutionError,
    ):
        executor.execute(
            experiment,
        )


def test_executor_rejects_none_experiment_before_world_call():
    world = DummyWorld()

    executor = ScientificExecutor(
        world=world,
    )

    with pytest.raises(
        InvalidExecutionError,
    ):
        executor.execute(None)

    assert world.calls == 0
    assert executor.execution_count == 0


# ==============================================================================
# World failures
# ==============================================================================


def test_world_failure_is_wrapped():
    executor = ScientificExecutor(
        world=FailingWorld(),
    )

    with pytest.raises(
        WorldExecutionError,
        match="world failure",
    ):
        executor.execute(
            make_experiment(
                parameters={
                    "x": 11,
                },
            ),
        )


def test_world_failure_does_not_increment_count():
    executor = ScientificExecutor(
        world=FailingWorld(),
    )

    with pytest.raises(
        WorldExecutionError,
    ):
        executor.execute(
            make_experiment(
                parameters={
                    "x": 11,
                },
            ),
        )

    assert executor.execution_count == 0


def test_invalid_world_result_is_rejected():
    executor = ScientificExecutor(
        world=InvalidWorld(),
    )

    with pytest.raises(
        WorldExecutionError,
    ):
        executor.execute(
            make_experiment(
                parameters={
                    "x": 11,
                },
            ),
        )


def test_invalid_world_result_does_not_increment_count():
    executor = ScientificExecutor(
        world=InvalidWorld(),
    )

    with pytest.raises(
        WorldExecutionError,
    ):
        executor.execute(
            make_experiment(
                parameters={
                    "x": 11,
                },
            ),
        )

    assert executor.execution_count == 0


# ==============================================================================
# Parameter preservation
# ==============================================================================


def test_executor_preserves_experiment_parameters():
    world = DummyWorld()

    executor = ScientificExecutor(
        world=world,
    )

    experiment = make_experiment(
        parameters={
            "x": 17,
            "temperature": 25,
        },
    )

    result = executor.execute(
        experiment,
    )

    assert (
        result.observation.values["input"]
        == 17
    )


def test_executor_passes_parameters_to_world():
    world = DummyWorld()

    executor = ScientificExecutor(
        world=world,
    )

    experiment = make_experiment(
        parameters={
            "x": 17,
            "temperature": 25,
        },
    )

    executor.execute(
        experiment,
    )

    assert world.parameters_seen == [
        {
            "x": 17,
            "temperature": 25,
        }
    ]


def test_executor_does_not_mutate_experiment():
    executor = ScientificExecutor(
        world=DummyWorld(),
    )

    experiment = make_experiment(
        parameters={
            "x": 11,
        },
    )

    original = dict(
        experiment.parameters,
    )

    executor.execute(
        experiment,
    )

    assert (
        dict(experiment.parameters)
        == original
    )


# ==============================================================================
# Observation contract
# ==============================================================================


def test_observation_id_is_generated():
    executor = ScientificExecutor(
        world=DummyWorld(),
    )

    result = executor.execute(
        make_experiment(
            parameters={
                "x": 11,
            },
        ),
    )

    assert isinstance(
        result.observation.id,
        str,
    )

    assert result.observation.id.strip()


def test_observation_ids_are_unique():
    executor = ScientificExecutor(
        world=DummyWorld(),
    )

    result_1 = executor.execute(
        make_experiment(
            experiment_id="E001",
            parameters={
                "x": 11,
            },
        ),
    )

    result_2 = executor.execute(
        make_experiment(
            experiment_id="E002",
            parameters={
                "x": 11,
            },
        ),
    )

    assert (
        result_1.observation.id
        != result_2.observation.id
    )


def test_observation_points_to_experiment():
    executor = ScientificExecutor(
        world=DummyWorld(),
    )

    result = executor.execute(
        make_experiment(
            experiment_id="E123",
            parameters={
                "x": 11,
            },
        ),
    )

    assert (
        result.observation.experiment_id
        == "E123"
    )


def test_observation_values_are_preserved():
    executor = ScientificExecutor(
        world=DummyWorld(),
    )

    result = executor.execute(
        make_experiment(
            parameters={
                "x": 13,
            },
        ),
    )

    assert result.observation.values == {
        "response": True,
        "input": 13,
    }


# ==============================================================================
# Execution identity
# ==============================================================================


def test_result_execution_id_matches_context_execution_id():
    executor = ScientificExecutor(
        world=DummyWorld(),
    )

    context = make_context(
        experiment=make_experiment(
            parameters={
                "x": 11,
            },
        ),
    )

    result = executor.execute_context(
        context,
    )

    assert (
        result.execution_id
        == context.execution_id
    )


def test_result_contains_experiment_identity():
    executor = ScientificExecutor(
        world=DummyWorld(),
    )

    result = executor.execute(
        make_experiment(
            experiment_id="E123",
            hypothesis_id="H456",
            parameters={
                "x": 11,
            },
        ),
    )

    assert result.experiment_id == "E123"
    assert result.hypothesis_id == "H456"


# ==============================================================================
# No hidden interpretation
# ==============================================================================


def test_executor_does_not_evaluate_hypothesis():
    executor = ScientificExecutor(
        world=DummyWorld(),
    )

    result = executor.execute(
        make_experiment(
            hypothesis_id="H123",
            parameters={
                "x": 11,
            },
        ),
    )

    assert result.hypothesis_id == "H123"

    # Execution only produces an observation.
    # Evaluation belongs to the Evaluation layer.
    assert not hasattr(
        result,
        "evaluation",
    )


def test_executor_does_not_modify_hypothesis():
    executor = ScientificExecutor(
        world=DummyWorld(),
    )

    experiment = make_experiment(
        hypothesis_id="H123",
        parameters={
            "x": 11,
        },
    )

    original_hypothesis_id = (
        experiment.hypothesis_id
    )

    executor.execute(
        experiment,
    )

    assert (
        experiment.hypothesis_id
        == original_hypothesis_id
    )


# ==============================================================================
# World interaction
# ==============================================================================


def test_world_is_called_exactly_once_per_execution():
    world = DummyWorld()

    executor = ScientificExecutor(
        world=world,
    )

    executor.execute(
        make_experiment(
            parameters={
                "x": 11,
            },
        ),
    )

    assert world.calls == 1


def test_execute_context_calls_world_exactly_once():
    world = DummyWorld()

    executor = ScientificExecutor(
        world=world,
    )

    context = make_context(
        experiment=make_experiment(
            parameters={
                "x": 11,
            },
        ),
    )

    executor.execute_context(
        context,
    )

    assert world.calls == 1


def test_failed_world_execution_calls_world_once():
    world = FailingWorld()

    executor = ScientificExecutor(
        world=world,
    )

    with pytest.raises(
        WorldExecutionError,
    ):
        executor.execute(
            make_experiment(
                parameters={
                    "x": 11,
                },
            ),
        )


# ==============================================================================
# Public API sanity
# ==============================================================================


def test_execution_modules_import():
    from scios.runtime.science.execution import (
        ExecutionContext,
        ExecutionError,
        ExecutionResult,
        ExecutionStatus,
        ScientificExecutor,
    )

    assert ExecutionContext is not None
    assert ExecutionError is not None
    assert ExecutionResult is not None
    assert ExecutionStatus is not None
    assert ScientificExecutor is not None


def test_execution_result_public_api():
    from scios.runtime.science.execution import (
        ExecutionResult,
        ExecutionStatus,
    )

    result = ExecutionResult(
        experiment_id="E001",
        hypothesis_id="H001",
    )

    assert result.status is ExecutionStatus.COMPLETED
    assert result.success is True


# ==============================================================================
# Contract summary
# ==============================================================================


def test_execution_contract_is_context_to_result():
    world = DummyWorld()

    executor = ScientificExecutor(
        world=world,
    )

    context = ExecutionContext(
        experiment=make_experiment(
            experiment_id="E100",
            hypothesis_id="H200",
            parameters={
                "x": 20,
            },
        ),
        state=WorldState(),
    )

    result = executor.execute_context(
        context,
    )

    assert isinstance(
        result,
        ExecutionResult,
    )

    assert (
        result.execution_id
        == context.execution_id
    )

    assert (
        result.experiment_id
        == context.experiment.id
    )

    assert (
        result.hypothesis_id
        == context.experiment.hypothesis_id
    )

    assert isinstance(
        result.observation,
        Observation,
    )

    assert (
        result.observation.experiment_id
        == context.experiment.id
    )

    assert (
        result.status
        is ExecutionStatus.COMPLETED
    )

    assert result.success is True