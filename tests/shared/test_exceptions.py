"""
Tests for SciOS exception contracts.
"""

import pytest

from scios.shared.exceptions import (
    AgentError,
    AlgebraError,
    BootError,
    CollaborationError,
    CompressionError,
    ConfigurationError,
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
    EmbeddingError,
)


# ============================================================================
# Public API
# ============================================================================


def test_exception_classes_exist():
    exceptions = (
        SciOSError,
        KernelError,
        BootError,
        LifecycleError,
        SchedulerError,
        SciOSRuntimeError,
        ExecutionError,
        AgentError,
        PlanningError,
        ReasoningError,
        ReflectionError,
        ToolError,
        CollaborationError,
        SciOSMemoryError,
        RetrievalError,
        StorageError,
        VectorStoreError,
        EmbeddingError,
        SearchError,
        VectorIndexError,
        QTCError,
        AlgebraError,
        MorphismError,
        CompressionError,
        VerificationError,
        ConfigurationError,
        ValidationError,
        SerializationError,
        PluginError,
        NetworkError,
    )

    for exception in exceptions:
        assert exception is not None
        assert issubclass(exception, Exception)


# ============================================================================
# Base exception
# ============================================================================


def test_scios_error_defaults():
    error = SciOSError()

    assert error.message == ""
    assert error.error_code is None
    assert error.details == {}
    assert error.cause is None


def test_scios_error_message():
    error = SciOSError("Something went wrong")

    assert error.message == "Something went wrong"
    assert str(error) == "Something went wrong"


def test_scios_error_error_code():
    error = SciOSError(
        "Task failed",
        error_code="TASK_FAILED",
    )

    assert error.message == "Task failed"
    assert error.error_code == "TASK_FAILED"
    assert str(error) == "[TASK_FAILED] Task failed"


def test_scios_error_details():
    details = {
        "task_id": "task-1",
        "worker": 3,
        "retryable": True,
    }

    error = SciOSError(
        "Task failed",
        details=details,
    )

    assert error.details == details
    assert error.details is details


def test_scios_error_cause():
    cause = ValueError("invalid value")

    error = SciOSError(
        "Task failed",
        cause=cause,
    )

    assert error.cause is cause
    assert "caused by invalid value" in str(error)


def test_scios_error_all_metadata():
    cause = RuntimeError("backend failure")

    error = SciOSError(
        "Execution failed",
        error_code="EXEC-001",
        details={
            "task_id": "task-42",
            "worker": "worker-1",
        },
        cause=cause,
    )

    text = str(error)

    assert "[EXEC-001]" in text
    assert "Execution failed" in text
    assert "caused by backend failure" in text


# ============================================================================
# to_dict
# ============================================================================


def test_to_dict_defaults():
    error = SciOSError()

    result = error.to_dict()

    assert result == {
        "type": "SciOSError",
        "message": "",
        "error_code": None,
        "details": {},
        "cause": None,
    }


def test_to_dict_contains_metadata():
    cause = ValueError("bad input")

    error = SciOSError(
        "Validation failed",
        error_code="VAL-001",
        details={
            "field": "workers",
            "value": -1,
        },
        cause=cause,
    )

    result = error.to_dict()

    assert result["type"] == "SciOSError"
    assert result["message"] == "Validation failed"
    assert result["error_code"] == "VAL-001"
    assert result["details"] == {
        "field": "workers",
        "value": -1,
    }
    assert result["cause"] == repr(cause)


def test_to_dict_uses_concrete_exception_type():
    error = BootError(
        "Kernel boot failed",
        error_code="BOOT-001",
    )

    result = error.to_dict()

    assert result["type"] == "BootError"


# ============================================================================
# Exception hierarchy
# ============================================================================


@pytest.mark.parametrize(
    ("child", "parent"),
    [
        (KernelError, SciOSError),
        (BootError, KernelError),
        (LifecycleError, KernelError),
        (SchedulerError, KernelError),

        (SciOSRuntimeError, SciOSError),
        (ExecutionError, SciOSRuntimeError),

        (AgentError, SciOSError),
        (PlanningError, AgentError),
        (ReasoningError, AgentError),
        (ReflectionError, AgentError),
        (ToolError, AgentError),
        (CollaborationError, AgentError),

        (SciOSMemoryError, SciOSError),
        (RetrievalError, SciOSMemoryError),
        (StorageError, SciOSMemoryError),

        (VectorStoreError, SciOSError),
        (EmbeddingError, VectorStoreError),
        (SearchError, VectorStoreError),
        (VectorIndexError, VectorStoreError),

        (QTCError, SciOSError),
        (AlgebraError, QTCError),
        (MorphismError, QTCError),
        (CompressionError, QTCError),
        (VerificationError, QTCError),

        (ConfigurationError, SciOSError),
        (ValidationError, SciOSError),
        (SerializationError, SciOSError),
        (PluginError, SciOSError),
        (NetworkError, SciOSError),
    ],
)
def test_exception_hierarchy(child, parent):
    assert issubclass(child, parent)


# ============================================================================
# Runtime isinstance checks
# ============================================================================


