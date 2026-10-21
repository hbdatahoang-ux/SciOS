"""
SciOS Runtime Observability
Tracing Test - Status

Tests:

- Status creation
- Status enum
- Status transitions
- OK / ERROR / UNSET
- Exception handling
- Attributes
- Serialization
- Snapshot / Restore
- Clone / Copy
- Validation
- Diagnostics
- Python protocols
- Equality / Hash

Python 3.11+
"""

from __future__ import annotations

import copy
import json

import pytest

from scios.runtime.observability.tracing.status import (
    Status,
    StatusCode,
)


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def status() -> Status:
    """Default status."""
    return Status()


@pytest.fixture
def ok_status() -> Status:
    """OK status."""
    return Status(
        code=StatusCode.OK,
    )


@pytest.fixture
def error_status() -> Status:
    """ERROR status."""
    return Status(
        code=StatusCode.ERROR,
        message="failure",
    )


# ==============================================================================
# Creation
# ==============================================================================


def test_status_creation(status: Status):
    assert status is not None


def test_default_status_code(status: Status):
    assert status.code == StatusCode.UNSET


def test_default_status_message(status: Status):
    assert status.message == ""


def test_status_message():
    value = Status(
        message="running",
    )

    assert value.message == "running"


def test_default_status_has_no_exception(status: Status):
    assert status.exception is None


def test_default_status_has_no_attributes(status: Status):
    assert status.attributes == {}


# ==============================================================================
# Status Codes
# ==============================================================================


def test_unset_status(status: Status):
    assert status.is_unset() is True
    assert status.is_ok() is False
    assert status.is_error() is False


def test_ok_status(ok_status: Status):
    assert ok_status.is_ok() is True
    assert ok_status.is_unset() is False
    assert ok_status.is_error() is False


def test_error_status(error_status: Status):
    assert error_status.is_error() is True
    assert error_status.is_unset() is False
    assert error_status.is_ok() is False


def test_status_code_string():
    assert str(StatusCode.UNSET) == "UNSET"
    assert str(StatusCode.OK) == "OK"
    assert str(StatusCode.ERROR) == "ERROR"


# ==============================================================================
# Lifecycle
# ==============================================================================


def test_set_ok(status: Status):
    status.set_ok()

    assert status.code == StatusCode.OK
    assert status.is_ok() is True


def test_set_ok_message(status: Status):
    status.set_ok(
        "completed",
    )

    assert status.code == StatusCode.OK
    assert status.message == "completed"


def test_set_error(status: Status):
    status.set_error(
        "runtime failed",
    )

    assert status.code == StatusCode.ERROR
    assert status.message == "runtime failed"
    assert status.is_error() is True


def test_reset_status(error_status: Status):
    error_status.set_attribute(
        "component",
        "runtime",
    )

    error_status.reset()

    assert error_status.code == StatusCode.UNSET
    assert error_status.message == ""
    assert error_status.exception is None
    assert error_status.attributes == {}


def test_state_transition_unset_to_ok(status: Status):
    status.set_ok()

    assert status.code == StatusCode.OK


def test_state_transition_ok_to_error(status: Status):
    status.set_ok()

    status.set_error(
        "failed",
    )

    assert status.code == StatusCode.ERROR


def test_state_transition_error_to_ok(status: Status):
    status.set_error(
        "failed",
    )

    status.set_ok(
        "recovered",
    )

    assert status.code == StatusCode.OK
    assert status.message == "recovered"
    assert status.exception is None


# ==============================================================================
# Exception Handling
# ==============================================================================


def test_attach_exception(status: Status):
    try:
        raise ValueError(
            "invalid value",
        )

    except Exception as exc:
        status.attach_exception(
            exc,
        )

    assert status.is_error() is True
    assert status.exception is not None


def test_exception_type(status: Status):
    try:
        raise RuntimeError(
            "failed",
        )

    except Exception as exc:
        status.attach_exception(
            exc,
        )

    assert status.exception_type() == "RuntimeError"


