# ==============================================================================
# test_counter.py
# ==============================================================================

import pytest

from scios.runtime.observability.metrics.core.counter import (
    Counter,
    CounterValidationError,
    DEFAULT_COUNTER_VALUE,
    DEFAULT_COUNTER_TYPE,
    DEFAULT_COUNTER_UNIT,
)

from scios.runtime.observability.metrics.core.metric import (
    MetricType,
    MetricUnit,
    MetricValidationError,
)


# ==============================================================================
# Part 1. Construction
# ==============================================================================


def test_default_counter():
    counter = Counter()

    assert isinstance(counter, Counter)
    assert counter.name == "metric"
    assert counter.value == 0
    assert counter.metric_type is MetricType.COUNTER
    assert counter.unit is MetricUnit.NONE


def test_custom_counter():
    counter = Counter(
        name="requests_total",
        value=42,
    )

    assert counter.name == "requests_total"
    assert counter.value == 42
    assert counter.metric_type is MetricType.COUNTER
    assert counter.unit is MetricUnit.NONE


def test_default_value():
    counter = Counter()

    assert counter.value == DEFAULT_COUNTER_VALUE
    assert counter.value == 0


def test_default_type():
    counter = Counter()

    assert counter.metric_type is DEFAULT_COUNTER_TYPE
    assert counter.metric_type is MetricType.COUNTER
    assert counter.is_counter is True


def test_default_unit():
    counter = Counter()

    assert counter.unit is DEFAULT_COUNTER_UNIT
    assert counter.unit is MetricUnit.NONE


def test_default_state():
    counter = Counter()

    assert counter.state is not None
    assert counter.state.enabled is True
    assert counter.state.active is True


# ==============================================================================
# Part 2. Validation
# ==============================================================================


def test_invalid_name():
    with pytest.raises(MetricValidationError):
        Counter(name=None)


def test_invalid_value():
    with pytest.raises(MetricValidationError):
        Counter(value="10")


def test_negative_value():
    with pytest.raises(CounterValidationError):
        Counter(value=-1)


def test_invalid_type():
    with pytest.raises(CounterValidationError):
        Counter(
            metric_type=MetricType.GAUGE,
        )


def test_validate():
    counter = Counter(
        name="requests_total",
        value=10,
    )

    result = counter.validate()

    assert result is True


# ==============================================================================
# Part 3. Properties
# ==============================================================================


def test_name():
    counter = Counter(
        name="requests_total",
    )

    assert counter.name == "requests_total"


def test_value():
    counter = Counter(
        value=10,
    )

    assert counter.value == 10

    counter.value = 20

    assert counter.value == 20


def test_metric_type():
    counter = Counter()

    assert counter.metric_type is MetricType.COUNTER


def test_unit():
    counter = Counter()

    assert counter.unit is MetricUnit.NONE


def test_is_counter():
    counter = Counter()

    assert counter.is_counter is True


# ==============================================================================
# Part 4. Increment
# ==============================================================================


def test_increment():
    counter = Counter(
        value=10,
    )

    result = counter.increment(5)

    assert result == 15
    assert counter.value == 15


def test_increment_default():
    counter = Counter(
        value=10,
    )

    result = counter.increment()

    assert result == 11
    assert counter.value == 11


def test_increment_multiple():
    counter = Counter()

    assert counter.increment(10) == 10
    assert counter.increment(20) == 30
    assert counter.increment(5) == 35

    assert counter.value == 35


def test_increment_rejects_negative():
    counter = Counter()

    with pytest.raises(CounterValidationError):
        counter.increment(-1)

    assert counter.value == 0


# ==============================================================================
# Part 5. Decrement
# ==============================================================================


def test_decrement():
    counter = Counter(
        value=10,
    )

    result = counter.decrement(3)

    assert result == 7
    assert counter.value == 7


