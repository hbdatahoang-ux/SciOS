"""
Tests the foundational Trace entity API.

Python 3.11+
"""

from __future__ import annotations


from datetime import datetime
import time


import pytest


from scios.runtime.observability.tracing.span import Span
from scios.runtime.observability.tracing.trace import (
    DEFAULT_TRACE_AUTO_FINISH,
    DEFAULT_TRACE_AUTO_START,
    DEFAULT_TRACE_NAME,
    DEFAULT_TRACE_VERSION,
    TRACE_VERSION,
    Trace,
    TraceValidationError,
)

# ==========================================================================
# Helpers
# ==========================================================================


def create_trace(
    **kwargs,
) -> Trace:
    """
    Create a Trace with automatic lifecycle disabled.
    """

    kwargs.setdefault(
        "auto_start",
        False,
    )

    kwargs.setdefault(
        "auto_finish",
        False,
    )

    return Trace(
        **kwargs,
    )


# ==========================================================================
# 1. Construction
# ==========================================================================


def test_trace_creation():

    value = create_trace()

    assert isinstance(
        value,
        Trace,
    )


def test_trace_default_values():

    value = Trace()

    assert value.name == DEFAULT_TRACE_NAME
    assert value.version == DEFAULT_TRACE_VERSION
    assert value.started is (
        DEFAULT_TRACE_AUTO_START
    )

    assert value.finished is False
    assert value.cancelled is False
    assert value.frozen is False
    assert value.closed is False


def test_trace_custom_id():

    value = create_trace(
        trace_id="trace-001",
    )

    assert value.id == "trace-001"


def test_trace_custom_name():

    value = create_trace(
        name="custom-trace",
    )

    assert value.name == "custom-trace"


def test_trace_validation():

    value = create_trace(
        name="valid-trace",
    )

    assert value.validate() is True

    with pytest.raises(
        TraceValidationError,
    ):
        Trace(
            name="",
        )

    with pytest.raises(
        TraceValidationError,
    ):
        Trace(
            name=123,
        )


# ==========================================================================
# 2. Identity
# ==========================================================================


def test_trace_id():

    value = create_trace()

    assert isinstance(
        value.id,
        str,
    )

    assert value.id


def test_trace_name():

    value = create_trace(
        name="identity-trace",
    )

    assert value.name == "identity-trace"


def test_trace_version():

    value = create_trace()

    assert value.version == TRACE_VERSION


# ==========================================================================
# 3. Lifecycle
# ==========================================================================


def test_trace_start():

    value = create_trace()

    assert value.started is False

    result = value.start()

    assert result is value
    assert value.started is True
    assert value.finished is False
    assert value.active is True
    assert value.start_time is not None


def test_trace_finish():

    value = create_trace()

    value.start()

    result = value.finish()

    assert result is value
    assert value.started is True
    assert value.finished is True
    assert value.active is False
    assert value.end_time is not None


def test_trace_reset():

    value = create_trace()

    value.start()
    value.finish()

    result = value.reset()

    assert result is value
    assert value.started is False
    assert value.finished is False
    assert value.cancelled is False
    assert value.frozen is False
    assert value.closed is False
    assert value.start_time is None
    assert value.end_time is None


def test_trace_restart():

    value = create_trace()

    value.start()
    value.finish()

    result = value.restart()

    assert result is value
    assert value.started is True
    assert value.finished is False
    assert value.active is True
    assert value.start_time is not None


def test_trace_cancel():

    value = create_trace()

    value.start()

    result = value.cancel()

    assert result is value
    assert value.cancelled is True
    assert value.active is False


def test_trace_freeze():

    value = create_trace()

    result = value.freeze()

    assert result is value
    assert value.frozen is True


def test_trace_unfreeze():

    value = create_trace()

    value.freeze()

    result = value.unfreeze()

    assert result is value
    assert value.frozen is False


def test_trace_close():

    value = create_trace()

    result = value.close()

    assert result is value
    assert value.closed is True
    assert value.active is False


# ==========================================================================
# 4. State
# ==========================================================================


