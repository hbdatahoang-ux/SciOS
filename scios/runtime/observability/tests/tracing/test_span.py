"""
SciOS-NG Observability
Tracing Tests - Span

Tests:

- Span creation
- Identity
- Constructor
- Defaults
- UUID generation
- Parent relationship
"""

from __future__ import annotations

import copy
import json
import time

import pytest

from scios.runtime.observability.tracing.span import (
    Span,
    SpanCapability,
    SpanKind,
    SpanState,
    SpanStatus,
)


# ==============================================================================
# Part 1. Fixtures
# ==============================================================================


@pytest.fixture
def span() -> Span:
    """
    Default standalone span.
    """

    return Span(
        name="test.span",
    )


@pytest.fixture
def trace_span() -> Span:
    """
    Span with predefined trace id.
    """

    return Span(
        name="runtime.execute",
        trace_id="trace-001",
    )


@pytest.fixture
def child_span() -> Span:
    """
    Child span.
    """

    return Span(
        name="child.operation",
        trace_id="trace-001",
        parent_span_id="parent-001",
    )


@pytest.fixture
def started_span() -> Span:
    """
    Started span.
    """

    s = Span(
        name="started.span",
    )

    s.start()

    return s


@pytest.fixture
def finished_span() -> Span:
    """
    Finished span.
    """

    s = Span(
        name="finished.span",
    )

    s.start()
    s.finish()

    return s


# ==============================================================================
# Part 2. Creation
# ==============================================================================


def test_create_default_span():

    span = Span()

    assert span is not None
    assert span.trace_id is not None
    assert span.span_id is not None


def test_create_named_span():

    span = Span(
        name="kernel.execute",
    )

    assert span.name == "kernel.execute"


def test_trace_id_assignment():

    span = Span(
        trace_id="trace-123",
    )

    assert span.trace_id == "trace-123"


def test_parent_span_assignment():

    span = Span(
        parent_span_id="parent-001",
    )

    assert span.parent_span_id == "parent-001"


def test_kind_assignment():

    span = Span(
        kind=SpanKind.CLIENT,
    )

    assert span.kind is SpanKind.CLIENT


def test_default_kind(span):

    assert span.kind is SpanKind.INTERNAL


def test_default_state(span):

    assert span.state is SpanState.INITIALIZED


def test_default_status(span):

    assert span.status is SpanStatus.UNSET


def test_default_duration(span):

    assert span.duration == 0.0


def test_default_attributes(span):

    assert span.attributes == {}


def test_default_events(span):

    assert span.events == []


def test_default_links(span):

    assert span.links == []


def test_default_metadata(span):

    assert span.metadata == {}


def test_default_tags(span):

    assert span.tags == []


def test_default_statistics(span):

    assert span.statistics is not None


def test_default_capabilities(span):

    assert span.capabilities == SpanCapability.ALL


def test_enabled_default(span):

    assert span.enabled is True


def test_auto_start_false():

    span = Span(
        auto_start=False,
    )

    assert span.started is False


def test_auto_start_true():

    span = Span(
        auto_start=True,
    )

    assert span.started is True


def test_unique_span_ids():

    first = Span(
        name="first",
    )

    second = Span(
        name="second",
    )

    assert first.span_id != second.span_id


def test_unique_trace_ids():

    first = Span()

    second = Span()

    assert first.trace_id != second.trace_id


def test_constructor_attributes():

    span = Span(
        attributes={
            "model": "SciOS",
            "version": 1,
        },
    )

    assert span.attributes["model"] == "SciOS"
    assert span.attributes["version"] == 1


def test_constructor_metadata():

    span = Span(
        metadata={
            "runtime": "python",
        },
    )

    assert span.metadata["runtime"] == "python"


def test_constructor_tags():

    span = Span(
        tags=[
            "kernel",
            "runtime",
        ],
    )

    assert span.tags == [
        "kernel",
        "runtime",
    ]


def test_created_timestamp(span):

    assert span.created_at > 0


def test_updated_timestamp(span):

    assert span.updated_at >= span.created_at


def test_invalid_empty_name():

    with pytest.raises(Exception):

        Span(
            name="",
        )
# ==============================================================================
# Part 3. Lifecycle
# ==============================================================================


def test_start(span):

    span.start()

    assert span.started is True
    assert span.state is SpanState.RUNNING
    assert span.started_at is not None


def test_start_twice(span):

    span.start()

    first = span.started_at

    span.start()

    assert span.started_at == first
    assert span.started is True


def test_finish(span):

    span.start()
    span.finish()

    assert span.finished is True
    assert span.state is SpanState.FINISHED
    assert span.finished_at is not None


