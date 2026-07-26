"""
Tests for TraceManager event APIs.

Coverage
--------
- add_event()
- emit()
- record_exception()
- event ordering
- exception metadata
- failure paths
"""

from __future__ import annotations

import pytest

from scios.runtime.observability.tracing.event import Event
from scios.runtime.observability.tracing.manager import TraceManager


# ==========================================================
# Helpers
# ==========================================================


def create_manager():

    manager = TraceManager()

    manager.start_trace("runtime")

    manager.start_span("planner")

    return manager


# ==========================================================
# add_event()
# ==========================================================


def test_add_event():

    manager = create_manager()

    event = Event(
        name="compute",
        phase="runtime",
    )

    returned = manager.add_event(event)

    assert returned is event

    assert manager.current_span.events[-1] is event


def test_add_multiple_events():

    manager = create_manager()

    for i in range(5):

        manager.add_event(

            Event(

                name=f"event-{i}",

                phase="runtime",

            )

        )

    assert len(manager.current_span.events) == 5


def test_add_event_without_active_span():

    manager = TraceManager()

    manager.start_trace("runtime")

    event = Event(

        name="invalid",

        phase="runtime",

    )

    with pytest.raises(RuntimeError):

        manager.add_event(event)


# ==========================================================
# emit()
# ==========================================================


def test_emit_creates_event():

    manager = create_manager()

    event = manager.emit(

        "load",

        "runtime",

    )

    assert isinstance(event, Event)

    assert event.name == "load"

    assert event.phase == "runtime"


def test_emit_attributes():

    manager = create_manager()

    event = manager.emit(

        "planner",

        "runtime",

        worker="cpu0",

        iteration=5,

    )

    assert event.attributes["worker"] == "cpu0"

    assert event.attributes["iteration"] == 5


def test_emit_appends_to_span():

    manager = create_manager()

    event = manager.emit(

        "planning",

        "runtime",

    )

    assert manager.current_span.events[-1] is event


# ==========================================================
# record_exception()
# ==========================================================


def test_record_exception_returns_event():

    manager = create_manager()

    try:

        raise ValueError("boom")

    except ValueError as exc:

        event = manager.record_exception(exc)

    assert event.name == "exception"

    assert event.phase == "exception"


def test_record_exception_metadata():

    manager = create_manager()

    try:

        raise RuntimeError("failure")

    except RuntimeError as exc:

        event = manager.record_exception(exc)

    attrs = event.attributes

    assert attrs["exception.type"] == "RuntimeError"

    assert attrs["exception.message"] == "failure"

    assert attrs["exception.escaped"] is False


def test_record_exception_escaped():

    manager = create_manager()

    try:

        raise KeyError("missing")

    except KeyError as exc:

        event = manager.record_exception(

            exc,

            escaped=True,

        )

    assert event.attributes["exception.escaped"] is True


def test_record_exception_appends_event():

    manager = create_manager()

    before = len(manager.current_span.events)

    try:

        raise ValueError()

    except ValueError as exc:

        manager.record_exception(exc)

    assert len(manager.current_span.events) == before + 1


def test_record_exception_without_span():

    manager = TraceManager()

    manager.start_trace("runtime")

    with pytest.raises(RuntimeError):

        manager.record_exception(

            RuntimeError("boom")

        )


# ==========================================================
# Ordering
# ==========================================================


def test_event_order_preserved():

    manager = create_manager()

    manager.emit(

        "A",

        "runtime",

    )

    manager.emit(

        "B",

        "runtime",

    )

    manager.emit(

        "C",

        "runtime",

    )

    names = [

        e.name

        for e in manager.current_span.events

    ]

    assert names == [

        "A",

        "B",

        "C",

    ]


def test_exception_after_event():

    manager = create_manager()

    manager.emit(

        "before",

        "runtime",

    )

    try:

        raise ValueError()

    except ValueError as exc:

        manager.record_exception(exc)

    names = [

        e.name

        for e in manager.current_span.events

    ]

    assert names == [

        "before",

        "exception",

    ]


# ==========================================================
# Regression
# ==========================================================


def test_finish_span_keeps_events():

    manager = create_manager()

    manager.emit(

        "planning",

        "runtime",

    )

    span = manager.current_span

    manager.finish_span()

    assert len(span.events) == 1


def test_finish_trace_keeps_span_events():

    manager = create_manager()

    manager.emit(

        "planning",

        "runtime",

    )

    span = manager.current_span

    manager.finish_span()

    manager.finish_trace()

    assert len(span.events) == 1


def test_many_events():

    manager = create_manager()

    for i in range(100):

        manager.emit(

            f"event-{i}",

            "runtime",

        )

    assert len(manager.current_span.events) == 100