@pytest.mark.parametrize(
    "exception_type",
    [
        KernelError,
        BootError,
        LifecycleError,
        SchedulerError,
        SciOSRuntimeError,
        ExecutionError,
        AgentError,
        PlanningError,
        ReasoningError,
        ReflectionError,
        ToolError,
        CollaborationError,
        SciOSMemoryError,
        RetrievalError,
        StorageError,
        VectorStoreError,
        EmbeddingError,
        SearchError,
        VectorIndexError,
        QTCError,
        AlgebraError,
        MorphismError,
        CompressionError,
        VerificationError,
        ConfigurationError,
        ValidationError,
        SerializationError,
        PluginError,
        NetworkError,
    ],
)
def test_all_specialized_exceptions_are_scios_errors(exception_type):
    error = exception_type("failure")

    assert isinstance(error, SciOSError)
    assert isinstance(error, Exception)


# ============================================================================
# Concrete exception construction
# ============================================================================


@pytest.mark.parametrize(
    "exception_type",
    [
        KernelError,
        BootError,
        LifecycleError,
        SchedulerError,
        SciOSRuntimeError,
        ExecutionError,
        AgentError,
        PlanningError,
        ReasoningError,
        ReflectionError,
        ToolError,
        CollaborationError,
        SciOSMemoryError,
        RetrievalError,
        StorageError,
        VectorStoreError,
        EmbeddingError,
        SearchError,
        VectorIndexError,
        QTCError,
        AlgebraError,
        MorphismError,
        CompressionError,
        VerificationError,
        ConfigurationError,
        ValidationError,
        SerializationError,
        PluginError,
        NetworkError,
    ],
)
def test_specialized_exception_preserves_metadata(exception_type):
    error = exception_type(
        "failure",
        error_code="ERR-001",
        details={"component": "test"},
    )

    assert error.message == "failure"
    assert error.error_code == "ERR-001"
    assert error.details == {"component": "test"}


# ============================================================================
# Python exception semantics
# ============================================================================


def test_scios_error_can_be_raised_and_caught():
    with pytest.raises(SciOSError) as captured:
        raise SciOSError("failure")

    assert captured.value.message == "failure"


def test_child_exception_can_be_caught_as_scios_error():
    with pytest.raises(SciOSError) as captured:
        raise ExecutionError("execution failed")

    assert isinstance(captured.value, ExecutionError)


def test_exception_can_be_caught_by_intermediate_class():
    with pytest.raises(KernelError):
        raise BootError("boot failed")

    with pytest.raises(AgentError):
        raise PlanningError("planning failed")

    with pytest.raises(VectorStoreError):
        raise SearchError("search failed")

    with pytest.raises(QTCError):
        raise CompressionError("compression failed")


# ============================================================================
# Explicit cause support
# ============================================================================


def test_explicit_cause_is_preserved():
    original = ValueError("original")

    error = ExecutionError(
        "execution failed",
        cause=original,
    )

    assert error.cause is original


def test_to_dict_preserves_cause_representation():
    original = ValueError("original")

    error = ExecutionError(
        "execution failed",
        cause=original,
    )

    result = error.to_dict()

    assert result["cause"] == repr(original)


# ============================================================================
# Details behavior
# ============================================================================


def test_details_default_is_new_dictionary():
    first = SciOSError()
    second = SciOSError()

    assert first.details == {}
    assert second.details == {}
    assert first.details is not second.details


def test_details_can_contain_nested_data():
    details = {
        "task": {
            "id": "task-1",
            "attempt": 2,
        },
        "errors": [
            "timeout",
            "retry",
        ],
    }

    error = SciOSError(
        "task failed",
        details=details,
    )

    assert error.details["task"]["id"] == "task-1"
    assert error.details["task"]["attempt"] == 2
    assert error.details["errors"] == ["timeout", "retry"]


# ============================================================================
# String representation
# ============================================================================


def test_str_without_message_or_code_or_cause():
    error = SciOSError()

    assert str(error) == ""


def test_str_with_message_only():
    assert str(SciOSError("failure")) == "failure"


def test_str_with_code_only():
    assert str(
        SciOSError(
            error_code="ERR-001",
        )
    ) == "[ERR-001]"


def test_str_with_cause_only():
    cause = ValueError("original")

    assert str(
        SciOSError(
            cause=cause,
        )
    ) == "(caused by original)"


# ============================================================================
# Public inheritance stability
# ============================================================================


def test_kernel_family_isolated_from_runtime_family():
    assert not issubclass(KernelError, SciOSRuntimeError)
    assert not issubclass(SciOSRuntimeError, KernelError)


def test_agent_family_isolated_from_memory_family():
    assert not issubclass(AgentError, SciOSMemoryError)
    assert not issubclass(SciOSMemoryError, AgentError)


def test_vector_family_isolated_from_qtc_family():
    assert not issubclass(VectorStoreError, QTCError)
    assert not issubclass(QTCError, VectorStoreError)


# ============================================================================
# Export contract
# ============================================================================


def test_module_all_exports_are_importable():
    import scios.shared.exceptions as exceptions

    for name in exceptions.__all__:
        assert hasattr(exceptions, name)


def test_module_all_contains_expected_count():
    import scios.shared.exceptions as exceptions

    assert len(exceptions.__all__) == 30
