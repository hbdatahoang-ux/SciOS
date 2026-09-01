"""
SciOS Cognitive Kernel
======================

Entrypoint chính của SciOS Cognitive Core.

CognitiveKernel là lớp điều phối cấp cao, ghép các thành phần:

    CognitiveKernel
        ├── StageRegistry
        ├── StageDispatcher
        ├── MiddlewareManager
        ├── EventBus
        ├── CognitivePipeline
        └── KernelState

Responsibilities
----------------
- Quản lý lifecycle của Cognitive Kernel
- Khởi động / shutdown / reset runtime
- Tạo execution context từ CognitiveRequest
- Thực thi CognitivePipeline
- Chuyển context thành CognitiveResponse
- Cung cấp kernel status và diagnostics

Python 3.11+
"""

from __future__ import annotations

from typing import Any

from .context import CognitiveContext
from .dispatcher import StageDispatcher
from .events import EventBus
from .middleware import MiddlewareManager
from .pipeline import CognitivePipeline
from .registry import StageRegistry
from .request import CognitiveRequest
from .response import CognitiveResponse
from .state import KernelState, KernelStatus


__all__ = [
    "CognitiveKernel",
]


class CognitiveKernel:
    """
    Top-level execution kernel for SciOS Cognitive Core.

    The kernel owns the runtime components and coordinates their
    lifecycle and execution.

    Parameters
    ----------
    config:
        Optional user-defined kernel configuration.

    Notes
    -----
    A kernel starts in a non-booted state. ``run()`` cannot be
    called until ``boot()`` has completed successfully.
    """

    VERSION = "0.1.0"

    def __init__(
        self,
        config: Any = None,
    ) -> None:
        # -----------------------------------------------------
        # Core components
        # -----------------------------------------------------

        self.registry = StageRegistry()
        self.dispatcher = StageDispatcher()
        self.middleware = MiddlewareManager()
        self.event_bus = EventBus()

        # Pipeline shares the kernel event bus so that events
        # generated during pipeline execution are observable
        # through the kernel-level event bus.
        self.pipeline = CognitivePipeline(
            event_bus=self.event_bus,
        )

        # -----------------------------------------------------
        # Kernel state
        # -----------------------------------------------------

        self.state = KernelState()

        # Preserve caller configuration exactly.
        self.config = config

        # Boot flag is intentionally independent from KernelState.
        self._booted = False

    # =========================================================
    # Lifecycle
    # =========================================================

    def boot(self) -> bool:
        """
        Boot the cognitive kernel.

        Returns
        -------
        bool
            ``True`` when the kernel is booted.

        Notes
        -----
        Boot is idempotent at the current contract level.
        Repeated calls keep the kernel in ``RUNNING`` state.
        """
        self._booted = True

        self.state.set_status(
            KernelStatus.RUNNING,
            "Kernel booted",
        )

        return True

    def shutdown(self) -> bool:
        """
        Shutdown the cognitive kernel.

        Returns
        -------
        bool
            ``True`` after shutdown has been requested.

        Notes
        -----
        Shutdown is safe even when the kernel has not previously
        been booted.
        """
        self._booted = False

        self.state.set_status(
            KernelStatus.STOPPED,
            "Kernel shutdown",
        )

        return True

    def reset(self) -> None:
        """
        Reset kernel runtime state.

        The pipeline runtime is reset while the kernel itself
        remains booted.

        Returns
        -------
        None
        """
        self.pipeline.reset()

        self.state.set_status(
            KernelStatus.IDLE,
            "Kernel reset",
        )

    # =========================================================
    # Execution
    # =========================================================

    def run(
        self,
        request: CognitiveRequest,
    ) -> CognitiveResponse:
        """
        Execute a cognitive request through the pipeline.

        Parameters
        ----------
        request:
            Cognitive request to execute.

        Returns
        -------
        CognitiveResponse
            Response generated from the resulting context.

        Raises
        ------
        Exception
            If the kernel has not been booted.
        TypeError
            If ``request`` is not a ``CognitiveRequest``.
        """
        if not self._booted:
            raise Exception("Kernel not booted")

        if not isinstance(request, CognitiveRequest):
            raise TypeError(
                "request must be an instance of CognitiveRequest"
            )

        # Create execution context.
        context = CognitiveContext(request)

        # Execute the complete cognitive pipeline.
        context = self.pipeline.run(context)

        # Convert execution context into public response.
        return CognitiveResponse.from_context(context)

    # =========================================================
    # Status
    # =========================================================

    def status(self) -> dict[str, Any]:
        """
        Return a diagnostic snapshot of the kernel.

        Returns
        -------
        dict[str, Any]
            Stable kernel-level status information.
        """
        return {
            "state": self.state.status.name,
            "booted": self._booted,
            "version": self.VERSION,
        }

    # =========================================================
    # Python Protocols
    # =========================================================

    def __repr__(self) -> str:
        """
        Return a concise diagnostic representation.
        """
        return (
            "<CognitiveKernel "
            f"state={self.state.status.name} "
            f"booted={self._booted}>"
        )