"""
Tests for the SciOS shared package public API.

These tests lock the public surface exposed by ``scios.shared``.
"""

from __future__ import annotations

import scios.shared as shared


# ============================================================================
# Expected public API
# ============================================================================


EXPECTED_PUBLIC_API = {
    # Configuration
    "AgentConfig",
    "KernelConfig",
    "LoggingConfig",
    "MemoryConfig",
    "QTCConfig",
    "RuntimeConfig",
    "SciOSConfig",
    "SystemConfig",
    "VectorStoreConfig",

    # Constants
    "SCIOS_NAME",
    "SCIOS_VERSION",
    "SCIOS_ORGANIZATION",
    "ROOT_DIRECTORY",
    "LOG_DIRECTORY",
    "CACHE_DIRECTORY",
    "DATA_DIRECTORY",
    "MODEL_DIRECTORY",
    "DEFAULT_WORKERS",
    "DEFAULT_TIMEOUT",
    "DEFAULT_SCHEDULER",
    "KERNEL_STATE_CREATED",
    "KERNEL_STATE_BOOTING",
    "KERNEL_STATE_RUNNING",
    "KERNEL_STATE_STOPPING",
    "KERNEL_STATE_STOPPED",
    "KERNEL_STATE_FAILED",
    "AGENT_IDLE",
    "AGENT_RUNNING",
    "AGENT_WAITING",
    "AGENT_FINISHED",
    "AGENT_FAILED",
    "MEMORY_WORKING",
    "MEMORY_EPISODIC",
    "MEMORY_SEMANTIC",
    "MEMORY_LONGTERM",
    "VECTOR_BACKEND_FLAT",
    "VECTOR_BACKEND_HNSW",
    "VECTOR_BACKEND_FAISS",
    "SIMILARITY_COSINE",
    "SIMILARITY_L2",
    "SIMILARITY_INNER_PRODUCT",
    "QTC_BACKEND_NATIVE",
    "QTC_BACKEND_SYMBOLIC",
    "EVENT_BOOT",
    "EVENT_SHUTDOWN",
    "EVENT_TASK_STARTED",
    "EVENT_TASK_COMPLETED",
    "EVENT_TASK_FAILED",
    "LOG_DEBUG",
    "LOG_INFO",
    "LOG_WARNING",
    "LOG_ERROR",
    "LOG_CRITICAL",

    # JSON
    "JSONPrimitive",
    "JSONValue",
    "JSONObject",
    "JSONArray",
    "is_json_primitive",
    "is_json_value",

    # Common types
    "ConfigDict",
    "Metadata",
    "TaskID",
    "Task",
    "TaskResult",
    "Embedding",
    "Embeddings",
    "EventName",
    "Event",
    "KernelState",
    "RuntimeState",
    "PipelineState",
    "AgentState",
    "Callback",
    "Executable",
    "Serializable",
    "Identifiable",
    "Named",
    "Initializable",
    "Shutdownable",

    # Exceptions
    "SciOSError",
    "KernelError",
    "BootError",
    "LifecycleError",
    "SchedulerError",
    "SciOSRuntimeError",
    "ExecutionError",
    "AgentError",
    "PlanningError",
    "ReasoningError",
    "ReflectionError",
    "ToolError",
    "CollaborationError",
    "SciOSMemoryError",
    "RetrievalError",
    "StorageError",
    "VectorStoreError",
    "EmbeddingError",
    "SearchError",
    "VectorIndexError",
    "QTCError",
    "AlgebraError",
    "MorphismError",
    "CompressionError",
    "VerificationError",
    "ConfigurationError",
    "ValidationError",
    "SerializationError",
    "PluginError",
    "NetworkError",

    # Logging
    "SciOSLogger",
    "get_logger",
    "configure_logging",

    # Event bus
    "EventBus",
}


# ============================================================================
# __all__
# ============================================================================


def test_public_api_is_declared():
    assert hasattr(shared, "__all__")
    assert isinstance(shared.__all__, list)


def test_public_api_contains_no_duplicates():
    assert len(shared.__all__) == len(set(shared.__all__))


def test_public_api_matches_expected_contract():
    assert set(shared.__all__) == EXPECTED_PUBLIC_API


def test_no_expected_public_symbol_is_missing():
    missing = [
        name
        for name in EXPECTED_PUBLIC_API
        if not hasattr(shared, name)
    ]

    assert missing == []


def test_all_declared_symbols_exist():
    missing = [
        name
        for name in shared.__all__
        if not hasattr(shared, name)
    ]

    assert missing == []


# ============================================================================
# Configuration
# ============================================================================


