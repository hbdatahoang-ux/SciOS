"""
SciOS End-to-End Pipeline Tests
===============================

Integration tests for the complete SciOS execution pipeline.

Pipeline

    Kernel
        ↓
    Planner
        ↓
    Scheduler
        ↓
    Runtime
        ↓
    Agent
        ↓
    QTC
        ↓
    Memory
        ↓
      Result
"""

from __future__ import annotations

import pytest

from scios.api.scios import SciOS


# ==========================================================
# Construction
# ==========================================================

def test_pipeline_construction() -> None:
    """
    SciOS should construct successfully.
    """

    os = SciOS()

    assert os is not None


# ==========================================================
# Boot
# ==========================================================

def test_pipeline_boot() -> None:
    """
    Entire system should boot.
    """

    os = SciOS()

    assert os.boot() is True


# ==========================================================
# Single Task
# ==========================================================

def test_single_task() -> None:
    """
    Execute one task.
    """

    os = SciOS()

    os.boot()

    result = os.run("ping")

    assert result is not None


# ==========================================================
# Multiple Tasks
# ==========================================================

def test_multiple_tasks() -> None:
    """
    Execute multiple tasks sequentially.
    """

    os = SciOS()

    os.boot()

    for i in range(20):

        result = os.run(f"task-{i}")

        assert result is not None


# ==========================================================
# Memory Persistence
# ==========================================================

def test_pipeline_memory() -> None:
    """
    Pipeline should remember previous tasks.
    """

    os = SciOS()

    os.boot()

    os.run("first")

    os.run("second")

    memory = os.kernel.context.memory

    assert len(memory) >= 2


# ==========================================================
# Scheduler Queue
# ==========================================================

def test_scheduler_pipeline() -> None:
    """
    Scheduler should become empty after execution.
    """

    os = SciOS()

    os.boot()

    for i in range(10):

        os.run(i)

    scheduler = os.kernel.scheduler

    assert scheduler.empty()


# ==========================================================
# Runtime Counter
# ==========================================================

def test_runtime_counter() -> None:
    """
    Runtime should count executed tasks.
    """

    os = SciOS()

    os.boot()

    for i in range(5):

        os.run(i)

    runtime = os.kernel.runtime

    assert runtime.status()["tasks_executed"] == 5


# ==========================================================
# Agent State
# ==========================================================

def test_agent_pipeline() -> None:
    """
    Agent should finish idle.
    """

    os = SciOS()

    os.boot()

    os.run("hello")

    agent = os.kernel.agent

    assert agent.status()["state"] == "idle"


# ==========================================================
# Kernel Status
# ==========================================================

def test_kernel_pipeline_status() -> None:
    """
    Kernel should remain running.
    """

    os = SciOS()

    os.boot()

    os.run("task")

    assert os.kernel.status()["state"] == "running"


# ==========================================================
# Shutdown
# ==========================================================

def test_pipeline_shutdown() -> None:
    """
    Entire pipeline should shutdown correctly.
    """

    os = SciOS()

    os.boot()

    os.shutdown()

    assert os.kernel.status()["state"] == "stopped"


# ==========================================================
# Boot -> Run -> Shutdown Cycles
# ==========================================================

@pytest.mark.parametrize(
    "cycles",
    [
        1,
        3,
        5,
    ],
)
def test_pipeline_cycles(
    cycles: int,
) -> None:
    """
    Entire system should survive repeated cycles.
    """

    os = SciOS()

    for _ in range(cycles):

        assert os.boot() is True

        result = os.run("hello")

        assert result is not None

        assert os.shutdown() is True


# ==========================================================
# Run Without Boot
# ==========================================================

def test_pipeline_requires_boot() -> None:
    """
    Running before boot should fail.
    """

    os = SciOS()

    with pytest.raises(Exception):

        os.run("task")


# ==========================================================
# End-to-End Stability
# ==========================================================

def test_pipeline_stress() -> None:
    """
    Execute many tasks without failure.
    """

    os = SciOS()

    os.boot()

    for i in range(100):

        result = os.run(i)

        assert result is not None

    assert os.kernel.status()["state"] == "running"