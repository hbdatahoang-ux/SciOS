from __future__ import annotations

from datetime import datetime
from typing import get_args, get_origin

import pytest

from scios.runtime.observability.tracing.span import (
    SPAN_VERSION,
    SPAN_API_VERSION,
    DEFAULT_SPAN_NAME,
    DEFAULT_SPAN_KIND,
    DEFAULT_SPAN_STATUS,
    DEFAULT_SPAN_AUTO_START,
    DEFAULT_SPAN_AUTO_FINISH,
    Span,
    SpanError,
    SpanValidationError,
    SpanStateError,
    SpanClosedError,
    SpanAlreadyStartedError,
    SpanAlreadyFinishedError,
    SpanNotStartedError,
    SpanNotFinishedError,
    SpanFrozenError,
    SpanCancelledError,
    SpanId,
    TraceId,
    ParentSpanId,
    SpanName,
    SpanAttributeKey,
    SpanAttributeValue,
    SpanAttributes,
    Timestamp,
)


# ==============================================================================
# Public Test API
# ==============================================================================


@pytest.fixture
def span():
    """
    Return a default Span instance.
    """
    return Span()


@pytest.fixture
def custom_span():
    """
    Return a Span with explicit identity information.
    """
    return Span(
        name="test-span",
        trace_id="trace-001",
        parent_id="parent-001",
    )


# ==============================================================================
# Part 1. Constants
# ==============================================================================


def test_span_version():
    assert isinstance(
        SPAN_VERSION,
        str,
    )

    assert SPAN_VERSION == "1.0.0"


def test_span_api_version():
    assert isinstance(
        SPAN_API_VERSION,
        str,
    )

    assert SPAN_API_VERSION == "1"


def test_default_span_name():
    assert isinstance(
        DEFAULT_SPAN_NAME,
        str,
    )

    assert DEFAULT_SPAN_NAME == "Span"


def test_default_span_kind():
    assert isinstance(
        DEFAULT_SPAN_KIND,
        str,
    )

    assert DEFAULT_SPAN_KIND == "internal"


def test_default_span_status():
    assert isinstance(
        DEFAULT_SPAN_STATUS,
        str,
    )

    assert DEFAULT_SPAN_STATUS == "unset"


def test_default_span_auto_start():
    assert isinstance(
        DEFAULT_SPAN_AUTO_START,
        bool,
    )

    assert DEFAULT_SPAN_AUTO_START is False


def test_default_span_auto_finish():
    assert isinstance(
        DEFAULT_SPAN_AUTO_FINISH,
        bool,
    )

    assert DEFAULT_SPAN_AUTO_FINISH is True


# ==============================================================================
# Part 2. Exceptions
# ==============================================================================


def test_span_error():
    assert issubclass(
        SpanError,
        RuntimeError,
    )


def test_span_validation_error():
    assert issubclass(
        SpanValidationError,
        SpanError,
    )


def test_span_state_error():
    assert issubclass(
        SpanStateError,
        SpanError,
    )


def test_span_closed_error():
    assert issubclass(
        SpanClosedError,
        SpanStateError,
    )


def test_span_already_started_error():
    assert issubclass(
        SpanAlreadyStartedError,
        SpanStateError,
    )


def test_span_already_finished_error():
    assert issubclass(
        SpanAlreadyFinishedError,
        SpanStateError,
    )


def test_span_not_started_error():
    assert issubclass(
        SpanNotStartedError,
        SpanStateError,
    )


def test_span_not_finished_error():
    assert issubclass(
        SpanNotFinishedError,
        SpanStateError,
    )


def test_span_frozen_error():
    assert issubclass(
        SpanFrozenError,
        SpanStateError,
    )


def test_span_cancelled_error():
    assert issubclass(
        SpanCancelledError,
        SpanStateError,
    )


# ==============================================================================
# Part 3. Type Aliases
# ==============================================================================


def test_span_id_alias():
    assert SpanId is str


def test_trace_id_alias():
    assert TraceId is str


def test_parent_span_id_alias():
    args = get_args(
        ParentSpanId,
    )

    assert str in args
    assert type(None) in args