def test_exception_message(status: Status):
    try:
        raise RuntimeError(
            "failed",
        )

    except Exception as exc:
        status.attach_exception(
            exc,
        )

    assert "failed" in status.exception_message()


def test_attach_exception_sets_error(status: Status):
    exception = RuntimeError(
        "failure",
    )

    status.attach_exception(
        exception,
    )

    assert status.code == StatusCode.ERROR


def test_attach_exception_sets_message_when_empty(
    status: Status,
):
    exception = RuntimeError(
        "failure",
    )

    status.attach_exception(
        exception,
    )

    assert status.message == "failure"


def test_attach_exception_preserves_existing_message(
    status: Status,
):
    status.message = "custom message"

    exception = RuntimeError(
        "failure",
    )

    status.attach_exception(
        exception,
    )

    assert status.message == "custom message"


def test_clear_exception(status: Status):
    exception = RuntimeError(
        "error",
    )

    status.attach_exception(
        exception,
    )

    assert status.exception is exception

    status.clear_exception()

    assert status.exception is None
    assert status.has_exception is False


def test_has_exception(status: Status):
    assert status.has_exception is False

    status.attach_exception(
        RuntimeError(
            "failed",
        ),
    )

    assert status.has_exception is True


# ==============================================================================
# Attributes
# ==============================================================================


def test_status_attributes(status: Status):
    status.set_attribute(
        "component",
        "kernel",
    )

    assert status.attributes["component"] == "kernel"


def test_remove_attribute(status: Status):
    status.set_attribute(
        "temp",
        True,
    )

    status.remove_attribute(
        "temp",
    )

    assert "temp" not in status.attributes


def test_attribute_count(status: Status):
    assert status.attribute_count == 0

    status.set_attribute(
        "one",
        1,
    )

    status.set_attribute(
        "two",
        2,
    )

    assert status.attribute_count == 2


def test_attribute_chaining(status: Status):
    result = (
        status
        .set_attribute("a", 1)
        .set_attribute("b", 2)
    )

    assert result is status
    assert status.attributes == {
        "a": 1,
        "b": 2,
    }


# ==============================================================================
# Serialization
# ==============================================================================


def test_status_to_dict(error_status: Status):
    data = error_status.to_dict()

    assert isinstance(
        data,
        dict,
    )

    assert data["code"] == "ERROR"
    assert data["message"] == "failure"


def test_status_to_json(error_status: Status):
    value = error_status.to_json()

    assert isinstance(
        value,
        str,
    )

    data = json.loads(
        value,
    )

    assert data["code"] == "ERROR"
    assert data["message"] == "failure"


def test_status_from_dict(error_status: Status):
    data = error_status.to_dict()

    restored = Status.from_dict(
        data,
    )

    assert restored.code == error_status.code
    assert restored.message == error_status.message
    assert restored.attributes == error_status.attributes


def test_status_from_json(error_status: Status):
    data = error_status.to_json()

    restored = Status.from_json(
        data,
    )

    assert restored.code == error_status.code
    assert restored.message == error_status.message


def test_status_serialization_preserves_attributes(
    status: Status,
):
    status.set_attribute(
        "component",
        "kernel",
    )

    status.set_attribute(
        "version",
        1,
    )

    restored = Status.from_dict(
        status.to_dict(),
    )

    assert restored.attributes == {
        "component": "kernel",
        "version": 1,
    }


# ==============================================================================
# Snapshot
# ==============================================================================


def test_status_snapshot(error_status: Status):
    snapshot = error_status.snapshot()

    assert isinstance(
        snapshot,
        dict,
    )

    assert snapshot["code"] == "ERROR"
    assert snapshot["message"] == "failure"


def test_status_restore(error_status: Status):
    snapshot = error_status.snapshot()

    restored = Status.restore(
        snapshot,
    )

    assert restored.code == error_status.code
    assert restored.message == error_status.message


