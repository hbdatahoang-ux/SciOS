"""
Tests for runtime scope integration.

Responsibilities
----------------
- Runtime scope lifecycle
- Exception handling
- Nested runtime scopes
- Context cleanup
"""

from __future__ import annotations

import pytest


# ==========================================================
# Successful runtime scope
# ==========================================================


def test_runtime_scope_success(plugin):

    plugin.before_runtime(
        runtime_name="Runtime",
    )

    trace = plugin.manager.current_trace

    assert trace is not None

    plugin.after_runtime()

    assert plugin.manager.current_trace is None


def test_runtime_scope_creates_single_trace(plugin):

    plugin.before_runtime(
        runtime_name="Runtime",
    )

    trace = plugin.manager.current_trace

    assert trace is not None

    plugin.after_runtime()

    assert plugin.manager.completed_trace_count == 1


# ==========================================================
# Exception handling
# ==========================================================


def test_runtime_scope_failure(plugin):

    plugin.before_runtime(
        runtime_name="Runtime",
    )

    plugin.after_runtime(
        success=False,
    )

    trace = next(
        iter(
            plugin.manager.completed_traces.values()
        )
    )

    assert not trace.success


def test_runtime_scope_exception_cleanup(plugin):

    plugin.before_runtime(
        runtime_name="Runtime",
    )

    plugin.after_runtime(
        success=False,
    )

    assert plugin.manager.current_trace is None


# ==========================================================
# Nested runtime
# ==========================================================


def test_nested_runtime_sessions(plugin):

    plugin.before_runtime(
        runtime_name="Outer",
    )

    outer = plugin.manager.current_trace

    plugin.after_runtime()

    plugin.before_runtime(
        runtime_name="Inner",
    )

    inner = plugin.manager.current_trace

    plugin.after_runtime()

    assert outer.trace_id != inner.trace_id


def test_multiple_runtime_sessions(plugin):

    for _ in range(5):

        plugin.before_runtime(
            runtime_name="Runtime",
        )

        plugin.after_runtime()

    assert plugin.manager.completed_trace_count == 5


# ==========================================================
# Context cleanup
# ==========================================================


def test_scope_clears_active_trace(plugin):

    plugin.before_runtime(
        runtime_name="Runtime",
    )

    plugin.after_runtime()

    assert plugin.manager.current_trace is None


def test_scope_clears_active_span(plugin):

    plugin.before_runtime(
        runtime_name="Runtime",
    )

    plugin.manager.start_span(
        "Planning",
    )

    plugin.manager.finish_span()

    plugin.after_runtime()

    assert plugin.manager.current_span is None


def test_scope_stack_depth_returns_zero(plugin):

    plugin.before_runtime(
        runtime_name="Runtime",
    )

    plugin.manager.start_span("A")

    plugin.manager.start_span("B")

    plugin.manager.finish_span()

    plugin.manager.finish_span()

    plugin.after_runtime()

    assert plugin.manager.span_depth == 0


# ==========================================================
# Robustness
# ==========================================================


def test_after_runtime_without_before(plugin):

    plugin.after_runtime()

    assert plugin.manager.completed_trace_count == 0


def test_runtime_scope_reuse(plugin):

    for _ in range(3):

        plugin.before_runtime(
            runtime_name="Runtime",
        )

        plugin.after_runtime()

    assert plugin.manager.completed_trace_count == 3


def test_runtime_scope_does_not_leak_context(plugin):

    plugin.before_runtime(
        runtime_name="Runtime",
    )

    first = plugin.manager.current_trace.trace_id

    plugin.after_runtime()

    plugin.before_runtime(
        runtime_name="Runtime",
    )

    second = plugin.manager.current_trace.trace_id

    plugin.after_runtime()

    assert first != second


# ==========================================================
# Disabled plugin
# ==========================================================


def test_disabled_plugin_scope(
    fake_manager,
    fake_processor,
    fake_exporter,
):

    from .builders import PluginBuilder

    plugin = (
        PluginBuilder()
        .enabled(False)
        .with_manager(fake_manager)
        .with_processor(fake_processor)
        .with_exporter(fake_exporter)
        .build()
    )

    plugin.before_runtime(
        runtime_name="Runtime",
    )

    assert plugin.manager.current_trace is None

    plugin.after_runtime()

    assert plugin.manager.completed_trace_count == 0


# ==========================================================
# Idempotency
# ==========================================================


def test_double_after_runtime(plugin):

    plugin.before_runtime(
        runtime_name="Runtime",
    )

    plugin.after_runtime()

    plugin.after_runtime()

    assert plugin.manager.completed_trace_count == 1


def test_multiple_cleanup_calls(plugin):

    plugin.before_runtime(
        runtime_name="Runtime",
    )

    plugin.after_runtime()

    plugin.cleanup()

    plugin.cleanup()

    assert plugin.manager.current_trace is None