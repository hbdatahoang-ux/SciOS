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
    """

    VERSION = "0.1.0"

    def __init__(
        self,
        config: Any = None,
    ) -> None:
        self.registry = StageRegistry()
        self.dispatcher = StageDispatcher()
        self.middleware = MiddlewareManager()
        self.event_bus = EventBus()

        self.pipeline = CognitivePipeline(
            dispatcher=self.dispatcher,
            middleware=self.middleware,
            event_bus=self.event_bus,
        )

        self.state = KernelState()
        self.config = config
        self._booted = False

    def boot(self) -> bool:
        self._booted = True

        self.state.set_status(
            KernelStatus.RUNNING,
            "Kernel booted",
        )

        return True

    def shutdown(self) -> bool:
        self._booted = False

        self.state.set_status(
            KernelStatus.STOPPED,
            "Kernel shutdown",
        )

        return True

    def reset(self) -> None:
        self.pipeline.reset()

        self.state.set_status(
            KernelStatus.IDLE,
            "Kernel reset",
        )

    def run(self, request: CognitiveRequest) -> CognitiveResponse:
        if not self._booted:
            raise RuntimeError("Kernel not booted")

        if not isinstance(request, CognitiveRequest):
            raise TypeError(
                "request must be an instance of CognitiveRequest"
            )

        context = CognitiveContext(request)
        self.pipeline.run(context)

        return CognitiveResponse.from_context(context)

    def status(self) -> dict[str, Any]:
        return {
            "booted": self._booted,
            "version": self.VERSION,
            "state": self.state.status.name,
        }

    def __repr__(self) -> str:
        return (
            "<CognitiveKernel "
            f"booted={self._booted} "
            f"state={self.state.status.name}>"
        )