def test_span_name_alias():
    assert SpanName is str


def test_span_attribute_key_alias():
    assert SpanAttributeKey is str


def test_span_attribute_value_alias():
    args = get_args(
        SpanAttributeValue,
    )

    assert len(args) > 0

    assert (
        str in args
        or int in args
        or float in args
        or bool in args
        or bytes in args
    )


def test_span_attributes_alias():
    origin = get_origin(
        SpanAttributes,
    )

    assert origin is dict


def test_timestamp_alias():
    assert Timestamp is datetime


# ==============================================================================
# Part 4. Constructor
# ==============================================================================


def test_span_constructor_defaults():
    value = Span()

    assert isinstance(
        value,
        Span,
    )

    assert value.name == DEFAULT_SPAN_NAME
    assert value.kind == DEFAULT_SPAN_KIND
    assert value.status == DEFAULT_SPAN_STATUS

    assert value.started is False
    assert value.finished is False
    assert value.cancelled is False
    assert value.closed is False


def test_span_constructor_custom_name():
    value = Span(
        name="custom-span",
    )

    assert value.name == "custom-span"


def test_span_constructor_identity():
    value = Span(
        name="identity-span",
        trace_id="trace-001",
        parent_id="parent-001",
    )

    assert value.id is not None
    assert value.trace_id == "trace-001"
    assert value.parent_id == "parent-001"
    assert value.name == "identity-span"


def test_span_constructor_trace_id():
    value = Span(
        trace_id="trace-123",
    )

    assert value.trace_id == "trace-123"


def test_span_constructor_parent_id():
    value = Span(
        parent_id="parent-123",
    )

    assert value.parent_id == "parent-123"


def test_span_constructor_kind():
    value = Span(
        kind="server",
    )

    assert value.kind == "server"


def test_span_constructor_attributes():
    value = Span(
        attributes={
            "service": "scios",
            "version": "1.0",
        },
    )

    assert value.get_attribute(
        "service",
    ) == "scios"

    assert value.get_attribute(
        "version",
    ) == "1.0"


def test_span_constructor_invalid_name():
    with pytest.raises(
        SpanValidationError,
    ):
        Span(
            name="",
        )


# ==============================================================================
# Part 5. Identity
# ==============================================================================


def test_span_id():
    value = Span()

    assert value.id is not None
    assert isinstance(
        value.id,
        str,
    )
    assert value.id


def test_span_trace_id():
    value = Span(
        trace_id="trace-001",
    )

    assert value.trace_id == "trace-001"


def test_span_parent_id():
    value = Span(
        parent_id="parent-001",
    )

    assert value.parent_id == "parent-001"


def test_span_name():
    value = Span(
        name="test-span",
    )

    assert value.name == "test-span"


def test_span_identity_is_stable():
    value = Span(
        name="stable-span",
        trace_id="trace-001",
        parent_id="parent-001",
    )

    span_id = value.id
    trace_id = value.trace_id
    parent_id = value.parent_id
    name = value.name

    assert value.id == span_id
    assert value.trace_id == trace_id
    assert value.parent_id == parent_id
    assert value.name == name

# ==============================================================================
# Part 6. Lifecycle
# ==============================================================================


def test_span_start():
    value = Span()

    result = value.start()

    assert result is value
    assert value.started is True
    assert value.finished is False
    assert value.cancelled is False
    assert value.closed is False
    assert value.active is True
    assert value.start_time is not None


def test_span_start_twice():
    value = Span()

    value.start()

    with pytest.raises(
        SpanAlreadyStartedError,
    ):
        value.start()


def test_span_finish():
    value = Span()

    value.start()

    result = value.finish()

    assert result is value
    assert value.started is True
    assert value.finished is True
    assert value.cancelled is False
    assert value.closed is False
    assert value.active is False
    assert value.end_time is not None


def test_span_finish_twice():
    value = Span()

    value.start()
    value.finish()

    with pytest.raises(
        SpanAlreadyFinishedError,
    ):
        value.finish()


