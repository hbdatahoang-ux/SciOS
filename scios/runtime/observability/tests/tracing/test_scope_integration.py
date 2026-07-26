"""
Integration tests for TraceScope and SpanScope.

Coverage
--------
- trace + span integration
- nested span hierarchy
- multiple traces
- exception propagation
- automatic cleanup
- decorators
- context restoration
"""

from __future__ import annotations

import pytest

from scios.runtime.observability.tracing.context import (
    TraceScope,
    SpanScope,
    trace_scope,
    span_scope,
)
from scios.runtime.observability.tracing.manager import TraceManager


# ==========================================================
# Basic Integration
# ==========================================================


def test_trace_and_span_scope():

    manager = TraceManager()

    with TraceScope(manager, "Runtime") as trace:

        with SpanScope(manager, "Planner") as span:

            assert manager.current_trace is trace

            assert manager.current_span is span

            assert span.trace_id == trace.trace_id

    assert manager.current_trace is None

    assert manager.current_span is None


def test_multiple_spans_inside_trace():

    manager = TraceManager()

    with TraceScope(manager, "Runtime"):

        with SpanScope(manager, "Planner"):

            pass

        with SpanScope(manager, "Executor"):

            pass

    assert manager.completed_trace_count == 1


# ==========================================================
# Nested Spans
# ==========================================================


def test_nested_span_hierarchy():

    manager = TraceManager()

    with TraceScope(manager, "Runtime"):

        with SpanScope(manager, "Root") as root:

            with SpanScope(manager, "Child") as child:

                with SpanScope(manager, "Leaf") as leaf:

                    assert leaf.parent_span_id == child.span_id

                assert manager.current_span is child

            assert manager.current_span is root


def test_span_depth_changes():

    manager = TraceManager()

    with TraceScope(manager, "Runtime"):

        assert manager.span_depth == 0

        with SpanScope(manager, "A"):

            assert manager.span_depth == 1

            with SpanScope(manager, "B"):

                assert manager.span_depth == 2

            assert manager.span_depth == 1

        assert manager.span_depth == 0


# ==========================================================
# Functional API
# ==========================================================


def test_functional_api():

    manager = TraceManager()

    with trace_scope(manager, "Runtime"):

        with span_scope(manager, "Planner"):

            assert manager.current_trace is not None

            assert manager.current_span is not None


# ==========================================================
# Decorators
# ==========================================================


def test_trace_and_span_decorators():

    manager = TraceManager()

    @TraceScope(manager, "Trace")
    @SpanScope(manager, "Span")
    def work():

        assert manager.current_trace is not None

        assert manager.current_span is not None

        return 123

    assert work() == 123

    assert manager.current_trace is None

    assert manager.current_span is None


# ==========================================================
# Exceptions
# ==========================================================


def test_exception_inside_span():

    manager = TraceManager()

    with pytest.raises(ValueError):

        with TraceScope(manager, "Runtime"):

            with SpanScope(manager, "Planner"):

                raise ValueError("boom")

    assert manager.current_trace is None

    assert manager.current_span is None


def test_exception_inside_trace_before_span():

    manager = TraceManager()

    with pytest.raises(RuntimeError):

        with TraceScope(manager, "Runtime"):

            raise RuntimeError()

    assert manager.current_trace is None


# ==========================================================
# Cleanup
# ==========================================================


def test_cleanup_after_trace():

    manager = TraceManager()

    with TraceScope(manager, "Runtime"):

        with SpanScope(manager, "Planner"):

            pass

    assert manager.current_trace is None

    assert manager.current_span is None

    assert manager.span_depth == 0


def test_multiple_traces_cleanup():

    manager = TraceManager()

    for i in range(10):

        with TraceScope(manager, f"T{i}"):

            with SpanScope(manager, "Planner"):

                pass

    assert manager.completed_trace_count == 10

    assert manager.current_trace is None

    assert manager.current_span is None


# ==========================================================
# Context Restoration
# ==========================================================


def test_parent_restored_after_child():

    manager = TraceManager()

    with TraceScope(manager, "Runtime"):

        with SpanScope(manager, "Parent") as parent:

            with SpanScope(manager, "Child"):

                pass

            assert manager.current_span is parent


def test_trace_restored_after_span_finish():

    manager = TraceManager()

    with TraceScope(manager, "Runtime") as trace:

        with SpanScope(manager, "Planner"):

            pass

        assert manager.current_trace is trace

        assert manager.current_span is None


# ==========================================================
# Regression
# ==========================================================


def test_many_nested_scopes():

    manager = TraceManager()

    with TraceScope(manager, "Runtime"):

        for i in range(20):

            with SpanScope(manager, f"S{i}"):

                assert manager.current_span is not None

    assert manager.current_trace is None

    assert manager.current_span is None


def test_trace_contains_all_spans():

    manager = TraceManager()

    with TraceScope(manager, "Runtime") as trace:

        for i in range(5):

            with SpanScope(manager, f"S{i}"):

                pass

    assert len(trace.spans) == 5


def test_trace_id_propagation():

    manager = TraceManager()

    with TraceScope(manager, "Runtime") as trace:

        with SpanScope(manager, "A") as a:

            with SpanScope(manager, "B") as b:

                assert a.trace_id == trace.trace_id

                assert b.trace_id == trace.trace_id


def test_root_span():

    manager = TraceManager()

    with TraceScope(manager, "Runtime"):

        with SpanScope(manager, "Root") as root:

            with SpanScope(manager, "Child"):

                pass

        assert manager.root_span() is root


def test_manager_validates_stack():

    manager = TraceManager()

    with TraceScope(manager, "Runtime"):

        with SpanScope(manager, "A"):

            with SpanScope(manager, "B"):

                assert manager.validate_span_stack()