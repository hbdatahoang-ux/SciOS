"""
SciOS Exception Hierarchy.

Centralized exception definitions for the Scientific Cognitive Operating
System (SciOS).

Design goals
------------
- Unified exception hierarchy
- Exception chaining
- Structured metadata
- Stable public API
- Production-ready diagnostics
"""

from __future__ import annotations

from typing import Any

__all__ = [
    # Base
    "SciOSError",

    # Kernel
    "KernelError",
    "BootError",
    "LifecycleError",
    "SchedulerError",

    # Runtime
    "SciOSRuntimeError",
    "ExecutionError",

    # Agent
    "AgentError",
    "PlanningError",
    "ReasoningError",
    "ReflectionError",
    "ToolError",
    "CollaborationError",

    # Memory
    "SciOSMemoryError",
    "RetrievalError",
    "StorageError",

    # Vector Store
    "VectorStoreError",
    "EmbeddingError",
    "SearchError",
    "VectorIndexError",

    # QTC
    "QTCError",
    "AlgebraError",
    "MorphismError",
    "CompressionError",
    "VerificationError",

    # Configuration
    "ConfigurationError",

    # Validation
    "ValidationError",

    # Serialization
    "SerializationError",

    # Plugin
    "PluginError",

    # Network
    "NetworkError",
]


# =====================================================================
# Base
# =====================================================================


class SciOSError(Exception):
    """
    Base class for every SciOS exception.

    Parameters
    ----------
    message:
        Human-readable error message.

    error_code:
        Optional machine-readable identifier.

    details:
        Additional structured information.

    cause:
        Original exception.
    """

    def __init__(
        self,
        message: str = "",
        *,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ) -> None:

        super().__init__(message)

        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.cause = cause

    def __str__(self) -> str:

        parts = []

        if self.error_code:
            parts.append(f"[{self.error_code}]")

        if self.message:
            parts.append(self.message)

        if self.cause:
            parts.append(f"(caused by {self.cause})")

        return " ".join(parts)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the exception into a structured dictionary.
        """

        return {
            "type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details,
            "cause": repr(self.cause) if self.cause else None,
        }


# =====================================================================
# Kernel
# =====================================================================


class KernelError(SciOSError):
    """Kernel subsystem failure."""


class BootError(KernelError):
    """Kernel boot failure."""


class LifecycleError(KernelError):
    """Kernel lifecycle failure."""


class SchedulerError(KernelError):
    """Kernel scheduler failure."""


# =====================================================================
# Runtime
# =====================================================================


class SciOSRuntimeError(SciOSError):
    """Runtime subsystem failure."""


class ExecutionError(SciOSRuntimeError):
    """Task execution failure."""


# =====================================================================
# Agent
# =====================================================================


class AgentError(SciOSError):
    """Agent subsystem failure."""


class PlanningError(AgentError):
    """Planning failure."""


class ReasoningError(AgentError):
    """Reasoning failure."""


class ReflectionError(AgentError):
    """Reflection failure."""


class ToolError(AgentError):
    """Tool execution failure."""


class CollaborationError(AgentError):
    """Multi-agent collaboration failure."""


# =====================================================================
# Memory
# =====================================================================


class SciOSMemoryError(SciOSError):
    """Memory subsystem failure."""


class RetrievalError(SciOSMemoryError):
    """Memory retrieval failure."""


class StorageError(SciOSMemoryError):
    """Persistent storage failure."""


# =====================================================================
# Vector Store
# =====================================================================


class VectorStoreError(SciOSError):
    """Vector store failure."""


class EmbeddingError(VectorStoreError):
    """Embedding generation failure."""


class SearchError(VectorStoreError):
    """Similarity search failure."""


class VectorIndexError(VectorStoreError):
    """Vector index failure."""


# =====================================================================
# QTC
# =====================================================================


class QTCError(SciOSError):
    """Quantum Temporal Compression subsystem failure."""


class AlgebraError(QTCError):
    """QTC algebra failure."""


class MorphismError(QTCError):
    """QTC morphism failure."""


class CompressionError(QTCError):
    """Temporal compression failure."""


class VerificationError(QTCError):
    """Formal verification failure."""


# =====================================================================
# Configuration
# =====================================================================


class ConfigurationError(SciOSError):
    """Configuration failure."""


# =====================================================================
# Validation
# =====================================================================


class ValidationError(SciOSError):
    """Validation failure."""


# =====================================================================
# Serialization
# =====================================================================


class SerializationError(SciOSError):
    """Serialization or deserialization failure."""


# =====================================================================
# Plugin
# =====================================================================


class PluginError(SciOSError):
    """Plugin subsystem failure."""


# =====================================================================
# Networking
# =====================================================================


class NetworkError(SciOSError):
    """Network communication failure."""
