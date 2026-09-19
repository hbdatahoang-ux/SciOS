# ============================================================
# Part 1 – Foundation
# Creation
# Trace / Span Identity
# ============================================================

from __future__ import annotations


import copy
import json

import pytest


from scios.runtime.observability.tracing.baggage import (
    Baggage,
)

from scios.runtime.observability.tracing.context import (
    TraceContext,
)


# ============================================================
# Fixtures
# ============================================================


@pytest.fixture
def context() -> TraceContext:
    """
    Empty tracing context.
    """

    return TraceContext()



@pytest.fixture
def populated_context() -> TraceContext:
    """
    Context with predefined trace identity.
    """

    ctx = TraceContext()

    ctx._trace_id = "trace-001"

    ctx._span_id = "span-001"

    ctx._parent_span_id = "parent-001"


    return ctx



# ============================================================
# Creation
# ============================================================


def test_context_creation(
    context,
):

    assert context is not None



def test_context_instance(
    context,
):

    assert isinstance(
        context,
        TraceContext,
    )



def test_context_default_identity(
    context,
):

    assert context.trace_id

    assert context.span_id



# ============================================================
# Trace Identity
# ============================================================


def test_trace_id_exists(
    context,
):

    assert isinstance(
        context.trace_id,
        str,
    )


    assert len(
        context.trace_id
    ) > 0



def test_set_trace_id(
    context,
):

    context._trace_id = "trace-123"


    assert (
        context.trace_id
        ==
        "trace-123"
    )



def test_populated_trace_id(
    populated_context,
):

    assert (
        populated_context.trace_id
        ==
        "trace-001"
    )



# ============================================================
# Span Identity
# ============================================================


def test_span_id_exists(
    context,
):

    assert isinstance(
        context.span_id,
        str,
    )


    assert len(
        context.span_id
    ) > 0



def test_set_span_id(
    context,
):

    context._span_id = "span-123"


    assert (
        context.span_id
        ==
        "span-123"
    )



def test_populated_span_id(
    populated_context,
):

    assert (
        populated_context.span_id
        ==
        "span-001"
    )



# ============================================================
# Parent Span
# ============================================================


def test_parent_span_id(
    populated_context,
):

    assert (
        populated_context.parent_span_id
        ==
        "parent-001"
    )



def test_missing_parent_span(
    context,
):

    assert (
        context.parent_span_id
        is None
    )

# ============================================================
# Part 2
# Attributes
# Baggage
# Serialization
# Snapshot
# Clone
# ============================================================


# ============================================================
# Attributes
# ============================================================


def test_set_attribute(
    context,
):

    context.set_attribute(
        "service.name",
        "SciOS",
    )


    assert (
        context.attributes["service.name"]
        ==
        "SciOS"
    )



def test_multiple_attributes(
    context,
):

    context.set_attribute(
        "service.name",
        "SciOS",
    )


    context.set_attribute(
        "service.version",
        "0.3",
    )


    assert (
        len(context.attributes)
        ==
        2
    )



def test_remove_attribute(
    context,
):

    context.set_attribute(
        "temporary",
        True,
    )


    context.remove_attribute(
        "temporary"
    )


    assert (
        "temporary"
        not in context.attributes
    )



# ============================================================
# Baggage
# ============================================================


def test_set_baggage(
    context,
):

    context.set_baggage(
        Baggage(
            {
                "tenant.id": "tenant-a",
            }
        )
    )


    assert (
        context.baggage["tenant.id"]
        ==
        "tenant-a"
    )



def test_get_baggage(
    context,
):

    context.set_baggage(
        Baggage(
            {
                "request.id": "req-001",
            }
        )
    )


    assert (
        context.baggage.get(
            "request.id"
        )
        ==
        "req-001"
    )



def test_multiple_baggage(
    context,
):

    context.set_baggage(
        Baggage(
            {
                "service.name": "SciOS",
                "service.version": "0.3",
            }
        )
    )


    assert (
        context.baggage.get(
            "service.name"
        )
        ==
        "SciOS"
    )


    assert (
        context.baggage.get(
            "service.version"
        )
        ==
        "0.3"
    )



