# ==============================================================================
# Part 1. Imports
# ==============================================================================

import time

import pytest

from scios.runtime.observability.metrics.core.metric import (
    DEFAULT_METRIC_VALUE,
    Metric,
    MetricType,
    MetricUnit,
    MetricValidationError,
)

from scios.runtime.observability.metrics.core.metric_state import (
    MetricState,
)


# ==============================================================================
# Part 2. Construction
# ==============================================================================


def test_default_metric():

    metric = Metric()

    assert metric.name == "metric"
    assert metric.value == DEFAULT_METRIC_VALUE
    assert metric.metric_type is MetricType.GAUGE
    assert metric.unit is MetricUnit.NONE


def test_custom_metric():

    metric = Metric(
        name="cpu",
        value=90,
        metric_type=MetricType.COUNTER,
        unit=MetricUnit.PERCENT,
    )

    assert metric.name == "cpu"
    assert metric.value == 90
    assert metric.metric_type is MetricType.COUNTER
    assert metric.unit is MetricUnit.PERCENT


# ==============================================================================
# Part 3. Defaults
# ==============================================================================


def test_default_value():

    metric = Metric()

    assert metric.value == 0.0


def test_default_state():

    metric = Metric()

    assert isinstance(metric.state, MetricState)
    assert metric.state.is_enabled()
    assert metric.state.is_active()


def test_default_metadata():

    metric = Metric()

    assert metric.labels is not None
    assert metric.attributes is not None
    assert metric.annotations is not None
    assert metric.tags is not None
    assert metric.hooks is not None


# ==============================================================================
# Part 4. Validation
# ==============================================================================


def test_invalid_name():

    with pytest.raises(MetricValidationError):
        Metric(name="")


def test_invalid_value():

    with pytest.raises(MetricValidationError):
        Metric(value="abc")


def test_invalid_type():

    with pytest.raises(MetricValidationError):
        Metric(metric_type="counter")


def test_validate():

    metric = Metric()

    assert metric.validate() is True


# ==============================================================================
# Part 5. Properties
# ==============================================================================


def test_name():

    metric = Metric(name="memory")

    assert metric.name == "memory"


def test_value():

    metric = Metric(value=12.5)

    assert metric.value == 12.5


def test_metric_type():

    metric = Metric(metric_type=MetricType.HISTOGRAM)

    assert metric.metric_type is MetricType.HISTOGRAM


def test_unit():

    metric = Metric(unit=MetricUnit.SECONDS)

    assert metric.unit is MetricUnit.SECONDS


# ==============================================================================
# Part 6. Value Operations
# ==============================================================================


def test_set_value():

    metric = Metric()

    metric.set_value(10)

    assert metric.value == 10


def test_get_value():

    metric = Metric(value=33)

    assert metric.get_value() == 33


def test_increment():

    metric = Metric(value=1)

    metric.increment()

    assert metric.value == 2

    metric.increment(3)

    assert metric.value == 5


def test_decrement():

    metric = Metric(value=10)

    metric.decrement()

    assert metric.value == 9

    metric.decrement(4)

    assert metric.value == 5


def test_reset():

    metric = Metric(value=99)

    metric.reset()

    assert metric.value == DEFAULT_METRIC_VALUE


def test_update():

    metric = Metric()

    metric.update(123)

    assert metric.value == 123


def test_touch():

    metric = Metric()

    before = metric.updated_at

    time.sleep(0.01)

    metric.touch()

    assert metric.updated_at >= before

# ==============================================================================
# Part 7. State Management
# ==============================================================================


def test_enable():

    metric = Metric()

    metric.disable()

    metric.enable()

    assert metric.state.is_enabled()


def test_disable():

    metric = Metric()

    metric.disable()

    assert not metric.state.is_enabled()


def test_activate():

    metric = Metric()

    metric.deactivate()

    metric.activate()

    assert metric.state.is_active()


def test_deactivate():

    metric = Metric()

    metric.deactivate()

    assert not metric.state.is_active()


def test_archive():

    metric = Metric()

    metric.archive()

    assert metric.state.lifecycle.name == "ARCHIVED"


def test_restore():

    metric = Metric()

    metric.archive()
    metric.restore()

    assert metric.state.lifecycle.name != "ARCHIVED"


def test_snapshot():

    metric = Metric(value=123)

    snapshot = metric.snapshot()

    assert snapshot.payload["value"] == 123


