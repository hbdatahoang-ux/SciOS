"""
SciOS Runtime Dispatcher Tests
==============================

Python 3.11+
"""

# ==============================================================================
# Part 1. Imports
# ==============================================================================

from __future__ import annotations

import copy
import json

import pytest

from ..collector import RuntimeCollector
from ..aggregator import RuntimeAggregator
from ..dispatcher import (
    RuntimeDispatcher,
    DEFAULT_NAME,
    DEFAULT_ENABLED,
    DEFAULT_QUEUE_LIMIT,
    DEFAULT_BATCH_SIZE,
    DEFAULT_TIMEOUT,
    DEFAULT_RETRIES,
)


# ==============================================================================
# Part 2. Helpers
# ==============================================================================


def create_collector() -> RuntimeCollector:

    collector = RuntimeCollector()

    collector.add(
        "cpu",
        20.0,
    )

    collector.add(
        "memory",
        50.0,
    )

    return collector


def create_aggregator() -> RuntimeAggregator:

    collector = create_collector()

    aggregator = RuntimeAggregator(
        collector=collector,
    )

    aggregator.aggregate()

    return aggregator


def create_dispatcher() -> RuntimeDispatcher:

    collector = create_collector()

    aggregator = RuntimeAggregator(
        collector=collector,
    )

    dispatcher = RuntimeDispatcher(
        name="demo",
        collector=collector,
        aggregator=aggregator,
    )

    dispatcher.enqueue(
        {
            "cpu": 30.0,
        }
    )

    dispatcher.enqueue(
        {
            "memory": 60.0,
        }
    )

    dispatcher.dispatch()

    return dispatcher


# ==============================================================================
# Part 3. Constructor
# ==============================================================================


def test_default_constructor():

    dispatcher = RuntimeDispatcher()

    assert dispatcher.name == DEFAULT_NAME
    assert dispatcher.enabled is DEFAULT_ENABLED
    assert dispatcher.queue_limit == DEFAULT_QUEUE_LIMIT
    assert dispatcher.batch_size == DEFAULT_BATCH_SIZE
    assert dispatcher.timeout == DEFAULT_TIMEOUT
    assert dispatcher.retries == DEFAULT_RETRIES

    assert isinstance(
        dispatcher.collector,
        RuntimeCollector,
    )

    assert isinstance(
        dispatcher.aggregator,
        RuntimeAggregator,
    )


def test_custom_constructor():

    collector = create_collector()

    aggregator = RuntimeAggregator(
        collector=collector,
    )

    dispatcher = RuntimeDispatcher(
        name="runtime",
        enabled=False,
        collector=collector,
        aggregator=aggregator,
        queue_limit=64,
        batch_size=8,
        timeout=2.5,
        retries=5,
    )

    assert dispatcher.name == "runtime"
    assert dispatcher.enabled is False
    assert dispatcher.collector is collector
    assert dispatcher.aggregator is aggregator
    assert dispatcher.queue_limit == 64
    assert dispatcher.batch_size == 8
    assert dispatcher.timeout == 2.5
    assert dispatcher.retries == 5


def test_slots():

    dispatcher = RuntimeDispatcher()

    with pytest.raises(
        AttributeError,
    ):
        dispatcher.random_attribute = 1


# ==============================================================================
# Part 4. Properties
# ==============================================================================


def test_properties():

    dispatcher = create_dispatcher()

    assert dispatcher.name == "demo"
    assert dispatcher.enabled is True

    assert isinstance(
        dispatcher.collector,
        RuntimeCollector,
    )

    assert isinstance(
        dispatcher.aggregator,
        RuntimeAggregator,
    )

    assert isinstance(
        dispatcher.queue,
        list,
    )

    assert dispatcher.dispatched >= 0
    assert dispatcher.failed >= 0
    assert dispatcher.created_at > 0

    if dispatcher.dispatched:
        assert dispatcher.last_dispatch is not None

    assert dispatcher.queue_limit > 0
    assert dispatcher.batch_size > 0
    assert dispatcher.timeout >= 0
    assert dispatcher.retries >= 0


def test_name_property():

    dispatcher = RuntimeDispatcher()

    dispatcher.name = "dispatcher"

    assert dispatcher.name == "dispatcher"


def test_enabled_property():

    dispatcher = RuntimeDispatcher()

    dispatcher.enabled = False

    assert dispatcher.enabled is False


def test_collector_property():

    collector = create_collector()

    dispatcher = RuntimeDispatcher()

    dispatcher.collector = collector

    assert dispatcher.collector is collector


def test_aggregator_property():

    aggregator = create_aggregator()

    dispatcher = RuntimeDispatcher()

    dispatcher.aggregator = aggregator

    assert dispatcher.aggregator is aggregator


def test_queue_property():

    dispatcher = create_dispatcher()

    assert isinstance(
        dispatcher.queue,
        list,
    )


def test_dispatched_property():

    dispatcher = create_dispatcher()

    assert dispatcher.dispatched >= 0


