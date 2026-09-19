"""
Tests for runtime processor integration.

Responsibilities
----------------
- Processor callbacks
- Multiple processors
- Callback ordering
- Processor isolation
- Disabled plugin behaviour
"""

from __future__ import annotations

import pytest


# ==========================================================
# Runtime Start
# ==========================================================


def test_before_runtime_calls_processor(plugin, fake_processor):

    plugin.before_runtime(
        runtime_name="Runtime",
    )

    assert fake_processor.trace_started == 1


def test_after_runtime_calls_processor(plugin, fake_processor):

    plugin.before_runtime(
        runtime_name="Runtime",
    )

    plugin.after_runtime()

    assert fake_processor.trace_finished == 1


# ==========================================================
# Multiple processors
# ==========================================================


def test_multiple_processors(fake_manager, fake_exporter):

    from .builders import PluginBuilder
    from .fakes import FakeProcessor

    p1 = FakeProcessor()
    p2 = FakeProcessor()
    p3 = FakeProcessor()

    plugin = (
        PluginBuilder()
        .with_manager(fake_manager)
        .with_processor(p1)
        .with_processor(p2)
        .with_processor(p3)
        .with_exporter(fake_exporter)
        .build()
    )

    plugin.before_runtime(
        runtime_name="Runtime",
    )

    assert p1.trace_started == 1
    assert p2.trace_started == 1
    assert p3.trace_started == 1


def test_all_processors_finish(fake_manager, fake_exporter):

    from .builders import PluginBuilder
    from .fakes import FakeProcessor

    processors = [
        FakeProcessor(),
        FakeProcessor(),
        FakeProcessor(),
    ]

    plugin = (
        PluginBuilder()
        .with_manager(fake_manager)
        .with_exporters([fake_exporter])
        .with_processors(processors)
        .build()
    )

    plugin.before_runtime(
        runtime_name="Runtime",
    )

    plugin.after_runtime()

    for processor in processors:

        assert processor.trace_finished == 1


# ==========================================================
# Ordering
# ==========================================================


def test_processor_order(plugin, fake_processor):

    plugin.before_runtime(
        runtime_name="Runtime",
    )

    plugin.after_runtime()

    assert fake_processor.events == [
        "trace_start",
        "trace_finish",
    ]


# ==========================================================
# Processor receives trace
# ==========================================================


def test_processor_receives_trace_instance(
    plugin,
    fake_processor,
):

    plugin.before_runtime(
        runtime_name="Runtime",
    )

    assert fake_processor.last_trace is not None

    assert (
        fake_processor.last_trace.name
        == "Runtime"
    )


# ==========================================================
# Disabled plugin
# ==========================================================


def test_disabled_plugin_does_not_call_processor(
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

    assert fake_processor.trace_started == 0

    assert fake_processor.trace_finished == 0


# ==========================================================
# Empty processor list
# ==========================================================


def test_plugin_without_processors(
    fake_manager,
    fake_exporter,
):

    from .builders import PluginBuilder

    plugin = (
        PluginBuilder()
        .with_manager(fake_manager)
        .with_exporter(fake_exporter)
        .build()
    )

    plugin.before_runtime(
        runtime_name="Runtime",
    )

    plugin.after_runtime()

    #
    # Should complete without exception.
    #


# ==========================================================
# Processor isolation
# ==========================================================


class BrokenProcessor:

    def on_trace_start(self, trace):
        raise RuntimeError("processor failure")


def test_processor_exception_isolated(
    fake_manager,
    fake_exporter,
):
    from .builders import PluginBuilder

    plugin = (
        PluginBuilder()
        .with_manager(fake_manager)
        .with_processor(BrokenProcessor())
        .with_exporter(fake_exporter)
        .build()
    )

    plugin.before_runtime(
        runtime_name="Runtime",
    )

    # Processor failures are isolated by the production plugin.
    # The exception must not escape from after_runtime().
    plugin.after_runtime()

    # Export must still happen despite the processor failure.
    assert fake_exporter.trace_exports == 1
    assert fake_exporter.last_trace is not None
