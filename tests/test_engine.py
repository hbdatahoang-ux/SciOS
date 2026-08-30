"""
SciOS Runtime Execution Engine Tests
====================================

Contract tests for ExecutionEngine.
"""

from __future__ import annotations

from typing import Any

import pytest

from scios.runtime.engine import ExecutionEngine
from scios.runtime.exceptions import InvalidTaskError
from scios.runtime.result import ExecutionResult


# ==========================================================
# Test Doubles
# ==========================================================

class SuccessWorker:

    def __init__(self) -> None:
        self.initialized = False
        self.shutdown_called = False
        self.executed: list[Any] = []

    def initialize(self) -> None:
        self.initialized = True

    def shutdown(self) -> None:
        self.shutdown_called = True

    def reset(self) -> None:
        self.executed.clear()

    def status(self) -> dict[str, Any]:
        return {}

    def execute(self, context):
        self.executed.append(context.task)
        return ExecutionResult.ok("ok")


class FailureWorker:

    def initialize(self) -> None:
        pass

    def shutdown(self) -> None:
        pass

    def reset(self) -> None:
        pass

    def status(self) -> dict[str, Any]:
        return {}

    def execute(self, context):
        return ExecutionResult.fail(
            RuntimeError("worker failure")
        )


class RaisingWorker:

    def initialize(self) -> None:
        pass

    def shutdown(self) -> None:
        pass

    def reset(self) -> None:
        pass

    def status(self) -> dict[str, Any]:
        return {}

    def execute(self, context):
        raise ValueError("boom")


class DummyEventBus:

    def __init__(self) -> None:
        self.events: list[tuple[str, dict[str, Any]]] = []

    def publish(self, topic, **payload) -> None:
        self.events.append((topic, payload))


# ==========================================================
# Construction
# ==========================================================

def test_engine_construction() -> None:

    engine = ExecutionEngine()

    assert engine is not None
    assert engine.state == "created"
    assert engine.executions == 0
    assert engine.pending == 0


def test_engine_components() -> None:

    worker = SuccessWorker()

    engine = ExecutionEngine(
        worker=worker,
    )

    assert engine.scheduler is not None
    assert engine.worker is worker
    assert engine.pipeline is None
    assert engine.hooks is not None


# ==========================================================
# Lifecycle
# ==========================================================

def test_initialize() -> None:

    worker = SuccessWorker()

    engine = ExecutionEngine(
        worker=worker,
    )

    result = engine.initialize()

    assert result is engine
    assert engine.state == "idle"
    assert worker.initialized


def test_initialize_is_idempotent() -> None:

    engine = ExecutionEngine()

    assert engine.initialize() is engine
    assert engine.initialize() is engine

    assert engine.state == "idle"


def test_shutdown() -> None:

    worker = SuccessWorker()

    engine = ExecutionEngine(
        worker=worker,
    )

    engine.initialize()

    result = engine.shutdown()

    assert result is None
    assert engine.state == "stopped"
    assert worker.shutdown_called


def test_shutdown_is_idempotent() -> None:

    engine = ExecutionEngine()

    engine.initialize()
    engine.shutdown()
    engine.shutdown()

    assert engine.state == "stopped"


def test_reset() -> None:

    engine = ExecutionEngine(
        worker=SuccessWorker(),
    )

    engine.run("task")

    assert engine.executions == 1

    result = engine.reset()

    assert result is engine
    assert engine.state == "idle"
    assert engine.executions == 0


# ==========================================================
# Context
# ==========================================================

def test_create_context() -> None:

    engine = ExecutionEngine()

    context = engine.create_context(
        "task",
        metadata={
            "source": "test",
        },
    )

    assert context.task == "task"
    assert context.metadata == {
        "source": "test",
    }


def test_create_context_rejects_none() -> None:

    engine = ExecutionEngine()

    with pytest.raises(InvalidTaskError):
        engine.create_context(None)


# ==========================================================
# Submit
# ==========================================================

def test_submit() -> None:

    engine = ExecutionEngine()

    context = engine.submit(
        "task",
        metadata={
            "x": 1,
        },
    )

    assert context.task == "task"
    assert context.metadata["x"] == 1
    assert engine.pending == 1


def test_submit_multiple_tasks() -> None:

    engine = ExecutionEngine()

    engine.submit("A")
    engine.submit("B")
    engine.submit("C")

    assert engine.pending == 3


# ==========================================================
# Successful Execution
# ==========================================================

def test_run_success() -> None:

    worker = SuccessWorker()

    engine = ExecutionEngine(
        worker=worker,
    )

    context = engine.run("task")

    assert context.task == "task"
    assert context.status == "completed"
    assert context.success
    assert context.result is not None
    assert context.result_value == "ok"

    assert engine.executions == 1
    assert engine.state == "idle"