def test_span_reset():
    value = Span(
        name="reset-span",
        trace_id="trace-001",
        parent_id="parent-001",
        attributes={
            "key": "value",
        },
    )

    value.start()
    value.finish()
    value.reset()

    assert value.started is False
    assert value.finished is False
    assert value.cancelled is False
    assert value.closed is False
    assert value.active is False
    assert value.start_time is None
    assert value.end_time is None
    assert value.duration == 0


def test_span_restart():
    value = Span()

    value.start()
    value.finish()

    result = value.restart()

    assert result is value
    assert value.started is True
    assert value.finished is False
    assert value.cancelled is False
    assert value.closed is False
    assert value.active is True
    assert value.start_time is not None


def test_span_cancel():
    value = Span()

    value.start()

    result = value.cancel()

    assert result is value
    assert value.cancelled is True
    assert value.finished is False
    assert value.closed is False
    assert value.active is False


def test_span_close():
    value = Span()

    value.start()

    result = value.close()

    assert result is value
    assert value.closed is True
    assert value.active is False


def test_span_freeze():
    value = Span()

    result = value.freeze()

    assert result is value
    assert value.frozen is True


def test_span_unfreeze():
    value = Span()

    value.freeze()

    result = value.unfreeze()

    assert result is value
    assert value.frozen is False


# ==============================================================================
# Part 7. State
# ==============================================================================


def test_span_status():
    value = Span()

    assert value.status == DEFAULT_SPAN_STATUS


def test_span_state():
    value = Span()

    assert value.state is not None


def test_span_started():
    value = Span()

    assert value.started is False

    value.start()

    assert value.started is True


def test_span_finished():
    value = Span()

    assert value.finished is False

    value.start()
    value.finish()

    assert value.finished is True


def test_span_cancelled():
    value = Span()

    assert value.cancelled is False

    value.start()
    value.cancel()

    assert value.cancelled is True


def test_span_closed():
    value = Span()

    assert value.closed is False

    value.close()

    assert value.closed is True


def test_span_active():
    value = Span()

    assert value.active is False

    value.start()

    assert value.active is True

    value.finish()

    assert value.active is False


def test_span_state_transitions():
    value = Span()

    assert value.started is False
    assert value.finished is False
    assert value.cancelled is False
    assert value.closed is False
    assert value.active is False

    value.start()

    assert value.started is True
    assert value.finished is False
    assert value.cancelled is False
    assert value.closed is False
    assert value.active is True

    value.finish()

    assert value.started is True
    assert value.finished is True
    assert value.cancelled is False
    assert value.closed is False
    assert value.active is False


# ==============================================================================
# Part 8. Timing
# ==============================================================================


def test_span_start_time():
    value = Span()

    assert value.start_time is None

    value.start()

    assert value.start_time is not None
    assert isinstance(
        value.start_time,
        datetime,
    )


def test_span_end_time():
    value = Span()

    assert value.end_time is None

    value.start()
    value.finish()

    assert value.end_time is not None
    assert isinstance(
        value.end_time,
        datetime,
    )


def test_span_duration():
    value = Span()

    assert value.duration == 0

    value.start()
    value.finish()

    assert value.duration >= 0


def test_span_elapsed():
    value = Span()

    assert value.elapsed == 0

    value.start()

    assert value.elapsed >= 0

    value.finish()

    assert value.elapsed >= 0


def test_span_timing_after_reset():
    value = Span()

    value.start()
    value.finish()

    assert value.start_time is not None
    assert value.end_time is not None

    value.reset()

    assert value.start_time is None
    assert value.end_time is None
    assert value.duration == 0
    assert value.elapsed == 0


# ==============================================================================
# Part 9. Attributes
# ==============================================================================


def test_span_attributes():
    value = Span()

    assert isinstance(
        value.attributes,
        dict,
    )

    assert value.attributes == {}


def test_set_attribute():
    value = Span()

    result = value.set_attribute(
        "service",
        "scios",
    )

    assert result is value
    assert value.get_attribute(
        "service",
    ) == "scios"


def test_get_attribute():
    value = Span(
        attributes={
            "service": "scios",
        },
    )

    assert value.get_attribute(
        "service",
    ) == "scios"

    assert value.get_attribute(
        "missing",
    ) is None


