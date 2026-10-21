# ==============================================================================
# test_gauge.py
# ==============================================================================

"""
Tests for SciOS Runtime Gauge.
"""

from __future__ import annotations


# ==============================================================================
# Part 1. Imports
# ==============================================================================

import pytest


from scios.runtime.observability.metrics.core.gauge import (
    Gauge,
    GaugeValidationError,
    DEFAULT_VALUE,
)

from scios.runtime.observability.metrics.core.metric_state import (
    MetricLifecycle,
)


# ==============================================================================
# Part 1. Construction
# ==============================================================================

def test_default_construction() -> None:
    gauge = Gauge()

    assert isinstance(gauge, Gauge)


def test_construction_with_name() -> None:
    gauge = Gauge(name="temperature")

    assert gauge.name == "temperature"


def test_construction_with_value() -> None:
    gauge = Gauge(value=42)

    assert gauge.value == 42


def test_construction_with_description() -> None:
    gauge = Gauge(
        description="Current temperature",
    )

    assert gauge.description == "Current temperature"


def test_construction_with_unit() -> None:
    gauge = Gauge(unit="celsius")

    assert gauge.unit == "celsius"


def test_construction_with_metadata() -> None:
    metadata = {
        "source": "sensor",
        "location": "lab",
    }

    gauge = Gauge(metadata=metadata)

    assert gauge.metadata == metadata


def test_initial_value() -> None:
    gauge = Gauge(value=12.5)

    assert gauge.value == 12.5


def test_default_value_is_zero() -> None:
    gauge = Gauge()

    assert gauge.value == DEFAULT_VALUE
    assert gauge.value == 0.0


def test_invalid_name() -> None:
    with pytest.raises(TypeError):
        Gauge(name=123)


def test_invalid_value() -> None:
    with pytest.raises(TypeError):
        Gauge(value="invalid")


def test_invalid_configuration() -> None:
    with pytest.raises(TypeError):
        Gauge(metadata="invalid")


# ==============================================================================
# Part 2. Properties
# ==============================================================================

def test_name_property() -> None:
    gauge = Gauge(name="temperature")

    assert gauge.name == "temperature"


def test_value_property() -> None:
    gauge = Gauge(value=25)

    assert gauge.value == 25


def test_description_property() -> None:
    gauge = Gauge(
        description="Temperature",
    )

    assert gauge.description == "Temperature"


def test_unit_property() -> None:
    gauge = Gauge(unit="°C")

    assert gauge.unit == "°C"


def test_metadata_property() -> None:
    gauge = Gauge(
        metadata={"source": "sensor"},
    )

    assert gauge.metadata == {
        "source": "sensor",
    }


def test_value_returns_current_value() -> None:
    gauge = Gauge(value=10)

    assert gauge.value == 10

    gauge.set(20)

    assert gauge.value == 20


def test_value_is_numeric() -> None:
    gauge = Gauge(value=10)

    assert isinstance(
        gauge.value,
        (int, float),
    )


def test_properties_are_readable() -> None:
    gauge = Gauge(
        name="load",
        value=50,
        description="System load",
        unit="%",
        metadata={"source": "runtime"},
    )

    assert gauge.name == "load"
    assert gauge.value == 50
    assert gauge.description == "System load"
    assert gauge.unit == "%"
    assert gauge.metadata == {
        "source": "runtime",
    }


# ==============================================================================
# Part 3. Value Operations
# ==============================================================================

def test_set() -> None:
    gauge = Gauge(value=10)

    result = gauge.set(25)

    assert result == 25
    assert gauge.value == 25


def test_set_integer() -> None:
    gauge = Gauge()

    gauge.set(42)

    assert gauge.value == 42


def test_set_float() -> None:
    gauge = Gauge()

    gauge.set(42.5)

    assert gauge.value == 42.5


def test_set_zero() -> None:
    gauge = Gauge(value=100)

    gauge.set(0)

    assert gauge.value == 0


