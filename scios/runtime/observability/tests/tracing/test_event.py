"""
SciOS-NG Observability
Tracing Test - Event

Tests:

- Event creation
- Event lifecycle
- Event attributes
- Event timestamps
- Event serialization
- Event snapshot
- Event validation
- Event protocols

"""

from __future__ import annotations


import copy
import json
from datetime import datetime, timezone


import pytest


from scios.runtime.observability.tracing.event import (
    Event,
)



# ============================================================
# Fixtures
# ============================================================


@pytest.fixture
def event() -> Event:
    """
    Create basic event.
    """

    return Event(
        name="test.event"
    )



@pytest.fixture
def span_event() -> Event:
    """
    Create span related event.
    """

    return Event(

        name="span.started",

        timestamp=datetime.now(
            timezone.utc
        ),

        attributes={
            "component": "runtime",
        },
    )



# ============================================================
# Creation
# ============================================================


def test_event_creation(event):

    assert event is not None


    assert (
        event.name
        ==
        "test.event"
    )



def test_event_identifier(event):

    assert (
        event.event_id
        is not None
    )



def test_event_unique_id():

    first = Event(
        name="a"
    )


    second = Event(
        name="b"
    )


    assert (
        first.event_id
        !=
        second.event_id
    )



# ============================================================
# Timestamp
# ============================================================


def test_event_timestamp(event):

    assert isinstance(
        event.timestamp,
        datetime,
    )



def test_event_timestamp_timezone(event):

    assert (
        event.timestamp.tzinfo
        is not None
    )



# ============================================================
# Attributes
# ============================================================


def test_event_attributes(event):

    event.set_attribute(
        "service",
        "scios",
    )


    assert (
        event.attributes["service"]
        ==
        "scios"
    )



def test_event_multiple_attributes(event):

    event.set_attribute(
        "a",
        1,
    )


    event.set_attribute(
        "b",
        2,
    )


    assert len(
        event.attributes
    ) == 2



def test_event_remove_attribute(event):

    event.set_attribute(
        "temporary",
        True,
    )


    event.remove_attribute(
        "temporary"
    )


    assert (
        "temporary"
        not in event.attributes
    )



# ============================================================
# Payload
# ============================================================


def test_event_payload(event):

    event.set_payload(
        "status",
        "running",
    )


    assert (
        event.payload["status"]
        ==
        "running"
    )



def test_event_update_payload(event):

    event.update_payload(
        {
            "worker": "main",
            "cpu": 20,
        }
    )


    assert (
        event.payload["cpu"]
        ==
        20
    )



def test_event_clear_payload(event):

    event.set_payload(
        "key",
        "value",
    )


    event.clear_payload()


    assert (
        event.payload
        ==
        {}
    )



# ============================================================
# Tags
# ============================================================


def test_event_tags(event):

    event.set_tag(
        "level",
        "info",
    )


    assert (
        event.tags["level"]
        ==
        "info"
    )



def test_remove_tag(event):

    event.set_tag(
        "temp",
        "true",
    )


    event.remove_tag(
        "temp"
    )


    assert (
        "temp"
        not in event.tags
    )



# ============================================================
# Lifecycle
# ============================================================


def test_event_activate(event):

    event.activate()


    assert (
        event.active
        is True
    )



def test_event_complete(event):

    event.complete()


    assert (
        event.completed
        is True
    )



def test_event_fail(event):

    event.fail(
        "runtime error"
    )


    assert (
        event.failed
        is True
    )



def test_event_cancel(event):

    event.cancel()


    assert (
        event.cancelled
        is True
    )



# ============================================================
# Serialization
# ============================================================


def test_event_to_dict(event):

    data = event.to_dict()


    assert isinstance(
        data,
        dict,
    )


    assert (
        data["name"]
        ==
        "test.event"
    )



def test_event_to_json(event):

    result = event.to_json()


    assert isinstance(
        result,
        str,
    )


    parsed = json.loads(
        result
    )


    assert (
        parsed["name"]
        ==
        "test.event"
    )



def test_event_from_dict(event):

    data = event.to_dict()


    restored = Event.from_dict(
        data
    )


    assert (
        restored.name
        ==
        event.name
    )



def test_event_from_json(event):

    data = event.to_json()


    restored = Event.from_json(
        data
    )


    assert (
        restored.event_id
        ==
        event.event_id
    )



# ============================================================
# Snapshot
# ============================================================


def test_event_snapshot(event):

    snapshot = event.snapshot()


    assert isinstance(
        snapshot,
        dict,
    )


    assert (
        snapshot["name"]
        ==
        "test.event"
    )



def test_event_restore(event):

    snapshot = event.snapshot()


    restored = Event.restore(
        snapshot
    )


    assert (
        restored.name
        ==
        event.name
    )



# ============================================================
# Clone / Copy
# ============================================================


def test_event_clone(event):

    clone = event.clone()


    assert (
        clone.event_id
        ==
        event.event_id
    )



def test_event_copy(event):

    copied = event.copy()


    assert (
        copied.name
        ==
        event.name
    )



def test_python_copy(event):

    copied = copy.copy(
        event
    )


    assert (
        copied.name
        ==
        event.name
    )



def test_python_deepcopy(event):

    copied = copy.deepcopy(
        event
    )


    assert (
        copied.name
        ==
        event.name
    )



# ============================================================
# Validation
# ============================================================


def test_event_validate(event):

    assert (
        event.validate()
        is True
    )



def test_invalid_event_name():

    with pytest.raises(
        Exception
    ):

        Event(
            name=""
        )



# ============================================================
# Diagnostics
# ============================================================


def test_event_diagnostics(event):

    result = event.diagnostics()


    assert isinstance(
        result,
        dict,
    )



def test_event_summary(event):

    result = event.summary()


    assert isinstance(
        result,
        dict,
    )



# ============================================================
# Python Protocols
# ============================================================


def test_event_repr(event):

    result = repr(
        event
    )


    assert (
        "Event"
        in result
    )



def test_event_str(event):

    result = str(
        event
    )


    assert isinstance(
        result,
        str,
    )



def test_event_len(event):

    assert (
        len(event)
        >= 0
    )



def test_event_contains(event):

    event["key"] = "value"


    assert (
        "key"
        in event
    )



def test_event_getitem(event):

    event["mode"] = "test"


    assert (
        event["mode"]
        ==
        "test"
    )



def test_event_setitem(event):

    event["enabled"] = True


    assert (
        event["enabled"]
        is True
    )



# ============================================================
# Equality / Hash
# ============================================================


def test_event_equality():

    first = Event(
        name="same"
    )


    second = Event(
        name="same"
    )


    assert (
        first != second
    )



def test_event_hash(event):

    value = hash(
        event
    )


    assert isinstance(
        value,
        int,
    )