def test_finish_without_start(span):

    span.finish()

    assert span.finished is True


def test_finish_error_status(span):

    span.start()
    span.finish(
        status=SpanStatus.ERROR,
    )

    assert span.status is SpanStatus.ERROR


def test_end(span):

    span.start()
    span.end()

    assert span.finished is True


def test_cancel(span):

    span.start()
    span.cancel()

    assert span.finished is True


def test_duration(span):

    span.start()

    time.sleep(0.01)

    span.finish()

    assert span.duration >= 0.0


def test_reset(span):

    span.start()

    span.set_attribute(
        "a",
        1,
    )

    span.add_event(
        "start",
    )

    span.finish()

    span.reset()

    assert span.state is SpanState.INITIALIZED
    assert span.status is SpanStatus.UNSET
    assert span.duration == 0.0
    assert span.attributes == {}
    assert span.events == []


def test_enable_disable(span):

    span.disable()

    assert span.enabled is False

    span.enable()

    assert span.enabled is True


def test_freeze_unfreeze(span):

    span.freeze()

    assert span.state is SpanState.FROZEN

    span.unfreeze()

    assert span.state is SpanState.RUNNING


def test_context_manager():

    with Span(
        name="context",
    ) as span:

        assert span.started is True

    assert span.finished is True


# ==============================================================================
# Part 4. Attributes
# ==============================================================================


def test_set_attribute(span):

    span.set_attribute(
        "model",
        "SciOS",
    )

    assert span.attributes["model"] == "SciOS"


def test_get_attribute(span):

    span.set_attribute(
        "version",
        1,
    )

    assert span.get_attribute(
        "version",
    ) == 1


def test_get_missing_attribute(span):

    assert (
        span.get_attribute(
            "missing",
        )
        is None
    )


def test_get_attribute_default(span):

    assert (
        span.get_attribute(
            "missing",
            "default",
        )
        == "default"
    )


def test_has_attribute(span):

    span.set_attribute(
        "enabled",
        True,
    )

    assert span.has_attribute(
        "enabled",
    )


def test_remove_attribute(span):

    span.set_attribute(
        "temp",
        1,
    )

    assert span.remove_attribute(
        "temp",
    ) is True

    assert "temp" not in span.attributes


def test_remove_missing_attribute(span):

    assert (
        span.remove_attribute(
            "missing",
        )
        is False
    )


def test_clear_attributes(span):

    span.set_attribute(
        "a",
        1,
    )

    span.set_attribute(
        "b",
        2,
    )

    span.clear_attributes()

    assert span.attributes == {}


def test_set_attributes(span):

    span.set_attributes(
        {
            "a": 1,
            "b": 2,
            "c": 3,
        }
    )

    assert len(span.attributes) == 3


def test_update_attributes(span):

    span.update_attributes(
        {
            "x": 10,
            "y": 20,
        }
    )

    assert span.attributes["x"] == 10
    assert span.attributes["y"] == 20


def test_copy_attributes(span):

    span.set_attribute(
        "name",
        "runtime",
    )

    copied = span.copy_attributes()

    assert copied == span.attributes
    assert copied is not span.attributes


def test_attribute_count(span):

    span.set_attribute(
        "a",
        1,
    )

    span.set_attribute(
        "b",
        2,
    )

    assert span.attribute_count == 2


def test_setitem_attribute(span):

    span["service"] = "planner"

    assert span.attributes["service"] == "planner"


def test_getitem_attribute(span):

    span["runtime"] = "kernel"

    assert span["runtime"] == "kernel"


def test_contains_attribute(span):

    span["model"] = "SciOS"

    assert "model" in span


def test_iter_attributes(span):

    span["a"] = 1
    span["b"] = 2

    keys = list(iter(span))

    assert "a" in keys
    assert "b" in keys
# ==============================================================================
# Part 5. Events
# ==============================================================================


def test_add_event(span):

    event = span.add_event(
        "runtime.start",
    )

    assert event is not None
    assert span.event_count == 1


def test_add_event_with_attributes(span):

    span.add_event(
        "request",
        {
            "method": "GET",
            "status": 200,
        },
    )

    event = span.events[0]

    assert event["name"] == "request"
    assert event["attributes"]["method"] == "GET"
    assert event["attributes"]["status"] == 200


def test_multiple_events(span):

    span.add_event("start")
    span.add_event("running")
    span.add_event("finish")

    assert span.event_count == 3


def test_get_event(span):

    event = span.add_event(
        "checkpoint",
    )

    restored = span.get_event(
        event["id"],
    )

    assert restored is not None
    assert restored["name"] == "checkpoint"


