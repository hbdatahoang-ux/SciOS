"""
SciOS-NG Observability
Tracing Test - Span

Tests:

- Span creation
- Span lifecycle
- Parent / Child relation
- Context propagation
- Attributes
- Events
- Status
- Exception handling
- Serialization
- Snapshot
- Clone
- Validation
- Python protocols

"""

from __future__ import annotations


import copy
import json
import time


import pytest


from scios.runtime.observability.tracing.span import (
    Span,
)



# ============================================================
# Fixtures
# ============================================================


@pytest.fixture
def span() -> Span:
    """
    Create standalone span.
    """

    return Span(
        name="test.span"
    )



@pytest.fixture
def trace_span() -> Span:
    """
    Create span with trace context.
    """

    return Span(
        name="runtime.execute",
        trace_id="trace-001",
    )



@pytest.fixture
def child_span() -> Span:

    return Span(

        name="child.operation",

        trace_id="trace-001",

        parent_span_id="parent-001",
    )



# ============================================================
# Creation
# ============================================================


def test_span_creation(span):

    assert span is not None

    assert (
        span.name
        ==
        "test.span"
    )


    assert (
        span.span_id
        is not None
    )



def test_span_unique_id():

    first = Span(
        name="a"
    )


    second = Span(
        name="b"
    )


    assert (
        first.span_id
        !=
        second.span_id
    )



# ============================================================
# Trace Context
# ============================================================


def test_span_trace_id(trace_span):

    assert (
        trace_span.trace_id
        ==
        "trace-001"
    )



def test_child_parent_relation(child_span):

    assert (
        child_span.parent_span_id
        ==
        "parent-001"
    )



# ============================================================
# Lifecycle
# ============================================================


def test_span_start(span):

    span.start()


    assert (
        span.started
        is True
    )



def test_span_finish(span):

    span.start()

    span.finish()


    assert (
        span.finished
        is True
    )



def test_span_duration(span):

    span.start()


    time.sleep(
        0.01
    )


    span.finish()


    assert (
        span.duration
        >=
        0
    )



def test_span_end_without_start():

    span = Span(
        name="invalid.end"
    )


    span.finish()


    assert (
        span.finished
        is True
    )



# ============================================================
# Status
# ============================================================


def test_default_status(span):

    assert (
        span.status
        is not None
    )



def test_success_status(span):

    span.start()

    span.finish()


    assert (
        span.finished
    )



def test_error_status(span):

    span.record_error(
        "failed"
    )


    assert (
        span.status
        is not None
    )



# ============================================================
# Attributes
# ============================================================


def test_set_attribute(span):

    span.set_attribute(

        "model",

        "SciOS-Agent",
    )


    assert (
        span.attributes["model"]
        ==
        "SciOS-Agent"
    )



def test_multiple_attributes(span):

    span.set_attribute(
        "a",
        1,
    )

    span.set_attribute(
        "b",
        2,
    )


    assert len(
        span.attributes
    ) == 2



def test_remove_attribute(span):

    span.set_attribute(
        "temp",
        True,
    )


    span.remove_attribute(
        "temp"
    )


    assert (
        "temp"
        not in span.attributes
    )



# ============================================================
# Events
# ============================================================


def test_add_event(span):

    span.add_event(
        "operation.started"
    )


    assert (
        "operation.started"
        in span.events
    )



def test_multiple_events(span):

    span.add_event(
        "start"
    )


    span.add_event(
        "end"
    )


    assert len(
        span.events
    ) == 2



def test_event_timestamp(span):

    event = span.add_event(
        "checkpoint"
    )


    assert (
        event
        is not None
    )



# ============================================================
# Exception Handling
# ============================================================


def test_record_exception(span):

    try:

        raise ValueError(
            "test error"
        )


    except Exception as exc:

        span.record_exception(
            exc
        )


    assert (
        len(
            span.exceptions
        )
        == 1
    )



