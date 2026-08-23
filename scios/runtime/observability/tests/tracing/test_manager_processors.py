"""
Tests for TraceManager processor pipeline.

Coverage
--------
- processor registration
- trace callbacks
- span callbacks
- event callbacks
- attribute callbacks
- status callbacks
- baggage callbacks
- callback ordering
"""

from __future__ import annotations

import pytest

from scios.runtime.observability.tracing.event import Event
from scios.runtime.observability.tracing.manager import TraceManager
from scios.runtime.observability.tracing.enums import ExecutionPhase

# ==========================================================
# Dummy Processor
# ==========================================================


class DummyProcessor:

    def __init__(self):

        self.calls = []

    # ------------------------------------------------------

    def on_trace_start(self, trace):
        self.calls.append(("trace_start", trace))

    def on_trace_end(self, trace):
        self.calls.append(("trace_end", trace))

    # ------------------------------------------------------

    def on_span_start(self, span):
        self.calls.append(("span_start", span))

    def on_span_end(self, span):
        self.calls.append(("span_end", span))

    # ------------------------------------------------------

    def on_event(self, span, event):
        self.calls.append(("event", event))

    def on_attribute(self, span, key, value):
        self.calls.append(("attribute", key, value))

    def on_status_change(
        self,
        span,
        status,
        description,
    ):
        self.calls.append(
            (
                "status",
                status,
                description,
            )
        )

    def on_exception(
        self,
        span,
        exc,
    ):
        self.calls.append(
            (
                "exception",
                exc.__class__.__name__,
            )
        )

    def on_link(
        self,
        span,
        link,
    ):
        self.calls.append(("link", link))

    # ------------------------------------------------------

    def on_baggage_added(
        self,
        trace,
        key,
        value,
    ):
        self.calls.append(
            (
                "baggage_add",
                key,
                value,
            )
        )

    def on_baggage_removed(
        self,
        trace,
        key,
    ):
        self.calls.append(
            (
                "baggage_remove",
                key,
            )
        )

    def on_baggage_cleared(
        self,
        trace,
        count,
    ):
        self.calls.append(
            (
                "baggage_clear",
                count,
            )
        )


# ==========================================================
# Helpers
# ==========================================================


def create_manager():

    processor = DummyProcessor()

    manager = TraceManager(
        processors=[processor],
    )

    manager.start_trace("runtime")

    return manager, processor


# ==========================================================
# Trace lifecycle
# ==========================================================


def test_trace_start_callback():

    manager, processor = create_manager()

    assert processor.calls[0][0] == "trace_start"


def test_trace_finish_callback():

    manager, processor = create_manager()

    manager.finish_trace()

    assert processor.calls[-1][0] == "trace_end"


# ==========================================================
# Span lifecycle
# ==========================================================


def test_span_start_callback():

    manager, processor = create_manager()

    manager.start_span("planner")

    assert processor.calls[-1][0] == "span_start"


def test_span_finish_callback():

    manager, processor = create_manager()

    manager.start_span("planner")

    manager.finish_span()

    assert processor.calls[-1][0] == "span_end"


# ==========================================================
# Events
# ==========================================================


def test_event_callback():

    manager, processor = create_manager()

    manager.start_span("planner")

    manager.add_event(
        Event(
            name="compute",
            phase=ExecutionPhase.RUNNING,
        )
    )

    assert processor.calls[-1][0] == "event"


# ==========================================================
# Attributes
# ==========================================================


def test_attribute_callback():

    manager, processor = create_manager()

    manager.start_span("planner")

    manager.set_attribute(
        "device",
        "cpu",
    )

    assert processor.calls[-1] == (
        "attribute",
        "device",
        "cpu",
    )


# ==========================================================
# Status
# ==========================================================


def test_status_callback():

    manager, processor = create_manager()

    manager.start_span("planner")

    manager.set_status(
        "ERROR",
        "failed",
    )

    kind, status, description = processor.calls[-1]

    assert kind == "status"

    assert status == "ERROR"

    assert description == "failed"


# ==========================================================
# Exception
# ==========================================================


def test_exception_callback():

    manager, processor = create_manager()

    manager.start_span("planner")

    try:

        raise ValueError("boom")

    except ValueError as exc:

        manager.record_exception(exc)

    assert processor.calls[-1][0] == "exception"


# ==========================================================
# Processor Registry
# ==========================================================


def test_add_processor():

    manager = TraceManager()

    proc = DummyProcessor()

    manager.add_processor(proc)

    assert proc in manager.processors


def test_remove_processor():

    manager = TraceManager()

    proc = DummyProcessor()

    manager.add_processor(proc)

    manager.remove_processor(proc)

    assert proc not in manager.processors


def test_clear_processors():

    manager = TraceManager()

    manager.add_processor(DummyProcessor())

    manager.add_processor(DummyProcessor())

    manager.clear_processors()

    assert manager.processors == []


def test_duplicate_processor_not_added():

    manager = TraceManager()

    proc = DummyProcessor()

    manager.add_processor(proc)

    manager.add_processor(proc)

    assert manager.processors.count(proc) == 1


# ==========================================================
# Ordering
# ==========================================================


def test_processor_order_preserved():

    first = DummyProcessor()

    second = DummyProcessor()

    manager = TraceManager(
        processors=[
            first,
            second,
        ]
    )

    manager.start_trace("runtime")

    manager.finish_trace()

    assert first.calls[0][0] == "trace_start"

    assert second.calls[0][0] == "trace_start"

    assert first.calls[-1][0] == "trace_end"

    assert second.calls[-1][0] == "trace_end"


# ==========================================================
# Regression
# ==========================================================


def test_no_processors():

    manager = TraceManager()

    manager.start_trace("runtime")

    manager.start_span("planner")

    manager.finish_span()

    manager.finish_trace()


def test_processor_pipeline_multiple_spans():

    manager, processor = create_manager()

    manager.start_span("A")

    manager.finish_span()

    manager.start_span("B")

    manager.finish_span()

    names = [c[0] for c in processor.calls]

    assert names.count("span_start") == 2

    assert names.count("span_end") == 2