def test_decrement_multiple():
    counter = Counter(
        value=20,
    )

    assert counter.decrement(5) == 15
    assert counter.decrement(3) == 12
    assert counter.decrement(2) == 10

    assert counter.value == 10


def test_decrement_below_zero():
    counter = Counter(
        value=5,
    )

    with pytest.raises(CounterValidationError):
        counter.decrement(6)

    assert counter.value == 5


def test_decrement_rejects_negative():
    counter = Counter(
        value=5,
    )

    with pytest.raises(CounterValidationError):
        counter.decrement(-1)

    assert counter.value == 5

# ==============================================================================
# Part 6. Reset
# ==============================================================================


def test_reset():
    counter = Counter(
        value=100,
    )

    result = counter.reset()

    assert result == 0
    assert counter.value == 0


def test_reset_preserves_metadata():
    counter = Counter(
        value=100,
    )

    counter.labels.add("host", "node01")
    counter.attributes.add("region", "test")
    counter.annotations.add("note", "counter")
    counter.tags.add("production")

    counter.reset()

    assert counter.value == 0
    assert counter.labels.get("host") == "node01"
    assert counter.attributes.get("region") == "test"
    assert counter.annotations.get("note") == "counter"
    assert "production" in counter.tags


# ==============================================================================
# Part 7. Lifecycle
# ==============================================================================


def test_enable():
    counter = Counter()

    counter.disable()
    assert counter.state.enabled is False

    counter.enable()

    assert counter.state.enabled is True


def test_disable():
    counter = Counter()

    counter.disable()

    assert counter.state.enabled is False


def test_activate():
    counter = Counter()

    counter.deactivate()
    assert counter.state.active is False

    counter.activate()

    assert counter.state.active is True


def test_deactivate():
    counter = Counter()

    counter.deactivate()

    assert counter.state.active is False


def test_archive():
    counter = Counter()

    counter.archive()

    assert counter.state.archived is True


# ==============================================================================
# Part 8. Restore
# ==============================================================================


def test_restore():
    counter = Counter(
        name="requests_total",
        value=10,
    )

    snapshot = counter.snapshot()

    counter.value = 50

    counter.restore(snapshot)

    assert counter.value == 10
    assert counter.name == "requests_total"
    assert counter.metric_type is MetricType.COUNTER


def test_snapshot_restore():
    counter = Counter(
        name="requests_total",
        value=25,
    )

    snapshot = counter.snapshot()

    counter.increment(10)

    assert counter.value == 35

    counter.restore(snapshot)

    assert counter.value == 25


def test_restore_rejects_invalid_counter():
    counter = Counter(
        name="requests_total",
        value=10,
    )

    snapshot = counter.snapshot()

    snapshot["metric_type"] = MetricType.GAUGE

    with pytest.raises(
        CounterValidationError,
    ):
        counter.restore(snapshot)


# ==============================================================================
# Part 9. Metadata
# ==============================================================================


def test_labels():
    counter = Counter()

    counter.labels.add(
        "host",
        "node01",
    )

    assert counter.labels.get("host") == "node01"


def test_attributes():
    counter = Counter()

    counter.attributes.add(
        "region",
        "test",
    )

    assert counter.attributes.get("region") == "test"


def test_annotations():
    counter = Counter()

    counter.annotations.add(
        "description",
        "request counter",
    )

    assert counter.annotations.get("description") == "request counter"


def test_tags():
    counter = Counter()

    counter.tags.add("production")

    assert "production" in counter.tags


def test_hooks():
    counter = Counter()

    assert counter.hooks is not None


# ==============================================================================
# Part 10. Serialization
# ==============================================================================


def test_to_dict():
    counter = Counter(
        name="requests_total",
        value=42,
    )

    data = counter.to_dict()

    assert isinstance(data, dict)
    assert data["name"] == "requests_total"
    assert data["value"] == 42
    assert data["metric_type"] == MetricType.COUNTER.value


