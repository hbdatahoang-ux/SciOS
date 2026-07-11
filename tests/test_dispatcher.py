"""
SciOS Dispatcher Tests
======================

Unit tests for the Kernel Dispatcher.
"""

from __future__ import annotations

from typing import Any

import pytest

from scios.kernel.dispatcher import Dispatcher
from scios.runtime import ExecutionContext


# ==========================================================
# Test Doubles
# ==========================================================

class DummyScheduler:
    """
    Minimal scheduler used for testing.
    """

    def __init__(self) -> None:
        self._queue: list[Any] = []

    def submit(self, task: Any) -> None:
        self._queue.append(task)

    def next(self) -> Any | None:
        if not self._queue:
            return None
        return self._queue.pop(0)

    def __len__(self) -> int:
        return len(self._queue)


class DummyExecutionEngine:
    """
    Minimal execution engine used for testing.
    """

    def __init__(self) -> None:
        self.calls: list[Any] = []

    def run(self, task: Any) -> ExecutionContext:
        self.calls.append(task)

        ctx = ExecutionContext(task)
        ctx.status = "completed"
        ctx.set_result(task)

        return ctx


# ==========================================================
# Fixtures
# ==========================================================

@pytest.fixture
def scheduler() -> DummyScheduler:
    return DummyScheduler()


@pytest.fixture
def engine() -> DummyExecutionEngine:
    return DummyExecutionEngine()


@pytest.fixture
def dispatcher(
    scheduler: DummyScheduler,
    engine: DummyExecutionEngine,
) -> Dispatcher:
    return Dispatcher(
        scheduler=scheduler,
        engine=engine,
    )


# ==========================================================
# Construction
# ==========================================================

def test_dispatcher_creation(
    dispatcher: Dispatcher,
) -> None:

    assert dispatcher is not None


# ==========================================================
# Direct Dispatch
# ==========================================================

def test_dispatch(
    dispatcher: Dispatcher,
    engine: DummyExecutionEngine,
) -> None:

    ctx = dispatcher.dispatch("hello")

    assert ctx.status == "completed"
    assert ctx.result == "hello"

    assert engine.calls == [
        "hello",
    ]


# ==========================================================
# Scheduler Dispatch
# ==========================================================

def test_dispatch_next(
    dispatcher: Dispatcher,
    scheduler: DummyScheduler,
    engine: DummyExecutionEngine,
) -> None:

    scheduler.submit("task-1")

    ctx = dispatcher.dispatch_next()

    assert ctx is not None

    assert ctx.result == "task-1"

    assert engine.calls == [
        "task-1",
    ]


# ==========================================================
# Empty Queue
# ==========================================================

def test_dispatch_next_empty_queue(
    dispatcher: Dispatcher,
) -> None:

    assert dispatcher.dispatch_next() is None


# ==========================================================
# Missing Engine
# ==========================================================

def test_dispatch_without_engine(
    scheduler: DummyScheduler,
) -> None:

    dispatcher = Dispatcher(
        scheduler=scheduler,
    )

    with pytest.raises(RuntimeError):
        dispatcher.dispatch("task")


def test_dispatch_next_without_engine(
    scheduler: DummyScheduler,
) -> None:

    scheduler.submit("task")

    dispatcher = Dispatcher(
        scheduler=scheduler,
    )

    with pytest.raises(RuntimeError):
        dispatcher.dispatch_next()


# ==========================================================
# Multiple Tasks
# ==========================================================

def test_dispatch_multiple_tasks(
    dispatcher: Dispatcher,
    scheduler: DummyScheduler,
    engine: DummyExecutionEngine,
) -> None:

    for i in range(5):
        scheduler.submit(f"task-{i}")

    results = []

    while True:

        ctx = dispatcher.dispatch_next()

        if ctx is None:
            break

        results.append(ctx.result)

    assert results == [
        "task-0",
        "task-1",
        "task-2",
        "task-3",
        "task-4",
    ]

    assert engine.calls == results


# ==========================================================
# Queue Length
# ==========================================================

def test_dispatcher_length(
    dispatcher: Dispatcher,
    scheduler: DummyScheduler,
) -> None:

    scheduler.submit("a")
    scheduler.submit("b")
    scheduler.submit("c")

    assert len(dispatcher) == 3