def test_execute_returns_execution_result() -> None:

    engine = ExecutionEngine(
        worker=SuccessWorker(),
    )

    result = engine.execute("task")

    assert isinstance(
        result,
        ExecutionResult,
    )

    assert result.success
    assert result.value == "ok"


def test_run_multiple_tasks() -> None:

    engine = ExecutionEngine(
        worker=SuccessWorker(),
    )

    for _ in range(5):
        context = engine.run("task")
        assert context.success

    assert engine.executions == 5
    assert engine.pending == 0


# ==========================================================
# Failure Result
# ==========================================================

def test_run_failure_result() -> None:

    engine = ExecutionEngine(
        worker=FailureWorker(),
    )

    context = engine.run("task")

    assert context.status == "failed"
    assert context.failed
    assert context.result is not None
    assert not context.result.success

    assert engine.executions == 0
    assert engine.state == "idle"


# ==========================================================
# Exception Handling
# ==========================================================

def test_run_worker_exception() -> None:

    engine = ExecutionEngine(
        worker=RaisingWorker(),
    )

    with pytest.raises(ValueError, match="boom"):
        engine.run("task")

    assert engine.executions == 0
    assert engine.state == "idle"


# ==========================================================
# Hooks
# ==========================================================

def test_register_hook() -> None:

    engine = ExecutionEngine()

    calls: list[str] = []

    def handler(context, *args) -> None:
        calls.append(context.task)

    result = engine.register_hook(
        "before_submit",
        handler,
    )

    assert result is not None

    engine.submit("task")

    assert calls == ["task"]


def test_unknown_hook_rejected() -> None:

    engine = ExecutionEngine()

    with pytest.raises(ValueError):
        engine.register_hook(
            "unknown_hook",
            lambda *_: None,
        )


def test_execution_hooks() -> None:

    engine = ExecutionEngine(
        worker=SuccessWorker(),
    )

    events: list[str] = []

    engine.register_hook(
        "execution_started",
        lambda *_: events.append("started"),
    )

    engine.register_hook(
        "before_execute",
        lambda *_: events.append("before_execute"),
    )

    engine.register_hook(
        "after_execute",
        lambda *_: events.append("after_execute"),
    )

    engine.register_hook(
        "execution_completed",
        lambda *_: events.append("completed"),
    )

    engine.register_hook(
        "after_success",
        lambda *_: events.append("success"),
    )

    engine.register_hook(
        "execution_finished",
        lambda *_: events.append("finished"),
    )

    engine.run("task")

    assert events == [
        "started",
        "before_execute",
        "after_execute",
        "completed",
        "success",
        "finished",
    ]


def test_failure_hooks() -> None:

    engine = ExecutionEngine(
        worker=FailureWorker(),
    )

    events: list[str] = []

    engine.register_hook(
        "execution_failed",
        lambda *_: events.append("failed"),
    )

    engine.register_hook(
        "after_failure",
        lambda *_: events.append("after_failure"),
    )

    engine.register_hook(
        "execution_finished",
        lambda *_: events.append("finished"),
    )

    engine.run("task")

    assert events == [
        "failed",
        "after_failure",
        "finished",
    ]


# ==========================================================
# EventBus
# ==========================================================

def test_event_bus_success() -> None:

    bus = DummyEventBus()

    engine = ExecutionEngine(
        worker=SuccessWorker(),
        event_bus=bus,
    )

    engine.run("task")

    topics = [
        topic
        for topic, _ in bus.events
    ]

    assert "task.submitted" in topics
    assert "task.completed" in topics


def test_event_bus_failure() -> None:

    bus = DummyEventBus()

    engine = ExecutionEngine(
        worker=FailureWorker(),
        event_bus=bus,
    )

    engine.run("task")

    topics = [
        topic
        for topic, _ in bus.events
    ]

    assert "task.submitted" in topics
    assert "task.failed" in topics


# ==========================================================
# Diagnostics
# ==========================================================

def test_status() -> None:

    engine = ExecutionEngine(
        worker=SuccessWorker(),
    )

    engine.run("task")

    status = engine.status()

    assert isinstance(
        status,
        dict,
    )

    required = {
        "state",
        "executions",
        "scheduler",
        "worker",
        "pending",
        "hooks",
    }

    assert required.issubset(
        status.keys()
    )


# ==========================================================
# Protocol
# ==========================================================

def test_len_matches_executions() -> None:

    engine = ExecutionEngine(
        worker=SuccessWorker(),
    )

    assert len(engine) == 0

    engine.run("A")
    engine.run("B")

    assert len(engine) == 2


def test_bool_state() -> None:

    engine = ExecutionEngine()

    assert not engine

    engine.initialize()

    assert engine

    engine.shutdown()

    assert not engine


def test_repr() -> None:

    engine = ExecutionEngine()

    text = repr(engine)

    assert "ExecutionEngine" in text
    assert "state='created'" in text
    assert "executions=0" in text
