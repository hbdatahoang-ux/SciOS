"""
Tests for SciOS shared EventBus contracts.
"""

from __future__ import annotations

import threading

import pytest

from scios.shared.event_bus import EventBus


# ============================================================================
# Construction
# ============================================================================


def test_event_bus_initializes_empty():
    bus = EventBus()

    assert len(bus) == 0
    assert bus.subscribers("event") == ()


def test_event_bus_repr_empty():
    bus = EventBus()

    result = repr(bus)

    assert result == "EventBus(events=0, subscribers=0)"


# ============================================================================
# Subscribe
# ============================================================================


def test_subscribe_registers_handler():
    bus = EventBus()

    def handler(**payload):
        pass

    bus.subscribe("event", handler)

    assert bus.subscribers("event") == (handler,)
    assert len(bus) == 1


def test_subscribe_same_handler_twice_is_idempotent():
    bus = EventBus()

    def handler(**payload):
        pass

    bus.subscribe("event", handler)
    bus.subscribe("event", handler)

    assert bus.subscribers("event") == (handler,)
    assert len(bus) == 1


def test_same_handler_can_subscribe_to_different_events():
    bus = EventBus()

    def handler(**payload):
        pass

    bus.subscribe("event.a", handler)
    bus.subscribe("event.b", handler)

    assert bus.subscribers("event.a") == (handler,)
    assert bus.subscribers("event.b") == (handler,)
    assert len(bus) == 2


def test_different_handlers_are_preserved():
    bus = EventBus()

    calls = []

    def first(**payload):
        calls.append("first")

    def second(**payload):
        calls.append("second")

    bus.subscribe("event", first)
    bus.subscribe("event", second)

    assert bus.subscribers("event") == (first, second)
    assert len(bus) == 2


def test_subscription_order_is_preserved():
    bus = EventBus()

    calls = []

    def first(**payload):
        calls.append("first")

    def second(**payload):
        calls.append("second")

    def third(**payload):
        calls.append("third")

    bus.subscribe("event", first)
    bus.subscribe("event", second)
    bus.subscribe("event", third)

    bus.publish("event")

    assert calls == ["first", "second", "third"]


# ============================================================================
# Unsubscribe
# ============================================================================


def test_unsubscribe_removes_handler():
    bus = EventBus()

    def handler(**payload):
        pass

    bus.subscribe("event", handler)

    assert len(bus) == 1

    bus.unsubscribe("event", handler)

    assert bus.subscribers("event") == ()
    assert len(bus) == 0


def test_unsubscribe_nonexistent_handler_is_safe():
    bus = EventBus()

    def handler(**payload):
        pass

    bus.unsubscribe("event", handler)

    assert len(bus) == 0


def test_unsubscribe_only_removes_target_handler():
    bus = EventBus()

    def first(**payload):
        pass

    def second(**payload):
        pass

    bus.subscribe("event", first)
    bus.subscribe("event", second)

    bus.unsubscribe("event", first)

    assert bus.subscribers("event") == (second,)
    assert len(bus) == 1


def test_unsubscribe_from_one_event_does_not_affect_another():
    bus = EventBus()

    def handler(**payload):
        pass

    bus.subscribe("event.a", handler)
    bus.subscribe("event.b", handler)

    bus.unsubscribe("event.a", handler)

    assert bus.subscribers("event.a") == ()
    assert bus.subscribers("event.b") == (handler,)
    assert len(bus) == 1


# ============================================================================
# Subscribers snapshot
# ============================================================================


def test_subscribers_returns_tuple():
    bus = EventBus()

    def handler(**payload):
        pass

    bus.subscribe("event", handler)

    result = bus.subscribers("event")

    assert isinstance(result, tuple)


def test_subscribers_returns_snapshot():
    bus = EventBus()

    def first(**payload):
        pass

    def second(**payload):
        pass

    bus.subscribe("event", first)

    snapshot = bus.subscribers("event")

    bus.subscribe("event", second)

    assert snapshot == (first,)
    assert bus.subscribers("event") == (first, second)


# ============================================================================
# Publish
# ============================================================================


def test_publish_calls_subscriber():
    bus = EventBus()

    calls = []

    def handler(**payload):
        calls.append(payload)

    bus.subscribe("event", handler)

    bus.publish("event")

    assert calls == [{}]


def test_publish_passes_keyword_payload():
    bus = EventBus()

    received = []

    def handler(**payload):
        received.append(payload)

    bus.subscribe("event", handler)

    bus.publish(
        "event",
        task_id="task-1",
        status="completed",
        value=42,
    )

    assert received == [
        {
            "task_id": "task-1",
            "status": "completed",
            "value": 42,
        }
    ]


def test_publish_calls_all_subscribers():
    bus = EventBus()

    calls = []

    def first(**payload):
        calls.append(("first", payload))

    def second(**payload):
        calls.append(("second", payload))

    bus.subscribe("event", first)
    bus.subscribe("event", second)

    bus.publish("event", value=42)

    assert calls == [
        ("first", {"value": 42}),
        ("second", {"value": 42}),
    ]


def test_publish_event_isolated():
    bus = EventBus()

    calls = []

    def first(**payload):
        calls.append("first")

    def second(**payload):
        calls.append("second")

    bus.subscribe("event.a", first)
    bus.subscribe("event.b", second)

    bus.publish("event.a")

    assert calls == ["first"]


def test_publish_without_subscribers_is_safe():
    bus = EventBus()

    bus.publish("event", value=42)

    assert len(bus) == 0