def test_has_attribute():
    value = Span()

    value.set_attribute(
        "service",
        "scios",
    )

    assert value.has_attribute(
        "service",
    ) is True

    assert value.has_attribute(
        "missing",
    ) is False


def test_remove_attribute():
    value = Span()

    value.set_attribute(
        "service",
        "scios",
    )

    result = value.remove_attribute(
        "service",
    )

    assert result is value
    assert value.has_attribute(
        "service",
    ) is False


def test_clear_attributes():
    value = Span(
        attributes={
            "service": "scios",
            "version": "1.0",
        },
    )

    result = value.clear_attributes()

    assert result is value
    assert value.attributes == {}


def test_attribute_mutation_rules():
    value = Span()

    value.set_attribute(
        "service",
        "scios",
    )

    assert value.get_attribute(
        "service",
    ) == "scios"

    value.freeze()

    with pytest.raises(
        SpanFrozenError,
    ):
        value.set_attribute(
            "service",
            "other",
        )

    value.unfreeze()

    value.set_attribute(
        "service",
        "other",
    )

    assert value.get_attribute(
        "service",
    ) == "other"


# ==============================================================================
# Part 10. Tags
# ==============================================================================


def test_span_tags():
    value = Span()

    assert isinstance(
        value.tags,
        dict,
    )

    assert value.tags == {}


def test_set_tag():
    value = Span()

    result = value.set_tag(
        "environment",
        "test",
    )

    assert result is value
    assert value.get_tag(
        "environment",
    ) == "test"


def test_get_tag():
    value = Span()

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


def test_has_tag():
    value = Span()

    value.set_tag(
        "environment",
        "test",
    )

    assert value.has_tag(
        "environment",
    ) is True

    assert value.has_tag(
        "missing",
    ) is False


def test_remove_tag():
    value = Span()

    value.set_tag(
        "environment",
        "test",
    )

    result = value.remove_tag(
        "environment",
    )

    assert result is value
    assert value.has_tag(
        "environment",
    ) is False


def test_clear_tags():
    value = Span()

    value.set_tag(
        "environment",
        "test",
    )

    value.set_tag(
        "version",
        "1.0",
    )

    result = value.clear_tags()

    assert result is value
    assert value.tags == {}


# ==============================================================================
# Part 11. Baggage
# ==============================================================================


def test_span_baggage():
    value = Span()

    assert isinstance(
        value.baggage,
        dict,
    )

    assert value.baggage == {}


def test_set_baggage():
    value = Span()

    result = value.set_baggage(
        "request-id",
        "req-001",
    )

    assert result is value
    assert value.get_baggage(
        "request-id",
    ) == "req-001"


def test_get_baggage():
    value = Span()

    value.set_baggage(
        "request-id",
        "req-001",
    )

    assert value.get_baggage(
        "request-id",
    ) == "req-001"

    assert value.get_baggage(
        "missing",
    ) is None


def test_has_baggage():
    value = Span()

    value.set_baggage(
        "request-id",
        "req-001",
    )

    assert value.has_baggage(
        "request-id",
    ) is True

    assert value.has_baggage(
        "missing",
    ) is False


def test_remove_baggage():
    value = Span()

    value.set_baggage(
        "request-id",
        "req-001",
    )

    result = value.remove_baggage(
        "request-id",
    )

    assert result is value
    assert value.has_baggage(
        "request-id",
    ) is False


def test_clear_baggage():
    value = Span()

    value.set_baggage(
        "request-id",
        "req-001",
    )

    value.set_baggage(
        "trace-state",
        "active",
    )

    result = value.clear_baggage()

    assert result is value
    assert value.baggage == {}


# ==============================================================================
# Part 12. Events
# ==============================================================================


def test_span_events():
    value = Span()

    assert isinstance(
        value.events,
        list,
    )

    assert value.events == []


def test_add_event():
    value = Span()

    result = value.add_event(
        "started",
        attributes={
            "source": "test",
        },
    )

    assert result is value
    assert len(
        value.events,
    ) == 1