def test_trace_state():

    value = create_trace()

    assert isinstance(
        value.state,
        str,
    )

    assert value.state == "created"


def test_trace_started():

    value = create_trace()

    assert value.started is False

    value.start()

    assert value.started is True


def test_trace_finished():

    value = create_trace()

    assert value.finished is False

    value.start()
    value.finish()

    assert value.finished is True


def test_trace_cancelled():

    value = create_trace()

    assert value.cancelled is False

    value.cancel()

    assert value.cancelled is True


def test_trace_frozen():

    value = create_trace()

    assert value.frozen is False

    value.freeze()

    assert value.frozen is True


def test_trace_closed():

    value = create_trace()

    assert value.closed is False

    value.close()

    assert value.closed is True


def test_trace_active():

    value = create_trace()

    assert value.active is False

    value.start()

    assert value.active is True

    value.finish()

    assert value.active is False


# ==========================================================================
# 5. Timing
# ==========================================================================


def test_start_time():

    value = create_trace()

    assert value.start_time is None

    value.start()

    assert value.start_time is not None
    assert isinstance(
        value.start_time,
        datetime,
    )


def test_end_time():

    value = create_trace()

    assert value.end_time is None

    value.start()
    value.finish()

    assert value.end_time is not None
    assert isinstance(
        value.end_time,
        datetime,
    )


def test_duration():

    value = create_trace()

    assert value.duration is None

    value.start()

    time.sleep(
        0.001,
    )

    value.finish()

    assert value.duration is not None
    assert value.duration >= 0

# ==========================================================================
# 6. Metadata
# ==========================================================================


def test_attributes():

    value = create_trace()

    assert isinstance(
        value.attributes,
        dict,
    )

    assert value.attributes == {}


def test_set_attribute():

    value = create_trace()

    result = value.set_attribute(
        "service",
        "scios",
    )

    assert result is value
    assert value.attributes["service"] == "scios"


def test_get_attribute():

    value = create_trace()

    value.set_attribute(
        "service",
        "scios",
    )

    assert value.get_attribute(
        "service",
    ) == "scios"

    assert value.get_attribute(
        "missing",
    ) is None

    assert value.get_attribute(
        "missing",
        "default",
    ) == "default"


def test_remove_attribute():

    value = create_trace()

    value.set_attribute(
        "service",
        "scios",
    )

    result = value.remove_attribute(
        "service",
    )

    assert result is value
    assert "service" not in value.attributes


def test_clear_attributes():

    value = create_trace(
        attributes={
            "service": "scios",
            "environment": "test",
        },
    )

    result = value.clear_attributes()

    assert result is value
    assert value.attributes == {}


def test_tags():

    value = create_trace()

    assert isinstance(
        value.tags,
        dict,
    )

    assert value.tags == {}


def test_set_tag():

    value = create_trace()

    result = value.set_tag(
        "environment",
        "test",
    )

    assert result is value
    assert value.tags["environment"] == "test"


def test_get_tag():

    value = create_trace()

    value.set_tag(
        "environment",
        "test",
    )

    assert value.get_tag(
        "environment",
    ) == "test"

    assert value.get_tag(
        "missing",
    ) is None

    assert value.get_tag(
        "missing",
        "default",
    ) == "default"


def test_remove_tag():

    value = create_trace()

    value.set_tag(
        "environment",
        "test",
    )

    result = value.remove_tag(
        "environment",
    )

    assert result is value
    assert "environment" not in value.tags


def test_clear_tags():

    value = create_trace()

    value.set_tag(
        "environment",
        "test",
    )

    value.set_tag(
        "service",
        "scios",
    )

    result = value.clear_tags()

    assert result is value
    assert value.tags == {}


def test_baggage():

    value = create_trace()

    assert isinstance(
        value.baggage,
        dict,
    )

    assert value.baggage == {}


