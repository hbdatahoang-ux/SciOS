"""
SciOS-NG Observability
Tracing Test - Trace

Tests:

- Trace creation
- Trace lifecycle
- Trace status
- Trace metadata
- Attributes
- Tags
- Events
- Serialization
- Snapshot
- Copy / Clone
- Validation
- Python protocols

"""

from __future__ import annotations


import copy
import json
import time


import pytest


from scios.runtime.observability.tracing.trace import (
    Trace,
)


# ============================================================
# Fixtures
# ============================================================


@pytest.fixture
def trace() -> Trace:
    """
    Create test trace.
    """

    return Trace(
        name="test.trace"
    )



@pytest.fixture
def running_trace() -> Trace:
    """
    Create started trace.
    """

    trace = Trace(
        name="runtime.pipeline"
    )


    trace.start()


    return trace



# ============================================================
# Creation
# ============================================================


def test_trace_creation(trace):

    assert trace is not None

    assert trace.name == (
        "test.trace"
    )

    assert trace.trace_id is not None



def test_trace_unique_identifier():

    first = Trace(
        name="a"
    )

    second = Trace(
        name="b"
    )


    assert (
        first.trace_id
        !=
        second.trace_id
    )



# ============================================================
# Lifecycle
# ============================================================


def test_trace_start(trace):

    trace.start()


    assert trace.started is True



def test_trace_finish(running_trace):

    running_trace.finish()


    assert (
        running_trace.finished
        is True
    )



def test_trace_duration(running_trace):

    time.sleep(
        0.01
    )


    running_trace.finish()


    assert (
        running_trace.duration
        >= 0
    )



def test_trace_stop_without_start():

    trace = Trace(
        name="invalid"
    )


    trace.finish()


    assert (
        trace.finished
        is True
    )



# ============================================================
# Attributes
# ============================================================


def test_trace_attributes(trace):

    trace.set_attribute(
        "service",
        "scios",
    )


    assert (
        trace.attributes["service"]
        ==
        "scios"
    )



def test_trace_multiple_attributes(trace):

    trace.set_attribute(
        "version",
        "0.3",
    )


    trace.set_attribute(
        "environment",
        "test",
    )


    assert len(
        trace.attributes
    ) == 2



def test_remove_attribute(trace):

    trace.set_attribute(
        "key",
        "value",
    )


    trace.remove_attribute(
        "key"
    )


    assert (
        "key"
        not in trace.attributes
    )



# ============================================================
# Tags
# ============================================================


def test_trace_tags(trace):

    trace.set_tag(
        "component",
        "runtime",
    )


    assert (
        trace.tags["component"]
        ==
        "runtime"
    )



def test_remove_tag(trace):

    trace.set_tag(
        "temporary",
        "true",
    )


    trace.remove_tag(
        "temporary"
    )


    assert (
        "temporary"
        not in trace.tags
    )



# ============================================================
# Events
# ============================================================


def test_trace_event(trace):

    trace.add_event(
        "pipeline.started"
    )


    assert (
        "pipeline.started"
        in trace.events
    )



def test_multiple_events(trace):

    trace.add_event(
        "start"
    )


    trace.add_event(
        "finish"
    )


    assert len(
        trace.events
    ) == 2



# ============================================================
# Status
# ============================================================


def test_trace_status(trace):

    assert (
        trace.status
        is not None
    )



def test_trace_finished_status(running_trace):

    running_trace.finish()


    assert (
        running_trace.finished
    )



# ============================================================
# Context
# ============================================================


def test_trace_context(trace):

    trace.set_context(
        "request_id",
        "req-001",
    )


    assert (
        trace.context["request_id"]
        ==
        "req-001"
    )



def test_trace_context_propagation(trace):

    trace.set_context(
        "user",
        "agent",
    )


    child = trace.clone()


    assert (
        child.context["user"]
        ==
        "agent"
    )



# ============================================================
# Serialization
# ============================================================


def test_trace_to_dict(trace):

    data = trace.to_dict()


    assert isinstance(
        data,
        dict,
    )


    assert (
        data["name"]
        ==
        "test.trace"
    )



def test_trace_to_json(trace):

    result = trace.to_json()


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
        "test.trace"
    )



def test_trace_from_dict(trace):

    data = trace.to_dict()


    restored = Trace.from_dict(
        data
    )


    assert (
        restored.name
        ==
        trace.name
    )



def test_trace_from_json(trace):

    data = trace.to_json()


    restored = Trace.from_json(
        data
    )


    assert (
        restored.trace_id
        ==
        trace.trace_id
    )



# ============================================================
# Snapshot
# ============================================================


def test_trace_snapshot(trace):

    snapshot = trace.snapshot()


    assert isinstance(
        snapshot,
        dict,
    )


    assert (
        snapshot["name"]
        ==
        "test.trace"
    )



def test_trace_restore(trace):

    snapshot = trace.snapshot()


    restored = Trace.restore(
        snapshot
    )


    assert (
        restored.name
        ==
        trace.name
    )



# ============================================================
# Clone / Copy
# ============================================================


def test_trace_clone(trace):

    cloned = trace.clone()


    assert (
        cloned.name
        ==
        trace.name
    )


    assert (
        cloned.trace_id
        ==
        trace.trace_id
    )



def test_trace_copy(trace):

    copied = trace.copy()


    assert (
        copied.name
        ==
        trace.name
    )



def test_python_copy(trace):

    copied = copy.copy(
        trace
    )


    assert (
        copied.name
        ==
        trace.name
    )



def test_python_deepcopy(trace):

    copied = copy.deepcopy(
        trace
    )


    assert (
        copied.name
        ==
        trace.name
    )



# ============================================================
# Validation
# ============================================================


def test_trace_validation(trace):

    assert (
        trace.validate()
        is True
    )



def test_trace_invalid_name():

    with pytest.raises(
        Exception
    ):

        Trace(
            name=""
        )



# ============================================================
# Diagnostics
# ============================================================


def test_trace_diagnostics(trace):

    result = trace.diagnostics()


    assert isinstance(
        result,
        dict,
    )



def test_trace_summary(trace):

    result = trace.summary()


    assert isinstance(
        result,
        dict,
    )



# ============================================================
# Python Protocols
# ============================================================


def test_trace_repr(trace):

    value = repr(
        trace
    )


    assert (
        "Trace"
        in value
    )



def test_trace_str(trace):

    value = str(
        trace
    )


    assert isinstance(
        value,
        str,
    )



def test_trace_len(trace):

    assert (
        len(trace)
        >= 0
    )



def test_trace_contains(trace):

    trace.set_attribute(
        "x",
        1,
    )


    assert (
        "x"
        in trace
    )



def test_trace_getitem(trace):

    trace["key"] = (
        "value"
    )


    assert (
        trace["key"]
        ==
        "value"
    )



def test_trace_setitem(trace):

    trace["enabled"] = True


    assert (
        trace["enabled"]
        is True
    )



# ============================================================
# Equality / Hash
# ============================================================


def test_trace_equality():

    a = Trace(
        name="same"
    )


    b = Trace(
        name="same"
    )


    assert (
        a != b
    )



def test_trace_hash(trace):

    value = hash(
        trace
    )


    assert isinstance(
        value,
        int,
    )