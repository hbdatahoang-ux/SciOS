"""
Tests for MetricEntry.
"""

from __future__ import annotations

import inspect
import time

import scios.runtime.observability.metrics.core.metrics.registry.entry as entry

assert "MetricEntry" in entry.__all__

from scios.runtime.observability.metrics.core.metrics.registry.entry import (
    MetricEntry,
)
from scios.runtime.observability.metrics.core.metrics.registry.key import (
    MetricKey,
)


# ==============================================================================
# Part 1. Constructor
# ==============================================================================


def test_default_constructor():

    e = MetricEntry()

    assert isinstance(e.key, MetricKey)
    assert e.metric is None
    assert e.value is None
    assert isinstance(e.timestamp, float)


def test_custom_constructor():

    key = MetricKey(
        "cpu",
        "system",
        {"host": "node1"},
    )

    e = MetricEntry(
        key=key,
        metric="gauge",
        value=42,
    )

    assert e.key == key
    assert e.metric == "gauge"
    assert e.value == 42


def test_slots():

    assert hasattr(MetricEntry, "__slots__")


def test_annotations():

    annotations = MetricEntry.__annotations__

    assert "key" in annotations
    assert "metric" in annotations
    assert "value" in annotations
    assert "timestamp" in annotations


def test_signature():

    sig = inspect.signature(MetricEntry)

    assert "key" in sig.parameters
    assert "metric" in sig.parameters
    assert "value" in sig.parameters
    assert "timestamp" in sig.parameters


# ==============================================================================
# Part 2. Properties
# ==============================================================================


def test_key_property():

    key = MetricKey("cpu", "system")

    e = MetricEntry(key=key)

    assert e.key is key


def test_metric_property():

    e = MetricEntry(metric="counter")

    assert e.metric == "counter"


def test_value_property():

    e = MetricEntry(value=123)

    assert e.value == 123


def test_timestamp_property():

    e = MetricEntry()

    assert isinstance(e.timestamp, float)


def test_state_property():

    e = MetricEntry()

    state = e.state

    assert isinstance(state, dict)
    assert state["key"] == e.key
    assert state["metric"] == e.metric
    assert state["value"] == e.value


# ==============================================================================
# Part 3. Operations
# ==============================================================================


def test_update():

    e = MetricEntry()

    ts = e.timestamp

    e.update(
        metric="counter",
        value=10,
    )

    assert e.metric == "counter"
    assert e.value == 10
    assert e.timestamp >= ts


def test_replace():

    old = MetricEntry(
        key=MetricKey("cpu", "system"),
        metric="counter",
        value=1,
    )

    new = MetricEntry(
        key=MetricKey("memory", "runtime"),
        metric="gauge",
        value=5,
    )

    old.replace(new)

    assert old.key == new.key
    assert old.metric == "gauge"
    assert old.value == 5


def test_reset():

    e = MetricEntry(
        key=MetricKey("cpu", "system"),
        metric="counter",
        value=5,
    )

    e.reset()

    assert isinstance(e.key, MetricKey)
    assert e.metric is None
    assert e.value is None


def test_touch():

    e = MetricEntry()

    before = e.timestamp

    time.sleep(0.01)

    e.touch()

    assert e.timestamp > before


# ==============================================================================
# Part 4. Serialization
# ==============================================================================


def test_to_dict():

    e = MetricEntry(
        key=MetricKey("cpu", "system"),
        metric="counter",
        value=10,
    )

    data = e.to_dict()

    assert data["metric"] == "counter"
    assert data["value"] == 10
    assert "key" in data


def test_from_dict():

    data = {
        "key": {
            "name": "cpu",
            "namespace": "system",
            "labels": {},
        },
        "metric": "counter",
        "value": 7,
    }

    e = MetricEntry.from_dict(data)

    assert e.key.name == "cpu"
    assert e.metric == "counter"
    assert e.value == 7


def test_to_tuple():

    e = MetricEntry(
        key=MetricKey("cpu", "system"),
        metric="counter",
        value=3,
    )

    value = e.to_tuple()

    assert isinstance(value, tuple)


def test_from_tuple():

    original = MetricEntry(
        key=MetricKey("cpu", "system"),
        metric="counter",
        value=99,
    )

    restored = MetricEntry.from_tuple(
        original.to_tuple(),
    )

    assert restored == original


def test_snapshot():

    e = MetricEntry(
        key=MetricKey("cpu", "system"),
    )

    assert e.snapshot() == e.to_dict()


def test_restore():

    e = MetricEntry()

    e.restore(
        {
            "key": {
                "name": "memory",
                "namespace": "runtime",
                "labels": {},
            },
            "metric": "gauge",
            "value": 55,
        }
    )

    assert e.key.name == "memory"
    assert e.metric == "gauge"
    assert e.value == 55


