"""
SciOS Cognitive Kernel
======================

Entrypoint chính của SciOS-NG.
Ghép Pipeline, Registry, Dispatcher, Middleware, EventBus.
"""

from .pipeline import CognitivePipeline
from .registry import StageRegistry
from .dispatcher import StageDispatcher
from .middleware import MiddlewareManager
from .events import EventBus
from .context import CognitiveContext
from .request import CognitiveRequest
from .response import CognitiveResponse
from .state import KernelState, KernelStatus


class CognitiveKernel:
    """
    CognitiveKernel wrap toàn bộ execution engine.
    """

    VERSION = "0.1.0"

    def __init__(self, config=None) -> None:
        self.registry = StageRegistry()
        self.dispatcher = StageDispatcher()
        self.middleware = MiddlewareManager()
        self.event_bus = EventBus()
        self.pipeline = CognitivePipeline(event_bus=self.event_bus)
        self.state = KernelState()
        self.config = config
        self._booted = False

    # -----------------------------------------------------
    # Lifecycle
    # -----------------------------------------------------

    def boot(self) -> bool:
        self._booted = True
        self.state.set_status(KernelStatus.RUNNING, "Kernel booted")
        return True

    def shutdown(self) -> bool:
        self._booted = False
        self.state.set_status(KernelStatus.STOPPED, "Kernel shutdown")
        return True

    def reset(self) -> None:
        self.pipeline.reset()
        self.state.set_status(KernelStatus.IDLE, "Kernel reset")

    # -----------------------------------------------------
    # Execution
    # -----------------------------------------------------

    def run(self, request: CognitiveRequest) -> CognitiveResponse:
        if not self._booted:
            raise Exception("Kernel not booted")

        context = CognitiveContext(request)
        context = self.pipeline.run(context)
        return CognitiveResponse.from_context(context)

    # -----------------------------------------------------
    # Status
    # -----------------------------------------------------

    def status(self) -> dict:
        return {
            "state": self.state.status.name,
            "booted": self._booted,
            "version": self.VERSION,
        }

    def __repr__(self) -> str:
        return f"<CognitiveKernel state={self.state.status.name} booted={self._booted}>"
