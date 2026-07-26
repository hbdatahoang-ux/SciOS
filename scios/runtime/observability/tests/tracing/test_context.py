"""
SciOS-NG Observability
Tracing Test - Context

Tests:

- Context creation
- Trace ID propagation
- Span ID propagation
- Parent context
- Attributes
- Baggage
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


from scios.runtime.observability.tracing.context import (
    TraceContext,
)



# ============================================================
# Fixtures
# ============================================================


@pytest.fixture
def context() -> TraceContext:
    """
    Create empty context.
    """

    return TraceContext()



@pytest.fixture
def populated_context() -> TraceContext:
    """
    Create context with tracing data.
    """

    ctx = TraceContext()


    ctx.set_trace_id(
        "trace-001"
    )


    ctx.set_span_id(
        "span-001"
    )


    ctx.set_parent_span_id(
        "parent-001"
    )


    return ctx



# ============================================================
# Creation
# ============================================================


def test_context_creation(context):

    assert context is not None



def test_context_default_values(context):

    assert (
        context.trace_id
        is None
    )


    assert (
        context.span_id
        is None
    )



# ============================================================
# Trace ID
# ============================================================


def test_set_trace_id(context):

    context.set_trace_id(
        "trace-123"
    )


    assert (
        context.trace_id
        ==
        "trace-123"
    )



def test_get_trace_id(context):

    context["trace_id"] = (
        "abc"
    )


    assert (
        context.trace_id
        ==
        "abc"
    )



def test_trace_id_validation():

    ctx = TraceContext()


    with pytest.raises(
        Exception
    ):

        ctx.set_trace_id(
            ""
        )



# ============================================================
# Span ID
# ============================================================


def test_set_span_id(context):

    context.set_span_id(
        "span-001"
    )


    assert (
        context.span_id
        ==
        "span-001"
    )



def test_parent_span_id(context):

    context.set_parent_span_id(
        "parent-001"
    )


    assert (
        context.parent_span_id
        ==
        "parent-001"
    )



# ============================================================
# Propagation
# ============================================================


def test_context_propagation(
    populated_context,
):

    child = (
        populated_context
        .propagate()
    )


    assert (
        child.trace_id
        ==
        populated_context.trace_id
    )


    assert (
        child.span_id
        ==
        populated_context.span_id
    )



def test_context_parent_relation(
    populated_context,
):

    assert (
        populated_context.parent_span_id
        ==
        "parent-001"
    )



# ============================================================
# Attributes
# ============================================================


def test_context_attributes(context):

    context.set_attribute(
        "service",
        "runtime",
    )


    assert (
        context.attributes["service"]
        ==
        "runtime"
    )



def test_multiple_attributes(context):

    context.set_attribute(
        "a",
        1,
    )


    context.set_attribute(
        "b",
        2,
    )


    assert len(
        context.attributes
    ) == 2



def test_remove_attribute(context):

    context.set_attribute(
        "temp",
        True,
    )


    context.remove_attribute(
        "temp"
    )


    assert (
        "temp"
        not in context.attributes
    )



# ============================================================
# Baggage
# ============================================================


def test_set_baggage(context):

    context.set_baggage(
        "tenant",
        "scios",
    )


    assert (
        context.baggage["tenant"]
        ==
        "scios"
    )



def test_get_baggage(context):

    context.set_baggage(
        "request",
        "001",
    )


    assert (
        context.get_baggage(
            "request"
        )
        ==
        "001"
    )



def test_remove_baggage(context):

    context.set_baggage(
        "temporary",
        "true",
    )


    context.remove_baggage(
        "temporary"
    )


    assert (
        "temporary"
        not in context.baggage
    )



# ============================================================
# Serialization
# ============================================================


def test_context_to_dict(
    populated_context,
):

    data = (
        populated_context
        .to_dict()
    )


    assert isinstance(
        data,
        dict,
    )


    assert (
        data["trace_id"]
        ==
        "trace-001"
    )



def test_context_to_json(
    populated_context,
):

    result = (
        populated_context
        .to_json()
    )


    assert isinstance(
        result,
        str,
    )


    parsed = json.loads(
        result
    )


    assert (
        parsed["span_id"]
        ==
        "span-001"
    )



def test_context_from_dict(
    populated_context,
):

    data = (
        populated_context
        .to_dict()
    )


    restored = (
        TraceContext
        .from_dict(data)
    )


    assert (
        restored.trace_id
        ==
        populated_context.trace_id
    )



def test_context_from_json(
    populated_context,
):

    data = (
        populated_context
        .to_json()
    )


    restored = (
        TraceContext
        .from_json(data)
    )


    assert (
        restored.span_id
        ==
        populated_context.span_id
    )



# ============================================================
# Snapshot
# ============================================================


def test_context_snapshot(
    populated_context,
):

    snapshot = (
        populated_context
        .snapshot()
    )


    assert isinstance(
        snapshot,
        dict,
    )


    assert (
        snapshot["trace_id"]
        ==
        "trace-001"
    )



def test_context_restore(
    populated_context,
):

    snapshot = (
        populated_context
        .snapshot()
    )


    restored = (
        TraceContext
        .restore(snapshot)
    )


    assert (
        restored.trace_id
        ==
        populated_context.trace_id
    )



# ============================================================
# Clone / Copy
# ============================================================


def test_context_clone(
    populated_context,
):

    clone = (
        populated_context
        .clone()
    )


    assert (
        clone.trace_id
        ==
        populated_context.trace_id
    )



def test_context_copy(
    populated_context,
):

    copied = (
        populated_context
        .copy()
    )


    assert (
        copied.span_id
        ==
        populated_context.span_id
    )



def test_python_copy(
    populated_context,
):

    copied = copy.copy(
        populated_context
    )


    assert (
        copied.trace_id
        ==
        populated_context.trace_id
    )



def test_python_deepcopy(
    populated_context,
):

    copied = copy.deepcopy(
        populated_context
    )


    assert (
        copied.trace_id
        ==
        populated_context.trace_id
    )



# ============================================================
# Validation
# ============================================================


def test_context_validate(
    populated_context,
):

    assert (
        populated_context.validate()
        is True
    )



def test_empty_context_validation(
    context,
):

    assert (
        context.validate()
        is True
    )



# ============================================================
# Diagnostics
# ============================================================


def test_context_diagnostics(
    context,
):

    result = (
        context
        .diagnostics()
    )


    assert isinstance(
        result,
        dict,
    )



def test_context_summary(
    populated_context,
):

    result = (
        populated_context
        .summary()
    )


    assert isinstance(
        result,
        dict,
    )



# ============================================================
# Python Protocols
# ============================================================


def test_context_repr(context):

    result = repr(
        context
    )


    assert (
        "Context"
        in result
    )



def test_context_str(context):

    result = str(
        context
    )


    assert isinstance(
        result,
        str,
    )



def test_context_len(context):

    assert (
        len(context)
        >= 0
    )



def test_context_contains(context):

    context["trace_id"] = (
        "abc"
    )


    assert (
        "trace_id"
        in context
    )



def test_context_getitem(context):

    context["key"] = (
        "value"
    )


    assert (
        context["key"]
        ==
        "value"
    )



def test_context_setitem(context):

    context["enabled"] = True


    assert (
        context["enabled"]
        is True
    )



# ============================================================
# Equality / Hash
# ============================================================


def test_context_equality():

    first = TraceContext()


    second = TraceContext()


    assert (
        first != second
    )



def test_context_hash(context):

    value = hash(
        context
    )


    assert isinstance(
        value,
        int,
    )