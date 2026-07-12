"""
SciOS Kernel Service Interfaces
===============================

Abstract service interfaces used throughout the SciOS Kernel.

Responsibilities
----------------
- Define lifecycle contracts.
- Define execution contracts.
- Provide common service interfaces.
- Enable dependency injection.

Design Goals
------------
- Framework independent
- Strong typing
- ABC based
- Compatible with Kernel, Runtime and Plugins
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Protocol
from typing import runtime_checkable


__all__ = [
    "Service",
    "LifecycleService",
    "ExecutionService",
    "NamedService",
    "ConfigurableService",
    "HealthCheckService",
]


# ==========================================================
# Base Service
# ==========================================================

class Service(ABC):
    """
    Root interface for every SciOS service.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Unique service name.
        """
        raise NotImplementedError

    @property
    def version(self) -> str:
        """
        Service version.
        """
        return "0.1.0"

    @property
    def description(self) -> str:
        """
        Human-readable description.
        """
        return self.__class__.__name__

    @abstractmethod
    def status(self) -> dict[str, Any]:
        """
        Return current service status.
        """
        raise NotImplementedError


# ==========================================================
# Lifecycle Service
# ==========================================================

class LifecycleService(Service):
    """
    Service supporting lifecycle operations.
    """

    @abstractmethod
    def initialize(self) -> None:
        """
        Initialize service.
        """
        raise NotImplementedError

    @abstractmethod
    def start(self) -> None:
        """
        Start service.
        """
        raise NotImplementedError

    @abstractmethod
    def shutdown(self) -> None:
        """
        Shutdown service.
        """
        raise NotImplementedError


# ==========================================================
# Execution Service
# ==========================================================

class ExecutionService(Service):
    """
    Service capable of executing work.
    """

    @abstractmethod
    def execute(
        self,
        task: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Execute a task.
        """
        raise NotImplementedError


# ==========================================================
# Configurable Service
# ==========================================================

class ConfigurableService(Service):
    """
    Service supporting runtime configuration.
    """

    @abstractmethod
    def configure(
        self,
        **config: Any,
    ) -> None:
        """
        Apply configuration.
        """
        raise NotImplementedError


# ==========================================================
# Health Check Service
# ==========================================================

class HealthCheckService(Service):
    """
    Service exposing health information.
    """

    @abstractmethod
    def healthy(self) -> bool:
        """
        Return True if healthy.
        """
        raise NotImplementedError

    @abstractmethod
    def health(self) -> dict[str, Any]:
        """
        Detailed health report.
        """
        raise NotImplementedError


# ==========================================================
# Runtime Protocols
# ==========================================================

@runtime_checkable
class NamedService(Protocol):
    """
    Lightweight runtime protocol.
    """

    @property
    def name(self) -> str:
        ...


@runtime_checkable
class Initializable(Protocol):

    def initialize(self) -> None:
        ...


@runtime_checkable
class Startable(Protocol):

    def start(self) -> None:
        ...


@runtime_checkable
class Shutdownable(Protocol):

    def shutdown(self) -> None:
        ...


@runtime_checkable
class Executable(Protocol):

    def execute(
        self,
        task: Any,
        **kwargs: Any,
    ) -> Any:
        ...


# ==========================================================
# Composite Service
# ==========================================================

class KernelService(
    LifecycleService,
    ExecutionService,
):
    """
    Complete kernel service interface.

    Used by:
        - Scheduler
        - Dispatcher
        - Runtime
        - Agent
        - Planner
        - Memory
        - PluginManager
    """

    pass