def test_set_negative_value() -> None:
    gauge = Gauge()

    gauge.set(-10)

    assert gauge.value == -10


def test_increment() -> None:
    gauge = Gauge(value=10)

    result = gauge.increment(5)

    assert result == 15
    assert gauge.value == 15


def test_increment_default_amount() -> None:
    gauge = Gauge(value=10)

    result = gauge.increment()

    assert result == 11
    assert gauge.value == 11


def test_increment_custom_amount() -> None:
    gauge = Gauge(value=10)

    result = gauge.increment(2.5)

    assert result == 12.5
    assert gauge.value == 12.5


def test_decrement() -> None:
    gauge = Gauge(value=10)

    result = gauge.decrement(5)

    assert result == 5
    assert gauge.value == 5


def test_decrement_default_amount() -> None:
    gauge = Gauge(value=10)

    result = gauge.decrement()

    assert result == 9
    assert gauge.value == 9


def test_decrement_custom_amount() -> None:
    gauge = Gauge(value=10)

    result = gauge.decrement(2.5)

    assert result == 7.5
    assert gauge.value == 7.5


def test_add() -> None:
    gauge = Gauge(value=10)

    result = gauge.add(5)

    assert result == 15
    assert gauge.value == 15


def test_add_integer() -> None:
    gauge = Gauge(value=10)

    gauge.add(5)

    assert gauge.value == 15


def test_add_float() -> None:
    gauge = Gauge(value=10)

    gauge.add(2.5)

    assert gauge.value == 12.5


def test_subtract() -> None:
    gauge = Gauge(value=10)

    result = gauge.subtract(5)

    assert result == 5
    assert gauge.value == 5


def test_subtract_integer() -> None:
    gauge = Gauge(value=10)

    gauge.subtract(5)

    assert gauge.value == 5


def test_subtract_float() -> None:
    gauge = Gauge(value=10)

    gauge.subtract(2.5)

    assert gauge.value == 7.5


def test_multiple_operations() -> None:
    gauge = Gauge(value=10)

    gauge.set(20)
    gauge.increment(5)
    gauge.decrement(3)
    gauge.add(10)
    gauge.subtract(2)

    assert gauge.value == 30


def test_value_after_multiple_operations() -> None:
    gauge = Gauge()

    gauge.increment()
    gauge.increment(4)
    gauge.decrement()
    gauge.add(10)
    gauge.subtract(5)

    assert gauge.value == 9


# ==============================================================================
# Part 4. State
# ==============================================================================

def test_state_property() -> None:
    gauge = Gauge()

    assert gauge.state is not None


def test_initial_state() -> None:
    gauge = Gauge()

    assert gauge.state.enabled is True
    assert gauge.state.active is True
    assert gauge.state.lifecycle is MetricLifecycle.CREATED


def test_state_after_set() -> None:
    gauge = Gauge()

    gauge.set(100)

    assert gauge.value == 100
    assert gauge.state.enabled is True
    assert gauge.state.active is True


def test_state_after_increment() -> None:
    gauge = Gauge(value=10)

    gauge.increment(5)

    assert gauge.value == 15
    assert gauge.state.active is True


def test_state_after_decrement() -> None:
    gauge = Gauge(value=10)

    gauge.decrement(5)

    assert gauge.value == 5
    assert gauge.state.active is True


def test_state_after_disable() -> None:
    gauge = Gauge()

    gauge.disable()

    assert gauge.state.enabled is False
    assert gauge.state.active is False


def test_state_after_archive() -> None:
    gauge = Gauge()

    gauge.archive()

    assert gauge.state.active is False
    assert gauge.state.lifecycle is MetricLifecycle.ARCHIVED


def test_state_contains_value() -> None:
    gauge = Gauge(value=42)

    state = gauge.snapshot()

    assert state["value"] == 42


def test_state_contains_lifecycle() -> None:
    gauge = Gauge()

    state = gauge.snapshot()

    assert "state" in state
    assert "lifecycle" in state["state"]


