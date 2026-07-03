"""
SciOS Boot Tests
================

Integration tests for the SciOS boot sequence.

These tests verify that the kernel can be created,
booted, queried for status, and shut down cleanly.
"""

from __future__ import annotations

import pytest

from scios.api.scios import SciOS


# ==========================================================
# Construction
# ==========================================================

def test_create_scios() -> None:
    """
    SciOS instance should be constructible.
    """

    os = SciOS()

    assert os is not None
    assert os.kernel is not None


# ==========================================================
# Version
# ==========================================================

def test_version() -> None:
    """
    Version should be a non-empty string.
    """

    os = SciOS()

    assert isinstance(os.version, str)
    assert len(os.version) > 0


# ==========================================================
# Boot
# ==========================================================

def test_boot() -> None:
    """
    Kernel should boot successfully.
    """

    os = SciOS()

    result = os.boot()

    assert result is True

    status = os.status()

    assert isinstance(status, dict)
    assert status["state"] == "running"


# ==========================================================
# Shutdown
# ==========================================================

def test_shutdown() -> None:
    """
    Kernel should shutdown successfully.
    """

    os = SciOS()

    os.boot()

    result = os.shutdown()

    assert result is True

    status = os.status()

    assert status["state"] == "stopped"


# ==========================================================
# Boot Idempotence
# ==========================================================

def test_double_boot() -> None:
    """
    Booting twice should not crash.
    """

    os = SciOS()

    os.boot()
    result = os.boot()

    assert result is True

    assert os.status()["state"] == "running"


# ==========================================================
# Shutdown Idempotence
# ==========================================================

def test_double_shutdown() -> None:
    """
    Shutting down twice should not crash.
    """

    os = SciOS()

    os.boot()

    os.shutdown()

    result = os.shutdown()

    assert result is True

    assert os.status()["state"] == "stopped"


# ==========================================================
# Boot / Shutdown Cycle
# ==========================================================

@pytest.mark.parametrize(
    "cycles",
    [
        1,
        3,
        5,
    ],
)
def test_boot_shutdown_cycles(
    cycles: int,
) -> None:
    """
    Kernel should survive repeated lifecycle transitions.
    """

    os = SciOS()

    for _ in range(cycles):

        assert os.boot() is True
        assert os.status()["state"] == "running"

        assert os.shutdown() is True
        assert os.status()["state"] == "stopped"


# ==========================================================
# Run Without Boot
# ==========================================================

def test_run_requires_boot() -> None:
    """
    Running without boot should fail.
    """

    os = SciOS()

    with pytest.raises(Exception):
        os.run("hello")


# ==========================================================
# Boot Then Run
# ==========================================================

def test_run_after_boot() -> None:
    """
    Runtime should accept a simple task after boot.
    """

    os = SciOS()

    os.boot()

    result = os.run("ping")

    assert result is not None


# ==========================================================
# Status Interface
# ==========================================================

def test_status_schema() -> None:
    """
    Status should expose a stable schema.
    """

    os = SciOS()

    os.boot()

    status = os.status()

    assert isinstance(status, dict)

    required = {
        "state",
        "booted",
        "version",
    }

    assert required.issubset(status.keys())