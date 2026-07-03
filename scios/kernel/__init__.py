"""
SciOS Kernel
============

Control Plane of the Scientific Cognitive Operating System.

The kernel is responsible for:

- System bootstrapping
- Lifecycle management
- Component registration
- Dependency injection
- Runtime execution
- Task scheduling
- Event dispatching
- Global execution context

Public Components
-----------------
Kernel
    Main kernel facade.

Bootstrap
    Kernel boot sequence.

LifecycleManager
    Kernel lifecycle controller.

Scheduler
    Kernel task scheduler.

Registry
    Global component registry.

DependencyContainer
    Dependency injection container.
"""

from .bootstrap import Bootstrap
from .dependency import DependencyContainer
from .kernel import Kernel
from .lifecycle import LifecycleManager
from .registry import Registry
from .scheduler import Scheduler

__version__ = "0.1.3"

__all__ = [
    "Kernel",
    "Bootstrap",
    "LifecycleManager",
    "Scheduler",
    "Registry",
    "DependencyContainer",
]