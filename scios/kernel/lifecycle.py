"""
SciOS Kernel Lifecycle Manager
==============================

Kernel lifecycle management for SciOS.

Responsibilities
----------------
- Manage kernel lifecycle states.
- Coordinate initialization/start/shutdown.
- Invoke lifecycle hooks.
- Remain fault tolerant.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from .state import KernelState


class LifecycleManager:
    """
    Kernel lifecycle coordinator.
    """

    def __init__(self) -> None:
        self._state: KernelState = "created"
        self._hooks: list[Any] = []

    # ==========================================================
    # Properties
    # ==========================================================

    @property
    def state(self) -> KernelState:
        """
        Current lifecycle state.
        """
        return self._state

    # ==========================================================
    # Hook Management
    # ==========================================================

    def add_hook(self, hook: Any) -> None:
        """
        Register a lifecycle-aware component.
        """
        if hook not in self._hooks:
            self._hooks.append(hook)

    def add_hooks(self, hooks: Iterable[Any]) -> None:
        """
        Register multiple lifecycle hooks.
        """
        for hook in hooks:
            self.add_hook(hook)

    def remove_hook(self, hook: Any) -> None:
        """
        Remove a lifecycle hook.
        """
        if hook in self._hooks:
            self._hooks.remove(hook)

    def clear_hooks(self) -> None:
        """
        Remove all hooks.
        """
        self._hooks.clear()

    # ==========================================================
    # Lifecycle
    # ==========================================================

    def initialize(self) -> None:
        """
        Initialize all registered components.
        """
        self._state = "booting"

        for hook in self._hooks:
            initialize = getattr(hook, "initialize", None)
            if callable(initialize):
                initialize()

        self._state = "created"

    def start(self) -> None:
        """
        Start all registered components.
        """
        for hook in self._hooks:
            start = getattr(hook, "start", None)
            if callable(start):
                start()

        self._state = "running"

    def shutdown(self) -> None:
        """
        Shutdown all registered components.
        """
        self._state = "stopping"

        for hook in reversed(self._hooks):
            shutdown = getattr(hook, "shutdown", None)
            if callable(shutdown):
                shutdown()

        self._state = "stopped"

    def restart(self) -> None:
        """
        Restart the lifecycle.
        """
        self.shutdown()
        self.initialize()
        self.start()

    # ==========================================================
    # Status
    # ==========================================================

    def status(self) -> dict[str, Any]:
        """
        Return lifecycle status.
        """
        return {
            "state": self._state,
            "hooks": len(self._hooks),
        }

    # ==========================================================
    # Helpers
    # ==========================================================

    def is_running(self) -> bool:
        return self._state == "running"

    def is_stopped(self) -> bool:
        return self._state == "stopped"

    def hook_count(self) -> int:
        return len(self._hooks)

    # ==========================================================
    # Magic Methods
    # ==========================================================

    def __len__(self) -> int:
        return len(self._hooks)

    def __contains__(self, hook: Any) -> bool:
        return hook in self._hooks

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"state={self._state!r}, "
            f"hooks={len(self._hooks)})"
        )