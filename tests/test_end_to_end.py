"""
SciOS End-to-End Tests
======================

End-to-end tests for the public SciOS API.

These tests validate the complete user-facing workflow from system
startup to task execution and shutdown without accessing internal
components directly.
"""

from __future__ import annotations

import pytest

from scios.api.scios import SciOS


# ==========================================================
# Full Lifecycle
# ==========================================================

def test_full_lifecycle() -> None:
    """
    Boot → Run → Shutdown.
    """

    os = SciOS()

    assert os.boot() is True

    result = os.run("ping")

    assert result is not None

    assert os.shutdown() is True


# ==========================================================
# Multiple Tasks
# ==========================================================

def test_multiple_tasks() -> None:
    """
    Execute multiple user tasks.
    """

    os = SciOS()

    os.boot()

    for i in range(20):

        result = os.run(f"task-{i}")

        assert result is not None

    os.shutdown()


# ==========================================================
# Repeated Sessions
# ==========================================================

@pytest.mark.parametrize(
    "sessions",
    [
        1,
        3,
        5,
    ],
)
def test_repeated_sessions(
    sessions: int,
) -> None:
    """
    Multiple independent sessions.
    """

    for _ in range(sessions):

        os = SciOS()

        assert os.boot()

        assert os.run("hello") is not None

        assert os.shutdown()


# ==========================================================
# Sequential Requests
# ==========================================================

def test_sequential_requests() -> None:
    """
    Sequential user requests.
    """

    os = SciOS()

    os.boot()

    requests = [
        "hello",
        "compute",
        "reason",
        "store",
        "retrieve",
    ]

    for request in requests:

        result = os.run(request)

        assert result is not None

    os.shutdown()


# ==========================================================
# Stress
# ==========================================================

def test_stress_execution() -> None:
    """
    Execute many requests.
    """

    os = SciOS()

    os.boot()

    for i in range(100):

        result = os.run(i)

        assert result is not None

    os.shutdown()


# ==========================================================
# Empty Task
# ==========================================================

def test_empty_task() -> None:
    """
    Empty task should fail.
    """

    os = SciOS()

    os.boot()

    with pytest.raises(Exception):

        os.run("")

    os.shutdown()


# ==========================================================
# None Task
# ==========================================================

def test_none_task() -> None:
    """
    None task should fail.
    """

    os = SciOS()

    os.boot()

    with pytest.raises(Exception):

        os.run(None)

    os.shutdown()


# ==========================================================
# Run Before Boot
# ==========================================================

def test_requires_boot() -> None:
    """
    Running before boot should fail.
    """

    os = SciOS()

    with pytest.raises(Exception):

        os.run("task")


# ==========================================================
# Shutdown Before Boot
# ==========================================================

def test_shutdown_before_boot() -> None:
    """
    Shutdown without boot should be safe.
    """

    os = SciOS()

    assert os.shutdown() is True


# ==========================================================
# Double Boot
# ==========================================================

def test_double_boot() -> None:
    """
    Boot should be idempotent.
    """

    os = SciOS()

    assert os.boot()

    assert os.boot()

    os.shutdown()


# ==========================================================
# Double Shutdown
# ==========================================================

def test_double_shutdown() -> None:
    """
    Shutdown should be idempotent.
    """

    os = SciOS()

    os.boot()

    assert os.shutdown()

    assert os.shutdown()


# ==========================================================
# User Scenario
# ==========================================================

def test_user_workflow() -> None:
    """
    Simulate a typical user workflow.
    """

    os = SciOS()

    assert os.boot()

    tasks = [
        "Create plan",
        "Analyze data",
        "Store result",
        "Summarize findings",
    ]

    outputs = []

    for task in tasks:

        outputs.append(os.run(task))

    assert len(outputs) == len(tasks)

    assert all(output is not None for output in outputs)

    assert os.shutdown()