"""
SciOS Kernel Core
=================

Central orchestration component of the Scientific Cognitive
Operating System (SciOS).

Responsibilities
----------------
- Own all kernel subsystems.
- Manage kernel lifecycle.
- Execute tasks.
- Provide service lookup.
- Expose kernel status.
"""

from __future__ import annotations

from typing import Any

from .bootstrap import build_components
from .state import KernelState


class Kernel:
    """
    SciOS Kernel.

    The Kernel is the central coordinator responsible for
    orchestrating all core subsystems.
    """

    def __init__(self) -> None:
        components = build_components()

        self.event_bus = components.event_bus
        self.lifecycle = components.lifecycle
        self.registry = components.registry
        self.scheduler = components.scheduler
        self.runtime = components.runtime
        self.dispatcher = components.dispatcher

        self._state: KernelState = "created"

    # ==========================================================
    # Lifecycle
    # ==========================================================

    def boot(self) -> bool:
        """
        Boot the kernel.
        """

        if self._state == "running":
            return True

        self.lifecycle.initialize()
        self.lifecycle.start()

        self._state = "running"

        return True

    def shutdown(self) -> bool:
        """
        Shutdown the kernel.
        """

        if self._state == "stopped":
            return True

        self.lifecycle.shutdown()

        self._state = "stopped"

        return True

    # ==========================================================
    # Execution
    # ==========================================================

    def run(
        self,
        task: Any,
        **metadata: Any,
    ) -> Any:
        """
        Execute one task.
        """

        if self._state != "running":
            raise RuntimeError(
                "Kernel is not running."
            )

        context = self.runtime.run(
            task=task,
            metadata=metadata,
        )

        return context.result

    # ==========================================================
    # Registry
    # ==========================================================

    def service(
        self,
        name: str,
    ) -> Any:
        """
        Retrieve a registered service.
        """

        return self.registry.require(name)

    # ==========================================================
    # Status
    # ==========================================================

    @property
    def state(self) -> KernelState:
        """
        Current kernel state.
        """

        return self._state

    def status(self) -> dict[str, Any]:
        """
        Return kernel status.
        """

        return {
            "state": self._state,
            "services": self.registry.count(),
            "scheduler_queue": len(self.scheduler),
        }

    # ==========================================================
    # Magic Methods
    # ==========================================================

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"state={self._state}, "
            f"services={self.registry.count()})"
        )