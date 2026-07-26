"""
Tests for task lifecycle of TracingPlugin.

Responsibilities
----------------
- before_task
- after_task
- nested tasks
- task metadata
- task failure
- processor/exporter callbacks
- robustness
"""

from __future__ import annotations

import pytest

from .builders import PluginBuilder


# ==========================================================
# Task lifecycle
# ==========================================================


def test_before_task_creates_span(plugin):

    plugin.before_runtime(runtime_name="Runtime")

    plugin.before_task(
        task_name="LoadModel",
    )

    span = plugin.manager.current_span

    assert span is not None
    assert span.name == "LoadModel"


def test_after_task_finishes_span(plugin):

    plugin.before_runtime(runtime_name="Runtime")

    plugin.before_task(
        task_name="LoadModel",
    )

    plugin.after_task()

    assert plugin.manager.current_span is None


def test_after_task_without_active_task(plugin):

    plugin.before_runtime(runtime_name="Runtime")

    plugin.after_task()

    assert plugin.manager.current_span is None


# ==========================================================
# Metadata
# ==========================================================


def test_task_component(plugin):

    plugin.before_runtime(runtime_name="Runtime")

    plugin.before_task(
        task_name="Planner",
        component="planning",
    )

    span = plugin.manager.current_span

    assert span.component == "planning"


def test_task_identifier(plugin):

    plugin.before_runtime(runtime_name="Runtime")

    plugin.before_task(
        task_name="Planner",
        task_id="task-001",
    )

    span = plugin.manager.current_span

    assert span.task_id == "task-001"


def test_task_attributes(plugin):

    plugin.before_runtime(runtime_name="Runtime")

    plugin.before_task(
        task_name="Planner",
        priority="high",
        worker="cpu0",
    )

    span = plugin.manager.current_span

    assert span.attributes["priority"] == "high"

    assert span.attributes["worker"] == "cpu0"


# ==========================================================
# Nested tasks
# ==========================================================


def test_nested_tasks(plugin):

    plugin.before_runtime(runtime_name="Runtime")

    plugin.before_task(task_name="Parent")

    parent = plugin.manager.current_span

    plugin.before_task(task_name="Child")

    child = plugin.manager.current_span

    assert child.parent_span_id == parent.span_id

    assert plugin.manager.span_depth == 2


def test_finish_nested_task(plugin):

    plugin.before_runtime(runtime_name="Runtime")

    plugin.before_task(task_name="Parent")

    plugin.before_task(task_name="Child")

    plugin.after_task()

    assert plugin.manager.current_span.name == "Parent"

    plugin.after_task()

    assert plugin.manager.current_span is None


# ==========================================================
# Success / Failure
# ==========================================================


def test_task_success(plugin):

    plugin.before_runtime(runtime_name="Runtime")

    plugin.before_task(task_name="Training")

    plugin.after_task(success=True)

    span = plugin.manager.root_span()

    assert span.success is True


def test_task_failure(plugin):

    plugin.before_runtime(runtime_name="Runtime")

    plugin.before_task(task_name="Training")

    plugin.after_task(success=False)

    span = plugin.manager.root_span()

    assert span.success is False


# ==========================================================
# Processor callbacks
# ==========================================================


def test_task_processor_callbacks(
    fake_manager,
    fake_processor,
    fake_exporter,
):

    plugin = (
        PluginBuilder()
        .with_manager(fake_manager)
        .with_processor(fake_processor)
        .with_exporter(fake_exporter)
        .build()
    )

    plugin.before_runtime(runtime_name="Runtime")

    plugin.before_task(task_name="Planner")

    plugin.after_task()

    assert fake_processor.started_spans == 1

    assert fake_processor.finished_spans == 1


# ==========================================================
# Exporter callbacks
# ==========================================================


def test_task_exported(
    fake_manager,
    fake_processor,
    fake_exporter,
):

    plugin = (
        PluginBuilder()
        .with_manager(fake_manager)
        .with_processor(fake_processor)
        .with_exporter(fake_exporter)
        .build()
    )

    plugin.before_runtime(runtime_name="Runtime")

    plugin.before_task(task_name="Planner")

    plugin.after_task()

    assert len(fake_exporter.exported_spans) == 1


# ==========================================================
# Reuse
# ==========================================================


def test_multiple_tasks(plugin):

    plugin.before_runtime(runtime_name="Runtime")

    for i in range(10):

        plugin.before_task(
            task_name=f"Task-{i}",
        )

        plugin.after_task()

    assert plugin.manager.current_span is None


def test_task_reuse(plugin):

    plugin.before_runtime(runtime_name="Runtime")

    plugin.before_task(task_name="Task-A")

    plugin.after_task()

    plugin.before_task(task_name="Task-B")

    assert plugin.manager.current_span.name == "Task-B"


# ==========================================================
# Cleanup
# ==========================================================


def test_cleanup_clears_task(plugin):

    plugin.before_runtime(runtime_name="Runtime")

    plugin.before_task(task_name="Planner")

    plugin.cleanup()

    assert plugin.manager.current_span is None

    assert plugin.manager.current_trace is None


# ==========================================================
# Exceptions
# ==========================================================


def test_task_exception(plugin):

    plugin.before_runtime(runtime_name="Runtime")

    plugin.before_task(task_name="Planner")

    try:
        raise RuntimeError("failure")
    except RuntimeError as exc:
        plugin.manager.record_exception(exc)

    plugin.after_task(success=False)

    span = plugin.manager.root_span()

    assert span.success is False


# ==========================================================
# Stack integrity
# ==========================================================


def test_task_stack_integrity(plugin):

    plugin.before_runtime(runtime_name="Runtime")

    plugin.before_task(task_name="A")

    plugin.before_task(task_name="B")

    plugin.before_task(task_name="C")

    assert plugin.manager.validate_span_stack()

    plugin.after_task()

    plugin.after_task()

    plugin.after_task()

    assert plugin.manager.current_span is None