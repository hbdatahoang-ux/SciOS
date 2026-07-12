"""
SciOS Shared Package
====================

Public API for the SciOS shared infrastructure.

This package contains common utilities, configuration,
types, exceptions, logging, and the shared EventBus used
throughout the SciOS platform.
"""

from __future__ import annotations

# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

from .config import *

# ---------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------

from .constants import *

# ---------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------

from .exceptions import *

# ---------------------------------------------------------------------
# JSON Types
# ---------------------------------------------------------------------

from .json_types import (
    JSONPrimitive,
    JSONValue,
    JSONObject,
    JSONArray,
    is_json_primitive,
    is_json_value,
)

# ---------------------------------------------------------------------
# Common Types
# ---------------------------------------------------------------------

from .types import (
    ConfigDict,
    Metadata,
    Task,
    TaskID,
    TaskResult,
    Embedding,
    Embeddings,
    Event,
    EventName,
    KernelState,
    RuntimeState,
    PipelineState,
    AgentState,
    Callback,
    Executable,
    Serializable,
)

# ---------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------

from .logger import *

# ---------------------------------------------------------------------
# Event Bus
# ---------------------------------------------------------------------

from .event_bus import EventBus

__all__ = [
    # JSON
    "JSONPrimitive",
    "JSONValue",
    "JSONObject",
    "JSONArray",
    "is_json_primitive",
    "is_json_value",

    # Types
    "ConfigDict",
    "Metadata",
    "Task",
    "TaskID",
    "TaskResult",
    "Embedding",
    "Embeddings",
    "Event",
    "EventName",
    "KernelState",
    "RuntimeState",
    "PipelineState",
    "AgentState",
    "Callback",
    "Executable",
    "Serializable",

    # Infrastructure
    "EventBus",
]