def test_state_contains_enabled() -> None:
    gauge = Gauge()

    state = gauge.snapshot()

    assert "state" in state
    assert "enabled" in state["state"]


def test_state_is_serializable() -> None:
    gauge = Gauge(
        name="temperature",
        value=25.5,
    )

    data = gauge.to_dict()

    assert isinstance(data, dict)
    assert isinstance(data["state"], dict)


# ==============================================================================
# Part 5. Lifecycle
# ==============================================================================

def test_enable() -> None:
    gauge = Gauge()

    gauge.disable()
    gauge.enable()

    assert gauge.state.enabled is True


def test_disable() -> None:
    gauge = Gauge()

    gauge.disable()

    assert gauge.state.enabled is False
    assert gauge.state.active is False
    assert gauge.state.lifecycle.value == "disabled"


def test_activate() -> None:
    gauge = Gauge()

    gauge.deactivate()
    gauge.activate()

    assert gauge.state.active is True
    assert gauge.state.lifecycle is MetricLifecycle.ACTIVE


def test_deactivate() -> None:
    gauge = Gauge()

    gauge.deactivate()

    assert gauge.state.active is False


def test_reset() -> None:
    gauge = Gauge(
        value=100,
    )

    gauge.disable()
    gauge.reset()

    assert gauge.value == DEFAULT_VALUE
    assert gauge.state.enabled is True
    assert gauge.state.active is True
    assert gauge.state.lifecycle is MetricLifecycle.CREATED


def test_archive() -> None:
    gauge = Gauge()

    gauge.archive()

    assert gauge.state.active is False
    assert gauge.state.lifecycle is MetricLifecycle.ARCHIVED


def test_restore() -> None:
    gauge = Gauge()

    gauge.archive()
    gauge.restore()

    assert gauge.state.enabled is True
    assert gauge.state.active is True
    assert gauge.state.lifecycle is MetricLifecycle.ACTIVE


def test_disable_deactivates_gauge() -> None:
    gauge = Gauge()

    gauge.disable()

    assert gauge.state.enabled is False
    assert gauge.state.active is False


def test_archive_deactivates_gauge() -> None:
    gauge = Gauge()

    gauge.archive()

    assert gauge.state.active is False


def test_restore_reactivates_gauge() -> None:
    gauge = Gauge()

    gauge.archive()
    gauge.restore()

    assert gauge.state.active is True


def test_reset_restores_default_state() -> None:
    gauge = Gauge(
        value=100,
    )

    gauge.disable()
    gauge.reset()

    assert gauge.value == 0.0
    assert gauge.state.enabled is True
    assert gauge.state.active is True
    assert gauge.state.lifecycle is MetricLifecycle.CREATED


def test_lifecycle_sequence() -> None:
    gauge = Gauge()

    assert gauge.state.enabled is True
    assert gauge.state.active is True

    gauge.deactivate()

    assert gauge.state.active is False

    gauge.activate()

    assert gauge.state.active is True

    gauge.disable()

    assert gauge.state.enabled is False
    assert gauge.state.active is False

    gauge.enable()

    assert gauge.state.enabled is True

    gauge.activate()

    assert gauge.state.active is True

    gauge.archive()

    assert gauge.state.active is False
    assert gauge.state.lifecycle is MetricLifecycle.ARCHIVED

    gauge.restore()

    assert gauge.state.enabled is True
    assert gauge.state.active is True
    assert gauge.state.lifecycle is MetricLifecycle.ACTIVE

# ==============================================================================
# Part 6. Annotations
# ==============================================================================


def test_annotations_exists():
    gauge = Gauge()

    assert hasattr(gauge, "annotations")
    assert gauge.annotations is not None


def test_annotations_add():
    gauge = Gauge()

    gauge.annotations.add("environment", "test")

    assert gauge.annotations.get("environment") == "test"


def test_annotations_get():
    gauge = Gauge()

    gauge.annotations.add("environment", "test")

    assert gauge.annotations.get("environment") == "test"
    assert gauge.annotations.get("missing") is None


