"""
SciOS Shared Package
====================

Public API for the SciOS shared infrastructure.

The ``scios.shared`` package provides stable, dependency-free
building blocks shared across the SciOS kernel, runtime, agents,
cognitive core, memory, vector store, and QTC subsystems.

Public areas
------------
- Configuration
- Global constants
- Exception hierarchy
- JSON type definitions
- Common type aliases
- Structural protocols
- Logging
- Event bus

Design goals
------------
- Python 3.11+
- Zero external runtime dependencies
- Explicit and stable public API
- Strong typing
- Minimal coupling between subsystems
- Safe imports for all SciOS layers
"""

from __future__ import annotations


# ============================================================================
# Configuration
# ============================================================================

# Keep the module import available internally without exposing ``config`` as
# part of the package public API.
from . import config as config_module

from .config import (
    AgentConfig,
    KernelConfig,
    LoggingConfig,
    MemoryConfig,
    QTCConfig,
    RuntimeConfig,
    SciOSConfig,
    SystemConfig,
    VectorStoreConfig,
)


# ============================================================================
# Global Constants
# ============================================================================

from .constants import (
    AGENT_FAILED,
    AGENT_FINISHED,
    AGENT_IDLE,
    AGENT_RUNNING,
    AGENT_WAITING,
    CACHE_DIRECTORY,
    DATA_DIRECTORY,
    DEFAULT_SCHEDULER,
    DEFAULT_TIMEOUT,
    DEFAULT_WORKERS,
    EVENT_BOOT,
    EVENT_SHUTDOWN,
    EVENT_TASK_COMPLETED,
    EVENT_TASK_FAILED,
    EVENT_TASK_STARTED,
    KERNEL_STATE_BOOTING,
    KERNEL_STATE_CREATED,
    KERNEL_STATE_FAILED,
    KERNEL_STATE_RUNNING,
    KERNEL_STATE_STOPPED,
    KERNEL_STATE_STOPPING,
    LOG_CRITICAL,
    LOG_DEBUG,
    LOG_DIRECTORY,
    LOG_ERROR,
    LOG_INFO,
    LOG_WARNING,
    MEMORY_EPISODIC,
    MEMORY_LONGTERM,
    MEMORY_SEMANTIC,
    MEMORY_WORKING,
    MODEL_DIRECTORY,
    QTC_BACKEND_NATIVE,
    QTC_BACKEND_SYMBOLIC,
    ROOT_DIRECTORY,
    SCIOS_NAME,
    SCIOS_ORGANIZATION,
    SCIOS_VERSION,
    SIMILARITY_COSINE,
    SIMILARITY_INNER_PRODUCT,
    SIMILARITY_L2,
    VECTOR_BACKEND_FAISS,
    VECTOR_BACKEND_FLAT,
    VECTOR_BACKEND_HNSW,
)


# ============================================================================
# Exception Hierarchy
# ============================================================================

from .exceptions import (
    AgentError,
    AlgebraError,
    BootError,
    CollaborationError,
    CompressionError,
    ConfigurationError,
    EmbeddingError,
    ExecutionError,
    KernelError,
    LifecycleError,
    MorphismError,
    NetworkError,
    PlanningError,
    PluginError,
    QTCError,
    ReasoningError,
    ReflectionError,
    RetrievalError,
    SciOSError,
    SciOSMemoryError,
    SciOSRuntimeError,
    SchedulerError,
    SearchError,
    SerializationError,
    StorageError,
    ToolError,
    ValidationError,
    VectorIndexError,
    VectorStoreError,
    VerificationError,
)


# ============================================================================
# JSON Types
# ============================================================================

from .json_types import (
    JSONArray,
    JSONPrimitive,
    JSONObject,
    JSONValue,
    is_json_primitive,
    is_json_value,
)


# ============================================================================
# Common Types
# ============================================================================

from .types import (
    AgentState,
    Callback,
    ConfigDict,
    Embedding,
    Embeddings,
    Event,
    EventName,
    KernelState,
    Metadata,
    PipelineState,
    RuntimeState,
    Task,
    TaskID,
    TaskResult,
)


# ============================================================================
# Structural Protocols
# ============================================================================

from .types import (
    Executable,
    Identifiable,
    Initializable,
    Named,
    Serializable,
    Shutdownable,
)


# ============================================================================
# Logging
# ============================================================================

from .logger import (
    SciOSLogger,
    configure_logging,
    get_logger,
)


# ============================================================================
# Event Bus
# ============================================================================

from .event_bus import EventBus


# ============================================================================
# Public API
# ============================================================================

