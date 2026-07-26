"""
Tests for SpanScope and span_scope().

Coverage
--------
- context manager
- functional API
- decorator
- nested spans
- automatic lifecycle
- attributes
- component
- task_id
- exception handling
"""

from __future__ import annotations

import pytest

from scios.runtime.observability.tracing.context import (
    SpanScope,
    span_scope,
)
from scios.runtime.observability.tracing.manager import TraceManager


# ==========================================================
# Helpers
# ==========================================================


def create_manager():

    manager = TraceManager()

    manager.start_trace("Runtime")

    return manager


# ==========================================================
# Context Manager
# ==========================================================


def test_span_scope_creates_span():

    manager = create_manager()

    with SpanScope(manager, "Planner") as span:

        assert span.name == "Planner"

        assert manager.current_span is span

    assert manager.current_span is None


def test_span_scope_finishes_span():

    manager = create_manager()

    with SpanScope(manager, "Planner"):

        pass

    assert manager.current_span is None

    assert manager.span_depth == 0


def test_span_scope_returns_span():

    manager = create_manager()

    with SpanScope(manager, "Planner") as span:

        assert span is manager.current_span


def test_span_scope_attributes():

    manager = create_manager()

    with SpanScope(

        manager,

        "Planner",

        worker="cpu0",

        iteration=3,

    ) as span:

        assert span.attributes["worker"] == "cpu0"

        assert span.attributes["iteration"] == 3


def test_span_scope_component():

    manager = create_manager()

    with SpanScope(

        manager,

        "Planner",

        component="runtime",

    ) as span:

        assert span.component == "runtime"


def test_span_scope_task_id():

    manager = create_manager()

    with SpanScope(

        manager,

        "Planner",

        task_id="task-001",

    ) as span:

        assert span.task_id == "task-001"


# ==========================================================
# Functional API
# ==========================================================


def test_span_scope_function():

    manager = create_manager()

    with span_scope(

        manager,

        "Solver",

    ) as span:

        assert span.name == "Solver"

        assert manager.current_span is span

    assert manager.current_span is None


def test_span_scope_function_attributes():

    manager = create_manager()

    with span_scope(

        manager,

        "Solver",

        worker="gpu0",

    ) as span:

        assert span.attributes["worker"] == "gpu0"


# ==========================================================
# Nested
# ==========================================================


def test_nested_span_scope():

    manager = create_manager()

    with SpanScope(manager, "Root") as root:

        with SpanScope(manager, "Child") as child:

            assert child.parent_span_id == root.span_id

            assert manager.current_span is child

        assert manager.current_span is root

    assert manager.current_span is None


def test_span_depth():

    manager = create_manager()

    with SpanScope(manager, "A"):

        assert manager.span_depth == 1

        with SpanScope(manager, "B"):

            assert manager.span_depth == 2

        assert manager.span_depth == 1

    assert manager.span_depth == 0


# ==========================================================
# Exceptions
# ==========================================================


def test_span_scope_exception():

    manager = create_manager()

    with pytest.raises(ValueError):

        with SpanScope(manager, "Planner"):

            raise ValueError("boom")

    assert manager.current_span is None


def test_span_scope_never_swallows_exception():

    manager = create_manager()

    with pytest.raises(RuntimeError):

        with SpanScope(manager, "Planner"):

            raise RuntimeError()


# ==========================================================
# Decorator
# ==========================================================


def test_span_scope_decorator():

    manager = create_manager()

    @SpanScope(manager, "Decorated")
    def work():

        assert manager.current_span is not None

        return 42

    result = work()

    assert result == 42

    assert manager.current_span is None


def test_span_scope_decorator_exception():

    manager = create_manager()

    @SpanScope(manager, "Decorated")
    def work():

        raise ValueError()

    with pytest.raises(ValueError):

        work()

    assert manager.current_span is None


# ==========================================================
# Properties
# ==========================================================


def test_span_scope_active_property():

    manager = create_manager()

    scope = SpanScope(

        manager,

        "Planner",

    )

    assert not scope.active

    with scope:

        assert scope.active


def test_span_scope_repr():

    manager = create_manager()

    scope = SpanScope(

        manager,

        "Planner",

        component="runtime",

        task_id="001",

    )

    text = repr(scope)

    assert "SpanScope" in text

    assert "Planner" in text

    assert "runtime" in text

    assert "001" in text


# ==========================================================
# Error Paths
# ==========================================================


def test_span_scope_without_trace():

    manager = TraceManager()

    with pytest.raises(RuntimeError):

        with SpanScope(

            manager,

            "Planner",

        ):

            pass


# ==========================================================
# Regression
# ==========================================================


def test_many_span_scopes():

    manager = create_manager()

    for i in range(50):

        with SpanScope(

            manager,

            f"S{i}",

        ):

            assert manager.current_span is not None

    assert manager.span_depth == 0


def test_current_span_inside_scope():

    manager = create_manager()

    with SpanScope(

        manager,

        "Planner",

    ) as span:

        assert manager.current_span is span

    assert manager.current_span is None


def test_finish_called_once():

    manager = create_manager()

    with SpanScope(

        manager,

        "Planner",

    ):

        pass

    assert manager.span_depth == 0


def test_parent_child_relationship():

    manager = create_manager()

    with SpanScope(manager, "Root") as root:

        with SpanScope(manager, "Child") as child:

            pass

    assert child.parent_span_id == root.span_id


def test_root_span_after_nested_scope():

    manager = create_manager()

    with SpanScope(manager, "Root") as root:

        with SpanScope(manager, "Child"):

            pass

        assert manager.current_span is root