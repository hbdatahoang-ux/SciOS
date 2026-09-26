"""
SciOS Cognitive Kernel package.

Public API facade for the canonical CognitiveKernel implementation.
"""

from .kernel import CognitiveKernel
from .pipeline import CognitivePipeline, Pipeline
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

__all__ = [
    "CognitiveKernel",
    "CognitivePipeline",
    "Pipeline",
    "CognitiveContext",
    "CognitiveRequest",
    "CognitiveResponse",
    "CognitiveStage",
    "StageRegistry",
    "StageDispatcher",
    "KernelLifecycle",
    "KernelState",
    "KernelStatus",
    "KernelEvent",
    "KernelEventType",
    "HookManager",
    "MiddlewareManager",
    "KernelSerializer",
    "KernelError",
    "StageError",
    "PipelineError",
    "LifecycleError",
    "ContextError",
]