def test_baggage_operations():

    value = create_trace()

    result = value.set_baggage(
        "request_id",
        "req-001",
    )

    assert result is value

    assert value.get_baggage(
        "request_id",
    ) == "req-001"

    assert value.get_baggage(
        "missing",
    ) is None

    assert value.get_baggage(
        "missing",
        "default",
    ) == "default"

    result = value.remove_baggage(
        "request_id",
    )

    assert result is value

    assert value.get_baggage(
        "request_id",
    ) is None

    value.set_baggage(
        "a",
        1,
    )

    value.set_baggage(
        "b",
        2,
    )

    result = value.clear_baggage()

    assert result is value
    assert value.baggage == {}


# ==========================================================================
# 7. Span Registry
# ==========================================================================


def test_spans():

    value = create_trace()

    assert isinstance(
        value.spans,
        list,
    )

    assert value.spans == []


def test_span_count():

    value = create_trace()

    assert value.span_count == 0

    span = value.start_span(
        "span-001",
    )

    assert value.span_count == 1

    assert span in value.spans


def test_add_span():

    value = create_trace()

    span = Span(
        name="span-001",
        auto_start=False,
        auto_finish=False,
    )

    result = value.add_span(
        span,
    )

    assert result is value
    assert span in value.spans
    assert value.span_count == 1


def test_remove_span():

    value = create_trace()

    span = Span(
        name="span-001",
        auto_start=False,
        auto_finish=False,
    )

    value.add_span(
        span,
    )

    result = value.remove_span(
        span,
    )

    assert result is value
    assert span not in value.spans
    assert value.span_count == 0


def test_get_span():

    value = create_trace()

    span = Span(
        name="span-001",
        auto_start=False,
        auto_finish=False,
    )

    value.add_span(
        span,
    )

    assert value.get_span(
        span.id,
    ) is span

    assert value.get_span(
        "missing",
    ) is None


def test_clear_spans():

    value = create_trace()

    value.add_span(
        Span(
            name="span-001",
            auto_start=False,
            auto_finish=False,
        ),
    )

    value.add_span(
        Span(
            name="span-002",
            auto_start=False,
            auto_finish=False,
        ),
    )

    result = value.clear_spans()

    assert result is value
    assert value.spans == []
    assert value.span_count == 0


def test_current_span():

    value = create_trace()

    assert value.current_span is None

    span = value.start_span(
        "span-001",
    )

    assert value.current_span is span


def test_root_span():

    value = create_trace()

    assert value.root_span is None

    span = value.start_span(
        "root-span",
    )

    assert value.root_span is span


# ==========================================================================
# 8. Span Lifecycle
# ==========================================================================


def test_start_span():

    value = create_trace()

    span = value.start_span(
        "worker",
    )

    assert isinstance(
        span,
        Span,
    )

    assert span in value.spans
    assert span.started is True
    assert value.current_span is span


def test_finish_span():

    value = create_trace()

    span = value.start_span(
        "worker",
    )

    result = value.finish_span()

    assert result is span
    assert span.finished is True
    assert value.current_span is None


def test_active_spans():

    value = create_trace()

    first = value.start_span(
        "first",
    )

    second = value.start_span(
        "second",
    )

    assert first in value.active_spans
    assert second in value.active_spans

    value.finish_span()

    assert second not in value.active_spans
    assert first in value.active_spans


# ==========================================================================
# 9. Exceptions
# ==========================================================================


def test_attach_exception():

    value = create_trace()

    error = ValueError(
        "test error",
    )

    result = value.attach_exception(
        error,
    )

    assert result is value
    assert value.exception is error


def test_has_exception():

    value = create_trace()

    assert value.has_exception is False

    value.attach_exception(
        RuntimeError(
            "failure",
        ),
    )

    assert value.has_exception is True


# ==========================================================================
# 10. Context
# ==========================================================================


def test_context():

    value = create_trace()

    context = {
        "trace_id": value.id,
        "span_id": "span-001",
    }

    value.context = context

    assert value.context == context


def test_context_id():

    value = create_trace()

    context = {
        "context_id": "ctx-001",
    }

    value.context = context

    assert value.context_id == "ctx-001"


def test_context_propagation():

    parent = create_trace(
        trace_id="trace-001",
    )

    context = {
        "trace_id": parent.id,
        "span_id": "parent-span",
        "context_id": "ctx-001",
    }

    parent.context = context

    child = parent.start_span(
        "child",
    )

    assert child.trace_id == parent.id
    assert child.parent_id == parent.id

    assert child.context_id == parent.context_id

