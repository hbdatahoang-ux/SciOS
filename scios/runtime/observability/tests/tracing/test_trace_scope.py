"""
Tests for TraceScope and trace_scope().

Coverage
--------
- context manager
- decorator
- trace lifecycle
- nested scopes
- exception handling
- automatic finish
- attributes
- current trace
"""

from __future__ import annotations

import pytest

from scios.runtime.observability.tracing.scope import (
    TraceScope,
    trace_scope,
)
from scios.runtime.observability.tracing.manager import TraceManager


# ==========================================================
# Context Manager
# ==========================================================


def test_trace_scope_creates_trace():

    manager = TraceManager()

    with TraceScope(manager, "Runtime") as trace:

        assert trace.name == "Runtime"

        assert manager.current_trace is trace

    assert manager.current_trace is None


def test_trace_scope_finishes_trace():

    manager = TraceManager()

    with TraceScope(manager, "Runtime"):

        pass

    assert manager.current_trace is None

    assert manager.completed_trace_count == 1


def test_trace_scope_returns_trace():

    manager = TraceManager()

    with TraceScope(manager, "Runtime") as trace:

        assert trace is manager.current_trace


def test_trace_scope_attributes():

    manager = TraceManager()

    with TraceScope(

        manager,

        "Runtime",

        worker="cpu0",

        node="A",

    ) as trace:

        assert trace.attributes["worker"] == "cpu0"

        assert trace.attributes["node"] == "A"


# ==========================================================
# Functional API
# ==========================================================


def test_trace_scope_function():

    manager = TraceManager()

    with trace_scope(manager, "Planner") as trace:

        assert trace.name == "Planner"

        assert manager.current_trace is trace

    assert manager.current_trace is None


def test_trace_scope_function_attributes():

    manager = TraceManager()

    with trace_scope(

        manager,

        "Planner",

        iteration=5,

    ) as trace:

        assert trace.attributes["iteration"] == 5


# ==========================================================
# Exceptions
# ==========================================================


def test_trace_scope_exception():

    manager = TraceManager()

    with pytest.raises(ValueError):

        with TraceScope(manager, "Runtime"):

            raise ValueError("boom")

    assert manager.current_trace is None

    assert manager.completed_trace_count == 1


def test_trace_scope_never_swallows_exception():

    manager = TraceManager()

    with pytest.raises(RuntimeError):

        with TraceScope(manager, "Runtime"):

            raise RuntimeError()


# ==========================================================
# Nested
# ==========================================================


def test_nested_trace_scope():

    manager = TraceManager()

    with TraceScope(manager, "Outer"):

        outer = manager.current_trace

        with TraceScope(manager, "Inner"):

            inner = manager.current_trace

            assert inner is not outer

        assert manager.current_trace is None


# ==========================================================
# Decorator
# ==========================================================


def test_trace_scope_decorator():

    manager = TraceManager()

    @TraceScope(manager, "Decorated")
    def work():

        assert manager.current_trace is not None

        return 123

    result = work()

    assert result == 123

    assert manager.current_trace is None


def test_trace_scope_decorator_exception():

    manager = TraceManager()

    @TraceScope(manager, "Decorated")
    def work():

        raise ValueError()

    with pytest.raises(ValueError):

        work()

    assert manager.current_trace is None


# ==========================================================
# Lifecycle
# ==========================================================


def test_multiple_trace_scopes():

    manager = TraceManager()

    for i in range(5):

        with TraceScope(

            manager,

            f"trace-{i}",

        ):

            pass

    assert manager.completed_trace_count == 5


def test_trace_scope_repr():

    manager = TraceManager()

    scope = TraceScope(

        manager,

        "Runtime",

    )

    text = repr(scope)

    assert "TraceScope" in text

    assert "Runtime" in text


# ==========================================================
# Regression
# ==========================================================


def test_trace_scope_current_trace_inside():

    manager = TraceManager()

    with TraceScope(manager, "Runtime"):

        assert manager.current_trace is not None

    assert manager.current_trace is None


def test_trace_scope_finish_called_once():

    manager = TraceManager()

    with TraceScope(manager, "Runtime"):

        pass

    assert manager.completed_trace_count == 1


def test_trace_scope_many_iterations():

    manager = TraceManager()

    for i in range(100):

        with TraceScope(

            manager,

            f"T{i}",

        ):

            assert manager.current_trace is not None

    assert manager.completed_trace_count == 100