def test_annotations_setitem():
    gauge = Gauge()

    gauge.annotations["environment"] = "production"

    assert gauge.annotations["environment"] == "production"


def test_annotations_getitem():
    gauge = Gauge()

    gauge.annotations["environment"] = "test"

    assert gauge.annotations["environment"] == "test"


def test_annotations_contains():
    gauge = Gauge()

    gauge.annotations["environment"] = "test"

    assert "environment" in gauge.annotations
    assert "missing" not in gauge.annotations


def test_annotations_update():
    gauge = Gauge()

    gauge.annotations.update(
        {
            "environment": "test",
            "service": "metrics",
        }
    )

    assert gauge.annotations["environment"] == "test"
    assert gauge.annotations["service"] == "metrics"


def test_annotations_remove():
    gauge = Gauge()

    gauge.annotations["environment"] = "test"

    gauge.annotations.remove("environment")

    assert "environment" not in gauge.annotations


def test_annotations_clear():
    gauge = Gauge()

    gauge.annotations.update(
        {
            "environment": "test",
            "service": "metrics",
        }
    )

    gauge.annotations.clear()

    assert len(gauge.annotations) == 0


def test_annotations_len():
    gauge = Gauge()

    gauge.annotations.update(
        {
            "environment": "test",
            "service": "metrics",
        }
    )

    assert len(gauge.annotations) == 2


def test_annotations_iteration():
    gauge = Gauge()

    gauge.annotations.update(
        {
            "environment": "test",
            "service": "metrics",
        }
    )

    keys = list(gauge.annotations)

    assert "environment" in keys
    assert "service" in keys


# ==============================================================================
# Part 7. Tags
# ==============================================================================


def test_tags_exists():
    gauge = Gauge()

    assert hasattr(gauge, "tags")
    assert gauge.tags is not None


def test_tags_add():
    gauge = Gauge()

    gauge.tags.add("production")

    assert "production" in gauge.tags


def test_tags_get():
    gauge = Gauge()

    gauge.tags.add("production")

    assert gauge.tags.get("production") is not None


def test_tags_setitem():
    gauge = Gauge()

    gauge.tags["environment"] = "production"

    assert gauge.tags["environment"] == "production"


def test_tags_getitem():
    gauge = Gauge()

    gauge.tags["environment"] = "production"

    assert gauge.tags["environment"] == "production"


def test_tags_contains():
    gauge = Gauge()

    gauge.tags.add("production")

    assert "production" in gauge.tags
    assert "missing" not in gauge.tags


def test_tags_update():
    gauge = Gauge()

    gauge.tags.update(
        {
            "environment": "production",
            "service": "metrics",
        }
    )

    assert gauge.tags["environment"] == "production"
    assert gauge.tags["service"] == "metrics"


def test_tags_remove():
    gauge = Gauge()

    gauge.tags["environment"] = "production"

    gauge.tags.remove("environment")

    assert "environment" not in gauge.tags


def test_tags_clear():
    gauge = Gauge()

    gauge.tags.update(
        {
            "environment": "production",
            "service": "metrics",
        }
    )

    gauge.tags.clear()

    assert len(gauge.tags) == 0


def test_tags_len():
    gauge = Gauge()

    gauge.tags.update(
        {
            "environment": "production",
            "service": "metrics",
        }
    )

    assert len(gauge.tags) == 2


def test_tags_iteration():
    gauge = Gauge()

    gauge.tags.update(
        {
            "environment": "production",
            "service": "metrics",
        }
    )

    keys = list(gauge.tags)

    assert "environment" in keys
    assert "service" in keys


# ==============================================================================
# Part 8. Snapshot
# ==============================================================================


def test_snapshot():
    gauge = Gauge(
        name="temperature",
        value=25.5,
        description="Room temperature",
        unit="C",
    )

    snapshot = gauge.snapshot()

    assert snapshot is not None


def test_snapshot_returns_dict():
    gauge = Gauge(value=25.5)

    snapshot = gauge.snapshot()

    assert isinstance(snapshot, dict)