# ==========================================================================
# 11. Events
# ==========================================================================


def test_events():

    value = create_trace()

    assert isinstance(
        value.events,
        list,
    )

    assert value.events == []


def test_add_event():

    value = create_trace()

    event = {
        "name": "started",
        "timestamp": datetime.now().astimezone(),
    }

    result = value.add_event(
        event,
    )

    assert result is value
    assert event in value.events


def test_event_count():

    value = create_trace()

    assert value.event_count == 0

    value.add_event(
        {"name": "event-1"},
    )

    value.add_event(
        {"name": "event-2"},
    )

    assert value.event_count == 2


def test_clear_events():

    value = create_trace()

    value.add_event(
        {"name": "event-1"},
    )

    value.add_event(
        {"name": "event-2"},
    )

    result = value.clear_events()

    assert result is value
    assert value.events == []
    assert value.event_count == 0


# ==========================================================================
# 12. Links
# ==========================================================================


def test_links():

    value = create_trace()

    assert isinstance(
        value.links,
        list,
    )

    assert value.links == []


def test_add_link():

    value = create_trace()

    link = {
        "trace_id": "trace-linked",
        "span_id": "span-linked",
    }

    result = value.add_link(
        link,
    )

    assert result is value
    assert link in value.links


def test_link_count():

    value = create_trace()

    assert value.link_count == 0

    value.add_link(
        {"trace_id": "trace-001"},
    )

    value.add_link(
        {"trace_id": "trace-002"},
    )

    assert value.link_count == 2


def test_clear_links():

    value = create_trace()

    value.add_link(
        {"trace_id": "trace-001"},
    )

    value.add_link(
        {"trace_id": "trace-002"},
    )

    result = value.clear_links()

    assert result is value
    assert value.links == []
    assert value.link_count == 0


# ==========================================================================
# 13. Diagnostics
# ==========================================================================


def test_summary():

    value = create_trace(
        name="summary-trace",
        trace_id="trace-001",
    )

    result = value.summary()

    assert isinstance(
        result,
        dict,
    )

    assert result["id"] == value.id
    assert result["name"] == "summary-trace"
    assert result["trace_id"] == "trace-001"


def test_diagnostics():

    value = create_trace(
        name="diagnostic-trace",
    )

    result = value.diagnostics()

    assert isinstance(
        result,
        dict,
    )

    assert "summary" in result
    assert "attributes" in result
    assert "tags" in result
    assert "baggage" in result
    assert "spans" in result
    assert "events" in result
    assert "links" in result


def test_validate():

    value = create_trace(
        name="valid-trace",
    )

    assert value.validate() is True


def test_health():

    value = create_trace(
        name="healthy-trace",
    )

    assert value.health() is True


# ==========================================================================
# 14. Persistence
# ==========================================================================


def test_to_dict():

    value = create_trace(
        name="serialization-trace",
        trace_id="trace-001",
    )

    result = value.to_dict()

    assert isinstance(
        result,
        dict,
    )

    assert result["id"] == value.id
    assert result["name"] == value.name
    assert result["trace_id"] == value.trace_id


def test_to_json():

    import json

    value = create_trace(
        name="json-trace",
    )

    result = value.to_json()

    assert isinstance(
        result,
        str,
    )

    decoded = json.loads(
        result,
    )

    assert decoded["id"] == value.id
    assert decoded["name"] == value.name


def test_snapshot():

    value = create_trace(
        name="snapshot-trace",
        trace_id="trace-001",
    )

    snapshot = value.snapshot()

    assert isinstance(
        snapshot,
        dict,
    )

    assert snapshot["id"] == value.id
    assert snapshot["name"] == value.name
    assert snapshot["trace_id"] == value.trace_id


def test_snapshot_preserves_identity():

    value = create_trace(
        name="identity-trace",
        trace_id="trace-001",
    )

    snapshot = value.snapshot()

    assert snapshot["id"] == value.id
    assert snapshot["name"] == value.name
    assert snapshot["trace_id"] == value.trace_id


