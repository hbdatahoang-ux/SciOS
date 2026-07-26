"""
Tests for TraceManager span lifecycle.

Coverage
--------
- start_span
- finish_span
- nesting
- parent-child relationship
- span stack
- current span
- root span
- validation
"""

from __future__ import annotations

import pytest

from scios.runtime.observability.tracing.manager import TraceManager


# ==========================================================
# Helpers
# ==========================================================


def create_manager() -> TraceManager:
    manager = TraceManager()
    manager.start_trace("runtime")
    return manager


# ==========================================================
# Basic lifecycle
# ==========================================================


def test_start_span_creates_active_span():

    manager = create_manager()

    span = manager.start_span("planner")

    assert span is manager.current_span
    assert manager.has_active_span()
    assert manager.span_depth == 1


def test_finish_span_returns_finished_span():

    manager = create_manager()

    span = manager.start_span("planner")

    finished = manager.finish_span()

    assert finished is span
    assert manager.current_span is None
    assert manager.span_depth == 0


def test_finish_without_active_span_returns_none():

    manager = create_manager()

    assert manager.finish_span() is None


def test_start_span_requires_active_trace():

    manager = TraceManager()

    with pytest.raises(RuntimeError):
        manager.start_span("planner")


# ==========================================================
# Parent / Child
# ==========================================================


def test_nested_span_sets_parent():

    manager = create_manager()

    root = manager.start_span("runtime")

    child = manager.start_span("planner")

    assert child.parent_span_id == root.span_id


def test_nested_span_becomes_current():

    manager = create_manager()

    root = manager.start_span("runtime")

    child = manager.start_span("planner")

    assert manager.current_span is child

    manager.finish_span()

    assert manager.current_span is root


def test_multiple_nested_depth():

    manager = create_manager()

    manager.start_span("A")

    manager.start_span("B")

    manager.start_span("C")

    assert manager.span_depth == 3


def test_finish_nested_updates_depth():

    manager = create_manager()

    manager.start_span("A")
    manager.start_span("B")
    manager.start_span("C")

    manager.finish_span()

    assert manager.span_depth == 2

    manager.finish_span()

    assert manager.span_depth == 1

    manager.finish_span()

    assert manager.span_depth == 0


# ==========================================================
# Root span
# ==========================================================


def test_root_span_returns_first_span():

    manager = create_manager()

    root = manager.start_span("root")

    manager.start_span("child")

    assert manager.root_span() is root


def test_root_span_without_trace():

    manager = TraceManager()

    assert manager.root_span() is None


def test_root_span_without_spans():

    manager = create_manager()

    assert manager.root_span() is None


# ==========================================================
# Active stack
# ==========================================================


def test_active_span_stack_snapshot():

    manager = create_manager()

    s1 = manager.start_span("A")
    s2 = manager.start_span("B")

    stack = manager.active_span_stack()

    assert stack == [s1, s2]


def test_active_stack_is_copy():

    manager = create_manager()

    manager.start_span("A")

    stack = manager.active_span_stack()

    stack.clear()

    assert manager.span_depth == 1


# ==========================================================
# Validation
# ==========================================================


def test_validate_empty_stack():

    manager = create_manager()

    assert manager.validate_span_stack()


def test_validate_nested_stack():

    manager = create_manager()

    manager.start_span("root")

    manager.start_span("planner")

    manager.start_span("solver")

    assert manager.validate_span_stack()


# ==========================================================
# Current span aliases
# ==========================================================


def test_active_span_alias():

    manager = create_manager()

    span = manager.start_span("planner")

    assert manager.active_span is span
    assert manager.current_span is span


def test_current_span_none_after_finish():

    manager = create_manager()

    manager.start_span("planner")

    manager.finish_span()

    assert manager.current_span is None


# ==========================================================
# Component / Task
# ==========================================================


def test_component_is_preserved():

    manager = create_manager()

    span = manager.start_span(
        "planner",
        component="reasoning",
    )

    assert span.component == "reasoning"


def test_task_id_is_preserved():

    manager = create_manager()

    span = manager.start_span(
        "planner",
        task_id="task-001",
    )

    assert span.task_id == "task-001"


# ==========================================================
# Attributes
# ==========================================================


def test_initial_attributes_are_attached():

    manager = create_manager()

    span = manager.start_span(
        "planner",
        worker="cpu0",
        stage="reasoning",
    )

    assert span.attributes["worker"] == "cpu0"
    assert span.attributes["stage"] == "reasoning"


# ==========================================================
# Trace linkage
# ==========================================================


def test_span_belongs_to_current_trace():

    manager = create_manager()

    span = manager.start_span("planner")

    assert span.trace_id == manager.current_trace.trace_id


def test_trace_collects_spans():

    manager = create_manager()

    manager.start_span("A")
    manager.start_span("B")

    assert len(manager.current_trace.spans) == 2


# ==========================================================
# Regression
# ==========================================================


def test_finish_all_nested_spans():

    manager = create_manager()

    manager.start_span("A")
    manager.start_span("B")
    manager.start_span("C")

    while manager.has_active_span():
        manager.finish_span()

    assert manager.current_span is None
    assert manager.span_depth == 0


def test_finish_trace_after_all_spans():

    manager = create_manager()

    manager.start_span("planner")

    manager.finish_span()

    trace = manager.finish_trace()

    assert trace is not None