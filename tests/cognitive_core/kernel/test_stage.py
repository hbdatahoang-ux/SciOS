"""
Tests for scios.cognitive_core.kernel.stage.
"""

from __future__ import annotations

import pytest

from scios.cognitive_core.kernel.context import CognitiveContext
from scios.cognitive_core.kernel.request import CognitiveRequest
from scios.cognitive_core.kernel.stage import CognitiveStage, Stage


class DemoStage(CognitiveStage):
    """Concrete stage used by tests."""

    def __init__(self, name: str = "demo") -> None:
        super().__init__(name)
        self.run_count = 0

    def run(self, context: CognitiveContext):
        self.run_count += 1
        context.set("result", "ok")
        return "ok"


class FailingStage(CognitiveStage):
    """Stage that always fails."""

    def run(self, context: CognitiveContext):
        raise RuntimeError("stage failed")


@pytest.fixture
def cognitive_request() -> CognitiveRequest:
    return CognitiveRequest(query="hello")


@pytest.fixture
def context(cognitive_request: CognitiveRequest) -> CognitiveContext:
    return CognitiveContext(cognitive_request)


@pytest.fixture
def stage() -> DemoStage:
    return DemoStage()


def test_cognitive_stage_is_abstract():
    assert CognitiveStage.__abstractmethods__ == frozenset({"run"})


def test_stage_alias_points_to_cognitive_stage():
    assert Stage is CognitiveStage


def test_stage_can_be_instantiated_through_concrete_subclass():
    stage = DemoStage()

    assert isinstance(stage, CognitiveStage)
    assert stage.name == "demo"


def test_default_status_is_idle():
    stage = DemoStage()

    assert stage.status == "idle"


def test_default_message_is_none():
    stage = DemoStage()

    assert stage.message is None


def test_default_executions_is_zero():
    stage = DemoStage()

    assert stage.executions == 0


def test_initialize_sets_ready():
    stage = DemoStage()

    stage.initialize()

    assert stage.status == "ready"
    assert stage.is_ready is True


def test_reset_returns_stage_to_idle():
    stage = DemoStage()

    stage.initialize()
    stage.message = "temporary"

    stage.reset()

    assert stage.status == "idle"
    assert stage.message is None


def test_is_ready():
    stage = DemoStage()

    assert stage.is_ready is False

    stage.initialize()

    assert stage.is_ready is True


def test_is_running():
    stage = DemoStage()

    assert stage.is_running is False

    stage.status = "running"

    assert stage.is_running is True


def test_is_completed():
    stage = DemoStage()

    assert stage.is_completed is False

    stage.status = "completed"

    assert stage.is_completed is True


def test_execute_calls_run(
    stage: DemoStage,
    context: CognitiveContext,
):
    result = stage.execute(context)

    assert result == "ok"
    assert stage.run_count == 1


def test_execute_increments_executions(
    stage: DemoStage,
    context: CognitiveContext,
):
    assert stage.executions == 0

    stage.execute(context)

    assert stage.executions == 1


def test_execute_multiple_times_increments_executions(
    stage: DemoStage,
    context: CognitiveContext,
):
    stage.execute(context)
    stage.execute(context)

    assert stage.executions == 2
    assert stage.run_count == 2


def test_execute_ends_in_completed_status(
    stage: DemoStage,
    context: CognitiveContext,
):
    stage.execute(context)

    assert stage.status == "completed"
    assert stage.is_completed is True


def test_execute_sets_running_before_run(
    context: CognitiveContext,
):
    observed = {}

    class InspectStage(CognitiveStage):
        def run(self, context: CognitiveContext):
            observed["status"] = self.status
            return "ok"

    stage = InspectStage("inspect")

    stage.execute(context)

    assert observed["status"] == "running"


