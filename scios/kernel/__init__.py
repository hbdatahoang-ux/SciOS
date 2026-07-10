"""
SciOS Kernel Package
====================

Core microkernel infrastructure for SciOS.

This package provides:

- Kernel (microkernel orchestrator)
- KernelState (enum of kernel lifecycle states)
- LifecycleManager (service lifecycle controller)
- KernelConfig (configuration dataclass)
- build_kernel() (Composition Root factory)

Infrastructure services:
- EventBus
- ServiceRegistry
- ContextManager
- Scheduler
- PluginManager
- ArtifactManager

Execution subsystem:
- Dispatcher
- ExecutionEngine
- Runtime

The public API exposed here is considered stable.
"""

from .bootstrap import build_kernel
from .kernel import Kernel
from .state import KernelState
from .lifecycle import LifecycleManager
from .config import KernelConfig

# Infrastructure
from .events import EventBus
from .registry import ServiceRegistry
from .context import ContextManager

# Scheduling
from .scheduler import Scheduler, Task

# Plugins
from .plugins import PluginManager

# Artifacts
from .artifacts import Artifact, ArtifactManager, ArtifactStatus, ArtifactType

# Execution
from .dispatcher import Dispatcher
from .execution import ExecutionEngine

# Runtime
from .runtime.runtime import Runtime

__version__ = "0.2.0"

__all__ = [
    # bootstrap
    "build_kernel",

    # kernel
    "Kernel",
    "KernelState",
    "LifecycleManager",
    "KernelConfig",

    # infrastructure
    "EventBus",
    "ServiceRegistry",
    "ContextManager",

    # scheduling
    "Scheduler",
    "Task",

    # plugins
    "PluginManager",

    # artifacts
    "Artifact",
    "ArtifactType",
    "ArtifactStatus",
    "ArtifactManager",

    # execution
    "Dispatcher",
    "ExecutionEngine",

    # runtime
    "Runtime",
]
