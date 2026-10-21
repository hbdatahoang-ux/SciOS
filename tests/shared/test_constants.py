"""
Tests for SciOS shared constants.
"""

from pathlib import Path

import scios.shared.constants as constants


# ============================================================================
# Public API
# ============================================================================


def test_public_api_exists():
    assert constants.__all__

    for name in constants.__all__:
        assert hasattr(constants, name)


def test_public_api_has_expected_size():
    assert len(constants.__all__) == 44


def test_public_api_has_no_duplicates():
    assert len(constants.__all__) == len(set(constants.__all__))


# ============================================================================
# System
# ============================================================================


def test_system_constants():
    assert constants.SCIOS_NAME == "SciOS"
    assert constants.SCIOS_VERSION == "0.1.3"
    assert constants.SCIOS_ORGANIZATION == "SciOS Project"


# ============================================================================
# Directories
# ============================================================================


def test_directory_constants():
    assert constants.ROOT_DIRECTORY == Path(".")
    assert constants.LOG_DIRECTORY == Path("logs")
    assert constants.CACHE_DIRECTORY == Path("cache")
    assert constants.DATA_DIRECTORY == Path("data")
    assert constants.MODEL_DIRECTORY == Path("models")


# ============================================================================
# Runtime
# ============================================================================


def test_runtime_constants():
    assert constants.DEFAULT_WORKERS == 4
    assert constants.DEFAULT_TIMEOUT == 300.0
    assert constants.DEFAULT_SCHEDULER == "fifo"


def test_runtime_constant_types():
    assert isinstance(constants.DEFAULT_WORKERS, int)
    assert isinstance(constants.DEFAULT_TIMEOUT, float)
    assert isinstance(constants.DEFAULT_SCHEDULER, str)


# ============================================================================
# Kernel states
# ============================================================================


def test_kernel_state_constants():
    assert constants.KERNEL_STATE_CREATED == "created"
    assert constants.KERNEL_STATE_BOOTING == "booting"
    assert constants.KERNEL_STATE_RUNNING == "running"
    assert constants.KERNEL_STATE_STOPPING == "stopping"
    assert constants.KERNEL_STATE_STOPPED == "stopped"
    assert constants.KERNEL_STATE_FAILED == "failed"


# ============================================================================
# Agent states
# ============================================================================


def test_agent_state_constants():
    assert constants.AGENT_IDLE == "idle"
    assert constants.AGENT_RUNNING == "running"
    assert constants.AGENT_WAITING == "waiting"
    assert constants.AGENT_FINISHED == "finished"
    assert constants.AGENT_FAILED == "failed"


# ============================================================================
# Memory
# ============================================================================


def test_memory_constants():
    assert constants.MEMORY_WORKING == "working"
    assert constants.MEMORY_EPISODIC == "episodic"
    assert constants.MEMORY_SEMANTIC == "semantic"
    assert constants.MEMORY_LONGTERM == "longterm"


# ============================================================================
# Vector store
# ============================================================================


def test_vector_backend_constants():
    assert constants.VECTOR_BACKEND_FLAT == "flat"
    assert constants.VECTOR_BACKEND_HNSW == "hnsw"
    assert constants.VECTOR_BACKEND_FAISS == "faiss"


def test_similarity_constants():
    assert constants.SIMILARITY_COSINE == "cosine"
    assert constants.SIMILARITY_L2 == "l2"
    assert constants.SIMILARITY_INNER_PRODUCT == "inner_product"


# ============================================================================
# QTC
# ============================================================================


def test_qtc_constants():
    assert constants.QTC_BACKEND_NATIVE == "native"
    assert constants.QTC_BACKEND_SYMBOLIC == "symbolic"


# ============================================================================
# Events
# ============================================================================


def test_event_constants():
    assert constants.EVENT_BOOT == "kernel.boot"
    assert constants.EVENT_SHUTDOWN == "kernel.shutdown"
    assert constants.EVENT_TASK_STARTED == "runtime.task.started"
    assert constants.EVENT_TASK_COMPLETED == "runtime.task.completed"
    assert constants.EVENT_TASK_FAILED == "runtime.task.failed"


def test_event_constants_are_strings():
    events = (
        constants.EVENT_BOOT,
        constants.EVENT_SHUTDOWN,
        constants.EVENT_TASK_STARTED,
        constants.EVENT_TASK_COMPLETED,
        constants.EVENT_TASK_FAILED,
    )

    assert all(isinstance(event, str) for event in events)


# ============================================================================
# Logging
# ============================================================================


def test_logging_constants():
    assert constants.LOG_DEBUG == "DEBUG"
    assert constants.LOG_INFO == "INFO"
    assert constants.LOG_WARNING == "WARNING"
    assert constants.LOG_ERROR == "ERROR"
    assert constants.LOG_CRITICAL == "CRITICAL"


def test_logging_constants_are_strings():
    levels = (
        constants.LOG_DEBUG,
        constants.LOG_INFO,
        constants.LOG_WARNING,
        constants.LOG_ERROR,
        constants.LOG_CRITICAL,
    )

    assert all(isinstance(level, str) for level in levels)


# ============================================================================
# Primitive contract
# ============================================================================


def test_state_constants_are_strings():
    state_constants = (
        constants.KERNEL_STATE_CREATED,
        constants.KERNEL_STATE_BOOTING,
        constants.KERNEL_STATE_RUNNING,
        constants.KERNEL_STATE_STOPPING,
        constants.KERNEL_STATE_STOPPED,
        constants.KERNEL_STATE_FAILED,
        constants.AGENT_IDLE,
        constants.AGENT_RUNNING,
        constants.AGENT_WAITING,
        constants.AGENT_FINISHED,
        constants.AGENT_FAILED,
    )

    assert all(isinstance(value, str) for value in state_constants)


def test_constants_are_importable_from_shared_package():
    import scios.shared as shared

    for name in constants.__all__:
        assert hasattr(shared, name)
