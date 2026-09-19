"""
Tests for TracingPlugin robustness.

Responsibilities
----------------
- Plugin reuse
- Disabled mode
- Multiple runtime sessions
- Cleanup
- Idempotency
- Failure recovery
- Reset behavior
"""

from __future__ import annotations

import pytest

from .builders import PluginBuilder


# ==========================================================
# Disabled plugin
# ==========================================================


def test_disabled_plugin_ignores_runtime(
    fake_manager,
    fake_processor,
    fake_exporter,
):

    plugin = (
        PluginBuilder()
        .enabled(False)
        .with_manager(fake_manager)
        .with_processor(fake_processor)
        .with_exporter(fake_exporter)
        .build()
    )

    plugin.before_runtime(runtime_name="Runtime")

    assert plugin.manager.current_trace is None

    plugin.after_runtime()

    assert plugin.manager.completed_trace_count == 0


# ==========================================================
# Plugin reuse
# ==========================================================


def test_plugin_can_be_reused(plugin):

    for _ in range(3):

        plugin.before_runtime(runtime_name="Runtime")

        plugin.after_runtime()

    assert plugin.manager.completed_trace_count == 3


def test_plugin_reuse_does_not_leak_context(plugin):

    plugin.before_runtime(runtime_name="Run-1")

    trace1 = plugin.manager.current_trace.trace_id

    plugin.after_runtime()

    plugin.before_runtime(runtime_name="Run-2")

    trace2 = plugin.manager.current_trace.trace_id

    plugin.after_runtime()

    assert trace1 != trace2


# ==========================================================
# Multiple runtime sessions
# ==========================================================


def test_multiple_runtime_sessions(plugin):

    total = 10

    for i in range(total):

        plugin.before_runtime(
            runtime_name=f"Runtime-{i}",
        )

        plugin.after_runtime()

    assert plugin.manager.completed_trace_count == total


def test_runtime_sessions_are_independent(plugin):

    ids = set()

    for i in range(5):

        plugin.before_runtime(
            runtime_name=f"Runtime-{i}",
        )

        ids.add(
            plugin.manager.current_trace.trace_id
        )

        plugin.after_runtime()

    assert len(ids) == 5


# ==========================================================
# Failure recovery
# ==========================================================


def test_runtime_failure_does_not_break_next_session(plugin):

    plugin.before_runtime(runtime_name="Failure")

    plugin.after_runtime(
        success=False,
    )

    plugin.before_runtime(runtime_name="Recovery")

    assert plugin.manager.current_trace is not None

    plugin.after_runtime()


def test_after_runtime_without_before(plugin):

    plugin.after_runtime()

    assert plugin.manager.completed_trace_count == 0


def test_double_after_runtime(plugin):

    plugin.before_runtime(runtime_name="Runtime")

    plugin.after_runtime()

    plugin.after_runtime()

    assert plugin.manager.completed_trace_count == 1


# ==========================================================
# Cleanup
# ==========================================================


def test_cleanup_clears_everything(plugin):

    plugin.before_runtime(runtime_name="Runtime")

    plugin.cleanup()

    assert plugin.manager.current_trace is None

    assert plugin.manager.current_span is None


def test_cleanup_is_idempotent(plugin):

    plugin.cleanup()

    plugin.cleanup()

    plugin.cleanup()

    assert plugin.manager.current_trace is None


# ==========================================================
# Reset
# ==========================================================


def test_reset_after_runtime(plugin):

    plugin.before_runtime(runtime_name="Runtime")

    plugin.after_runtime()

    plugin.manager.reset()

    assert plugin.manager.active_trace_count == 0

    assert plugin.manager.completed_trace_count == 0


def test_reset_without_runtime(plugin):

    plugin.manager.reset()

    assert plugin.manager.active_trace_count == 0

    assert plugin.manager.completed_trace_count == 0


# ==========================================================
# Stress
# ==========================================================


def test_many_runtime_cycles(plugin):

    for _ in range(50):

        plugin.before_runtime(runtime_name="Runtime")

        plugin.after_runtime()

    assert plugin.manager.completed_trace_count == 50


def test_many_cleanup_cycles(plugin):

    for _ in range(50):

        plugin.cleanup()

    assert plugin.manager.current_trace is None


# ==========================================================
# Context integrity
# ==========================================================


def test_context_is_clean_after_every_runtime(plugin):

    for _ in range(5):

        plugin.before_runtime(runtime_name="Runtime")

        plugin.after_runtime()

        assert plugin.manager.current_trace is None

        assert plugin.manager.current_span is None


def test_no_active_span_after_runtime(plugin):

    plugin.before_runtime(runtime_name="Runtime")

    plugin.manager.start_span("Planning")

    plugin.manager.finish_span()

    plugin.after_runtime()

    assert plugin.manager.current_span is None


# ==========================================================
# Robustness against repeated calls
# ==========================================================


def test_before_runtime_called_twice(plugin):

    plugin.before_runtime(runtime_name="Runtime")

    plugin.before_runtime(runtime_name="Runtime")

    assert plugin.manager.current_trace is not None

    plugin.after_runtime()


def test_cleanup_after_shutdown(plugin):

    plugin.shutdown()

    plugin.cleanup()

    assert plugin.manager.current_trace is None