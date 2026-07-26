"""
Tests for event instrumentation of TracingPlugin.

Responsibilities
----------------
- emit()
- add_event()
- record_exception()
- processor callbacks
- exporter integration
- event ordering
- robustness
"""

from __future__ import annotations

import pytest

from .builders import PluginBuilder
from .fakes import FakeEvent


# ==========================================================
# Basic Events
# ==========================================================


def test_emit_creates_event(plugin):

    plugin.before_runtime(runtime_name="Runtime")

    plugin.before_stage(stage_name="Planner")

    event = plugin.manager.emit(
        "planning.started",
        phase="start",
    )

    span = plugin.manager.current_span

    assert event in span.events

    assert event.name == "planning.started"


def test_add_event(plugin):

    plugin.before_runtime(runtime_name="Runtime")

    plugin.before_stage(stage_name="Planner")

    event = FakeEvent(
        name="custom",
        phase="runtime",
    )

    plugin.manager.add_event(event)

    span = plugin.manager.current_span

    assert span.events[-1] is event


def test_multiple_events(plugin):

    plugin.before_runtime(runtime_name="Runtime")

    plugin.before_stage(stage_name="Planner")

    plugin.manager.emit("one", phase="runtime")

    plugin.manager.emit("two", phase="runtime")

    plugin.manager.emit("three", phase="runtime")

    span = plugin.manager.current_span

    assert len(span.events) == 3


# ==========================================================
# Attributes
# ==========================================================


def test_event_attributes(plugin):

    plugin.before_runtime(runtime_name="Runtime")

    plugin.before_stage(stage_name="Planner")

    event = plugin.manager.emit(
        "planner",
        phase="runtime",
        worker="cpu0",
        iteration=3,
    )

    assert event.attributes["worker"] == "cpu0"

    assert event.attributes["iteration"] == 3


# ==========================================================
# Exception Recording
# ==========================================================


def test_record_exception(plugin):

    plugin.before_runtime(runtime_name="Runtime")

    plugin.before_stage(stage_name="Planner")

    try:
        raise ValueError("boom")
    except ValueError as exc:

        event = plugin.manager.record_exception(exc)

    span = plugin.manager.current_span

    assert event in span.events

    assert event.attributes["exception.type"] == "ValueError"


def test_record_exception_marks_error(plugin):

    plugin.before_runtime(runtime_name="Runtime")

    plugin.before_stage(stage_name="Planner")

    try:
        raise RuntimeError("failure")
    except RuntimeError as exc:

        plugin.manager.record_exception(exc)

    span = plugin.manager.current_span

    assert span.status == "ERROR"


# ==========================================================
# Ordering
# ==========================================================


def test_event_order(plugin):

    plugin.before_runtime(runtime_name="Runtime")

    plugin.before_stage(stage_name="Planner")

    plugin.manager.emit("A", phase="runtime")

    plugin.manager.emit("B", phase="runtime")

    plugin.manager.emit("C", phase="runtime")

    names = [
        e.name
        for e in plugin.manager.current_span.events
    ]

    assert names == [
        "A",
        "B",
        "C",
    ]


# ==========================================================
# Processor callbacks
# ==========================================================


def test_processor_receives_event(
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

    plugin.before_stage(stage_name="Planner")

    plugin.manager.emit(
        "planner",
        phase="runtime",
    )

    assert fake_processor.events == 1


# ==========================================================
# Exporter
# ==========================================================


def test_events_exported(
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

    plugin.before_stage(stage_name="Planner")

    plugin.manager.emit(
        "planner",
        phase="runtime",
    )

    plugin.after_stage()

    assert len(fake_exporter.exported_spans) == 1


# ==========================================================
# Robustness
# ==========================================================


def test_emit_without_span(plugin):

    plugin.before_runtime(runtime_name="Runtime")

    with pytest.raises(RuntimeError):

        plugin.manager.emit(
            "planner",
            phase="runtime",
        )


def test_add_event_without_span(plugin):

    plugin.before_runtime(runtime_name="Runtime")

    with pytest.raises(RuntimeError):

        plugin.manager.add_event(
            FakeEvent(
                name="x",
                phase="runtime",
            )
        )


def test_record_exception_without_span(plugin):

    plugin.before_runtime(runtime_name="Runtime")

    with pytest.raises(RuntimeError):

        plugin.manager.record_exception(
            RuntimeError("boom")
        )


# ==========================================================
# Cleanup
# ==========================================================


def test_events_do_not_leak_between_spans(plugin):

    plugin.before_runtime(runtime_name="Runtime")

    plugin.before_stage(stage_name="A")

    plugin.manager.emit("event", phase="runtime")

    plugin.after_stage()

    plugin.before_stage(stage_name="B")

    span = plugin.manager.current_span

    assert len(span.events) == 0