def test_remove_baggage(
    context,
):

    context.set_baggage(
        Baggage(
            {
                "temporary": "true",
            }
        )
    )


    context.baggage.remove(
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

    data = populated_context.to_dict()


    assert isinstance(
        data,
        dict,
    )


    assert (
        data["trace_id"]
        ==
        "trace-001"
    )



def test_context_from_dict(
    populated_context,
):

    data = populated_context.to_dict()


    restored = TraceContext.from_dict(
        data
    )


    assert (
        restored.trace_id
        ==
        populated_context.trace_id
    )



def test_context_to_json(
    populated_context,
):

    value = populated_context.to_json()


    assert isinstance(
        value,
        str,
    )


    data = json.loads(
        value
    )


    assert (
        data["span_id"]
        ==
        "span-001"
    )



def test_context_from_json(
    populated_context,
):

    value = populated_context.to_json()


    restored = TraceContext.from_json(
        value
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

    snapshot = populated_context.snapshot()


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

    snapshot = populated_context.snapshot()


    restored = TraceContext.restore(
        snapshot
    )


    assert (
        restored.trace_id
        ==
        populated_context.trace_id
    )



# ============================================================
# Clone
# ============================================================


def test_context_clone(
    populated_context,
):

    clone = populated_context.clone()


    assert clone is not populated_context


    assert (
        clone.to_dict()
        ==
        populated_context.to_dict()
    )



def test_context_copy(
    populated_context,
):

    copied = populated_context.copy()


    assert copied is not populated_context


    assert (
        copied.to_dict()
        ==
        populated_context.to_dict()
    )



def test_python_copy(
    populated_context,
):

    copied = copy.copy(
        populated_context
    )


    assert (
        copied.to_dict()
        ==
        populated_context.to_dict()
    )



def test_python_deepcopy(
    populated_context,
):

    copied = copy.deepcopy(
        populated_context
    )


    assert (
        copied.to_dict()
        ==
        populated_context.to_dict()
    )

# ============================================================
# Part 3
# Validation
# Diagnostics
# Python Protocols
# Equality
# Hash
# ============================================================


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



def test_empty_context_validate(
    context,
):

    assert (
        context.validate()
        is True
    )



def test_invalid_context_validation(
    context,
):

    context._trace_id = ""


    assert (
        context.validate()
        is False
    )



# ============================================================
# Diagnostics
# ============================================================


def test_context_diagnostics(
    populated_context,
):

    result = (
        populated_context
        .diagnostics()
    )


    assert isinstance(
        result,
        dict,
    )


    assert (
        "trace_id"
        in result
        or
        "identity"
        in result
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


    assert (
        "trace_id"
        in result
        or
        "size"
        in result
    )



# ============================================================
# Python Protocols
# ============================================================


def test_repr(
    context,
):

    result = repr(
        context
    )


    assert isinstance(
        result,
        str,
    )


    assert (
        "TraceContext"
        in result
    )



def test_str(
    context,
):

    result = str(
        context
    )


    assert isinstance(
        result,
        str,
    )



def test_len(
    populated_context,
):

    assert (
        len(populated_context)
        >=
        0
    )



def test_contains(
    populated_context,
):

    assert (
        "trace_id"
        in populated_context
    )



def test_getitem(
        populated_context,
):

    assert (
        populated_context["trace_id"]
        ==
        "trace-001"
    )



def test_setitem(
    context,
):

    context["runtime"] = (
        "engine"
    )


    assert (
        context["runtime"]
        ==
        "engine"
    )



def test_delitem(
    context,
):

    context["temporary"] = True


    del context["temporary"]


    assert (
        "temporary"
        not in context
    )



def test_iter(
    populated_context,
):

    keys = list(
        iter(
            populated_context
        )
    )


    assert (
        "trace_id"
        in keys
    )



def test_bool(
    populated_context,
):

    assert (
        bool(populated_context)
        is True
    )



# ============================================================
# Equality
# ============================================================


def test_context_equality():

    first = TraceContext()

    first._trace_id = (
        "trace-001"
    )

    first._span_id = (
        "span-001"
    )


    second = TraceContext()

    second._trace_id = (
        "trace-001"
    )

    second._span_id = (
        "span-001"
    )


    assert (
        first
        ==
        second
    )



def test_context_not_equal():

    first = TraceContext()

    first._trace_id = (
        "trace-001"
    )


    second = TraceContext()

    second._trace_id = (
        "trace-002"
    )


    assert (
        first
        !=
        second
    )



# ============================================================
# Hash
# ============================================================


def test_context_hash(
    context,
):

    value = hash(
        context
    )


    assert isinstance(
        value,
        int,
    )