def test_failed_property():

    dispatcher = create_dispatcher()

    assert dispatcher.failed >= 0


def test_created_at_property():

    assert create_dispatcher().created_at > 0


def test_last_dispatch_property():

    dispatcher = create_dispatcher()

    if dispatcher.dispatched:
        assert dispatcher.last_dispatch is not None


def test_queue_limit_property():

    dispatcher = RuntimeDispatcher()

    dispatcher.queue_limit = 512

    assert dispatcher.queue_limit == 512


def test_batch_size_property():

    dispatcher = RuntimeDispatcher()

    dispatcher.batch_size = 16

    assert dispatcher.batch_size == 16


def test_timeout_property():

    dispatcher = RuntimeDispatcher()

    dispatcher.timeout = 10.0

    assert dispatcher.timeout == 10.0


def test_retries_property():

    dispatcher = RuntimeDispatcher()

    dispatcher.retries = 8

    assert dispatcher.retries == 8


# ==============================================================================
# Part 5. Lifecycle
# ==============================================================================


def test_enable():

    dispatcher = RuntimeDispatcher(
        enabled=False,
    )

    dispatcher.enable()

    assert dispatcher.enabled is True


def test_disable():

    dispatcher = RuntimeDispatcher()

    dispatcher.disable()

    assert dispatcher.enabled is False


def test_clear():

    dispatcher = create_dispatcher()

    dispatcher.enqueue(
        {
            "disk": 1,
        }
    )

    dispatcher.clear()

    assert len(dispatcher.queue) == 0


def test_reset():

    dispatcher = create_dispatcher()

    dispatcher.reset()

    assert dispatcher.dispatched == 0
    assert dispatcher.failed == 0
    assert dispatcher.queue == []


def test_dispatch():

    dispatcher = RuntimeDispatcher()

    dispatcher.enqueue(
        {
            "cpu": 1,
        }
    )

    assert dispatcher.dispatch() is True

    if dispatcher.dispatched:
        assert dispatcher.last_dispatch is not None


def test_disabled_dispatch():

    dispatcher = RuntimeDispatcher(
        enabled=False,
    )

    dispatcher.enqueue(
        {
            "cpu": 1,
        }
    )

    assert dispatcher.dispatch() is False


def test_enable_disable():

    dispatcher = RuntimeDispatcher()

    dispatcher.disable()

    assert dispatcher.enabled is False

    dispatcher.enable()

    assert dispatcher.enabled is True

# ==============================================================================
# Part 6. Dispatch API
# ==============================================================================


def test_enqueue():

    dispatcher = RuntimeDispatcher()

    assert dispatcher.enqueue({"cpu": 10.0}) is True

    assert dispatcher.queue_size() == 1


def test_enqueue_many():

    dispatcher = RuntimeDispatcher()

    added = dispatcher.enqueue_many(
        [
            {"cpu": 1},
            {"memory": 2},
        ]
    )

    assert added == 2

    assert dispatcher.queue_size() == 2


def test_dequeue():

    dispatcher = RuntimeDispatcher()

    dispatcher.enqueue({"cpu": 1})

    item = dispatcher.dequeue()

    assert item == {"cpu": 1}

    assert dispatcher.queue_size() == 0


def test_peek():

    dispatcher = RuntimeDispatcher()

    dispatcher.enqueue({"cpu": 1})

    assert dispatcher.peek() == {"cpu": 1}

    assert dispatcher.queue_size() == 1


def test_dispatch_item():

    dispatcher = RuntimeDispatcher()

    assert dispatcher.dispatch_item({"cpu": 99}) is True

    assert dispatcher.dispatched == 1


def test_dispatch_batch():

    dispatcher = RuntimeDispatcher()

    dispatcher.enqueue_many(
        [
            {"cpu": 1},
            {"memory": 2},
        ]
    )

    processed = dispatcher.dispatch_batch()

    assert processed == 2

    assert dispatcher.queue_size() == 0


def test_flush():

    dispatcher = RuntimeDispatcher()

    dispatcher.enqueue_many(
        [
            {"cpu": 1},
            {"memory": 2},
            {"disk": 3},
        ]
    )

    total = dispatcher.flush()

    assert total == 3

    assert dispatcher.queue_size() == 0


def test_pending():

    dispatcher = RuntimeDispatcher()

    dispatcher.enqueue({"cpu": 1})

    pending = dispatcher.pending()

    assert isinstance(
        pending,
        list,
    )

    assert len(pending) == 1


def test_has_pending():

    dispatcher = RuntimeDispatcher()

    assert dispatcher.has_pending() is False

    dispatcher.enqueue({"cpu": 1})

    assert dispatcher.has_pending() is True


def test_queue_size():

    dispatcher = RuntimeDispatcher()

    dispatcher.enqueue({"cpu": 1})

    dispatcher.enqueue({"memory": 2})

    assert dispatcher.queue_size() == 2


# ==============================================================================
# Part 7. Statistics
# ==============================================================================