def test_get_events(span):

    span.add_event("a")
    span.add_event("b")

    events = span.get_events()

    assert isinstance(events, list)
    assert len(events) == 2


def test_remove_event(span):

    event = span.add_event(
        "temporary",
    )

    assert span.remove_event(
        event["id"],
    ) is True

    assert span.event_count == 0


def test_remove_missing_event(span):

    assert (
        span.remove_event(
            "missing",
        )
        is False
    )


def test_clear_events(span):

    span.add_event("a")
    span.add_event("b")

    span.clear_events()

    assert span.event_count == 0
    assert span.events == []


def test_record_exception(span):

    try:
        raise RuntimeError(
            "runtime failure",
        )

    except Exception as exc:

        span.record_exception(
            exc,
        )

    assert span.status is SpanStatus.ERROR
    assert span.statistics.error_count == 1
    assert span.event_count == 1


def test_record_exception_attributes(span):

    try:
        raise ValueError(
            "invalid",
        )

    except Exception as exc:

        span.record_exception(
            exc,
            attributes={
                "stage": "planner",
            },
        )

    event = span.events[0]

    assert (
        event["attributes"]["stage"]
        == "planner"
    )


# ==============================================================================
# Part 6. Links
# ==============================================================================


def test_add_link(span):

    span.add_link(
        trace_id="trace-001",
        span_id="span-001",
    )

    assert len(span.links) == 1


def test_add_multiple_links(span):

    span.add_link(
        "trace-1",
        "span-1",
    )

    span.add_link(
        "trace-2",
        "span-2",
    )

    assert len(span.links) == 2


def test_link_content(span):

    span.add_link(
        trace_id="trace-x",
        span_id="span-x",
    )

    link = span.links[0]

    assert link["trace_id"] == "trace-x"
    assert link["span_id"] == "span-x"


def test_remove_link(span):

    link = span.add_link(
        "trace-remove",
        "span-remove",
    )

    assert span.remove_link(
        link["span_id"],
    ) is True

    assert len(span.links) == 0


def test_remove_missing_link(span):

    assert (
        span.remove_link(
            "missing",
        )
        is False
    )


def test_clear_links(span):

    span.add_link(
        "trace-1",
        "span-1",
    )

    span.add_link(
        "trace-2",
        "span-2",
    )

    span.clear_links()

    assert span.links == []


def test_link_count(span):

    span.add_link(
        "trace-1",
        "span-1",
    )

    span.add_link(
        "trace-2",
        "span-2",
    )

    assert len(span.links) == 2


def test_link_with_metadata(span):

    span.add_link(
        trace_id="trace-meta",
        span_id="span-meta",
        service="planner",
        node="worker-1",
    )

    link = span.links[0]

    assert link["service"] == "planner"
    assert link["node"] == "worker-1"
# ==============================================================================
# Part 7. Serialization
# ==============================================================================


def test_to_dict(span):

    data = span.to_dict()

    assert isinstance(data, dict)
    assert data["name"] == span.name
    assert data["trace_id"] == span.trace_id
    assert data["span_id"] == span.span_id


def test_to_dict_contains_attributes(span):

    span.set_attribute(
        "model",
        "SciOS",
    )

    data = span.to_dict()

    assert (
        data["attributes"]["model"]
        == "SciOS"
    )


def test_from_dict(span):

    data = span.to_dict()

    restored = Span.from_dict(
        data,
    )

    assert restored.name == span.name
    assert restored.trace_id == span.trace_id
    assert restored.span_id == span.span_id


def test_to_json(span):

    payload = span.to_json()

    assert isinstance(
        payload,
        str,
    )


    data = json.loads(
        payload,
    )

    assert (
        data["name"]
        == span.name
    )


def test_from_json(span):

    payload = span.to_json()

    restored = Span.from_json(
        payload,
    )

    assert restored.name == span.name
    assert restored.trace_id == span.trace_id
    assert restored.span_id == span.span_id


def test_snapshot(span):

    snapshot = span.snapshot()

    assert snapshot is not None


    if isinstance(snapshot, dict):

        assert (
            snapshot["name"]
            == span.name
        )

    else:

        assert (
            snapshot.name
            == span.name
        )


def test_restore_from_snapshot(span):

    span.set_attribute(
        "service",
        "planner",
    )

    snapshot = span.snapshot()

    restored = Span.restore(
        snapshot,
    )

    assert restored is not None


def test_serialization_roundtrip(span):

    span.set_attribute(
        "framework",
        "SciOS",
    )

    span.add_event(
        "created",
    )

    payload = span.to_json()

    restored = Span.from_json(
        payload,
    )

    assert restored.name == span.name
    assert (
        restored.attributes["framework"]
        == "SciOS"
    )


