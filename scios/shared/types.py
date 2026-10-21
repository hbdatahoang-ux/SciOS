"""
SciOS Common Types
==================

Canonical type definitions shared across the Scientific Cognitive
Operating System (SciOS).

Design Goals
------------
- Python 3.11+
- Zero runtime dependencies
- Shared across all SciOS subsystems
- Strong typing
- IDE and static-analysis friendly
- Runtime-checkable structural protocols
- Stable public API
"""

from __future__ import annotations

from collections.abc import Callable
from collections.abc import Mapping
from collections.abc import MutableMapping
from collections.abc import Sequence
from typing import Any
from typing import Literal
from typing import Protocol
from typing import TypeAlias
from typing import runtime_checkable

from .json_types import (
    JSONArray,
    JSONObject,
    JSONValue,
)


__all__ = [
    # JSON
    "JSONValue",
    "JSONObject",
    "JSONArray",

    # Generic
    "ConfigDict",
    "Metadata",

    # Runtime
    "TaskID",
    "Task",
    "TaskResult",

    # Vector Store
    "Embedding",
    "Embeddings",

    # Events
    "EventName",
    "Event",

    # States
    "KernelState",
    "RuntimeState",
    "PipelineState",
    "AgentState",

    # Callback
    "Callback",

    # Protocols
    "Executable",
    "Serializable",
    "Identifiable",
    "Named",
    "Initializable",
    "Shutdownable",
]


# ============================================================================
# Generic Types
# ============================================================================

ConfigDict: TypeAlias = dict[str, Any]

Metadata: TypeAlias = dict[str, Any]


# ============================================================================
# Runtime Types
# ============================================================================

TaskID: TypeAlias = str

Task: TypeAlias = str | Mapping[str, Any]

TaskResult: TypeAlias = MutableMapping[str, Any]


# ============================================================================
# Vector / Embedding Types
# ============================================================================

Embedding: TypeAlias = Sequence[float]

Embeddings: TypeAlias = Sequence[Embedding]


# ============================================================================
# Event Types
# ============================================================================

EventName: TypeAlias = str

Event: TypeAlias = Mapping[str, Any]


# ============================================================================
# Kernel State
# ============================================================================

KernelState: TypeAlias = Literal[
    "created",
    "booting",
    "running",
    "stopping",
    "stopped",
    "failed",
]


# ============================================================================
# Runtime State
# ============================================================================

RuntimeState: TypeAlias = Literal[
    "created",
    "idle",
    "running",
    "completed",
    "failed",
]


# ============================================================================
# Pipeline State
# ============================================================================

PipelineState: TypeAlias = Literal[
    "created",
    "running",
    "completed",
    "failed",
]


# ============================================================================
# Agent State
# ============================================================================

AgentState: TypeAlias = Literal[
    "idle",
    "planning",
    "running",
    "waiting",
    "reflecting",
    "finished",
    "failed",
]


# ============================================================================
# Callback
# ============================================================================

Callback: TypeAlias = Callable[..., Any]


# ============================================================================
# Protocols
# ============================================================================


@runtime_checkable
class Executable(Protocol):
    """
    Common execution interface.

    Any object implementing ``execute(*args, **kwargs)`` satisfies
    this protocol structurally.
    """

    def execute(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        ...


@runtime_checkable
class Serializable(Protocol):
    """
    Common serialization interface.

    Implementations must expose a ``to_dict()`` method returning
    a SciOS JSON object.
    """

    def to_dict(self) -> JSONObject:
        ...


@runtime_checkable
class Identifiable(Protocol):
    """
    Object exposing a globally unique identifier.
    """

    @property
    def id(self) -> str:
        ...


@runtime_checkable
class Named(Protocol):
    """
    Object exposing a human-readable name.
    """

    @property
    def name(self) -> str:
        ...


@runtime_checkable
class Initializable(Protocol):
    """
    Lifecycle initialization interface.
    """

    def initialize(self) -> None:
        ...


@runtime_checkable
class Shutdownable(Protocol):
    """
    Lifecycle shutdown interface.
    """

    def shutdown(self) -> None:
        ...