def test_snapshot_contains_value():
    gauge = Gauge(value=25.5)

    snapshot = gauge.snapshot()

    assert snapshot["value"] == 25.5


def test_snapshot_contains_state():
    gauge = Gauge()

    snapshot = gauge.snapshot()

    assert "state" in snapshot


def test_snapshot_preserves_name():
    gauge = Gauge(name="temperature")

    snapshot = gauge.snapshot()

    assert snapshot["name"] == "temperature"


def test_snapshot_preserves_description():
    gauge = Gauge(
        description="Room temperature",
    )

    snapshot = gauge.snapshot()

    assert snapshot["description"] == "Room temperature"


def test_snapshot_preserves_unit():
    gauge = Gauge(unit="C")

    snapshot = gauge.snapshot()

    assert snapshot["unit"] == "C"


def test_snapshot_preserves_annotations():
    gauge = Gauge()

    gauge.annotations["environment"] = "test"

    snapshot = gauge.snapshot()

    assert snapshot["annotations"]["environment"] == "test"


def test_snapshot_preserves_tags():
    gauge = Gauge()

    gauge.tags.add("production")

    snapshot = gauge.snapshot()

    assert "production" in snapshot["tags"]


def test_snapshot_after_value_change():
    gauge = Gauge(value=10)

    gauge.set(25)

    snapshot = gauge.snapshot()

    assert snapshot["value"] == 25


def test_snapshot_after_archive():
    gauge = Gauge(value=10)

    gauge.archive()

    snapshot = gauge.snapshot()

    assert snapshot["state"] is not None


def test_snapshot_is_independent():
    gauge = Gauge(value=10)

    gauge.annotations["environment"] = "test"

    snapshot = gauge.snapshot()

    gauge.set(20)
    gauge.annotations["environment"] = "production"

    assert snapshot["value"] == 10
    assert snapshot["annotations"]["environment"] == "test"


# ==============================================================================
# Part 9. Serialization
# ==============================================================================


def test_to_dict():
    gauge = Gauge(
        name="temperature",
        value=25.5,
        description="Room temperature",
        unit="C",
    )

    data = gauge.to_dict()

    assert isinstance(data, dict)


def test_to_dict_contains_required_fields():
    gauge = Gauge(
        name="temperature",
        value=25.5,
    )

    data = gauge.to_dict()

    assert "name" in data
    assert "value" in data
    assert "state" in data


def test_from_dict():
    gauge = Gauge(
        name="temperature",
        value=25.5,
    )

    data = gauge.to_dict()

    restored = Gauge.from_dict(data)

    assert isinstance(restored, Gauge)


def test_from_dict_restores_value():
    gauge = Gauge(value=25.5)

    restored = Gauge.from_dict(gauge.to_dict())

    assert restored.value == 25.5


def test_from_dict_restores_state():
    gauge = Gauge(value=25.5)

    gauge.disable()

    restored = Gauge.from_dict(gauge.to_dict())

    assert restored.state == gauge.state


def test_from_dict_restores_metadata():
    gauge = Gauge(
        metadata={
            "source": "sensor",
            "channel": 1,
        }
    )

    restored = Gauge.from_dict(gauge.to_dict())

    assert restored.metadata == gauge.metadata


def test_dict_roundtrip():
    gauge = Gauge(
        name="temperature",
        value=25.5,
        description="Room temperature",
        unit="C",
        metadata={
            "source": "sensor",
        },
    )

    gauge.annotations["environment"] = "test"
    gauge.tags.add("production")

    restored = Gauge.from_dict(gauge.to_dict())

    assert restored == gauge


def test_to_json():
    gauge = Gauge(
        name="temperature",
        value=25.5,
    )

    data = gauge.to_json()

    assert isinstance(data, str)


def test_to_json_returns_string():
    gauge = Gauge(value=25.5)

    assert isinstance(gauge.to_json(), str)


