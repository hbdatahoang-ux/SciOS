"""
SciOS Common Types
==================

Canonical type definitions shared across the Scientific Cognitive
Operating System.

This module centralizes common type aliases and protocols used by
Kernel, Runtime, Agents, Memory, Vector Store, and QTC.

Guidelines
----------
- No business logic.
- No runtime dependencies.
- Only reusable type definitions.
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

__all__ = [

    # Generic
    "JSONValue",
    "JSONObject",
    "JSONArray",

    "ConfigDict",
    "Metadata",

    # Runtime
    "Task",
    "TaskResult",

    # Memory
    "Embedding",
    "Embeddings",

    # Events
    "Event",

    # States
    "KernelState",
    "AgentState",

    # Callbacks
    "Callback",

    # Protocols
    "Executable",
    "Serializable",
]


# ==========================================================
# JSON
# ==========================================================

JSONValue: TypeAlias = (
    str
    | int
    | float
    | bool
    | None
    | "JSONObject"
    | "JSONArray"
)

JSONObject: TypeAlias = dict[str, JSONValue]

JSONArray: TypeAlias = list[JSONValue]


# ==========================================================
# Generic
# ==========================================================

ConfigDict: TypeAlias = dict[str, Any]

Metadata: TypeAlias = dict[str, Any]


# ==========================================================
# Runtime
# ==========================================================

Task: TypeAlias = str | Mapping[str, Any]

TaskResult: TypeAlias = MutableMapping[str, Any]


# ==========================================================
# Vector Store
# ==========================================================

Embedding: TypeAlias = Sequence[float]

Embeddings: TypeAlias = Sequence[Embedding]


# ==========================================================
# Events
# ==========================================================

Event: TypeAlias = Mapping[str, Any]


# ==========================================================
# Kernel States
# ==========================================================

KernelState: TypeAlias = Literal[
    "created",
    "booting",
    "running",
    "stopping",
    "stopped",
    "failed",
]


# ==========================================================
# Agent States
# ==========================================================

AgentState: TypeAlias = Literal[
    "idle",
    "running",
    "waiting",
    "finished",
    "failed",
]


# ==========================================================
# Callback
# ==========================================================

Callback: TypeAlias = Callable[..., Any]


# ==========================================================
# Protocols
# ==========================================================

class Executable(Protocol):
    """
    Common execution interface.
    """

    def execute(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        ...


class Serializable(Protocol):
    """
    Serialization interface.
    """

    def to_dict(self) -> JSONObject:
        ...