def test_from_dict():
    data = {
        "name": "requests_total",
        "value": 42,
        "metric_type": MetricType.COUNTER.value,
        "unit": MetricUnit.NONE.value,
    }

    counter = Counter.from_dict(data)

    assert isinstance(counter, Counter)
    assert counter.name == "requests_total"
    assert counter.value == 42
    assert counter.metric_type is MetricType.COUNTER


def test_to_json():
    counter = Counter(
        name="requests_total",
        value=42,
    )

    data = counter.to_json()

    assert isinstance(data, str)
    assert "requests_total" in data
    assert "42" in data


def test_from_json():
    counter = Counter(
        name="requests_total",
        value=42,
    )

    data = counter.to_json()

    restored = Counter.from_json(data)

    assert isinstance(restored, Counter)
    assert restored.name == "requests_total"
    assert restored.value == 42
    assert restored.metric_type is MetricType.COUNTER


# ==============================================================================
# Part 11. Copy / Clone
# ==============================================================================


def test_copy():
    counter = Counter(
        name="requests_total",
        value=10,
    )

    copied = counter.copy()

    assert isinstance(copied, Counter)
    assert copied is not counter
    assert copied.name == counter.name
    assert copied.value == counter.value
    assert copied.metric_type is MetricType.COUNTER


def test_clone():
    counter = Counter(
        name="requests_total",
        value=10,
    )

    cloned = counter.clone()

    assert isinstance(cloned, Counter)
    assert cloned is not counter
    assert cloned.value == counter.value


def test_clone_independence():
    counter = Counter(
        name="requests_total",
        value=10,
    )

    cloned = counter.clone()

    cloned.increment(5)

    assert counter.value == 10
    assert cloned.value == 15


def test_metadata_independence():
    counter = Counter()

    counter.labels.add(
        "host",
        "node01",
    )

    counter.attributes.add(
        "region",
        "test",
    )

    counter.tags.add("production")

    cloned = counter.clone()

    cloned.labels.add(
        "host",
        "node02",
    )

    cloned.attributes.add(
        "region",
        "prod",
    )

    cloned.tags.add("staging")

    assert counter.labels.get("host") == "node01"
    assert counter.attributes.get("region") == "test"
    assert "staging" not in counter.tags


# ==============================================================================
# Part 12. Snapshot
# ==============================================================================


def test_snapshot():
    counter = Counter(
        name="requests_total",
        value=42,
    )

    snapshot = counter.snapshot()

    assert snapshot is not None
    assert snapshot["name"] == "requests_total"
    assert snapshot["value"] == 42


def test_snapshot_is_immutable():
    counter = Counter(
        name="requests_total",
        value=42,
    )

    snapshot = counter.snapshot()

    original_value = snapshot["value"]

    counter.value = 100

    assert snapshot["value"] == original_value
    assert snapshot["value"] == 42


# ==============================================================================
# Part 13. Equality / Hash
# ==============================================================================


def test_eq():
    first = Counter(
        name="requests_total",
        value=10,
    )

    second = Counter(
        name="requests_total",
        value=10,
    )

    assert first == second


def test_hash():
    counter = Counter(
        name="requests_total",
        value=10,
    )

    assert isinstance(hash(counter), int)


def test_hash_consistency():
    counter = Counter(
        name="requests_total",
        value=10,
    )

    first_hash = hash(counter)
    second_hash = hash(counter)

    assert first_hash == second_hash


# ==============================================================================
# Part 14. Representation
# ==============================================================================


def test_repr():
    counter = Counter(
        name="requests_total",
        value=42,
    )

    result = repr(counter)

    assert isinstance(result, str)
    assert "Counter" in result
    assert "requests_total" in result
    assert "42" in result
    assert "counter" in result.lower()


def test_str():
    counter = Counter(
        name="requests_total",
        value=42,
    )

    result = str(counter)

    assert isinstance(result, str)
    assert "requests_total" in result
    assert "42" in result
    assert "counter" in result.lower()    