def test_publish_does_not_return_handler_results():
    bus = EventBus()

    def handler(**payload):
        return "result"

    bus.subscribe("event", handler)

    assert bus.publish("event") is None


# ============================================================================
# Publish snapshot semantics
# ============================================================================


def test_unsubscribe_during_publish_does_not_corrupt_dispatch():
    bus = EventBus()

    calls = []

    def first(**payload):
        calls.append("first")
        bus.unsubscribe("event", second)

    def second(**payload):
        calls.append("second")

    bus.subscribe("event", first)
    bus.subscribe("event", second)

    bus.publish("event")

    assert calls == ["first", "second"]
    assert bus.subscribers("event") == (first,)


def test_subscribe_during_publish_does_not_receive_current_event():
    bus = EventBus()

    calls = []

    def first(**payload):
        calls.append("first")
        bus.subscribe("event", third)

    def second(**payload):
        calls.append("second")

    def third(**payload):
        calls.append("third")

    bus.subscribe("event", first)
    bus.subscribe("event", second)

    bus.publish("event")

    assert calls == ["first", "second"]
    assert bus.subscribers("event") == (first, second, third)


def test_new_subscriber_receives_next_event():
    bus = EventBus()

    calls = []

    def first(**payload):
        calls.append("first")
        bus.subscribe("event", second)

    def second(**payload):
        calls.append("second")

    bus.subscribe("event", first)

    bus.publish("event")
    assert calls == ["first"]

    bus.publish("event")
    assert calls == ["first", "first", "second"]


# ============================================================================
# Exception behavior
# ============================================================================


def test_handler_exception_propagates():
    bus = EventBus()

    def handler(**payload):
        raise ValueError("handler failed")

    bus.subscribe("event", handler)

    with pytest.raises(ValueError, match="handler failed"):
        bus.publish("event")


def test_handler_exception_stops_subsequent_handlers():
    bus = EventBus()

    calls = []

    def first(**payload):
        calls.append("first")
        raise ValueError("failure")

    def second(**payload):
        calls.append("second")

    bus.subscribe("event", first)
    bus.subscribe("event", second)

    with pytest.raises(ValueError):
        bus.publish("event")

    assert calls == ["first"]


# ============================================================================
# Clear
# ============================================================================


def test_clear_removes_all_subscriptions():
    bus = EventBus()

    def first(**payload):
        pass

    def second(**payload):
        pass

    bus.subscribe("event.a", first)
    bus.subscribe("event.b", second)

    assert len(bus) == 2

    bus.clear()

    assert len(bus) == 0
    assert bus.subscribers("event.a") == ()
    assert bus.subscribers("event.b") == ()


def test_clear_allows_future_subscriptions():
    bus = EventBus()

    calls = []

    def first(**payload):
        calls.append("first")

    def second(**payload):
        calls.append("second")

    bus.subscribe("event", first)
    bus.clear()

    bus.subscribe("event", second)
    bus.publish("event")

    assert calls == ["second"]


# ============================================================================
# Length
# ============================================================================


def test_len_counts_total_subscriptions():
    bus = EventBus()

    def first(**payload):
        pass

    def second(**payload):
        pass

    bus.subscribe("event.a", first)
    bus.subscribe("event.a", second)
    bus.subscribe("event.b", first)

    assert len(bus) == 3


def test_len_decreases_after_unsubscribe():
    bus = EventBus()

    def first(**payload):
        pass

    def second(**payload):
        pass

    bus.subscribe("event", first)
    bus.subscribe("event", second)

    bus.unsubscribe("event", first)

    assert len(bus) == 1


# ============================================================================
# Representation
# ============================================================================


def test_repr_reports_event_and_subscriber_counts():
    bus = EventBus()

    def first(**payload):
        pass

    def second(**payload):
        pass

    bus.subscribe("event.a", first)
    bus.subscribe("event.a", second)
    bus.subscribe("event.b", first)

    assert repr(bus) == "EventBus(events=2, subscribers=3)"


# ============================================================================
# Thread safety
# ============================================================================


def test_concurrent_subscription_is_safe():
    bus = EventBus()

    barrier = threading.Barrier(20)

    handlers = []

    def make_handler(index):
        def handler(**payload):
            pass

        handler.__name__ = f"handler_{index}"
        return handler

    handlers.extend(make_handler(i) for i in range(20))

    def worker(handler):
        barrier.wait()
        bus.subscribe("event", handler)

    threads = [
        threading.Thread(
            target=worker,
            args=(handler,),
        )
        for handler in handlers
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    assert len(bus) == 20
    assert len(bus.subscribers("event")) == 20


def test_concurrent_duplicate_subscription_is_safe():
    bus = EventBus()

    barrier = threading.Barrier(20)

    def handler(**payload):
        pass

    def worker():
        barrier.wait()
        bus.subscribe("event", handler)

    threads = [
        threading.Thread(target=worker)
        for _ in range(20)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    assert len(bus) == 1
    assert bus.subscribers("event") == (handler,)


def test_concurrent_unsubscribe_is_safe():
    bus = EventBus()

    def handler(**payload):
        pass

    bus.subscribe("event", handler)

    barrier = threading.Barrier(20)

    def worker():
        barrier.wait()
        bus.unsubscribe("event", handler)

    threads = [
        threading.Thread(target=worker)
        for _ in range(20)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    assert len(bus) == 0


# ============================================================================
# Public contract
# ============================================================================


def test_event_bus_public_methods_exist():
    expected = (
        "subscribe",
        "unsubscribe",
        "publish",
        "subscribers",
        "clear",
    )

    for name in expected:
        assert hasattr(EventBus, name)
        assert callable(getattr(EventBus, name))