def test_get_event():
    value = Span()

    value.add_event(
        "started",
    )

    event = value.get_event(
        "started",
    )

    assert event is not None


def test_clear_events():
    value = Span()

    value.add_event(
        "first",
    )

    value.add_event(
        "second",
    )

    result = value.clear_events()

    assert result is value
    assert value.events == []


def test_event_order():
    value = Span()

    value.add_event(
        "first",
    )

    value.add_event(
        "second",
    )

    value.add_event(
        "third",
    )

    events = value.events

    assert len(
        events,
    ) == 3

    names = [
        getattr(
            event,
            "name",
            None,
        )
        for event in events
    ]

    assert names == [
        "first",
        "second",
        "third",
    ]

# ==============================================================================
# Part 13. Links
# ==============================================================================


def test_span_links():
    value = Span()

    assert isinstance(
        value.links,
        list,
    )

    assert value.links == []


def test_add_link():
    value = Span()

    result = value.add_link(
        "trace-001",
    )

    assert result is value
    assert len(
        value.links,
    ) == 1


def test_clear_links():
    value = Span()

    value.add_link(
        "trace-001",
    )

    value.add_link(
        "trace-002",
    )

    result = value.clear_links()

    assert result is value
    assert value.links == []


def test_link_order():
    value = Span()

    value.add_link(
        "trace-001",
    )

    value.add_link(
        "trace-002",
    )

    value.add_link(
        "trace-003",
    )

    links = value.links

    assert len(
        links,
    ) == 3

    assert links[0] == "trace-001"
    assert links[1] == "trace-002"
    assert links[2] == "trace-003"


# ==============================================================================
# Part 14. Context
# ==============================================================================


def test_span_context():
    value = Span()

    assert value.context is None


def test_span_context_id():
    value = Span()

    assert value.context_id is None


def test_context_assignment():
    value = Span()

    context = {
        "trace_id": "trace-001",
        "span_id": "span-001",
    }

    value.context = context

    assert value.context == context
    assert value.context_id is not None


def test_context_propagation():
    parent = Span(
        name="parent",
        trace_id="trace-001",
    )

    context = {
        "trace_id": parent.trace_id,
        "span_id": parent.id,
    }

    parent.context = context

    child = Span(
        name="child",
        trace_id=parent.trace_id,
        parent_id=parent.id,
    )

    child.context = parent.context

    assert child.context == parent.context
    assert child.trace_id == parent.trace_id
    assert child.parent_id == parent.id


# ==============================================================================
# Part 15. Parent / Children
# ==============================================================================


def test_span_parent():
    value = Span()

    assert value.parent is None


def test_span_parent_id():
    value = Span(
        parent_id="parent-001",
    )

    assert value.parent_id == "parent-001"


def test_span_children():
    value = Span()

    assert isinstance(
        value.children,
        list,
    )

    assert value.children == []


def test_span_child_count():
    value = Span()

    assert value.child_count == 0


def test_add_child():
    parent = Span(
        name="parent",
        trace_id="trace-001",
    )

    child = Span(
        name="child",
        trace_id="trace-001",
        parent_id=parent.id,
    )

    result = parent.add_child(
        child,
    )

    assert result is parent
    assert child in parent.children
    assert parent.child_count == 1


def test_parent_child_relationship():
    parent = Span(
        name="parent",
        trace_id="trace-001",
    )

    child = Span(
        name="child",
        trace_id="trace-001",
        parent_id=parent.id,
    )

    parent.add_child(
        child,
    )

    assert child.parent is parent
    assert child.parent_id == parent.id
    assert child in parent.children
    assert parent.child_count == 1


# ==============================================================================
# Part 16. Error / Exception
# ==============================================================================


def test_span_exception():
    value = Span()

    assert value.exception is None


def test_attach_exception():
    value = Span()

    error = ValueError(
        "test error",
    )

    result = value.attach_exception(
        error,
    )

    assert result is value
    assert value.exception is error


def test_exception_state():
    value = Span()

    error = RuntimeError(
        "runtime failure",
    )

    value.attach_exception(
        error,
    )

    assert value.exception is error
    assert value.status != DEFAULT_SPAN_STATUS