def test_from_json():
    gauge = Gauge(
        name="temperature",
        value=25.5,
    )

    restored = Gauge.from_json(gauge.to_json())

    assert isinstance(restored, Gauge)


def test_json_roundtrip():
    gauge = Gauge(
        name="temperature",
        value=25.5,
        description="Room temperature",
        unit="C",
    )

    restored = Gauge.from_json(gauge.to_json())

    assert restored == gauge


def test_serialization_preserves_annotations_and_tags():
    gauge = Gauge(value=25.5)

    gauge.annotations["environment"] = "test"
    gauge.tags.add("production")

    restored = Gauge.from_json(gauge.to_json())

    assert restored.annotations["environment"] == "test"
    assert "production" in restored.tags


# ==============================================================================
# Part 10. Copy / Clone
# ==============================================================================


def test_copy():
    gauge = Gauge(
        name="temperature",
        value=25.5,
    )

    copied = gauge.copy()

    assert copied is not gauge


def test_copy_returns_gauge():
    gauge = Gauge()

    assert isinstance(gauge.copy(), Gauge)


def test_copy_preserves_value():
    gauge = Gauge(value=25.5)

    copied = gauge.copy()

    assert copied.value == gauge.value


def test_copy_preserves_state():
    gauge = Gauge(value=25.5)

    gauge.disable()

    copied = gauge.copy()

    assert copied.state == gauge.state


def test_copy_preserves_metadata():
    gauge = Gauge(
        metadata={
            "source": "sensor",
        }
    )

    copied = gauge.copy()

    assert copied.metadata == gauge.metadata


def test_copy_is_independent():
    gauge = Gauge(value=10)

    gauge.annotations["environment"] = "test"
    gauge.tags.add("production")

    copied = gauge.copy()

    gauge.set(20)
    gauge.annotations["environment"] = "production"
    gauge.tags.remove("production")

    assert copied.value == 10
    assert copied.annotations["environment"] == "test"
    assert "production" in copied.tags


def test_clone():
    gauge = Gauge(
        name="temperature",
        value=25.5,
    )

    cloned = gauge.clone()

    assert cloned is not gauge


def test_clone_returns_gauge():
    gauge = Gauge()

    assert isinstance(gauge.clone(), Gauge)


def test_clone_preserves_value():
    gauge = Gauge(value=25.5)

    cloned = gauge.clone()

    assert cloned.value == gauge.value


def test_clone_preserves_state():
    gauge = Gauge(value=25.5)

    gauge.disable()

    cloned = gauge.clone()

    assert cloned.state == gauge.state


def test_clone_preserves_metadata():
    gauge = Gauge(
        metadata={
            "source": "sensor",
        }
    )

    cloned = gauge.clone()

    assert cloned.metadata == gauge.metadata


def test_clone_is_independent():
    gauge = Gauge(value=10)

    gauge.annotations["environment"] = "test"
    gauge.tags.add("production")

    cloned = gauge.clone()

    gauge.set(20)
    gauge.annotations["environment"] = "production"
    gauge.tags.remove("production")

    assert cloned.value == 10
    assert cloned.annotations["environment"] == "test"
    assert "production" in cloned.tags


# ==============================================================================
# Part 11. Validation
# ==============================================================================


def test_validate():
    gauge = Gauge()

    result = gauge.validate()

    assert result is True


def test_valid_default_gauge():
    gauge = Gauge()

    assert gauge.validate() is True


def test_valid_gauge_after_set():
    gauge = Gauge()

    gauge.set(100)

    assert gauge.validate() is True


def test_valid_gauge_after_lifecycle_change():
    gauge = Gauge()

    gauge.disable()
    assert gauge.validate() is True

    gauge.enable()
    gauge.activate()
    assert gauge.validate() is True


def test_invalid_value_state():
    gauge = Gauge()

    gauge._value = "invalid"

    try:
        gauge.validate()
    except (GaugeValidationError, ValueError, TypeError):
        pass
    else:
        raise AssertionError(
            "validate() must reject an invalid value state."
        )


