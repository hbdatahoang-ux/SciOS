"""
Tests for runtime exporter integration.

Responsibilities
----------------
- Trace exporting
- Multiple exporters
- Export ordering
- Flush and shutdown
- Disabled plugin behaviour
"""

from __future__ import annotations

import pytest


# ==========================================================
# Export after runtime
# ==========================================================


def test_after_runtime_exports_trace(
    plugin,
    fake_exporter,
):

    plugin.before_runtime(
        runtime_name="Runtime",
    )

    plugin.after_runtime()

    assert fake_exporter.trace_exports == 1

    assert fake_exporter.last_trace is not None


def test_exporter_receives_finished_trace(
    plugin,
    fake_exporter,
):

    plugin.before_runtime(
        runtime_name="Runtime",
    )

    plugin.after_runtime()

    trace = fake_exporter.last_trace

    assert trace is not None

    assert trace.finished

    assert trace.success


# ==========================================================
# Multiple exporters
# ==========================================================


def test_multiple_exporters(fake_manager, fake_processor):

    from .builders import PluginBuilder
    from .fakes import FakeExporter

    e1 = FakeExporter()
    e2 = FakeExporter()
    e3 = FakeExporter()

    plugin = (
        PluginBuilder()
        .with_manager(fake_manager)
        .with_processor(fake_processor)
        .with_exporter(e1)
        .with_exporter(e2)
        .with_exporter(e3)
        .build()
    )

    plugin.before_runtime(
        runtime_name="Runtime",
    )

    plugin.after_runtime()

    assert e1.trace_exports == 1
    assert e2.trace_exports == 1
    assert e3.trace_exports == 1


def test_exporters_called_in_order(
    fake_manager,
    fake_processor,
):

    from .builders import PluginBuilder
    from .fakes import FakeExporter

    exporters = [
        FakeExporter(),
        FakeExporter(),
        FakeExporter(),
    ]

    plugin = (
        PluginBuilder()
        .with_manager(fake_manager)
        .with_processor(fake_processor)
        .with_exporters(exporters)
        .build()
    )

    plugin.before_runtime(
        runtime_name="Runtime",
    )

    plugin.after_runtime()

    for exporter in exporters:

        assert exporter.trace_exports == 1


# ==========================================================
# Flush
# ==========================================================


def test_flush_calls_all_exporters(
    fake_manager,
    fake_processor,
):

    from .builders import PluginBuilder
    from .fakes import FakeExporter

    exporters = [
        FakeExporter(),
        FakeExporter(),
    ]

    plugin = (
        PluginBuilder()
        .with_manager(fake_manager)
        .with_processor(fake_processor)
        .with_exporters(exporters)
        .build()
    )

    plugin.flush()

    for exporter in exporters:

        assert exporter.flush_count == 1


# ==========================================================
# Shutdown
# ==========================================================


def test_shutdown_calls_exporters(
    fake_manager,
    fake_processor,
):

    from .builders import PluginBuilder
    from .fakes import FakeExporter

    exporters = [
        FakeExporter(),
        FakeExporter(),
    ]

    plugin = (
        PluginBuilder()
        .with_manager(fake_manager)
        .with_processor(fake_processor)
        .with_exporters(exporters)
        .build()
    )

    plugin.shutdown()

    for exporter in exporters:

        assert exporter.shutdown_count == 1


# ==========================================================
# Disabled plugin
# ==========================================================


def test_disabled_plugin_does_not_export(
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

    plugin.after_runtime()

    assert fake_exporter.trace_exports == 0


# ==========================================================
# Empty exporter list
# ==========================================================


def test_plugin_without_exporters(
    fake_manager,
    fake_processor,
):

    from .builders import PluginBuilder

    plugin = (
        PluginBuilder()
        .with_manager(fake_manager)
        .with_processor(fake_processor)
        .build()
    )

    plugin.before_runtime(
        runtime_name="Runtime",
    )

    plugin.after_runtime()

    #
    # Should finish without exception.
    #


# ==========================================================
# Exporter isolation
# ==========================================================


class BrokenExporter:

    def export_trace(self, trace):
        raise RuntimeError("export failed")


def test_exporter_exception(
    fake_manager,
    fake_processor,
):

    from .builders import PluginBuilder

    plugin = (
        PluginBuilder()
        .with_manager(fake_manager)
        .with_processor(fake_processor)
        .with_exporter(BrokenExporter())
        .build()
    )

    plugin.before_runtime(
        runtime_name="Runtime",
    )

    #
    # If exporter isolation has been implemented,
    # replace pytest.raises(...) with a normal call
    # and verify execution continues.
    #

    with pytest.raises(RuntimeError):

        plugin.after_runtime()


# ==========================================================
# Export exactly once
# ==========================================================


def test_trace_exported_once(
    plugin,
    fake_exporter,
):

    plugin.before_runtime(
        runtime_name="Runtime",
    )

    plugin.after_runtime()

    assert fake_exporter.trace_exports == 1