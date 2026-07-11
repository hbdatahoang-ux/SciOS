"""
SciOS End-to-End Tests
======================

End-to-end tests for the complete SciOS execution flow.

System Flow

    User
      │
      ▼
    SciOS API
      │
      ▼
    Kernel
      │
      ▼
 Runtime Engine
      │
      ▼
 Pipeline
      │
      ▼
 Result
"""

from __future__ import annotations

import pytest

from scios.api.scios import SciOS


# ==========================================================
# Construction
# ==========================================================

def test_scios_creation() -> None:
    """
    SciOS should construct successfully.
    """

    os = SciOS()

    assert os is not None


# ==========================================================
# Boot
# ==========================================================

def test_boot() -> None:
    """
    SciOS should boot successfully.
    """

    os = SciOS()

    assert os.boot() is True


# ==========================================================
# Shutdown
# ==========================================================

def test_shutdown() -> None:
    """
    SciOS should shutdown successfully.
    """

    os = SciOS()

    os.boot()

    assert os.shutdown() is True


# ==========================================================
# Single Task
# ==========================================================

def test_single_task() -> None:
    """
    Execute one task.
    """

    os = SciOS()

    os.boot()

    result = os.run(
        "hello world"
    )

    assert result is not None


# ==========================================================
# Multiple Tasks
# ==========================================================

def test_multiple_tasks() -> None:
    """
    Execute multiple tasks.
    """

    os = SciOS()

    os.boot()

    for i in range(20):

        result = os.run(
            f"task-{i}"
        )

        assert result is not None


# ==========================================================
# Boot Required
# ==========================================================

def test_run_requires_boot() -> None:
    """
    Running before boot should fail.
    """

    os = SciOS()

    with pytest.raises(Exception):

        os.run("task")


# ==========================================================
# Repeated Boot Cycles
# ==========================================================

@pytest.mark.parametrize(
    "cycles",
    [
        1,
        3,
        5,
    ],
)
def test_boot_cycles(
    cycles: int,
) -> None:
    """
    SciOS should survive repeated boot cycles.
    """

    os = SciOS()

    for _ in range(cycles):

        assert os.boot() is True

        result = os.run(
            "benchmark"
        )

        assert result is not None

        assert os.shutdown() is True


# ==========================================================
# Stress
# ==========================================================

def test_many_tasks() -> None:
    """
    Execute many tasks.
    """

    os = SciOS()

    os.boot()

    for i in range(100):

        result = os.run(
            f"task-{i}"
        )

        assert result is not None


# ==========================================================
# Consecutive Runs
# ==========================================================

def test_consecutive_runs() -> None:
    """
    Runtime should support consecutive execution.
    """

    os = SciOS()

    os.boot()

    results = []

    for i in range(10):

        results.append(
            os.run(f"job-{i}")
        )

    assert len(results) == 10

    assert all(r is not None for r in results)


# ==========================================================
# Shutdown After Workload
# ==========================================================

def test_shutdown_after_workload() -> None:
    """
    System should shutdown cleanly after workload.
    """

    os = SciOS()

    os.boot()

    for i in range(25):

        os.run(i)

    assert os.shutdown() is True