def test_configuration_public_api():
    for name in (
        "SystemConfig",
        "RuntimeConfig",
        "KernelConfig",
        "AgentConfig",
        "MemoryConfig",
        "VectorStoreConfig",
        "QTCConfig",
        "LoggingConfig",
        "SciOSConfig",
    ):
        assert hasattr(shared, name)
        assert callable(getattr(shared, name))


# ============================================================================
# Constants
# ============================================================================


def test_system_constants():
    assert shared.SCIOS_NAME == "SciOS"
    assert isinstance(shared.SCIOS_VERSION, str)
    assert isinstance(shared.SCIOS_ORGANIZATION, str)


def test_directory_constants():
    for name in (
        "ROOT_DIRECTORY",
        "LOG_DIRECTORY",
        "CACHE_DIRECTORY",
        "DATA_DIRECTORY",
        "MODEL_DIRECTORY",
    ):
        assert hasattr(shared, name)


def test_runtime_constants():
    assert isinstance(shared.DEFAULT_WORKERS, int)
    assert shared.DEFAULT_WORKERS > 0

    assert isinstance(shared.DEFAULT_TIMEOUT, float)
    assert shared.DEFAULT_TIMEOUT > 0

    assert isinstance(shared.DEFAULT_SCHEDULER, str)


# ============================================================================
# JSON API
# ============================================================================


def test_json_public_api():
    assert shared.is_json_primitive(42)
    assert shared.is_json_value(
        {
            "runtime": {
                "workers": 4,
                "enabled": True,
            }
        }
    )

    assert not shared.is_json_value(
        {
            "invalid": {1, 2, 3},
        }
    )


# ============================================================================
# Common types
# ============================================================================


def test_common_type_api():
    for name in (
        "ConfigDict",
        "Metadata",
        "TaskID",
        "Task",
        "TaskResult",
        "Embedding",
        "Embeddings",
        "EventName",
        "Event",
        "KernelState",
        "RuntimeState",
        "PipelineState",
        "AgentState",
        "Callback",
    ):
        assert hasattr(shared, name)


# ============================================================================
# Protocol API
# ============================================================================


def test_protocol_api():
    protocols = (
        shared.Executable,
        shared.Serializable,
        shared.Identifiable,
        shared.Named,
        shared.Initializable,
        shared.Shutdownable,
    )

    for protocol in protocols:
        assert getattr(protocol, "_is_protocol", False) is True
        assert getattr(protocol, "_is_runtime_protocol", False) is True


# ============================================================================
# Exception API
# ============================================================================


def test_exception_api():
    for name in (
        "SciOSError",
        "KernelError",
        "BootError",
        "LifecycleError",
        "SchedulerError",
        "SciOSRuntimeError",
        "ExecutionError",
        "AgentError",
        "PlanningError",
        "ReasoningError",
        "ReflectionError",
        "ToolError",
        "CollaborationError",
        "SciOSMemoryError",
        "RetrievalError",
        "StorageError",
        "VectorStoreError",
        "EmbeddingError",
        "SearchError",
        "VectorIndexError",
        "QTCError",
        "AlgebraError",
        "MorphismError",
        "CompressionError",
        "VerificationError",
        "ConfigurationError",
        "ValidationError",
        "SerializationError",
        "PluginError",
        "NetworkError",
    ):
        cls = getattr(shared, name)

        assert isinstance(cls, type)
        assert issubclass(cls, Exception)


# ============================================================================
# Logging API
# ============================================================================


def test_logging_api():
    assert isinstance(shared.SciOSLogger, type)
    assert callable(shared.get_logger)
    assert callable(shared.configure_logging)


# ============================================================================
# Event bus API
# ============================================================================


def test_event_bus_api():
    assert isinstance(shared.EventBus, type)

    bus = shared.EventBus()

    assert len(bus) == 0


# ============================================================================
# Public import smoke test
# ============================================================================


def test_public_import_smoke():
    namespace = {}

    exec(
        "from scios.shared import *",
        namespace,
    )

    for name in EXPECTED_PUBLIC_API:
        assert name in namespace


# ============================================================================
# Private implementation details
# ============================================================================


def test_private_names_are_not_exported():
    for name in shared.__all__:
        assert not name.startswith("_")


def test_module_names_are_not_accidentally_public():
    forbidden = {
        "annotations",
        "Path",
        "Any",
        "Callable",
        "Mapping",
        "MutableMapping",
        "Sequence",
        "Protocol",
        "TypeAlias",
        "Union",
    }

    exported = set(shared.__all__)

    assert exported.isdisjoint(forbidden)