def test_snapshot_is_independent(status: Status):
    status.set_attribute(
        "component",
        "kernel",
    )

    snapshot = status.snapshot()

    snapshot["attributes"]["component"] = "changed"

    assert status.attributes["component"] == "kernel"


# ==============================================================================
# Clone / Copy
# ==============================================================================


def test_status_clone(error_status: Status):
    clone = error_status.clone()

    assert clone is not error_status
    assert clone.code == error_status.code
    assert clone.message == error_status.message


def test_status_clone_is_independent(status: Status):
    status.set_attribute(
        "component",
        "kernel",
    )

    clone = status.clone()

    clone.attributes["component"] = "changed"

    assert status.attributes["component"] == "kernel"


def test_status_copy(error_status: Status):
    copied = error_status.copy()

    assert copied is not error_status
    assert copied.message == error_status.message
    assert copied.code == error_status.code


def test_python_copy(error_status: Status):
    copied = copy.copy(
        error_status,
    )

    assert copied is not error_status
    assert copied.code == error_status.code


def test_python_deepcopy(error_status: Status):
    copied = copy.deepcopy(
        error_status,
    )

    assert copied is not error_status
    assert copied.code == error_status.code


# ==============================================================================
# Validation
# ==============================================================================


def test_validate_status(status: Status):
    assert status.validate() is True


def test_validate_ok_status(ok_status: Status):
    assert ok_status.validate() is True


def test_validate_error_status(error_status: Status):
    assert error_status.validate() is True


def test_invalid_status():
    with pytest.raises(
        Exception,
    ):
        Status(
            code="INVALID",
        )


# ==============================================================================
# Diagnostics
# ==============================================================================


def test_status_diagnostics(error_status: Status):
    result = error_status.diagnostics()

    assert isinstance(
        result,
        dict,
    )

    assert result["valid"] is True
    assert result["code"] == "ERROR"
    assert result["message"] == "failure"


def test_status_summary(error_status: Status):
    result = error_status.summary()

    assert isinstance(
        result,
        dict,
    )

    assert result["code"] == "ERROR"
    assert result["message"] == "failure"


# ==============================================================================
# Python Protocols
# ==============================================================================


def test_status_repr(status: Status):
    value = repr(
        status,
    )

    assert "Status" in value


def test_status_str(status: Status):
    value = str(
        status,
    )

    assert isinstance(
        value,
        str,
    )

    assert "UNSET" in value


def test_status_len(status: Status):
    assert len(status) >= 0


def test_status_contains(status: Status):
    status["key"] = "value"

    assert "key" in status


def test_status_getitem(status: Status):
    status["mode"] = "test"

    assert status["mode"] == "test"


def test_status_setitem(status: Status):
    status["enabled"] = True

    assert status["enabled"] is True


def test_status_delitem(status: Status):
    status["temporary"] = True

    del status["temporary"]

    assert "temporary" not in status


def test_status_iteration(status: Status):
    status["a"] = 1
    status["b"] = 2

    assert set(iter(status)) == {
        "a",
        "b",
    }


def test_status_bool(status: Status):
    assert bool(status) is True


# ==============================================================================
# Equality / Hash
# ==============================================================================


def test_status_equality():
    first = Status()
    second = Status()

    assert first == second


def test_status_inequality():
    first = Status(
        message="one",
    )

    second = Status(
        message="two",
    )

    assert first != second


def test_status_hash(status: Status):
    value = hash(
        status,
    )

    assert isinstance(
        value,
        int,
    )


# ==============================================================================
# Public API
# ==============================================================================


def test_status_public_api():
    from scios.runtime.observability.tracing.status import (
        StatusAttributeMap,
        StatusError,
        StatusJSON,
        StatusSerializationError,
        StatusValidationError,
        TraceStatus,
    )

    assert Status is not None
    assert StatusCode is not None
    assert TraceStatus is Status
    assert StatusError is not None
    assert StatusValidationError is not None
    assert StatusSerializationError is not None
    assert StatusAttributeMap is not None
    assert StatusJSON is not None