def test_record_success():

    dispatcher = RuntimeDispatcher()

    dispatcher.dispatch_item({"cpu": 1})

    assert dispatcher.dispatched == 1


def test_record_failure():

    dispatcher = RuntimeDispatcher()

    dispatcher._failed += 1

    assert dispatcher.failed == 1


def test_success_rate():

    dispatcher = RuntimeDispatcher()

    dispatcher.dispatch_item({"cpu": 1})

    assert dispatcher.success_rate() == pytest.approx(1.0)


def test_failure_rate():

    dispatcher = RuntimeDispatcher()

    dispatcher._failed = 1

    assert dispatcher.failure_rate() == pytest.approx(1.0)


def test_statistics():

    dispatcher = create_dispatcher()

    stats = dispatcher.statistics()

    assert isinstance(stats, dict)

    assert "dispatched" in stats


def test_reset_statistics():

    dispatcher = create_dispatcher()

    dispatcher.reset_statistics()

    assert dispatcher.dispatched == 0

    assert dispatcher.failed == 0


# ==============================================================================
# Part 8. Operations
# ==============================================================================


def test_clone():

    dispatcher = create_dispatcher()

    cloned = dispatcher.clone()

    assert cloned == dispatcher

    assert cloned is not dispatcher


def test_copy():

    dispatcher = create_dispatcher()

    copied = dispatcher.copy()

    assert copied == dispatcher

    assert copied is not dispatcher


def test_merge():

    left = create_dispatcher()

    right = create_dispatcher()

    left.merge(right)

    assert left.dispatched >= right.dispatched


def test_update():

    dispatcher = create_dispatcher()

    dispatcher.update(
        {
            "name": "updated",
        }
    )

    assert dispatcher.name == "updated"


def test_snapshot():

    dispatcher = create_dispatcher()

    snapshot = dispatcher.snapshot()

    assert isinstance(snapshot, dict)


def test_restore():

    dispatcher = create_dispatcher()

    snapshot = dispatcher.snapshot()

    restored = RuntimeDispatcher()

    restored.restore(snapshot)

    assert restored == dispatcher


# ==============================================================================
# Part 9. Validation
# ==============================================================================


def test_validate():

    assert create_dispatcher().validate() is True


def test_normalize():

    dispatcher = RuntimeDispatcher()

    assert dispatcher.normalize(5.0) == 5.0

    assert dispatcher.normalize(float("nan")) == 0.0

    assert dispatcher.normalize(float("inf")) == 0.0


def test_validate_empty():

    dispatcher = RuntimeDispatcher()

    assert dispatcher.validate() is True


# ==============================================================================
# Part 10. Serialization
# ==============================================================================


def test_to_dict():

    value = create_dispatcher().to_dict()

    assert isinstance(value, dict)


def test_from_dict():

    dispatcher = create_dispatcher()

    restored = RuntimeDispatcher.from_dict(
        dispatcher.to_dict(),
    )

    assert restored == dispatcher


def test_to_tuple():

    value = create_dispatcher().to_tuple()

    assert isinstance(value, tuple)


def test_from_tuple():

    dispatcher = create_dispatcher()

    restored = RuntimeDispatcher.from_tuple(
        dispatcher.to_tuple(),
    )

    assert restored == dispatcher


def test_to_json():

    payload = create_dispatcher().to_json()

    assert isinstance(payload, str)

    json.loads(payload)


def test_from_json():

    dispatcher = create_dispatcher()

    restored = RuntimeDispatcher.from_json(
        dispatcher.to_json(),
    )

    assert restored == dispatcher


# ==============================================================================
# Part 11. Diagnostics
# ==============================================================================


def test_summary():

    summary = create_dispatcher().summary()

    assert isinstance(summary, dict)


def test_diagnostics():

    diagnostics = create_dispatcher().diagnostics()

    assert isinstance(diagnostics, dict)


def test_report():

    report = create_dispatcher().report()

    assert isinstance(report, str)


def test_status():

    status = create_dispatcher().status()

    assert isinstance(status, dict)


# ==============================================================================
# Part 12. Protocols
# ==============================================================================


def test_len():

    dispatcher = create_dispatcher()

    assert len(dispatcher) == dispatcher.queue_size()


def test_contains():

    dispatcher = RuntimeDispatcher()

    item = {"cpu": 1}

    dispatcher.enqueue(item)

    assert item in dispatcher


def test_iter():

    dispatcher = create_dispatcher()

    assert list(iter(dispatcher)) == dispatcher.queue


def test_hash():

    assert isinstance(
        hash(create_dispatcher()),
        int,
    )


def test_eq():

    assert create_dispatcher() == create_dispatcher()


def test_repr():

    assert isinstance(
        repr(create_dispatcher()),
        str,
    )


def test_str():

    assert isinstance(
        str(create_dispatcher()),
        str,
    )


def test_bool():

    assert bool(create_dispatcher()) is True

    assert bool(RuntimeDispatcher(enabled=False)) is False    