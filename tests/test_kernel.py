"""
SciOS Kernel Tests
==================

Unit tests for the SciOS kernel.

These tests validate the core kernel lifecycle,
runtime interface, and state transitions independently
from the public SciOS API.
"""

from __future__ import annotations

import pytest

from scios.kernel.kernel import Kernel


# ==========================================================
# Construction
# ==========================================================

def test_kernel_construction() -> None:
    """
    Kernel should be constructible.
    """

    kernel = Kernel()

    assert kernel is not None


# ==========================================================
# Initial State
# ==========================================================

def test_initial_state() -> None:
    """
    Newly created kernel should not be booted.
    """

    kernel = Kernel()

    status = kernel.status()

    assert status["booted"] is False
    assert status["state"] == "created"


# ==========================================================
# Boot
# ==========================================================

def test_kernel_boot() -> None:
    """
    Kernel should boot successfully.
    """

    kernel = Kernel()

    assert kernel.boot() is True

    status = kernel.status()

    assert status["booted"] is True
    assert status["state"] == "running"


# ==========================================================
# Shutdown
# ==========================================================

def test_kernel_shutdown() -> None:
    """
    Kernel should shutdown successfully.
    """

    kernel = Kernel()

    kernel.boot()

    assert kernel.shutdown() is True

    status = kernel.status()

    assert status["booted"] is False
    assert status["state"] == "stopped"


# ==========================================================
# Boot Idempotence
# ==========================================================

def test_kernel_double_boot() -> None:
    """
    Booting twice should be safe.
    """

    kernel = Kernel()

    assert kernel.boot() is True
    assert kernel.boot() is True

    assert kernel.status()["state"] == "running"


# ==========================================================
# Shutdown Idempotence
# ==========================================================

def test_kernel_double_shutdown() -> None:
    """
    Shutdown twice should be safe.
    """

    kernel = Kernel()

    kernel.boot()

    assert kernel.shutdown() is True
    assert kernel.shutdown() is True

    assert kernel.status()["state"] == "stopped"


# ==========================================================
# Lifecycle Cycles
# ==========================================================

@pytest.mark.parametrize(
    "cycles",
    [1, 3, 5],
)
def test_kernel_lifecycle_cycles(
    cycles: int,
) -> None:
    """
    Kernel should survive repeated lifecycle cycles.
    """

    kernel = Kernel()

    for _ in range(cycles):

        assert kernel.boot() is True
        assert kernel.status()["state"] == "running"

        assert kernel.shutdown() is True
        assert kernel.status()["state"] == "stopped"


# ==========================================================
# Run Before Boot
# ==========================================================

def test_run_before_boot() -> None:
    """
    Running before boot should fail.
    """

    kernel = Kernel()

    with pytest.raises(Exception):

        kernel.run("task")


# ==========================================================
# Run After Boot
# ==========================================================

def test_run_after_boot() -> None:
    """
    Kernel should execute a task after boot.
    """

    kernel = Kernel()

    kernel.boot()

    result = kernel.run("ping")

    assert result is not None


# ==========================================================
# Status Schema
# ==========================================================

def test_status_schema() -> None:
    """
    Kernel status should expose a stable schema.
    """

    kernel = Kernel()

    kernel.boot()

    status = kernel.status()

    required = {
        "state",
        "booted",
        "version",
    }

    assert required.issubset(status.keys())


# ==========================================================
# Version
# ==========================================================

def test_kernel_version() -> None:
    """
    Kernel version should be available.
    """

    kernel = Kernel()

    status = kernel.status()

    assert isinstance(status["version"], str)
    assert len(status["version"]) > 0


# ==========================================================
# Multiple Run Calls
# ==========================================================

def test_multiple_runs() -> None:
    """
    Kernel should support multiple sequential tasks.
    """

    kernel = Kernel()

    kernel.boot()

    for i in range(10):

        result = kernel.run(f"task-{i}")

        assert result is not None