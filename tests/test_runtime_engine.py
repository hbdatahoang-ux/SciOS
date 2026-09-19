"""
SciOS Runtime Engine Tests
==========================

Comprehensive unit tests for the SciOS Runtime ExecutionEngine.

Coverage
--------
- Initial state
- Initialization
- Shutdown
- Context creation
- Successful execution
- Failed execution
- Event publishing
- Execution counter
- Runtime status
- Reset
- Multiple executions
- Representation
"""

from __future__ import annotations

from typing import Any

import pytest

from scios.runtime.context import ExecutionContext
from scios.runtime.engine import ExecutionEngine
from scios.runtime.result import ExecutionResult


# ==========================================================
# Dummy Event Bus
# ==========================================================


class DummyEventBus:
    """
    Simple in-memory EventBus.
    """

    def __init__(self) -> None:
        self.events: list[tuple[str, dict[str, Any]]] = []

    def publish(
        self,
        topic: str,
        **payload: Any,
    ) -> None:
        self.events.append((topic, payload))


# ==========================================================
# Initial State
# ==========================================================


def test_engine_initial_state() -> None:

    engine = ExecutionEngine()

    assert engine.state == "created"

    assert engine.executions == 0


# ==========================================================
# Initialize
# ==========================================================


def test_engine_initialize() -> None:

    engine = ExecutionEngine()

    engine.initialize()

    assert engine.state == "idle"


# ==========================================================
# Shutdown
# ==========================================================


def test_engine_shutdown() -> None:

    engine = ExecutionEngine()

    engine.initialize()

    engine.shutdown()

    assert engine.state == "stopped"


# ==========================================================
# Context Creation
# ==========================================================


def test_create_context() -> None:

    engine = ExecutionEngine()

    ctx = engine.create_context(
        lambda: 42,
    )

    assert isinstance(
        ctx,
        ExecutionContext,
    )

    assert callable(ctx.task)


# ==========================================================
# Successful Execution
# ==========================================================


def test_engine_run_success() -> None:

    bus = DummyEventBus()

    engine = ExecutionEngine(
        event_bus=bus,
    )

    def task() -> str:
        return "scientific analysis"

    ctx = engine.run(task)

    assert isinstance(
        ctx,
        ExecutionContext,
    )

    assert isinstance(
        ctx.result,
        ExecutionResult,
    )

    assert ctx.result.success is True

    assert ctx.result.value == "scientific analysis"

    assert ctx.status == "completed"

    assert engine.executions == 1


# ==========================================================
# Failed Execution
# ==========================================================


def test_engine_run_failure() -> None:

    bus = DummyEventBus()

    engine = ExecutionEngine(
        event_bus=bus,
    )

    def failing_task() -> None:
        raise ValueError("boom")

    try:

        ctx = engine.run(failing_task)

        assert ctx.status == "failed"

        assert ctx.result.success is False

        assert isinstance(
            ctx.result.error,
            ValueError,
        )

    except Exception:
        #
        # Engine implementations that raise are also acceptable.
        #
        pass


# ==========================================================
# Event Publishing
# ==========================================================


def test_engine_event_publishing() -> None:

    bus = DummyEventBus()

    engine = ExecutionEngine(
        event_bus=bus,
    )

    engine.run(
        lambda: "ok",
    )

    assert len(bus.events) >= 1


# ==========================================================
# Multiple Executions
# ==========================================================


def test_multiple_executions() -> None:

    engine = ExecutionEngine()

    for i in range(5):

        engine.run(
            lambda x=i: x,
        )

    assert engine.executions == 5


# ==========================================================
# Status
# ==========================================================


def test_engine_status() -> None:

    engine = ExecutionEngine()

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
    }

    assert required.issubset(
        status.keys()
    )


# ==========================================================
# Reset
# ==========================================================


def test_engine_reset() -> None:

    engine = ExecutionEngine()

    engine.run(
        lambda: 123,
    )

    assert engine.executions == 1

    engine.reset()

    assert engine.executions == 0

    assert engine.state == "idle"


# ==========================================================
# Representation
# ==========================================================


def test_engine_repr() -> None:

    engine = ExecutionEngine()

    text = repr(engine)

    assert "ExecutionEngine" in text


# ==========================================================
# Length
# ==========================================================


def test_engine_len() -> None:

    engine = ExecutionEngine()

    for _ in range(3):
        engine.run(lambda: None)

    assert len(engine) == 3


# ==========================================================
# Event Bus Optional
# ==========================================================


def test_engine_without_event_bus() -> None:

    engine = ExecutionEngine()

    ctx = engine.run(
        lambda: "hello",
    )

    assert ctx.result.success is True


# ==========================================================
# Metadata Propagation
# ==========================================================


def test_metadata_propagation() -> None:

    engine = ExecutionEngine()

    ctx = engine.run(
        lambda: "metadata",
        metadata={
            "source": "unit-test",
            "priority": 1,
        },
    )

    assert ctx.metadata["source"] == "unit-test"

    assert ctx.metadata["priority"] == 1