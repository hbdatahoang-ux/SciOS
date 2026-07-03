"""
SciOS Runtime Tests
===================

Unit tests for the SciOS Runtime Engine.

The runtime is responsible for executing tasks after the kernel has
been booted. These tests validate the runtime contract independent of
the kernel lifecycle.
"""

from __future__ import annotations

import pytest

from scios.kernel.runtime.engine import Runtime


# ==========================================================
# Construction
# ==========================================================

def test_runtime_construction() -> None:
    """
    Runtime should be constructible.
    """

    runtime = Runtime()

    assert runtime is not None


# ==========================================================
# Initial Status
# ==========================================================

def test_runtime_initial_status() -> None:
    """
    Runtime should start idle.
    """

    runtime = Runtime()

    status = runtime.status()

    assert isinstance(status, dict)
    assert status["running"] is False


# ==========================================================
# Start
# ==========================================================

def test_runtime_start() -> None:
    """
    Runtime should start successfully.
    """

    runtime = Runtime()

    assert runtime.start() is True

    status = runtime.status()

    assert status["running"] is True


# ==========================================================
# Stop
# ==========================================================

def test_runtime_stop() -> None:
    """
    Runtime should stop successfully.
    """

    runtime = Runtime()

    runtime.start()

    assert runtime.stop() is True

    status = runtime.status()

    assert status["running"] is False


# ==========================================================
# Start Idempotence
# ==========================================================

def test_runtime_double_start() -> None:
    """
    Starting twice should be safe.
    """

    runtime = Runtime()

    assert runtime.start() is True
    assert runtime.start() is True

    assert runtime.status()["running"] is True


# ==========================================================
# Stop Idempotence
# ==========================================================

def test_runtime_double_stop() -> None:
    """
    Stopping twice should be safe.
    """

    runtime = Runtime()

    runtime.start()

    assert runtime.stop() is True
    assert runtime.stop() is True

    assert runtime.status()["running"] is False


# ==========================================================
# Execute
# ==========================================================

def test_runtime_execute() -> None:
    """
    Runtime should execute a simple task.
    """

    runtime = Runtime()

    runtime.start()

    result = runtime.execute("ping")

    assert result is not None


# ==========================================================
# Execute Multiple Tasks
# ==========================================================

def test_runtime_multiple_tasks() -> None:
    """
    Runtime should execute multiple tasks.
    """

    runtime = Runtime()

    runtime.start()

    for i in range(20):

        result = runtime.execute(f"task-{i}")

        assert result is not None


# ==========================================================
# Execute Without Start
# ==========================================================

def test_execute_without_start() -> None:
    """
    Runtime should reject execution while stopped.
    """

    runtime = Runtime()

    with pytest.raises(Exception):

        runtime.execute("task")


# ==========================================================
# Status Schema
# ==========================================================

def test_runtime_status_schema() -> None:
    """
    Runtime should expose a stable status schema.
    """

    runtime = Runtime()

    runtime.start()

    status = runtime.status()

    required = {
        "running",
        "tasks_executed",
    }

    assert required.issubset(status.keys())


# ==========================================================
# Task Counter
# ==========================================================

def test_runtime_task_counter() -> None:
    """
    Runtime should count executed tasks.
    """

    runtime = Runtime()

    runtime.start()

    for i in range(5):
        runtime.execute(f"task-{i}")

    status = runtime.status()

    assert status["tasks_executed"] == 5


# ==========================================================
# Lifecycle
# ==========================================================

@pytest.mark.parametrize("cycles", [1, 3, 5])
def test_runtime_lifecycle(cycles: int) -> None:
    """
    Runtime should survive repeated start/stop cycles.
    """

    runtime = Runtime()

    for _ in range(cycles):

        assert runtime.start() is True
        assert runtime.status()["running"] is True

        assert runtime.stop() is True
        assert runtime.status()["running"] is False