"""
Tests for scios.cognitive_core.kernel.dispatcher.
"""

from __future__ import annotations

import pytest

from scios.cognitive_core.kernel.context import CognitiveContext
from scios.cognitive_core.kernel.request import CognitiveRequest
from scios.cognitive_core.kernel.stage import CognitiveStage
from scios.cognitive_core.kernel.dispatcher import StageDispatcher
from scios.cognitive_core.kernel.events import KernelEventType


# =========================================================
# Test doubles
# =========================================================


class DemoStage(CognitiveStage):
    """Successful cognitive stage."""

    def __init__(self, name: str = "demo") -> None:
        super().__init__(name)
        self.run_count = 0

    def run(self, context: CognitiveContext):
        self.run_count += 1
        context.set(self.name, "ok")
        return "ok"


class ResultStage(CognitiveStage):
    """Stage returning a custom result."""

    def __init__(self, name: str = "result") -> None:
        super().__init__(name)

    def run(self, context: CognitiveContext):
        return {"answer": 42}


class FailingStage(CognitiveStage):
    """Stage that always fails."""

    def run(self, context: CognitiveContext):
        raise RuntimeError("stage failed")


class RecordingMiddleware:
    """Middleware used to verify lifecycle hooks."""

    def __init__(self) -> None:
        self.before_calls = []
        self.after_calls = []

    def before_stage(
        self,
        stage: CognitiveStage,
        context: CognitiveContext,
    ) -> None:
        self.before_calls.append((stage, context))

    def after_stage(
        self,
        stage: CognitiveStage,
        context: CognitiveContext,
    ) -> None:
        self.after_calls.append((stage, context))


class RecordingEventBus:
    """
    Event bus compatible with SciOS EventBus.publish().

    Contract:
        publish(event: str, **payload)
    """

    def __init__(self) -> None:
        self.events = []

    def publish(
        self,
        event_name: str,
        **payload,
    ) -> None:
        self.events.append((event_name, payload))


# =========================================================
# Fixtures
# =========================================================


@pytest.fixture
def cognitive_request() -> CognitiveRequest:
    return CognitiveRequest(query="hello")


@pytest.fixture
def cognitive_context(
    cognitive_request: CognitiveRequest,
) -> CognitiveContext:
    return CognitiveContext(cognitive_request)


@pytest.fixture
def dispatcher() -> StageDispatcher:
    return StageDispatcher()


@pytest.fixture
def stage() -> DemoStage:
    return DemoStage()


# =========================================================
# Construction
# =========================================================


def test_dispatcher_can_be_created():
    dispatcher = StageDispatcher()

    assert dispatcher is not None


def test_default_executed_count_is_zero(
    dispatcher: StageDispatcher,
):
    assert dispatcher.executed == 0


def test_status_returns_executed_count(
    dispatcher: StageDispatcher,
):
    assert dispatcher.status() == {
        "executed": 0,
    }


# =========================================================
# Single stage dispatch
# =========================================================


def test_dispatch_executes_stage(
    dispatcher: StageDispatcher,
    stage: DemoStage,
    cognitive_context: CognitiveContext,
):
    dispatcher.dispatch(
        stage,
        cognitive_context,
    )

    assert stage.run_count == 1


def test_dispatch_returns_stage_result(
    dispatcher: StageDispatcher,
    stage: DemoStage,
    cognitive_context: CognitiveContext,
):
    result = dispatcher.dispatch(
        stage,
        cognitive_context,
    )

    assert result == "ok"


def test_dispatch_passes_context_to_stage(
    dispatcher: StageDispatcher,
    cognitive_context: CognitiveContext,
):
    observed = {}

    class InspectStage(CognitiveStage):
        def run(self, context: CognitiveContext):
            observed["context"] = context
            return "ok"

    stage = InspectStage("inspect")

    dispatcher.dispatch(
        stage,
        cognitive_context,
    )

    assert observed["context"] is cognitive_context