def test_error_status():
    value = Span()

    error = ValueError(
        "invalid value",
    )

    value.attach_exception(
        error,
    )

    assert value.status in {
        "error",
        "ERROR",
        "Error",
    }


def test_error_transition():
    value = Span()

    assert value.status == DEFAULT_SPAN_STATUS

    value.attach_exception(
        ValueError(
            "failure",
        ),
    )

    assert value.exception is not None
    assert value.status in {
        "error",
        "ERROR",
        "Error",
    }


# ==============================================================================
# Part 17. Diagnostics
# ==============================================================================


def test_span_summary():
    value = Span(
        name="summary-span",
        trace_id="trace-001",
    )

    result = value.summary()

    assert isinstance(
        result,
        dict,
    )

    assert result["name"] == "summary-span"


def test_span_diagnostics():
    value = Span(
        name="diagnostic-span",
    )

    result = value.diagnostics()

    assert isinstance(
        result,
        dict,
    )


def test_span_validate():
    value = Span(
        name="valid-span",
    )

    result = value.validate()

    assert result is True


def test_span_health():
    value = Span(
        name="healthy-span",
    )

    result = value.health()

    assert result is True


# ==============================================================================
# Part 18. Serialization
# ==============================================================================


def test_span_to_dict():
    value = Span(
        name="serialized-span",
        trace_id="trace-001",
        parent_id="parent-001",
    )

    result = value.to_dict()

    assert isinstance(
        result,
        dict,
    )

    assert result["id"] == value.id
    assert result["trace_id"] == value.trace_id
    assert result["parent_id"] == value.parent_id
    assert result["name"] == value.name


def test_span_snapshot():
    value = Span(
        name="snapshot-span",
        trace_id="trace-001",
    )

    result = value.snapshot()

    assert isinstance(
        result,
        dict,
    )

    assert result["id"] == value.id
    assert result["trace_id"] == value.trace_id
    assert result["name"] == value.name


def test_span_clone():
    value = Span(
        name="clone-span",
        trace_id="trace-001",
    )

    result = value.clone()

    assert isinstance(
        result,
        Span,
    )

    assert result is not value
    assert result.id == value.id
    assert result.trace_id == value.trace_id
    assert result.name == value.name


def test_snapshot_preserves_identity():
    value = Span(
        name="identity-span",
        trace_id="trace-001",
        parent_id="parent-001",
    )

    snapshot = value.snapshot()

    assert snapshot["id"] == value.id
    assert snapshot["trace_id"] == value.trace_id
    assert snapshot["parent_id"] == value.parent_id
    assert snapshot["name"] == value.name


def test_clone_is_independent():
    value = Span(
        name="original-span",
        trace_id="trace-001",
        attributes={
            "key": "original",
        },
    )

    clone = value.clone()

    assert clone is not value

    clone.set_attribute(
        "key",
        "clone",
    )

    assert value.get_attribute(
        "key",
    ) == "original"

    assert clone.get_attribute(
        "key",
    ) == "clone"


# ==============================================================================
# Part 19. Python Protocols
# ==============================================================================


def test_span_repr():
    value = Span(
        name="repr-span",
    )

    result = repr(
        value,
    )

    assert isinstance(
        result,
        str,
    )

    assert "Span" in result
    assert "repr-span" in result


def test_span_str():
    value = Span(
        name="string-span",
    )

    result = str(
        value,
    )

    assert isinstance(
        result,
        str,
    )

    assert "string-span" in result


def test_span_bool():
    value = Span()

    assert bool(
        value,
    ) is True


def test_span_eq():
    value = Span(
        name="equal-span",
        trace_id="trace-001",
    )

    clone = value.clone()

    assert value == clone


def test_span_hash():
    value = Span()

    result = hash(
        value,
    )

    assert isinstance(
        result,
        int,
    )


def test_span_len():
    value = Span()

    result = len(
        value,
    )

    assert isinstance(
        result,
        int,
    )

    assert result >= 0


# ==============================================================================
# Part 20. Lifecycle Integration
# ==============================================================================