def test_restore():

    value = create_trace(
        name="restore-trace",
        trace_id="trace-001",
    )

    snapshot = value.snapshot()

    value.name = "changed"

    result = value.restore(
        snapshot,
    )

    assert result is value
    assert value.id == snapshot["id"]
    assert value.name == snapshot["name"]
    assert value.trace_id == snapshot["trace_id"]


def test_clone():

    value = create_trace(
        name="clone-trace",
        trace_id="trace-001",
    )

    clone = value.clone()

    assert isinstance(
        clone,
        Trace,
    )

    assert clone is not value
    assert clone.id == value.id
    assert clone.name == value.name
    assert clone.trace_id == value.trace_id


def test_clone_is_independent():

    value = create_trace(
        name="original-trace",
        attributes={
            "service": "scios",
        },
    )

    clone = value.clone()

    clone.set_attribute(
        "service",
        "changed",
    )

    assert value.get_attribute(
        "service",
    ) == "scios"

    assert clone.get_attribute(
        "service",
    ) == "changed"


# ==========================================================================
# 15. Protocol
# ==========================================================================


def test_repr():

    value = create_trace(
        name="repr-trace",
    )

    result = repr(
        value,
    )

    assert isinstance(
        result,
        str,
    )

    assert "Trace" in result
    assert value.id in result


def test_str():

    value = create_trace(
        name="str-trace",
    )

    result = str(
        value,
    )

    assert isinstance(
        result,
        str,
    )

    assert "str-trace" in result


def test_bool():

    value = create_trace()

    assert bool(
        value,
    ) is True

    value.close()

    assert bool(
        value,
    ) is False


def test_len():

    value = create_trace()

    assert len(
        value,
    ) == value.span_count


def test_getitem():

    value = create_trace()

    span = value.start_span(
        "getitem-span",
    )

    assert value[0] is span


def test_iter():

    value = create_trace()

    first = value.start_span(
        "first",
    )

    second = value.start_span(
        "second",
    )

    result = list(
        iter(value),
    )

    assert result == [
        first,
        second,
    ]


def test_eq():

    value = create_trace(
        name="equal-trace",
        trace_id="trace-001",
    )

    clone = value.clone()

    assert value == clone

    other = create_trace(
        name="other-trace",
        trace_id="trace-002",
    )

    assert value != other


def test_hash():

    value = create_trace(
        trace_id="trace-hash-001",
    )

    result = hash(
        value,
    )

    assert isinstance(
        result,
        int,
    )

    assert hash(
        value,
    ) == result


# ==========================================================================
# 16. Complete Workflow
# ==========================================================================


def test_trace_complete_workflow():

    value = create_trace(
        name="workflow-trace",
        trace_id="trace-workflow",
        attributes={
            "service": "scios",
        },
    )

    assert value.validate() is True
    assert value.health() is True

    value.start()

    assert value.started is True
    assert value.active is True
    assert value.start_time is not None

    value.set_attribute(
        "environment",
        "test",
    )

    value.set_tag(
        "component",
        "runtime",
    )

    value.set_baggage(
        "request_id",
        "req-001",
    )

    value.add_event(
        {
            "name": "workflow-start",
        },
    )

    value.add_link(
        {
            "trace_id": "linked-trace",
        },
    )

    span = value.start_span(
        "worker",
    )

    assert span.started is True
    assert value.span_count == 1
    assert value.current_span is span
    assert value.root_span is span

    value.finish_span()

    assert span.finished is True
    assert value.active_spans == []

    value.attach_exception(
        ValueError(
            "workflow error",
        ),
    )

    assert value.has_exception is True

    value.finish()

    assert value.finished is True
    assert value.active is False
    assert value.end_time is not None

    assert value.validate() is True
    assert value.health() is True

    snapshot = value.snapshot()

    assert snapshot["id"] == value.id
    assert snapshot["name"] == value.name

    clone = value.clone()

    assert clone is not value
    assert clone.id == value.id
    assert clone.name == value.name

    assert len(
        value,
    ) == value.span_count

    assert bool(
        value,
    ) is True
