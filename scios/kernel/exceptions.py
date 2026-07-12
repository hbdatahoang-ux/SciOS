"""
SciOS Kernel Exceptions
=======================

Exception hierarchy for the SciOS Kernel.

Responsibilities
----------------
- Provide a canonical exception hierarchy.
- Enable fine-grained error handling.
- Improve debugging and observability.
- Support future distributed execution.

Design Goals
------------
- Lightweight
- Explicit
- Extensible
- Pythonic
"""

from __future__ import annotations

from typing import Any

__all__ = [
    # Base
    "KernelError",

    # Lifecycle
    "KernelStateError",
    "KernelBootError",
    "KernelShutdownError",

    # Registry
    "ServiceError",
    "ServiceAlreadyRegisteredError",
    "ServiceNotFoundError",

    # Scheduler
    "SchedulerError",
    "SchedulerEmptyError",

    # Dispatcher
    "DispatcherError",

    # Runtime
    "ExecutionError",

    # Plugin
    "PluginError",
    "PluginAlreadyRegisteredError",
    "PluginNotFoundError",
    "PluginDisabledError",

    # Artifact
    "ArtifactError",
    "ArtifactNotFoundError",

    # Configuration
    "ConfigurationError",
]


# ==========================================================
# Base Exception
# ==========================================================

class KernelError(Exception):
    """
    Root exception for all kernel-related errors.
    """

    def __init__(
        self,
        message: str = "",
        *,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.__class__.__name__,
            "message": self.message,
            "details": self.details,
        }

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(message={self.message!r})"
        )


# ==========================================================
# Kernel Lifecycle
# ==========================================================

class KernelStateError(KernelError):
    """
    Invalid kernel state transition.
    """


class KernelBootError(KernelError):
    """
    Kernel boot failed.
    """


class KernelShutdownError(KernelError):
    """
    Kernel shutdown failed.
    """


# ==========================================================
# Service Registry
# ==========================================================

class ServiceError(KernelError):
    """
    Base service registry exception.
    """


class ServiceAlreadyRegisteredError(ServiceError):
    """
    Service already exists.
    """


class ServiceNotFoundError(ServiceError):
    """
    Service not found.
    """


# ==========================================================
# Scheduler
# ==========================================================

class SchedulerError(KernelError):
    """
    Scheduler error.
    """


class SchedulerEmptyError(SchedulerError):
    """
    Scheduler queue is empty.
    """


# ==========================================================
# Dispatcher
# ==========================================================

class DispatcherError(KernelError):
    """
    Dispatcher error.
    """


# ==========================================================
# Runtime
# ==========================================================

class ExecutionError(KernelError):
    """
    Runtime execution failed.
    """


# ==========================================================
# Plugin
# ==========================================================

class PluginError(KernelError):
    """
    Base plugin exception.
    """


class PluginAlreadyRegisteredError(PluginError):
    """
    Plugin already registered.
    """


class PluginNotFoundError(PluginError):
    """
    Plugin not found.
    """


class PluginDisabledError(PluginError):
    """
    Plugin exists but is disabled.
    """


# ==========================================================
# Artifact
# ==========================================================

class ArtifactError(KernelError):
    """
    Artifact management error.
    """


class ArtifactNotFoundError(ArtifactError):
    """
    Artifact not found.
    """


# ==========================================================
# Configuration
# ==========================================================

class ConfigurationError(KernelError):
    """
    Invalid configuration.
    """