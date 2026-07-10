"""
SciOS Cognitive Kernel
======================

Package `kernel` tập trung các contract chính:
- CognitiveKernel
- CognitivePipeline
- CognitiveContext
- CognitiveRequest
- CognitiveResponse
- StageRegistry, StageDispatcher
- KernelLifecycle, KernelState
- Hooks, Middleware, Serializer, Exceptions
"""

from .pipeline import CognitivePipeline
from .context import CognitiveContext
from .request import CognitiveRequest
from .response import CognitiveResponse
from .stage import CognitiveStage
from .registry import StageRegistry
from .dispatcher import StageDispatcher
from .lifecycle import KernelLifecycle
from .state import KernelState, KernelStatus
from .events import KernelEvent, KernelEventType
from .hooks import HookManager
from .middleware import MiddlewareManager
from .serializer import KernelSerializer
from .exceptions import (
    KernelError,
    StageError,
    PipelineError,
    LifecycleError,
    ContextError,
)

# -----------------------------------------------------
# Kernel entrypoint
# -----------------------------------------------------

class CognitiveKernel:
    """
    CognitiveKernel là entrypoint chính.
    Nó wrap pipeline, dispatcher, registry, lifecycle và config.
    """

    def __init__(self, config=None) -> None:
        self.pipeline = CognitivePipeline()
        self.registry = StageRegistry()
        self.dispatcher = StageDispatcher(self.registry)
        self.lifecycle = KernelLifecycle(self)
        self.state = KernelState()
        self.hooks = HookManager()
        self.middleware = MiddlewareManager()
        self.config = config

    def run(self, request: CognitiveRequest) -> CognitiveResponse:
        """Chạy pipeline với request và trả về response."""
        context = CognitiveContext(request)
        # chạy middleware chain trước khi dispatch
        self.middleware.run(context, final_handler=lambda ctx: self.dispatcher.dispatch(ctx))
        return CognitiveResponse.from_context(context)

    def reset(self) -> None:
        """Reset toàn bộ kernel."""
        self.pipeline.reset()
        self.registry.reset()
        self.state.set_status(KernelStatus.IDLE, "Kernel reset")