def test_dispatch_sets_running_before_execution(
    dispatcher: StageDispatcher,
    cognitive_context: CognitiveContext,
):
    observed = {}

    class InspectStage(CognitiveStage):
        def run(self, context: CognitiveContext):
            observed["status"] = self.status
            return "ok"

    stage = InspectStage("inspect")

    dispatcher.dispatch(
        stage,
        cognitive_context,
    )

    assert observed["status"] == "running"


def test_dispatch_sets_completed_after_success(
    dispatcher: StageDispatcher,
    stage: DemoStage,
    cognitive_context: CognitiveContext,
):
    dispatcher.dispatch(
        stage,
        cognitive_context,
    )

    assert stage.status == "completed"
    assert stage.is_completed is True


def test_dispatch_increments_executed_count(
    dispatcher: StageDispatcher,
    stage: DemoStage,
    cognitive_context: CognitiveContext,
):
    dispatcher.dispatch(
        stage,
        cognitive_context,
    )

    assert dispatcher.executed == 1


def test_dispatch_updates_context(
    dispatcher: StageDispatcher,
    stage: DemoStage,
    cognitive_context: CognitiveContext,
):
    dispatcher.dispatch(
        stage,
        cognitive_context,
    )

    assert cognitive_context.get("demo") == "ok"


def test_dispatch_supports_custom_result(
    dispatcher: StageDispatcher,
    cognitive_context: CognitiveContext,
):
    stage = ResultStage()

    result = dispatcher.dispatch(
        stage,
        cognitive_context,
    )

    assert result == {
        "answer": 42,
    }


# =========================================================
# Multiple dispatches
# =========================================================


def test_dispatch_multiple_times(
    dispatcher: StageDispatcher,
    stage: DemoStage,
    cognitive_context: CognitiveContext,
):
    dispatcher.dispatch(
        stage,
        cognitive_context,
    )

    dispatcher.dispatch(
        stage,
        cognitive_context,
    )

    assert stage.run_count == 2
    assert dispatcher.executed == 2


def test_dispatch_multiple_stages(
    dispatcher: StageDispatcher,
    cognitive_context: CognitiveContext,
):
    first = DemoStage("first")
    second = DemoStage("second")
    third = DemoStage("third")

    result = dispatcher.dispatch(
        context=cognitive_context,
        stages=[
            first,
            second,
            third,
        ],
    )

    assert result == "ok"

    assert first.run_count == 1
    assert second.run_count == 1
    assert third.run_count == 1

    assert dispatcher.executed == 3


def test_pipeline_mode_returns_last_result(
    dispatcher: StageDispatcher,
    cognitive_context: CognitiveContext,
):
    first = DemoStage("first")
    second = ResultStage("second")

    result = dispatcher.dispatch(
        context=cognitive_context,
        stages=[
            first,
            second,
        ],
    )

    assert result == {
        "answer": 42,
    }


def test_empty_stage_list_returns_none(
    dispatcher: StageDispatcher,
    cognitive_context: CognitiveContext,
):
    result = dispatcher.dispatch(
        context=cognitive_context,
        stages=[],
    )

    assert result is None
    assert dispatcher.executed == 0


# =========================================================
# Middleware
# =========================================================


def test_middleware_before_stage_is_called(
    dispatcher: StageDispatcher,
    stage: DemoStage,
    cognitive_context: CognitiveContext,
):
    middleware = RecordingMiddleware()

    dispatcher.dispatch(
        stage,
        cognitive_context,
        middleware=middleware,
    )

    assert len(middleware.before_calls) == 1

    recorded_stage, recorded_context = middleware.before_calls[0]

    assert recorded_stage is stage
    assert recorded_context is cognitive_context


