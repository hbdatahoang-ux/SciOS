"""
SciOS-NG Observability
Tracing Test - Status

Tests:

- Status creation
- Status enum
- Status transitions
- OK / ERROR / UNSET
- Exception handling
- Serialization
- Snapshot
- Clone / Copy
- Validation
- Python protocols

"""

from __future__ import annotations


import copy
import json


import pytest


from scios.runtime.observability.tracing.status import (
    Status,
    StatusCode,
)



# ============================================================
# Fixtures
# ============================================================


@pytest.fixture
def status() -> Status:
    """
    Default status.
    """

    return Status()



@pytest.fixture
def ok_status() -> Status:

    return Status(
        code=StatusCode.OK
    )



@pytest.fixture
def error_status() -> Status:

    return Status(
        code=StatusCode.ERROR,
        message="failure",
    )



# ============================================================
# Creation
# ============================================================


def test_status_creation(status):

    assert status is not None



def test_default_status_code(status):

    assert (
        status.code
        ==
        StatusCode.UNSET
    )



def test_status_message():

    value = Status(
        message="running"
    )


    assert (
        value.message
        ==
        "running"
    )



# ============================================================
# Status Codes
# ============================================================


def test_unset_status(status):

    assert (
        status.is_unset()
        is True
    )



def test_ok_status(ok_status):

    assert (
        ok_status.is_ok()
        is True
    )



def test_error_status(error_status):

    assert (
        error_status.is_error()
        is True
    )



# ============================================================
# Lifecycle
# ============================================================


def test_set_ok(status):

    status.set_ok()


    assert (
        status.code
        ==
        StatusCode.OK
    )



def test_set_error(status):

    status.set_error(
        "runtime failed"
    )


    assert (
        status.code
        ==
        StatusCode.ERROR
    )


    assert (
        status.message
        ==
        "runtime failed"
    )



def test_reset_status(error_status):

    error_status.reset()


    assert (
        error_status.code
        ==
        StatusCode.UNSET
    )



# ============================================================
# Exception Handling
# ============================================================


def test_attach_exception(status):

    try:

        raise ValueError(
            "invalid value"
        )


    except Exception as exc:

        status.attach_exception(
            exc
        )


    assert (
        status.is_error()
        is True
    )



def test_exception_type(status):

    try:

        raise RuntimeError(
            "failed"
        )


    except Exception as exc:

        status.attach_exception(
            exc
        )


    assert (
        status.exception_type()
        ==
        "RuntimeError"
    )



def test_exception_message(status):

    try:

        raise RuntimeError(
            "failed"
        )


    except Exception as exc:

        status.attach_exception(
            exc
        )


    assert (
        "failed"
        in
        status.exception_message()
    )



def test_clear_exception(status):

    try:

        raise Exception(
            "error"
        )


    except Exception as exc:

        status.attach_exception(
            exc
        )


    status.clear_exception()


    assert (
        status.exception
        is None
    )



# ============================================================
# Metadata
# ============================================================


def test_status_attributes(status):

    status.set_attribute(
        "component",
        "kernel",
    )


    assert (
        status.attributes["component"]
        ==
        "kernel"
    )



def test_remove_attribute(status):

    status.set_attribute(
        "temp",
        True,
    )


    status.remove_attribute(
        "temp"
    )


    assert (
        "temp"
        not in status.attributes
    )



# ============================================================
# Serialization
# ============================================================


def test_status_to_dict(error_status):

    data = (
        error_status
        .to_dict()
    )


    assert isinstance(
        data,
        dict,
    )


    assert (
        data["code"]
        ==
        "ERROR"
    )



def test_status_to_json(error_status):

    value = (
        error_status
        .to_json()
    )


    assert isinstance(
        value,
        str,
    )


    data = json.loads(
        value
    )


    assert (
        data["code"]
        ==
        "ERROR"
    )



def test_status_from_dict(error_status):

    data = (
        error_status
        .to_dict()
    )


    restored = (
        Status
        .from_dict(data)
    )


    assert (
        restored.code
        ==
        error_status.code
    )



def test_status_from_json(error_status):

    data = (
        error_status
        .to_json()
    )


    restored = (
        Status
        .from_json(data)
    )


    assert (
        restored.message
        ==
        error_status.message
    )



# ============================================================
# Snapshot
# ============================================================


def test_status_snapshot(error_status):

    snapshot = (
        error_status
        .snapshot()
    )


    assert isinstance(
        snapshot,
        dict,
    )


    assert (
        snapshot["code"]
        ==
        "ERROR"
    )



def test_status_restore(error_status):

    snapshot = (
        error_status
        .snapshot()
    )


    restored = (
        Status
        .restore(snapshot)
    )


    assert (
        restored.code
        ==
        error_status.code
    )



# ============================================================
# Clone / Copy
# ============================================================


def test_status_clone(error_status):

    clone = (
        error_status
        .clone()
    )


    assert (
        clone.code
        ==
        error_status.code
    )



def test_status_copy(error_status):

    copied = (
        error_status
        .copy()
    )


    assert (
        copied.message
        ==
        error_status.message
    )



def test_python_copy(error_status):

    copied = copy.copy(
        error_status
    )


    assert (
        copied.code
        ==
        error_status.code
    )



def test_python_deepcopy(error_status):

    copied = copy.deepcopy(
        error_status
    )


    assert (
        copied.code
        ==
        error_status.code
    )



# ============================================================
# Validation
# ============================================================


def test_validate_status(status):

    assert (
        status.validate()
        is True
    )



def test_invalid_status():

    with pytest.raises(
        Exception
    ):

        Status(
            code="INVALID"
        )



# ============================================================
# Diagnostics
# ============================================================


def test_status_diagnostics(error_status):

    result = (
        error_status
        .diagnostics()
    )


    assert isinstance(
        result,
        dict,
    )



def test_status_summary(error_status):

    result = (
        error_status
        .summary()
    )


    assert isinstance(
        result,
        dict,
    )



# ============================================================
# Python Protocols
# ============================================================


def test_status_repr(status):

    value = repr(
        status
    )


    assert (
        "Status"
        in value
    )



def test_status_str(status):

    value = str(
        status
    )


    assert isinstance(
        value,
        str,
    )



def test_status_len(status):

    assert (
        len(status)
        >= 0
    )



def test_status_contains(status):

    status["key"] = (
        "value"
    )


    assert (
        "key"
        in status
    )



def test_status_getitem(status):

    status["mode"] = (
        "test"
    )


    assert (
        status["mode"]
        ==
        "test"
    )



def test_status_setitem(status):

    status["enabled"] = True


    assert (
        status["enabled"]
        is True
    )



# ============================================================
# Equality / Hash
# ============================================================


def test_status_equality():

    first = Status()

    second = Status()


    assert (
        first == second
    )



def test_status_hash(status):

    value = hash(
        status
    )


    assert isinstance(
        value,
        int,
    )