__all__ = [
    # ------------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------------
    "AgentConfig",
    "KernelConfig",
    "LoggingConfig",
    "MemoryConfig",
    "QTCConfig",
    "RuntimeConfig",
    "SciOSConfig",
    "SystemConfig",
    "VectorStoreConfig",

    # ------------------------------------------------------------------------
    # System / Version
    # ------------------------------------------------------------------------
    "SCIOS_NAME",
    "SCIOS_VERSION",
    "SCIOS_ORGANIZATION",

    # ------------------------------------------------------------------------
    # Directories
    # ------------------------------------------------------------------------
    "ROOT_DIRECTORY",
    "LOG_DIRECTORY",
    "CACHE_DIRECTORY",
    "DATA_DIRECTORY",
    "MODEL_DIRECTORY",

    # ------------------------------------------------------------------------
    # Runtime Constants
    # ------------------------------------------------------------------------
    "DEFAULT_WORKERS",
    "DEFAULT_TIMEOUT",
    "DEFAULT_SCHEDULER",

    # ------------------------------------------------------------------------
    # Kernel States
    # ------------------------------------------------------------------------
    "KERNEL_STATE_CREATED",
    "KERNEL_STATE_BOOTING",
    "KERNEL_STATE_RUNNING",
    "KERNEL_STATE_STOPPING",
    "KERNEL_STATE_STOPPED",
    "KERNEL_STATE_FAILED",

    # ------------------------------------------------------------------------
    # Agent States
    # ------------------------------------------------------------------------
    "AGENT_IDLE",
    "AGENT_RUNNING",
    "AGENT_WAITING",
    "AGENT_FINISHED",
    "AGENT_FAILED",

    # ------------------------------------------------------------------------
    # Memory
    # ------------------------------------------------------------------------
    "MEMORY_WORKING",
    "MEMORY_EPISODIC",
    "MEMORY_SEMANTIC",
    "MEMORY_LONGTERM",

    # ------------------------------------------------------------------------
    # Vector Store
    # ------------------------------------------------------------------------
    "VECTOR_BACKEND_FLAT",
    "VECTOR_BACKEND_HNSW",
    "VECTOR_BACKEND_FAISS",
    "SIMILARITY_COSINE",
    "SIMILARITY_L2",
    "SIMILARITY_INNER_PRODUCT",

    # ------------------------------------------------------------------------
    # QTC
    # ------------------------------------------------------------------------
    "QTC_BACKEND_NATIVE",
    "QTC_BACKEND_SYMBOLIC",

    # ------------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------------
    "EVENT_BOOT",
    "EVENT_SHUTDOWN",
    "EVENT_TASK_STARTED",
    "EVENT_TASK_COMPLETED",
    "EVENT_TASK_FAILED",

    # ------------------------------------------------------------------------
    # Logging Constants
    # ------------------------------------------------------------------------
    "LOG_DEBUG",
    "LOG_INFO",
    "LOG_WARNING",
    "LOG_ERROR",
    "LOG_CRITICAL",

    # ------------------------------------------------------------------------
    # JSON Types
    # ------------------------------------------------------------------------
    "JSONPrimitive",
    "JSONValue",
    "JSONObject",
    "JSONArray",
    "is_json_primitive",
    "is_json_value",

    # ------------------------------------------------------------------------
    # Generic Types
    # ------------------------------------------------------------------------
    "ConfigDict",
    "Metadata",

    # ------------------------------------------------------------------------
    # Runtime Types
    # ------------------------------------------------------------------------
    "TaskID",
    "Task",
    "TaskResult",

    # ------------------------------------------------------------------------
    # Vector / Embedding Types
    # ------------------------------------------------------------------------
    "Embedding",
    "Embeddings",

    # ------------------------------------------------------------------------
    # Event Types
    # ------------------------------------------------------------------------
    "EventName",
    "Event",

    # ------------------------------------------------------------------------
    # State Types
    # ------------------------------------------------------------------------
    "KernelState",
    "RuntimeState",
    "PipelineState",
    "AgentState",

    # ------------------------------------------------------------------------
    # Callback
    # ------------------------------------------------------------------------
    "Callback",

    # ------------------------------------------------------------------------
    # Structural Protocols
    # ------------------------------------------------------------------------
    "Executable",
    "Serializable",
    "Identifiable",
    "Named",
    "Initializable",
    "Shutdownable",

    # ------------------------------------------------------------------------
    # Exceptions
    # ------------------------------------------------------------------------
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

    # ------------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------------
    "SciOSLogger",
    "get_logger",
    "configure_logging",

    # ------------------------------------------------------------------------
    # Event Bus
    # ------------------------------------------------------------------------
    "EventBus",
]