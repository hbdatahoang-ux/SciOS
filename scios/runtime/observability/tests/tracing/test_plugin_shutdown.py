"""
Tests for TracingPlugin shutdown lifecycle.

Responsibilities
----------------
- cleanup()
- shutdown()
- exporter shutdown
- exporter flush
- context reset
- idempotency
- robustness
"""

from __future__ import annotations

import pytest

from .builders import PluginBuilder


# ==========================================================
# Cleanup
# ==========================================================


def test_cleanup_resets_manager(plugin):

    plugin.before_runtime(runtime_name="Runtime")

    plugin.before_stage(stage_name="Planner")

    plugin.cleanup()

    assert plugin.manager.current_trace is None
    assert plugin.manager.current_span is None
    assert plugin.manager.active_trace_count == 0


def test_cleanup_without_runtime(plugin):

    plugin.cleanup()

    assert plugin.manager.current_trace is None


# ==========================================================
# Shutdown
# ==========================================================


def test_shutdown_flushes_exporters(
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

    plugin.shutdown()

    assert fake_exporter.flush_called


def test_shutdown_calls_exporter_shutdown(
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

    plugin.shutdown()

    assert fake_exporter.shutdown_called


def test_shutdown_resets_context(plugin):

    plugin.before_runtime(runtime_name="Runtime")

    plugin.before_stage(stage_name="Planner")

    plugin.shutdown()

    assert plugin.manager.current_trace is None

    assert plugin.manager.current_span is None


# ==========================================================
# Multiple Exporters
# ==========================================================


def test_shutdown_multiple_exporters(

    fake_manager,

    fake_processor,

    fake_exporter,

    fake_exporter_two,

):

    plugin = (

        PluginBuilder()

        .with_manager(fake_manager)

        .with_processor(fake_processor)

        .with_exporter(fake_exporter)

        .with_exporter(fake_exporter_two)

        .build()

    )

    plugin.shutdown()

    assert fake_exporter.shutdown_called

    assert fake_exporter_two.shutdown_called


# ==========================================================
# Runtime active
# ==========================================================


def test_shutdown_during_active_runtime(plugin):

    plugin.before_runtime(runtime_name="Runtime")

    plugin.shutdown()

    assert plugin.manager.current_trace is None


def test_shutdown_after_finished_runtime(plugin):

    plugin.before_runtime(runtime_name="Runtime")

    plugin.after_runtime()

    plugin.shutdown()

    assert plugin.manager.completed_trace_count == 0


# ==========================================================
# Idempotency
# ==========================================================


def test_shutdown_twice(plugin):

    plugin.shutdown()

    plugin.shutdown()

    assert plugin.manager.current_trace is None


def test_cleanup_twice(plugin):

    plugin.cleanup()

    plugin.cleanup()

    assert plugin.manager.current_trace is None


# ==========================================================
# Registry
# ==========================================================


def test_shutdown_clears_registry(plugin):

    plugin.before_runtime(runtime_name="Runtime")

    plugin.after_runtime()

    plugin.shutdown()

    assert plugin.manager.active_trace_count == 0

    assert plugin.manager.completed_trace_count == 0


# ==========================================================
# Robustness
# ==========================================================


def test_shutdown_disabled_plugin(disabled_plugin):

    disabled_plugin.shutdown()

    assert disabled_plugin.manager.current_trace is None


def test_cleanup_disabled_plugin(disabled_plugin):

    disabled_plugin.cleanup()

    assert disabled_plugin.manager.current_trace is None


def test_shutdown_after_exception(plugin):

    plugin.before_runtime(runtime_name="Runtime")

    try:
        raise RuntimeError("boom")

    except RuntimeError as exc:

        plugin.manager.record_exception(exc)

    plugin.shutdown()

    assert plugin.manager.current_trace is None


# ==========================================================
# Reuse
# ==========================================================


def test_plugin_reuse_after_shutdown(plugin):

    plugin.shutdown()

    plugin.before_runtime(runtime_name="Runtime")

    assert plugin.manager.current_trace is not None


def test_shutdown_preserves_plugin_instance(plugin):

    plugin.shutdown()

    plugin.before_runtime(runtime_name="AnotherRuntime")

    plugin.after_runtime()

    assert plugin.manager.completed_trace_count == 1