def test_middleware_after_stage_is_called(
    dispatcher: StageDispatcher,
    stage: DemoStage,
    cognitive_context: CognitiveContext,
):
    middleware = RecordingMiddleware()

    dispatcher.dispatch(
        stage,
        cognitive_context,
        middleware=middleware,
    )

    assert len(middleware.after_calls) == 1

    recorded_stage, recorded_context = middleware.after_calls[0]

    assert recorded_stage is stage
    assert recorded_context is cognitive_context


def test_middleware_is_used_in_pipeline_mode(
    dispatcher: StageDispatcher,
    cognitive_context: CognitiveContext,
):
    middleware = RecordingMiddleware()

    first = DemoStage("first")
    second = DemoStage("second")

    dispatcher.dispatch(
        context=cognitive_context,
        stages=[
            first,
            second,
        ],
        middleware=middleware,
    )

    assert len(middleware.before_calls) == 2
    assert len(middleware.after_calls) == 2


def test_middleware_before_runs_before_stage(
    dispatcher: StageDispatcher,
    cognitive_context: CognitiveContext,
):
    observed = []

    class Middleware:
        def before_stage(self, stage, context):
            observed.append("before")

        def after_stage(self, stage, context):
            observed.append("after")

    class Stage(CognitiveStage):
        def run(self, context):
            observed.append("run")
            return "ok"

    dispatcher.dispatch(
        Stage("test"),
        cognitive_context,
        middleware=Middleware(),
    )

    assert observed == [
        "before",
        "run",
        "after",
    ]


# =========================================================
# Event bus
# =========================================================


def test_event_bus_publishes_started_event(
    dispatcher: StageDispatcher,
    stage: DemoStage,
    cognitive_context: CognitiveContext,
):
    event_bus = RecordingEventBus()

    dispatcher.dispatch(
        stage,
        cognitive_context,
        event_bus=event_bus,
    )

    assert len(event_bus.events) >= 1

    event_name, payload = event_bus.events[0]

    assert event_name == KernelEventType.STAGE_STARTED.value
    assert payload == {
        "stage": "demo",
    }


def test_event_bus_publishes_completed_event(
    dispatcher: StageDispatcher,
    stage: DemoStage,
    cognitive_context: CognitiveContext,
):
    event_bus = RecordingEventBus()

    dispatcher.dispatch(
        stage,
        cognitive_context,
        event_bus=event_bus,
    )

    assert len(event_bus.events) >= 2

    event_name, payload = event_bus.events[-1]

    assert event_name == KernelEventType.STAGE_COMPLETED.value
    assert payload == {
        "stage": "demo",
    }


def test_event_bus_event_order(
    dispatcher: StageDispatcher,
    stage: DemoStage,
    cognitive_context: CognitiveContext,
):
    event_bus = RecordingEventBus()

    dispatcher.dispatch(
        stage,
        cognitive_context,
        event_bus=event_bus,
    )

    assert [
        event[0]
        for event in event_bus.events
    ] == [
        KernelEventType.STAGE_STARTED.value,
        KernelEventType.STAGE_COMPLETED.value,
    ]


def test_event_bus_works_in_pipeline_mode(
    dispatcher: StageDispatcher,
    cognitive_context: CognitiveContext,
):
    event_bus = RecordingEventBus()

    first = DemoStage("first")
    second = DemoStage("second")

    dispatcher.dispatch(
        context=cognitive_context,
        stages=[
            first,
            second,
        ],
        event_bus=event_bus,
    )

    assert [
        event[0]
        for event in event_bus.events
    ] == [
        KernelEventType.STAGE_STARTED.value,
        KernelEventType.STAGE_COMPLETED.value,
        KernelEventType.STAGE_STARTED.value,
        KernelEventType.STAGE_COMPLETED.value,
    ]


# =========================================================
# Failure handling
# =========================================================