# ==============================================================================
# Part 8. Validation
# ==============================================================================


def test_validate(span):

    assert (
        span.validate()
        is True
    )


def test_valid_property(span):

    assert (
        span.valid
        is True
    )


def test_invalid_empty_name():

    with pytest.raises(
        Exception,
    ):

        Span(
            name="",
        )


def test_invalid_attribute_key(span):

    with pytest.raises(
        Exception,
    ):

        span.set_attribute(
            "",
            1,
        )


def test_invalid_event_name(span):

    with pytest.raises(
        Exception,
    ):

        span.add_event(
            "",
        )


def test_invalid_state_transition(span):

    span.finish()

    assert (
        span.finished
        is True
    )


def test_closed_span_cannot_modify(span):

    span.close()

    with pytest.raises(
        Exception,
    ):

        span.set_attribute(
            "x",
            1,
        )


def test_health(span):

    assert (
        span.health()
        is True
    )


def test_summary(span):

    summary = span.summary()

    assert isinstance(
        summary,
        dict,
    )


def test_diagnostics(span):

    diagnostics = span.diagnostics()

    assert isinstance(
        diagnostics,
        dict,
    )
# ==============================================================================
# Part 9. Diagnostics
# ==============================================================================


def test_runtime_statistics(span):

    stats = span.runtime_statistics()

    assert isinstance(
        stats,
        dict,
    )

    assert (
        stats["identity"]["span_id"]
        == span.span_id
    )


def test_report(span):

    report = span.report()

    assert report is not None

    if hasattr(
        report,
        "name",
    ):

        assert (
            report.name
            == span.name
        )

    else:

        assert (
            report["name"]
            == span.name
        )


def test_summary(span):

    summary = span.summary()

    assert isinstance(
        summary,
        dict,
    )

    assert (
        summary["name"]
        == span.name
    )


def test_diagnostics(span):

    result = span.diagnostics()

    assert isinstance(
        result,
        dict,
    )

    assert (
        "summary"
        in result
    )


def test_success_rate(span):

    span.start()

    span.finish()

    assert (
        0.0
        <=
        span.success_rate()
        <=
        1.0
    )


def test_failure_rate(span):

    rate = span.failure_rate()

    assert (
        0.0
        <=
        rate
        <=
        1.0
    )


def test_duration_statistics(span):

    span.start()

    time.sleep(
        0.01,
    )

    span.finish()

    stats = (
        span.duration_statistics()
    )

    assert isinstance(
        stats,
        dict,
    )

    assert (
        stats["current"]
        >= 0
    )


def test_throughput(span):

    span.start()

    span.add_event(
        "event",
    )

    time.sleep(
        0.01,
    )

    span.finish()

    assert (
        span.throughput()
        >= 0.0
    )


def test_health(span):

    assert (
        span.health()
        is True
    )


# ==============================================================================
# Part 10. Python Protocols
# ==============================================================================


def test_repr(span):

    result = repr(
        span,
    )

    assert isinstance(
        result,
        str,
    )

    assert (
        "TraceSpan"
        in result
    )


def test_str(span):

    result = str(
        span,
    )

    assert isinstance(
        result,
        str,
    )


def test_len(span):

    span.set_attribute(
        "a",
        1,
    )

    span.add_event(
        "created",
    )

    span.add_link(
        "trace-1",
        "span-1",
    )

    assert (
        len(span)
        == 3
    )


def test_contains(span):

    span["service"] = "planner"

    assert (
        "service"
        in span
    )


def test_getitem(span):

    span["mode"] = "runtime"

    assert (
        span["mode"]
        == "runtime"
    )


def test_setitem(span):

    span["enabled"] = True

    assert (
        span.attributes["enabled"]
        is True
    )


def test_iter(span):

    span["a"] = 1
    span["b"] = 2

    keys = list(
        iter(span),
    )

    assert (
        "a"
        in keys
    )

    assert (
        "b"
        in keys
    )


def test_bool(span):

    assert bool(
        span,
    ) is True


def test_copy(span):

    cloned = copy.copy(
        span,
    )

    assert (
        cloned.name
        == span.name
    )

    assert (
        cloned.span_id
        == span.span_id
    )


def test_deepcopy(span):

    cloned = copy.deepcopy(
        span,
    )

    assert (
        cloned.name
        == span.name
    )

    assert (
        cloned.span_id
        == span.span_id
    )


def test_context_manager():

    with Span(
        name="context",
    ) as span:

        span.set_attribute(
            "active",
            True,
        )

    assert (
        span.finished
        is True
    )                    