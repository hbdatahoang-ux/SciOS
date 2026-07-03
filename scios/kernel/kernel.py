"""
SciOS Kernel
============

Core microkernel of the Scientific Cognitive Operating System.

The kernel coordinates all major SciOS subsystems while keeping
their implementations independent.

Responsibilities
----------------
- Lifecycle management
- Boot / shutdown
- Runtime orchestration
- Component registry
- Event bus
- Execution entry point
- Status reporting
"""

from __future__ import annotations

from typing import Any

from .bootstrap import Bootstrap
from .context import KernelContext
from .eventbus.bus import EventBus
from .lifecycle import KernelState, LifecycleManager
from .registry import ComponentRegistry
from .runtime.engine import Runtime


__all__ = [
    "Kernel",
]


class Kernel:
    """
    SciOS microkernel.
    """

    VERSION = "0.2.0"

    def __init__(self) -> None:

        self.lifecycle = LifecycleManager()

        self.registry = ComponentRegistry()

        self.context = KernelContext()

        self.eventbus = EventBus()

        self.runtime = Runtime()

        self.bootstrap = Bootstrap()

    # ---------------------------------------------------------
    # Properties
    # ---------------------------------------------------------

    @property
    def state(self) -> str:
        return self.lifecycle.state.value

    @property
    def booted(self) -> bool:
        return self.lifecycle.state is KernelState.READY

    # ---------------------------------------------------------
    # Lifecycle
    # ---------------------------------------------------------

    def boot(self) -> bool:
        """
        Boot kernel.
        """

        if self.booted:
            return True

        self.bootstrap.boot(self)

        return True

    def shutdown(self) -> bool:
        """
        Shutdown kernel.
        """

        if self.lifecycle.state is KernelState.STOPPED:
            return True

        self.bootstrap.shutdown(self)

        return True

    def restart(self) -> bool:

        self.shutdown()
        self.boot()

        return True

    # ---------------------------------------------------------
    # Runtime
    # ---------------------------------------------------------

    def run(
        self,
        task: Any,
    ) -> Any:
        """
        Execute a task.
        """

        if not self.booted:
            raise RuntimeError(
                "Kernel has not been booted."
            )

        return self.runtime.run(task)

    # ---------------------------------------------------------
    # Status
    # ---------------------------------------------------------

    def status(self) -> dict[str, Any]:
        """
        Return kernel status.
        """

        return {
            "state": self.state,
            "runtime": self.runtime.status(),
            "registry": self.registry.status(),
            "context": self.context.status(),
            "eventbus": self.eventbus.status(),
        }

    # ---------------------------------------------------------
    # Representation
    # ---------------------------------------------------------

    def __repr__(self) -> str:

        return (
            f"Kernel("
            f"state='{self.state}', "
            f"version='{self.VERSION}')"
        )