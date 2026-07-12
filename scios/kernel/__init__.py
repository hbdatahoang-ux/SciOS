"""
SciOS Kernel
============

Core orchestration layer of the Scientific Cognitive Operating System.
"""

from __future__ import annotations

# ==========================================================
# Core
# ==========================================================

from .kernel import Kernel
from .bootstrap import Bootstrap


# ==========================================================
# Factory
# ==========================================================

def build_kernel() -> Kernel:
    """
    Build a default SciOS Kernel.

    Returns
    -------
    Kernel
        A fully initialized Kernel instance.
    """
    return Kernel()


# ==========================================================
# Infrastructure
# ==========================================================

from .lifecycle import LifecycleManager
from .registry import ServiceRegistry
from .scheduler import Scheduler
from .dispatcher import Dispatcher
from .plugin_manager import PluginManager
from .artifact_manager import ArtifactManager


# ==========================================================
# State
# ==========================================================

from .state import KernelState, KernelStatus


# ==========================================================
# Services
# ==========================================================

from .services import (
    Service,
    LifecycleService,
    ExecutionService,
    ConfigurableService,
    HealthCheckService,
    KernelService,
)


# ==========================================================
# Exceptions
# ==========================================================

from .exceptions import *


# ==========================================================
# Version
# ==========================================================

__version__ = "0.3.0-alpha"


# ==========================================================
# Public API
# ==========================================================

__all__ = [
    # Core
    "Kernel",
    "Bootstrap",
    "build_kernel",

    # Infrastructure
    "LifecycleManager",
    "ServiceRegistry",
    "Scheduler",
    "Dispatcher",
    "PluginManager",
    "ArtifactManager",

    # State
    "KernelState",
    "KernelStatus",

    # Services
    "Service",
    "LifecycleService",
    "ExecutionService",
    "ConfigurableService",
    "HealthCheckService",
    "KernelService",
]