def test_execute_passes_context_to_run(
    context: CognitiveContext,
):
    observed = {}

    class InspectStage(CognitiveStage):
        def run(self, ctx: CognitiveContext):
            observed["context"] = ctx
            return "ok"

    stage = InspectStage("inspect")

    stage.execute(context)

    assert observed["context"] is context


def test_execute_returns_stage_result(
    context: CognitiveContext,
):
    class ResultStage(CognitiveStage):
        def run(self, context: CognitiveContext):
            return {"answer": 42}

    stage = ResultStage("result")

    result = stage.execute(context)

    assert result == {"answer": 42}


def test_execute_failure_sets_failed_status(
    context: CognitiveContext,
):
    stage = FailingStage("failing")

    with pytest.raises(RuntimeError, match="stage failed"):
        stage.execute(context)

    assert stage.status == "failed"


def test_execute_failure_stores_message(
    context: CognitiveContext,
):
    stage = FailingStage("failing")

    with pytest.raises(RuntimeError, match="stage failed"):
        stage.execute(context)

    assert stage.message == "stage failed"


def test_execute_failure_does_not_increment_executions(
    context: CognitiveContext,
):
    stage = FailingStage("failing")

    with pytest.raises(RuntimeError):
        stage.execute(context)

    assert stage.executions == 0


def test_execute_failure_reraises_original_exception(
    context: CognitiveContext,
):
    stage = FailingStage("failing")

    with pytest.raises(RuntimeError, match="stage failed"):
        stage.execute(context)


def test_to_dict_contains_expected_keys(
    stage: DemoStage,
):
    result = stage.to_dict()

    assert set(result) == {
        "name",
        "status",
        "message",
        "executions",
    }


def test_to_dict_contains_initial_values(
    stage: DemoStage,
):
    result = stage.to_dict()

    assert result == {
        "name": "demo",
        "status": "idle",
        "message": None,
        "executions": 0,
    }


def test_to_dict_reflects_current_state(
    stage: DemoStage,
):
    stage.initialize()
    stage.message = "ready"

    result = stage.to_dict()

    assert result == {
        "name": "demo",
        "status": "ready",
        "message": "ready",
        "executions": 0,
    }


def test_status_info_matches_to_dict(
    stage: DemoStage,
):
    assert stage.status_info() == stage.to_dict()


def test_repr_contains_name(
    stage: DemoStage,
):
    result = repr(stage)

    assert "demo" in result


def test_repr_contains_status(
    stage: DemoStage,
):
    result = repr(stage)

    assert "idle" in result


def test_execute_updates_context(
    stage: DemoStage,
    context: CognitiveContext,
):
    stage.execute(context)

    assert context.get("result") == "ok"


def test_stage_name_is_preserved():
    stage = DemoStage("reasoning")

    assert stage.name == "reasoning"


def test_stage_name_can_be_empty():
    stage = DemoStage("")

    assert stage.name == ""


def test_reset_clears_failure_message(
    context: CognitiveContext,
):
    stage = FailingStage("failing")

    with pytest.raises(RuntimeError):
        stage.execute(context)

    assert stage.status == "failed"
    assert stage.message == "stage failed"

    stage.reset()

    assert stage.status == "idle"
    assert stage.message is None


def test_initialize_after_failure_makes_stage_ready(
    context: CognitiveContext,
):
    stage = FailingStage("failing")

    with pytest.raises(RuntimeError):
        stage.execute(context)

    stage.initialize()

    assert stage.status == "ready"
    assert stage.is_ready is True
    assert stage.message == "stage failed"


def test_initialize_does_not_reset_execution_count(
    stage: DemoStage,
    context: CognitiveContext,
):
    stage.execute(context)

    assert stage.executions == 1

    stage.initialize()

    assert stage.executions == 1


def test_reset_does_not_reset_execution_count(
    stage: DemoStage,
    context: CognitiveContext,
):
    stage.execute(context)

    assert stage.executions == 1

    stage.reset()

    assert stage.executions == 1