def test_start_finish_cycle():
    value = Span(
        name="cycle-span",
    )

    assert value.active is False

    value.start()

    assert value.active is True
    assert value.started is True

    value.finish()

    assert value.active is False
    assert value.finished is True


def test_start_cancel_cycle():
    value = Span(
        name="cancel-cycle",
    )

    value.start()

    assert value.active is True

    value.cancel()

    assert value.cancelled is True
    assert value.active is False


def test_start_close_cycle():
    value = Span(
        name="close-cycle",
    )

    value.start()

    assert value.active is True

    value.close()

    assert value.closed is True
    assert value.active is False


def test_restart_cycle():
    value = Span(
        name="restart-cycle",
    )

    value.start()
    value.finish()

    assert value.finished is True

    value.restart()

    assert value.started is True
    assert value.finished is False
    assert value.cancelled is False
    assert value.closed is False
    assert value.active is True


def test_freeze_unfreeze_cycle():
    value = Span(
        name="freeze-cycle",
    )

    assert value.frozen is False

    value.freeze()

    assert value.frozen is True

    value.unfreeze()

    assert value.frozen is False


# ==============================================================================
# Part 21. Final Integration
# ==============================================================================


def test_span_complete_workflow():
    value = Span(
        name="workflow-span",
        trace_id="trace-001",
        attributes={
            "service": "scios",
        },
    )

    value.start()

    value.set_tag(
        "environment",
        "test",
    )

    value.set_baggage(
        "request-id",
        "req-001",
    )

    value.add_event(
        "processing",
    )

    value.add_link(
        "trace-002",
    )

    assert value.started is True
    assert value.active is True
    assert value.get_attribute(
        "service",
    ) == "scios"
    assert value.get_tag(
        "environment",
    ) == "test"
    assert value.get_baggage(
        "request-id",
    ) == "req-001"
    assert len(
        value.events,
    ) == 1
    assert len(
        value.links,
    ) == 1

    value.finish()

    assert value.finished is True
    assert value.active is False


def test_span_parent_child_workflow():
    parent = Span(
        name="parent",
        trace_id="trace-001",
    )

    child = Span(
        name="child",
        trace_id=parent.trace_id,
        parent_id=parent.id,
    )

    parent.add_child(
        child,
    )

    parent.start()
    child.start()

    assert parent.active is True
    assert child.active is True
    assert child.parent is parent
    assert child.parent_id == parent.id
    assert parent.child_count == 1

    child.finish()
    parent.finish()

    assert child.finished is True
    assert parent.finished is True


def test_span_error_workflow():
    value = Span(
        name="error-workflow",
        trace_id="trace-001",
    )

    value.start()

    error = RuntimeError(
        "processing failure",
    )

    value.attach_exception(
        error,
    )

    assert value.exception is error
    assert value.status in {
        "error",
        "ERROR",
        "Error",
    }

    value.finish()

    assert value.finished is True
    assert value.active is False


def test_span_snapshot_restore():
    value = Span(
        name="snapshot-workflow",
        trace_id="trace-001",
        parent_id="parent-001",
        attributes={
            "service": "scios",
        },
    )

    value.start()

    snapshot = value.snapshot()

    restored = Span.from_snapshot(
        snapshot,
    )

    assert restored.id == value.id
    assert restored.trace_id == value.trace_id
    assert restored.parent_id == value.parent_id
    assert restored.name == value.name
    assert restored.get_attribute(
        "service",
    ) == "scios"


def test_span_clone_workflow():
    value = Span(
        name="clone-workflow",
        trace_id="trace-001",
        attributes={
            "service": "scios",
        },
    )

    value.start()

    clone = value.clone()

    assert clone is not value
    assert clone.id == value.id
    assert clone.trace_id == value.trace_id
    assert clone.name == value.name
    assert clone.get_attribute(
        "service",
    ) == "scios"

    clone.set_attribute(
        "service",
        "clone",
    )

    assert value.get_attribute(
        "service",
    ) == "scios"

    assert clone.get_attribute(
        "service",
    ) == "clone"