def test_failed_stage_sets_failed_status(
    dispatcher: StageDispatcher,
    cognitive_context: CognitiveContext,
):
    stage = FailingStage("failing")

    with pytest.raises(
        RuntimeError,
        match="stage failed",
    ):
        dispatcher.dispatch(
            stage,
            cognitive_context,
        )

    assert stage.status == "failed"


def test_failed_stage_stores_error_message(
    dispatcher: StageDispatcher,
    cognitive_context: CognitiveContext,
):
    stage = FailingStage("failing")

    with pytest.raises(RuntimeError):
        dispatcher.dispatch(
            stage,
            cognitive_context,
        )

    assert stage.message == "stage failed"


def test_failed_stage_does_not_increment_executed(
    dispatcher: StageDispatcher,
    cognitive_context: CognitiveContext,
):
    stage = FailingStage("failing")

    with pytest.raises(RuntimeError):
        dispatcher.dispatch(
            stage,
            cognitive_context,
        )

    assert dispatcher.executed == 0


def test_failed_stage_reraises_original_exception(
    dispatcher: StageDispatcher,
    cognitive_context: CognitiveContext,
):
    stage = FailingStage("failing")

    with pytest.raises(
        RuntimeError,
        match="stage failed",
    ):
        dispatcher.dispatch(
            stage,
            cognitive_context,
        )


# =========================================================
# Diagnostics and reset
# =========================================================


def test_status_reflects_execution_count(
    dispatcher: StageDispatcher,
    stage: DemoStage,
    cognitive_context: CognitiveContext,
):
    dispatcher.dispatch(
        stage,
        cognitive_context,
    )

    assert dispatcher.status() == {
        "executed": 1,
    }


def test_reset_clears_execution_count(
    dispatcher: StageDispatcher,
    stage: DemoStage,
    cognitive_context: CognitiveContext,
):
    dispatcher.dispatch(
        stage,
        cognitive_context,
    )

    assert dispatcher.executed == 1

    dispatcher.reset()

    assert dispatcher.executed == 0


def test_reset_status_returns_zero(
    dispatcher: StageDispatcher,
):
    dispatcher.reset()

    assert dispatcher.status() == {
        "executed": 0,
    }


def test_reset_does_not_modify_stage(
    dispatcher: StageDispatcher,
    stage: DemoStage,
    cognitive_context: CognitiveContext,
):
    dispatcher.dispatch(
        stage,
        cognitive_context,
    )

    dispatcher.reset()

    assert stage.executions == 0
    assert stage.run_count == 1
    assert stage.status == "completed"


# =========================================================
# Representation
# =========================================================


def test_repr_contains_class_name(
    dispatcher: StageDispatcher,
):
    result = repr(dispatcher)

    assert "StageDispatcher" in result


def test_repr_contains_executed_count(
    dispatcher: StageDispatcher,
    stage: DemoStage,
    cognitive_context: CognitiveContext,
):
    dispatcher.dispatch(
        stage,
        cognitive_context,
    )

    result = repr(dispatcher)

    assert "executed=1" in result


# =========================================================
# API contract
# =========================================================


def test_dispatch_method_is_callable(
    dispatcher: StageDispatcher,
):
    assert callable(dispatcher.dispatch)


def test_status_method_is_callable(
    dispatcher: StageDispatcher,
):
    assert callable(dispatcher.status)


def test_reset_method_is_callable(
    dispatcher: StageDispatcher,
):
    assert callable(dispatcher.reset)


def test_dispatch_accepts_two_positional_arguments(
    dispatcher: StageDispatcher,
    stage: DemoStage,
    cognitive_context: CognitiveContext,
):
    result = dispatcher.dispatch(
        stage,
        cognitive_context,
    )

    assert result == "ok"


def test_dispatch_accepts_pipeline_keyword_arguments(
    dispatcher: StageDispatcher,
    stage: DemoStage,
    cognitive_context: CognitiveContext,
):
    result = dispatcher.dispatch(
        context=cognitive_context,
        stages=[stage],
    )

    assert result == "ok"
