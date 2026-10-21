"""
SciOS Kernel Tests
==================

Unit tests for the SciOS Kernel.
"""

from __future__ import annotations

import pytest

from scios.kernel.kernel import Kernel


# ==========================================================
# Construction
# ==========================================================

def test_kernel_creation() -> None:
    """
    Kernel should construct successfully.
    """

    kernel = Kernel()

    assert kernel is not None


# ==========================================================
# Boot
# ==========================================================

def test_kernel_boot() -> None:
    """
    Kernel should boot successfully.
    """

    kernel = Kernel()

    assert kernel.boot() is True

    assert kernel.status()["state"] == "running"


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

    assert kernel.status()["state"] == "stopped"


# ==========================================================
# Boot Cycle
# ==========================================================

@pytest.mark.parametrize(
    "cycles",
    [
        1,
        3,
        5,
    ],
)
def test_kernel_boot_cycles(
    cycles: int,
) -> None:
    """
    Kernel should survive repeated boot/shutdown cycles.
    """

    kernel = Kernel()

    for _ in range(cycles):

        assert kernel.boot() is True

        assert kernel.status()["state"] == "running"

        assert kernel.shutdown() is True

        assert kernel.status()["state"] == "stopped"


# ==========================================================
# Registry
# ==========================================================

def test_kernel_registry_exists() -> None:
    """
    Kernel should expose a service registry.
    """

    kernel = Kernel()

    assert kernel.registry is not None


# ==========================================================
# Dispatcher
# ==========================================================

def test_kernel_dispatcher_exists() -> None:
    """
    Kernel should expose a dispatcher.
    """

    kernel = Kernel()

    assert kernel.dispatcher is not None


# ==========================================================
# Lifecycle
# ==========================================================

def test_kernel_lifecycle_exists() -> None:
    """
    Kernel should expose lifecycle management.
    """

    kernel = Kernel()

    assert kernel.lifecycle is not None


# ==========================================================
# Status
# ==========================================================

def test_kernel_status_structure() -> None:
    """
    Kernel status should return a dictionary.
    """

    kernel = Kernel()

    status = kernel.status()

    assert isinstance(status, dict)

    assert "state" in status


# ==========================================================
# Double Boot
# ==========================================================

def test_kernel_double_boot() -> None:
    """
    Booting twice should not fail.
    """

    kernel = Kernel()

    assert kernel.boot() is True

    assert kernel.boot() is True

    assert kernel.status()["state"] == "running"


# ==========================================================
# Double Shutdown
# ==========================================================

def test_kernel_double_shutdown() -> None:
    """
    Shutting down twice should not fail.
    """

    kernel = Kernel()

    kernel.boot()

    assert kernel.shutdown() is True

    assert kernel.shutdown() is True

    assert kernel.status()["state"] == "stopped"