def test_invalid_lifecycle_state():
    gauge = Gauge()

    gauge._state = None

    try:
        gauge.validate()
    except (GaugeValidationError, ValueError, TypeError):
        pass
    else:
        raise AssertionError(
            "validate() must reject an invalid lifecycle state."
        )


def test_validation_after_operations():
    gauge = Gauge()

    gauge.set(10)
    gauge.increment(5)
    gauge.decrement(2)
    gauge.add(10)
    gauge.subtract(3)

    assert gauge.validate() is True


# ==============================================================================
# Part 12. Equality
# ==============================================================================


def test_equal_gauges():
    gauge_a = Gauge(
        name="temperature",
        value=25.5,
        description="Room temperature",
        unit="C",
    )

    gauge_b = Gauge(
        name="temperature",
        value=25.5,
        description="Room temperature",
        unit="C",
    )

    assert gauge_a == gauge_b


def test_unequal_gauges():
    gauge_a = Gauge(
        name="temperature",
        value=25.5,
    )

    gauge_b = Gauge(
        name="temperature",
        value=30.0,
    )

    assert gauge_a != gauge_b


def test_equality_same_value():
    gauge_a = Gauge(value=25.5)
    gauge_b = Gauge(value=25.5)

    assert gauge_a == gauge_b


def test_inequality_different_value():
    gauge_a = Gauge(value=25.5)
    gauge_b = Gauge(value=30.0)

    assert gauge_a != gauge_b


def test_equality_same_configuration():
    gauge_a = Gauge(
        name="temperature",
        value=25.5,
        description="Room temperature",
        unit="C",
        metadata={
            "source": "sensor",
        },
    )

    gauge_b = Gauge(
        name="temperature",
        value=25.5,
        description="Room temperature",
        unit="C",
        metadata={
            "source": "sensor",
        },
    )

    assert gauge_a == gauge_b


def test_inequality_different_configuration():
    gauge_a = Gauge(
        name="temperature",
        value=25.5,
        unit="C",
    )

    gauge_b = Gauge(
        name="temperature",
        value=25.5,
        unit="F",
    )

    assert gauge_a != gauge_b


def test_equality_with_non_gauge():
    gauge = Gauge(value=25.5)

    assert gauge != 25.5
    assert gauge != None
    assert gauge != "gauge"


def test_equality_after_mutation():
    gauge_a = Gauge(value=10)
    gauge_b = Gauge(value=10)

    assert gauge_a == gauge_b

    gauge_a.set(20)

    assert gauge_a != gauge_b


# ==============================================================================
# Part 13. Representation
# ==============================================================================


def test_repr():
    gauge = Gauge(
        name="temperature",
        value=25.5,
    )

    result = repr(gauge)

    assert isinstance(result, str)


def test_repr_contains_class_name():
    gauge = Gauge()

    result = repr(gauge)

    assert "Gauge" in result


def test_repr_contains_name():
    gauge = Gauge(
        name="temperature",
    )

    result = repr(gauge)

    assert "temperature" in result


def test_repr_contains_value():
    gauge = Gauge(value=25.5)

    result = repr(gauge)

    assert "25.5" in result


def test_repr_contains_lifecycle():
    gauge = Gauge()

    result = repr(gauge)

    assert "state" in result.lower() or "active" in result.lower()


def test_str():
    gauge = Gauge(
        name="temperature",
        value=25.5,
    )

    result = str(gauge)

    assert isinstance(result, str)


def test_str_contains_name():
    gauge = Gauge(
        name="temperature",
    )

    result = str(gauge)

    assert "temperature" in result


def test_str_contains_value():
    gauge = Gauge(value=25.5)

    result = str(gauge)

    assert "25.5" in result


def test_repr_and_str_are_stable():
    gauge = Gauge(
        name="temperature",
        value=25.5,
    )

    repr_1 = repr(gauge)
    repr_2 = repr(gauge)

    str_1 = str(gauge)
    str_2 = str(gauge)

    assert repr_1 == repr_2
    assert str_1 == str_2