"""
SciOS LifecycleManager Tests
============================

Unit tests for the SciOS Kernel LifecycleManager.
"""

from __future__ import annotations

from scios.kernel.lifecycle import LifecycleManager


class DummyHook:
    """
    Test lifecycle hook.
    """

    def __init__(self) -> None:
        self.initialized = False
        self.shutdown_called = False

    def initialize(self) -> None:
        self.initialized = True

    def shutdown(self) -> None:
        self.shutdown_called = True


# ==========================================================
# Construction
# ==========================================================

def test_initial_state() -> None:
    manager = LifecycleManager()

    assert manager.state == "created"


# ==========================================================
# Initialize
# ==========================================================

def test_initialize() -> None:
    manager = LifecycleManager()

    hook = DummyHook()

    manager.add_hook(hook)

    manager.initialize()

    assert manager.state == "booting"

    assert hook.initialized is True


# ==========================================================
# Start
# ==========================================================

def test_start() -> None:
    manager = LifecycleManager()

    manager.start()

    assert manager.state == "running"


# ==========================================================
# Shutdown
# ==========================================================

def test_shutdown() -> None:
    manager = LifecycleManager()

    hook = DummyHook()

    manager.add_hook(hook)

    manager.initialize()

    manager.shutdown()

    assert manager.state == "stopped"

    assert hook.shutdown_called is True


# ==========================================================
# Status
# ==========================================================

def test_status() -> None:
    manager = LifecycleManager()

    status = manager.status()

    assert status["state"] == "created"

    assert status["hooks"] == 0


# ==========================================================
# Hook Management
# ==========================================================

def test_add_remove_hook() -> None:
    manager = LifecycleManager()

    hook = DummyHook()

    manager.add_hook(hook)

    assert len(manager) == 1

    manager.remove_hook(hook)

    assert len(manager) == 0


def test_clear_hooks() -> None:
    manager = LifecycleManager()

    manager.add_hook(DummyHook())

    manager.add_hook(DummyHook())

    assert len(manager) == 2

    manager.clear_hooks()

    assert len(manager) == 0


# ==========================================================
# Representation
# ==========================================================

def test_repr() -> None:
    manager = LifecycleManager()

    text = repr(manager)

    assert "LifecycleManager" in text

    assert "created" in text