def test_exception_message(span):

    try:

        raise RuntimeError(
            "runtime failed"
        )


    except Exception as exc:

        span.record_exception(
            exc
        )


    assert (
        "runtime failed"
        in str(
            span.exceptions[0]
        )
    )



# ============================================================
# Context
# ============================================================


def test_span_context(span):

    span.set_context(
        "request_id",
        "req-001",
    )


    assert (
        span.context["request_id"]
        ==
        "req-001"
    )



def test_context_clone(span):

    span.set_context(
        "service",
        "kernel",
    )


    cloned = span.clone()


    assert (
        cloned.context["service"]
        ==
        "kernel"
    )



# ============================================================
# Serialization
# ============================================================


def test_span_to_dict(span):

    data = span.to_dict()


    assert isinstance(
        data,
        dict,
    )


    assert (
        data["name"]
        ==
        "test.span"
    )



def test_span_json(span):

    result = span.to_json()


    assert isinstance(
        result,
        str,
    )


    parsed = json.loads(
        result
    )


    assert (
        parsed["name"]
        ==
        "test.span"
    )



def test_span_from_dict(span):

    data = span.to_dict()


    restored = Span.from_dict(
        data
    )


    assert (
        restored.name
        ==
        span.name
    )



def test_span_from_json(span):

    data = span.to_json()


    restored = Span.from_json(
        data
    )


    assert (
        restored.span_id
        ==
        span.span_id
    )



# ============================================================
# Snapshot
# ============================================================


def test_span_snapshot(span):

    snapshot = span.snapshot()


    assert isinstance(
        snapshot,
        dict,
    )


    assert (
        snapshot["name"]
        ==
        "test.span"
    )



def test_span_restore(span):

    snapshot = span.snapshot()


    restored = Span.restore(
        snapshot
    )


    assert (
        restored.name
        ==
        span.name
    )



# ============================================================
# Clone / Copy
# ============================================================


def test_span_clone(span):

    clone = span.clone()


    assert (
        clone.span_id
        ==
        span.span_id
    )



def test_span_copy(span):

    copied = span.copy()


    assert (
        copied.name
        ==
        span.name
    )



def test_python_copy(span):

    copied = copy.copy(
        span
    )


    assert (
        copied.name
        ==
        span.name
    )



def test_python_deepcopy(span):

    copied = copy.deepcopy(
        span
    )


    assert (
        copied.name
        ==
        span.name
    )



# ============================================================
# Validation
# ============================================================


def test_span_validate(span):

    assert (
        span.validate()
        is True
    )



def test_invalid_span_name():

    with pytest.raises(
        Exception
    ):

        Span(
            name=""
        )



# ============================================================
# Diagnostics
# ============================================================


def test_span_diagnostics(span):

    result = span.diagnostics()


    assert isinstance(
        result,
        dict,
    )



def test_span_summary(span):

    result = span.summary()


    assert isinstance(
        result,
        dict,
    )



# ============================================================
# Python Protocols
# ============================================================


def test_repr(span):

    result = repr(
        span
    )


    assert (
        "Span"
        in result
    )



def test_str(span):

    result = str(
        span
    )


    assert isinstance(
        result,
        str,
    )



def test_len(span):

    assert (
        len(span)
        >= 0
    )



def test_contains(span):

    span["key"] = "value"


    assert (
        "key"
        in span
    )



def test_getitem(span):

    span["mode"] = "test"


    assert (
        span["mode"]
        ==
        "test"
    )



def test_setitem(span):

    span["enabled"] = True


    assert (
        span["enabled"]
        is True
    )



# ============================================================
# Equality / Hash
# ============================================================


def test_span_equality():

    first = Span(
        name="same"
    )


    second = Span(
        name="same"
    )


    assert (
        first != second
    )



def test_span_hash(span):

    value = hash(
        span
    )


    assert isinstance(
        value,
        int,
    )