# ==============================================================================
# Part 8. Metadata
# ==============================================================================


def test_labels():

    metric = Metric()

    assert metric.labels() is metric.labels


def test_attributes():

    metric = Metric()

    assert metric.attributes() is metric.attributes


def test_annotations():

    metric = Metric()

    assert metric.annotations() is metric.annotations


def test_tags():

    metric = Metric()

    assert metric.tags() is metric.tags


def test_hooks():

    metric = Metric()

    assert metric.hooks() is metric.hooks


# ==============================================================================
# Part 9. Serialization
# ==============================================================================


def test_to_dict():

    metric = Metric(name="cpu", value=50)

    data = metric.to_dict()

    assert data["name"] == "cpu"
    assert data["value"] == 50


def test_from_dict():

    metric = Metric(name="cpu", value=88)

    restored = Metric.from_dict(metric.to_dict())

    assert restored == metric


def test_to_json():

    metric = Metric()

    payload = metric.to_json()

    assert isinstance(payload, str)


def test_from_json():

    metric = Metric(value=66)

    restored = Metric.from_json(metric.to_json())

    assert restored == metric


# ==============================================================================
# Part 10. Copy
# ==============================================================================


def test_copy():

    metric = Metric(value=77)

    copied = metric.copy()

    assert copied == metric
    assert copied is not metric


def test_clone():

    metric = Metric(value=88)

    cloned = metric.clone()

    assert cloned == metric
    assert cloned is not metric


# ==============================================================================
# Part 11. Equality
# ==============================================================================


def test_eq():

    m1 = Metric(name="cpu", value=1)

    m2 = Metric(name="cpu", value=1)

    assert m1 == m2


def test_hash():

    metric = Metric()

    assert isinstance(hash(metric), int)


# ==============================================================================
# Part 12. Representation
# ==============================================================================


def test_repr():

    metric = Metric()

    assert "Metric" in repr(metric)


def test_str():

    metric = Metric(name="cpu", value=5)

    assert "cpu" in str(metric)


# ==============================================================================
# Part 13. Public API
# ==============================================================================


def test_all():

    from scios.runtime.observability.metrics.core.metric import __all__

    assert "Metric" in __all__


def test_version():

    from scios.runtime.observability.metrics.core.metric import METRIC_VERSION

    assert isinstance(METRIC_VERSION, str)


# ==============================================================================
# Part 14. Regression
# ==============================================================================


def test_json_roundtrip():

    metric = Metric(name="cpu", value=99)

    assert Metric.from_json(metric.to_json()) == metric


def test_dict_roundtrip():

    metric = Metric(name="cpu", value=99)

    assert Metric.from_dict(metric.to_dict()) == metric


def test_clone_independence():

    metric = Metric(value=10)

    cloned = metric.clone()

    cloned.set_value(99)

    assert metric.value == 10
    assert cloned.value == 99


def test_snapshot_restores_metric():

    metric = Metric(value=10)

    snap = metric.snapshot()

    metric.set_value(50)

    metric.restore(snap)

    assert metric.value == 10


def test_snapshot_is_immutable():

    metric = Metric(value=10)

    snap = metric.snapshot()

    metric.set_value(20)

    assert snap.payload["value"] == 10


def test_metadata_is_copied():

    metric = Metric()

    cloned = metric.clone()

    assert cloned.labels is not metric.labels
    assert cloned.attributes is not metric.attributes


def test_labels_are_independent():

    metric = Metric()

    cloned = metric.clone()

    cloned.labels.add("a", "1")

    assert not metric.labels.has("a")


def test_attributes_are_independent():

    metric = Metric()

    cloned = metric.clone()

    cloned.attributes.add("a", 1)

    assert not metric.attributes.has("a")


def test_hooks_are_independent():

    metric = Metric()

    cloned = metric.clone()

    assert cloned.hooks is not metric.hooks


def test_state_is_preserved():

    metric = Metric()

    metric.disable()

    restored = Metric.from_dict(metric.to_dict())

    assert restored.state.is_enabled() == metric.state.is_enabled()


def test_touch_updates_timestamp():

    metric = Metric()

    old = metric.updated_at

    time.sleep(0.01)

    metric.touch()

    assert metric.updated_at > old


def test_hash_consistency():

    metric = Metric()

    assert hash(metric) == hash(metric)


def test_validate():

    metric = Metric()

    assert metric.validate() is True    