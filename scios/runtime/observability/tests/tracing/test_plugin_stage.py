"""
Tests for TracingPlugin as a runtime stage.

Responsibilities
----------------
- before_stage
- after_stage
- stage metadata
- stage failures
- nested stages
- processor/exporter callbacks
"""

from __future__ import annotations

import pytest

from .builders import PluginBuilder


# ==========================================================
# Basic lifecycle
# ==========================================================


def test_before_stage_creates_span(plugin):

    plugin.before_runtime(runtime_name="Runtime")

    plugin.before_stage(
        stage_name="Planner",
    )

    span = plugin.manager.current_span

    assert span is not None
    assert span.name == "Planner"


def test_after_stage_finishes_span(plugin):

    plugin.before_runtime(runtime_name="Runtime")

    plugin.before_stage(
        stage_name="Planner",
    )

    plugin.after_stage()

    assert plugin.manager.current_span is None


# ==========================================================
# Metadata
# ==========================================================


def test_stage_component_metadata(plugin):

    plugin.before_runtime(runtime_name="Runtime")

    plugin.before_stage(
        stage_name="Planner",
        component="planning",
    )

    span = plugin.manager.current_span

    assert span.component == "planning"


def test_stage_task_metadata(plugin):

    plugin.before_runtime(runtime_name="Runtime")

    plugin.before_stage(
        stage_name="Planner",
        task_id="task-001",
    )

    span = plugin.manager.current_span

    assert span.task_id == "task-001"


def test_stage_custom_attributes(plugin):

    plugin.before_runtime(runtime_name="Runtime")

    plugin.before_stage(
        stage_name="Planner",
        worker="cpu0",
        priority="high",
    )

    span = plugin.manager.current_span

    assert span.attributes["worker"] == "cpu0"

    assert span.attributes["priority"] == "high"


# ==========================================================
# Nested stages
# ==========================================================


def test_nested_stage_depth(plugin):

    plugin.before_runtime(runtime_name="Runtime")

    plugin.before_stage(stage_name="Planning")

    plugin.before_stage(stage_name="Scheduling")

    assert plugin.manager.span_depth == 2


def test_nested_stage_parent(plugin):

    plugin.before_runtime(runtime_name="Runtime")

    plugin.before_stage(stage_name="Parent")

    parent = plugin.manager.current_span

    plugin.before_stage(stage_name="Child")

    child = plugin.manager.current_span

    assert child.parent_span_id == parent.span_id


def test_nested_stage_finish(plugin):

    plugin.before_runtime(runtime_name="Runtime")

    plugin.before_stage(stage_name="A")

    plugin.before_stage(stage_name="B")

    plugin.after_stage()

    assert plugin.manager.current_span.name == "A"

    plugin.after_stage()

    assert plugin.manager.current_span is None


# ==========================================================
# Failure
# ==========================================================


def test_stage_failure(plugin):

    plugin.before_runtime(runtime_name="Runtime")

    plugin.before_stage(stage_name="Planner")

    plugin.after_stage(success=False)

    span = plugin.manager.root_span()

    assert span.success is False


def test_after_stage_without_active_span(plugin):

    plugin.before_runtime(runtime_name="Runtime")

    plugin.after_stage()

    assert plugin.manager.current_span is None


# ==========================================================
# Processor
# ==========================================================


def test_processor_receives_stage_callbacks(
    fake_processor,
    fake_manager,
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

    plugin.before_stage(stage_name="Planner")

    plugin.after_stage()

    assert fake_processor.started_spans == 1

    assert fake_processor.finished_spans == 1


# ==========================================================
# Exporter
# ==========================================================


def test_stage_exported(
    fake_exporter,
    fake_manager,
    fake_processor,
):

    plugin = (
        PluginBuilder()
        .with_manager(fake_manager)
        .with_processor(fake_processor)
        .with_exporter(fake_exporter)
        .build()
    )

    plugin.before_runtime(runtime_name="Runtime")

    plugin.before_stage(stage_name="Planner")

    plugin.after_stage()

    assert len(fake_exporter.exported_spans) == 1


# ==========================================================
# Robustness
# ==========================================================


def test_multiple_stage_cycles(plugin):

    plugin.before_runtime(runtime_name="Runtime")

    for i in range(10):

        plugin.before_stage(
            stage_name=f"Stage-{i}",
        )

        plugin.after_stage()

    assert plugin.manager.current_span is None


def test_stage_reuse(plugin):

    plugin.before_runtime(runtime_name="Runtime")

    plugin.before_stage(stage_name="Planner")

    plugin.after_stage()

    plugin.before_stage(stage_name="Executor")

    assert plugin.manager.current_span.name == "Executor"


def test_stage_cleanup(plugin):

    plugin.before_runtime(runtime_name="Runtime")

    plugin.before_stage(stage_name="Planner")

    plugin.cleanup()

    assert plugin.manager.current_span is None

    assert plugin.manager.current_trace is None