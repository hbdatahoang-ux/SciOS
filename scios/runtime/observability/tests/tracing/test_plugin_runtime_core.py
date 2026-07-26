"""
Tests for TracingPlugin runtime lifecycle.

Coverage
--------
- before_runtime()
- after_runtime()
- runtime cleanup
- disabled plugin
- success/failure paths
"""

from __future__ import annotations

import pytest

from scios.runtime.observability.tests.tracing.builders import PluginBuilder
from scios.runtime.observability.tests.tracing.fakes import (
    FakeExporter,
    FakeProcessor,
    FakeTraceManager,
)


# ============================================================================
# before_runtime
# ============================================================================


def test_before_runtime_creates_trace(
    fake_manager: FakeTraceManager,
    fake_processor: FakeProcessor,
    fake_exporter: FakeExporter,
):
    plugin = (
        PluginBuilder()
        .with_manager(fake_manager)
        .with_processor(fake_processor)
        .with_exporter(fake_exporter)
        .build()
    )

    plugin.before_runtime(
        runtime_name="Planner",
    )

    assert fake_manager.start_trace_called == 1
    assert fake_manager.current_trace is not None


def test_before_runtime_disabled(
    fake_manager,
):
    plugin = (
        PluginBuilder()
        .with_manager(fake_manager)
        .enabled(False)
        .build()
    )

    plugin.before_runtime(
        runtime_name="Planner",
    )

    assert fake_manager.start_trace_called == 0
    assert fake_manager.current_trace is None


# ============================================================================
# after_runtime
# ============================================================================


def test_after_runtime_success(
    plugin,
    fake_manager,
):
    plugin.before_runtime(
        runtime_name="Planner",
    )

    plugin.after_runtime(
        success=True,
    )

    assert fake_manager.finish_trace_called == 1

    trace = fake_manager.last_finished_trace

    assert trace is not None
    assert trace.success is True


def test_after_runtime_failure(
    plugin,
    fake_manager,
):
    plugin.before_runtime(
        runtime_name="Planner",
    )

    plugin.after_runtime(
        success=False,
    )

    trace = fake_manager.last_finished_trace

    assert trace is not None
    assert trace.success is False


def test_after_runtime_without_active_trace(
    plugin,
    fake_manager,
):
    plugin.after_runtime()

    assert fake_manager.finish_trace_called == 0


# ============================================================================
# Cleanup
# ============================================================================


def test_runtime_cleanup(
    plugin,
    fake_manager,
):
    plugin.before_runtime(
        runtime_name="Planner",
    )

    plugin.after_runtime()

    assert fake_manager.current_trace is None
    assert fake_manager.current_span is None


# ============================================================================
# Multiple runtimes
# ============================================================================


def test_runtime_can_be_started_twice(
    plugin,
    fake_manager,
):
    plugin.before_runtime(
        runtime_name="Planner",
    )

    plugin.after_runtime()

    plugin.before_runtime(
        runtime_name="Executor",
    )

    assert fake_manager.start_trace_called == 2
    assert fake_manager.current_trace.name == "Executor"


# ============================================================================
# Idempotency
# ============================================================================


def test_after_runtime_twice_is_safe(
    plugin,
    fake_manager,
):
    plugin.before_runtime(
        runtime_name="Planner",
    )

    plugin.after_runtime()

    plugin.after_runtime()

    assert fake_manager.finish_trace_called == 1