# ==============================================================================
# Part 5. Validation
# ==============================================================================


def test_validate_key():

    assert MetricEntry.validate_key(
        MetricKey("cpu", "system")
    )

    assert not MetricEntry.validate_key(None)


def test_validate_metric():

    assert MetricEntry.validate_metric("counter")

    assert not MetricEntry.validate_metric(123)


def test_validate_value():

    assert MetricEntry.validate_value(1)
    assert MetricEntry.validate_value(1.5)
    assert MetricEntry.validate_value("ok")


def test_validate_entry():

    e = MetricEntry(
        key=MetricKey("cpu", "system"),
    )

    assert MetricEntry.validate_entry(e)


def test_validate():

    e = MetricEntry(
        key=MetricKey("cpu", "system"),
    )

    assert e.validate()

# ==============================================================================
# Part 6. Utilities
# ==============================================================================


def test_clone():

    entry = MetricEntry(
        key=MetricKey("cpu", "system"),
        metric="counter",
        value=100,
    )

    cloned = entry.clone()

    assert cloned == entry
    assert cloned is not entry
    assert cloned.key is not entry.key


def test_copy():

    entry = MetricEntry(
        key=MetricKey("cpu", "system"),
        metric="counter",
        value=100,
    )

    copied = entry.copy()

    assert copied == entry
    assert copied is not entry
    assert copied.key is not entry.key


def test_merge():

    entry = MetricEntry(
        key=MetricKey("cpu", "system"),
        metric="counter",
        value=10,
    )

    merged = entry.merge(
        metric="gauge",
        value=20,
    )

    assert merged is not entry
    assert merged.metric == "gauge"
    assert merged.value == 20
    assert merged.key == entry.key


def test_clear():

    entry = MetricEntry(
        key=MetricKey("cpu", "system"),
        metric="counter",
        value=5,
    )

    entry.clear()

    assert isinstance(entry.key, MetricKey)
    assert entry.metric is None
    assert entry.value is None


def test_normalize():

    entry = MetricEntry(
        key=MetricKey(" CPU ", " SYSTEM "),
        metric=" Counter ",
        value=1,
    )

    entry.normalize()

    assert entry.key.name == "cpu"
    assert entry.key.namespace == "system"

    if isinstance(entry.metric, str):
        assert entry.metric == "counter"


# ==============================================================================
# Part 7. Protocols
# ==============================================================================


def test_hash():

    entry = MetricEntry(
        key=MetricKey("cpu", "system"),
    )

    assert isinstance(hash(entry), int)


def test_eq():

    a = MetricEntry(
        key=MetricKey("cpu", "system"),
        metric="counter",
        value=1,
    )

    b = MetricEntry(
        key=MetricKey("cpu", "system"),
        metric="counter",
        value=1,
    )

    assert a == b


def test_lt():

    a = MetricEntry(
        key=MetricKey("a", "system"),
    )

    b = MetricEntry(
        key=MetricKey("b", "system"),
    )

    assert a < b


def test_repr():

    entry = MetricEntry(
        key=MetricKey("cpu", "system"),
    )

    text = repr(entry)

    assert "MetricEntry" in text


def test_str():

    entry = MetricEntry(
        key=MetricKey("cpu", "system"),
    )

    text = str(entry)

    assert isinstance(text, str)
    assert "cpu" in text


def test_bool():

    assert bool(
        MetricEntry(
            key=MetricKey("cpu", "system"),
        )
    )

    assert not bool(MetricEntry())


# ==============================================================================
# Part 8. Diagnostics
# ==============================================================================


def test_summary():

    entry = MetricEntry(
        key=MetricKey("cpu", "system"),
        metric="counter",
        value=5,
    )

    result = entry.summary()

    assert isinstance(result, dict)
    assert "metric" in result
    assert "value" in result


def test_diagnostics():

    entry = MetricEntry(
        key=MetricKey("cpu", "system"),
    )

    result = entry.diagnostics()

    assert isinstance(result, dict)


def test_entry_report():

    entry = MetricEntry(
        key=MetricKey("cpu", "system"),
    )

    report = entry.entry_report()

    assert isinstance(report, dict)
    assert "summary" in report
    assert "diagnostics" in report


def test_overall_status():

    entry = MetricEntry(
        key=MetricKey("cpu", "system"),
    )

    assert isinstance(
        entry.overall_status(),
        bool,
    )


# ==============================================================================
# Part 9. Public API
# ==============================================================================


def test_public_api():

    expected = {
        "MetricEntry",
    }

    for symbol in expected:
        assert symbol in entry.__all__    