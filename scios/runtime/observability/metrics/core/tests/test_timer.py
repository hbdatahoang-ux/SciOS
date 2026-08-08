"""
Tests for the Timer metric implementation.

Python 3.11+
"""

# ==============================================================================

# Part 1. Imports

# ==============================================================================

from __future__ import annotations

import copy
import json
from copy import deepcopy

import pytest

from scios.runtime.observability.metrics.core.timer import (
    DEFAULT_ANNOTATIONS,
    DEFAULT_DESCRIPTION,
    DEFAULT_METADATA,
    DEFAULT_NAME,
    DEFAULT_TAGS,
    DEFAULT_UNIT,
    DEFAULT_VALUE,
    Timer,
    TimerValidationError,
)

from scios.runtime.observability.metrics.core.metric_state import (
    MetricState,
)

# ==============================================================================



# ==============================================================================
# Part 2. Constants
# ==============================================================================

TEST_VALUE = 42.0
TEST_NAME = "request_timer"
TEST_DESCRIPTION = "Request duration timer"
TEST_UNIT = "seconds"

TEST_METADATA = {
    "source": "test",
    "service": "api",
}

TEST_ANNOTATIONS = {
    "kind": "timer",
    "environment": "test",
}

TEST_TAGS = {
    "env": "test",
    "component": "runtime",
}


# ==============================================================================
# Part 3. Construction
# ==============================================================================

def test_timer_can_be_constructed() -> None:
    timer = Timer()

    assert isinstance(timer, Timer)


def test_timer_constructed_with_value() -> None:
    timer = Timer(value=TEST_VALUE)

    assert timer.value == TEST_VALUE


def test_timer_constructed_with_name() -> None:
    timer = Timer(name=TEST_NAME)

    assert timer.name == TEST_NAME


def test_timer_constructed_with_full_configuration() -> None:
    state = MetricState()

    timer = Timer(
        value=TEST_VALUE,
        name=TEST_NAME,
        description=TEST_DESCRIPTION,
        unit=TEST_UNIT,
        metadata=TEST_METADATA,
        annotations=TEST_ANNOTATIONS,
        tags=TEST_TAGS,
        state=state,
    )

    assert timer.value == TEST_VALUE
    assert timer.name == TEST_NAME
    assert timer.description == TEST_DESCRIPTION
    assert timer.unit == TEST_UNIT
    assert timer.metadata == TEST_METADATA
    assert timer.annotations == TEST_ANNOTATIONS
    assert timer.tags == TEST_TAGS
    assert timer.state is state


def test_timer_constructor_copies_metadata() -> None:
    metadata = {
        "source": "test",
    }

    timer = Timer(metadata=metadata)

    metadata["source"] = "changed"

    assert timer.metadata["source"] == "test"
    assert timer.metadata is not metadata


def test_timer_constructor_copies_annotations() -> None:
    annotations = {
        "kind": "timer",
    }

    timer = Timer(annotations=annotations)

    annotations["kind"] = "changed"

    assert timer.annotations["kind"] == "timer"
    assert timer.annotations is not annotations


def test_timer_constructor_copies_tags() -> None:
    tags = {
        "env": "test",
    }

    timer = Timer(tags=tags)

    tags["env"] = "changed"

    assert timer.tags["env"] == "test"
    assert timer.tags is not tags


# ==============================================================================
# Part 4. Default values
# ==============================================================================

def test_default_value() -> None:
    timer = Timer()

    assert timer.value == DEFAULT_VALUE


def test_default_name() -> None:
    timer = Timer()

    assert timer.name == DEFAULT_NAME


def test_default_description() -> None:
    timer = Timer()

    assert timer.description == DEFAULT_DESCRIPTION


def test_default_unit() -> None:
    timer = Timer()

    assert timer.unit == DEFAULT_UNIT


def test_default_metadata() -> None:
    timer = Timer()

    assert timer.metadata == DEFAULT_METADATA
    assert timer.metadata is not DEFAULT_METADATA


def test_default_annotations() -> None:
    timer = Timer()

    assert timer.annotations == DEFAULT_ANNOTATIONS
    assert timer.annotations is not DEFAULT_ANNOTATIONS


def test_default_tags() -> None:
    timer = Timer()

    assert timer.tags == DEFAULT_TAGS
    assert timer.tags is not DEFAULT_TAGS


# ==============================================================================
# Part 5. Properties
# ==============================================================================

def test_name_property() -> None:
    timer = Timer(name=TEST_NAME)

    assert timer.name == TEST_NAME

    timer.name = "updated_timer"

    assert timer.name == "updated_timer"


def test_value_property() -> None:
    timer = Timer(value=TEST_VALUE)

    assert timer.value == TEST_VALUE

    timer.value = 100.0

    assert timer.value == 100.0


def test_description_property() -> None:
    timer = Timer(description=TEST_DESCRIPTION)

    assert timer.description == TEST_DESCRIPTION

    timer.description = "Updated description"

    assert timer.description == "Updated description"


def test_unit_property() -> None:
    timer = Timer(unit=TEST_UNIT)

    assert timer.unit == TEST_UNIT

    timer.unit = "ms"

    assert timer.unit == "ms"


def test_metadata_property() -> None:
    timer = Timer(metadata=TEST_METADATA)

    assert timer.metadata == TEST_METADATA

    timer.metadata["extra"] = "value"

    assert timer.metadata["extra"] == "value"


def test_annotations_property() -> None:
    timer = Timer(annotations=TEST_ANNOTATIONS)

    assert timer.annotations == TEST_ANNOTATIONS

    timer.annotations["extra"] = "value"

    assert timer.annotations["extra"] == "value"


def test_tags_property() -> None:
    timer = Timer(tags=TEST_TAGS)

    assert timer.tags == TEST_TAGS

    timer.tags["extra"] = "value"

    assert timer.tags["extra"] == "value"


def test_state_property() -> None:
    timer = Timer()

    assert isinstance(timer.state, MetricState)


def test_state_property_setter() -> None:
    timer = Timer()

    state = MetricState()

    timer.state = state

    assert timer.state is state


# ==============================================================================
# Part 6. Value operations
# ==============================================================================

def test_set_value() -> None:
    timer = Timer()

    result = timer.set_value(42)

    assert result is timer
    assert timer.value == 42


def test_reset_value() -> None:
    timer = Timer(value=42)

    result = timer.reset()

    assert result is timer
    assert timer.value == DEFAULT_VALUE


def test_add_value() -> None:
    timer = Timer(value=10)

    result = timer.add_value()

    assert result is timer
    assert timer.value == 11


def test_subtract_value() -> None:
    timer = Timer(value=10)

    result = timer.subtract_value()

    assert result is timer
    assert timer.value == 9


def test_increment_value() -> None:
    timer = Timer(value=10)

    result = timer.increment()

    assert result is timer
    assert timer.value == 11


def test_increment_value_by_amount() -> None:
    timer = Timer(value=10)

    result = timer.increment(5)

    assert result is timer
    assert timer.value == 15


def test_decrement_value() -> None:
    timer = Timer(value=10)

    result = timer.decrement()

    assert result is timer
    assert timer.value == 9


def test_decrement_value_by_amount() -> None:
    timer = Timer(value=10)

    result = timer.decrement(5)

    assert result is timer
    assert timer.value == 5


def test_add_negative_value() -> None:
    timer = Timer(value=10)

    result = timer.add_value(-5)

    assert result is timer
    assert timer.value == 5


def test_subtract_negative_value() -> None:
    timer = Timer(value=10)

    result = timer.subtract_value(-5)

    assert result is timer
    assert timer.value == 15


def test_value_operations_are_chainable() -> None:
    timer = Timer(value=10)

    result = (
        timer
        .add_value(5)
        .subtract_value(2)
        .increment()
        .decrement(3)
    )

    assert result is timer
    assert timer.value == 11


# ==============================================================================
# Part 7. Timer operations
# ==============================================================================

def test_start(monkeypatch: pytest.MonkeyPatch) -> None:
    timer = Timer()

    monkeypatch.setattr(
        timer,
        "_now",
        lambda: 100.0,
    )

    timer.start()

    assert timer.is_running() is True
    assert timer.is_paused() is False


def test_stop(monkeypatch: pytest.MonkeyPatch) -> None:
    timer = Timer()

    monkeypatch.setattr(
        timer,
        "_now",
        lambda: 100.0,
    )

    timer.start()

    monkeypatch.setattr(
        timer,
        "_now",
        lambda: 105.0,
    )

    timer.stop()

    assert timer.is_running() is False
    assert timer.is_paused() is False


def test_start_returns_timer() -> None:
    timer = Timer()

    result = timer.start()

    assert result is timer


def test_stop_returns_timer() -> None:
    timer = Timer()

    result = timer.stop()

    assert result is timer


def test_elapsed_before_start() -> None:
    timer = Timer()

    assert timer.elapsed() == pytest.approx(0.0)


def test_elapsed_after_start(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    timer = Timer()

    current_time = 100.0

    monkeypatch.setattr(
        timer,
        "_now",
        lambda: current_time,
    )

    timer.start()

    current_time = 103.5

    assert timer.elapsed() == pytest.approx(3.5)


def test_elapsed_after_stop(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    timer = Timer()

    current_time = 100.0

    monkeypatch.setattr(
        timer,
        "_now",
        lambda: current_time,
    )

    timer.start()

    current_time = 107.0

    timer.stop()

    current_time = 120.0

    assert timer.elapsed() == pytest.approx(7.0)


def test_duration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    timer = Timer()

    current_time = 100.0

    monkeypatch.setattr(
        timer,
        "_now",
        lambda: current_time,
    )

    timer.start()

    current_time = 112.5

    assert timer.duration() == pytest.approx(12.5)


def test_pause(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    timer = Timer()

    current_time = 100.0

    monkeypatch.setattr(
        timer,
        "_now",
        lambda: current_time,
    )

    timer.start()

    current_time = 105.0

    timer.pause()

    assert timer.is_running() is False
    assert timer.is_paused() is True
    assert timer.elapsed() == pytest.approx(5.0)


def test_resume(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    timer = Timer()

    current_time = 100.0

    monkeypatch.setattr(
        timer,
        "_now",
        lambda: current_time,
    )

    timer.start()

    current_time = 105.0

    timer.pause()

    current_time = 110.0

    timer.resume()

    assert timer.is_running() is True
    assert timer.is_paused() is False

    current_time = 113.0

    assert timer.elapsed() == pytest.approx(8.0)


def test_pause_returns_timer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    timer = Timer()

    monkeypatch.setattr(
        timer,
        "_now",
        lambda: 100.0,
    )

    timer.start()

    result = timer.pause()

    assert result is timer


def test_resume_returns_timer() -> None:
    timer = Timer()

    result = timer.resume()

    assert result is timer


def test_is_running() -> None:
    timer = Timer()

    assert timer.is_running() is False

    timer.start()

    assert timer.is_running() is True

    timer.stop()

    assert timer.is_running() is False


def test_is_paused() -> None:
    timer = Timer()

    assert timer.is_paused() is False

    timer.start()
    timer.pause()

    assert timer.is_paused() is True

    timer.resume()

    assert timer.is_paused() is False


def test_clear(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    timer = Timer(value=42)

    monkeypatch.setattr(
        timer,
        "_now",
        lambda: 100.0,
    )

    timer.start()

    monkeypatch.setattr(
        timer,
        "_now",
        lambda: 105.0,
    )

    timer.clear()

    assert timer.value == DEFAULT_VALUE
    assert timer.elapsed() == pytest.approx(0.0)
    assert timer.is_running() is False
    assert timer.is_paused() is False


def test_multiple_start_stop_cycles(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    timer = Timer()

    current_time = 100.0

    monkeypatch.setattr(
        timer,
        "_now",
        lambda: current_time,
    )

    timer.start()

    current_time = 103.0

    timer.stop()

    current_time = 110.0

    timer.start()

    current_time = 114.0

    timer.stop()

    assert timer.elapsed() == pytest.approx(7.0)


def test_timer_accumulates_elapsed_time(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    timer = Timer()

    current_time = 100.0

    monkeypatch.setattr(
        timer,
        "_now",
        lambda: current_time,
    )

    timer.start()

    current_time = 105.0

    timer.stop()

    current_time = 110.0

    timer.start()

    current_time = 117.0

    timer.stop()

    assert timer.elapsed() == pytest.approx(12.0)


# ==============================================================================
# Part 8. Lifecycle
# ==============================================================================

def test_enable() -> None:
    timer = Timer(
        state=MetricState(),
    )

    timer.disable()

    result = timer.enable()

    assert result is timer
    assert timer.state.enabled is True


def test_disable() -> None:
    timer = Timer(
        state=MetricState(),
    )

    result = timer.disable()

    assert result is timer
    assert timer.state.enabled is False


def test_activate() -> None:
    timer = Timer(
        state=MetricState(),
    )

    timer.deactivate()

    result = timer.activate()

    assert result is timer
    assert timer.state.active is True


def test_deactivate() -> None:
    timer = Timer(
        state=MetricState(),
    )

    result = timer.deactivate()

    assert result is timer
    assert timer.state.active is False


def test_lifecycle_with_state_object() -> None:
    state = MetricState()
    timer = Timer(state=state)

    timer.disable()

    assert state.enabled is False

    timer.enable()

    assert state.enabled is True

    timer.deactivate()

    assert state.active is False

    timer.activate()

    assert state.active is True


def test_lifecycle_operations_without_state_do_not_fail() -> None:
    timer = Timer()

    assert timer.enable() is timer
    assert timer.disable() is timer
    assert timer.activate() is timer
    assert timer.deactivate() is timer


def test_none_state_is_allowed_by_validation_contract() -> None:
    timer = Timer(state=None)

    assert timer.state is None
    assert timer.validate() is True


# ==============================================================================
# Part 9. Metadata
# ==============================================================================

def test_set_metadata() -> None:
    timer = Timer()

    result = timer.set_metadata(
        "source",
        "test",
    )

    assert result is timer
    assert timer.metadata["source"] == "test"


def test_get_metadata() -> None:
    timer = Timer(
        metadata={
            "source": "test",
        },
    )

    assert timer.get_metadata("source") == "test"


def test_get_metadata_missing_key() -> None:
    timer = Timer()

    assert timer.get_metadata("missing") is None


def test_get_metadata_default() -> None:
    timer = Timer()

    assert timer.get_metadata(
        "missing",
        "default",
    ) == "default"


def test_remove_metadata() -> None:
    timer = Timer(
        metadata={
            "source": "test",
        },
    )

    result = timer.remove_metadata("source")

    assert result is timer
    assert "source" not in timer.metadata


def test_remove_missing_metadata() -> None:
    timer = Timer()

    result = timer.remove_metadata("missing")

    assert result is timer


def test_clear_metadata() -> None:
    timer = Timer(
        metadata={
            "a": 1,
            "b": 2,
        },
    )

    result = timer.clear_metadata()

    assert result is timer
    assert timer.metadata == {}


def test_metadata_supports_multiple_values() -> None:
    timer = Timer()

    timer.set_metadata("a", 1)
    timer.set_metadata("b", 2)
    timer.set_metadata("c", 3)

    assert timer.metadata == {
        "a": 1,
        "b": 2,
        "c": 3,
    }


# ==============================================================================
# Part 10. Annotations
# ==============================================================================

def test_set_annotation() -> None:
    timer = Timer()

    result = timer.set_annotation(
        "kind",
        "timer",
    )

    assert result is timer
    assert timer.annotations["kind"] == "timer"


def test_get_annotation() -> None:
    timer = Timer(
        annotations={
            "kind": "timer",
        },
    )

    assert timer.get_annotation("kind") == "timer"


def test_get_annotation_missing_key() -> None:
    timer = Timer()

    assert timer.get_annotation("missing") is None


def test_get_annotation_default() -> None:
    timer = Timer()

    assert timer.get_annotation(
        "missing",
        "default",
    ) == "default"


def test_remove_annotation() -> None:
    timer = Timer(
        annotations={
            "kind": "timer",
        },
    )

    result = timer.remove_annotation("kind")

    assert result is timer
    assert "kind" not in timer.annotations


def test_remove_missing_annotation() -> None:
    timer = Timer()

    result = timer.remove_annotation("missing")

    assert result is timer


def test_clear_annotations() -> None:
    timer = Timer(
        annotations={
            "a": 1,
            "b": 2,
        },
    )

    result = timer.clear_annotations()

    assert result is timer
    assert timer.annotations == {}


# ==============================================================================
# Part 11. Tags
# ==============================================================================

def test_set_tag() -> None:
    timer = Timer()

    result = timer.set_tag(
        "env",
        "test",
    )

    assert result is timer
    assert timer.tags["env"] == "test"


def test_get_tag() -> None:
    timer = Timer(
        tags={
            "env": "test",
        },
    )

    assert timer.get_tag("env") == "test"


def test_get_tag_missing_key() -> None:
    timer = Timer()

    assert timer.get_tag("missing") is None


def test_get_tag_default() -> None:
    timer = Timer()

    assert timer.get_tag(
        "missing",
        "default",
    ) == "default"


def test_remove_tag() -> None:
    timer = Timer(
        tags={
            "env": "test",
        },
    )

    result = timer.remove_tag("env")

    assert result is timer
    assert "env" not in timer.tags


def test_remove_missing_tag() -> None:
    timer = Timer()

    result = timer.remove_tag("missing")

    assert result is timer


def test_clear_tags() -> None:
    timer = Timer(
        tags={
            "a": 1,
            "b": 2,
        },
    )

    result = timer.clear_tags()

    assert result is timer
    assert timer.tags == {}


# ==============================================================================
# Part 12. Snapshot / restore
# ==============================================================================

def test_snapshot_returns_dict(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    timer = Timer(
        value=42,
        name=TEST_NAME,
    )

    monkeypatch.setattr(
        timer,
        "_now",
        lambda: 100.0,
    )

    timer.start()

    snapshot = timer.snapshot()

    assert isinstance(snapshot, dict)


def test_snapshot_contains_timer_data(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    timer = Timer(
        value=TEST_VALUE,
        name=TEST_NAME,
        description=TEST_DESCRIPTION,
        unit=TEST_UNIT,
        metadata=TEST_METADATA,
        annotations=TEST_ANNOTATIONS,
        tags=TEST_TAGS,
    )

    monkeypatch.setattr(
        timer,
        "_now",
        lambda: 100.0,
    )

    timer.start()

    snapshot = timer.snapshot()

    assert snapshot["value"] == TEST_VALUE
    assert snapshot["name"] == TEST_NAME
    assert snapshot["description"] == TEST_DESCRIPTION
    assert snapshot["unit"] == TEST_UNIT
    assert snapshot["metadata"] == TEST_METADATA
    assert snapshot["annotations"] == TEST_ANNOTATIONS
    assert snapshot["tags"] == TEST_TAGS


def test_snapshot_is_independent() -> None:
    timer = Timer(
        metadata={
            "source": "test",
        },
        annotations={
            "kind": "timer",
        },
        tags={
            "env": "test",
        },
    )

    snapshot = timer.snapshot()

    snapshot["metadata"]["source"] = "changed"
    snapshot["annotations"]["kind"] = "changed"
    snapshot["tags"]["env"] = "changed"

    assert timer.metadata["source"] == "test"
    assert timer.annotations["kind"] == "timer"
    assert timer.tags["env"] == "test"


def test_restore() -> None:
    source = Timer(
        value=42,
        name=TEST_NAME,
        description=TEST_DESCRIPTION,
        unit=TEST_UNIT,
        metadata=TEST_METADATA,
        annotations=TEST_ANNOTATIONS,
        tags=TEST_TAGS,
    )

    snapshot = source.snapshot()

    target = Timer()

    result = target.restore(snapshot)

    assert result is target
    assert target.value == source.value
    assert target.name == source.name
    assert target.description == source.description
    assert target.unit == source.unit
    assert target.metadata == source.metadata
    assert target.annotations == source.annotations
    assert target.tags == source.tags


def test_restore_does_not_alias_snapshot_containers() -> None:
    source = Timer(
        metadata={
            "source": "test",
        },
        annotations={
            "kind": "timer",
        },
        tags={
            "env": "test",
        },
    )

    snapshot = source.snapshot()

    target = Timer()

    target.restore(snapshot)

    target.metadata["source"] = "changed"
    target.annotations["kind"] = "changed"
    target.tags["env"] = "changed"

    assert snapshot["metadata"]["source"] == "test"
    assert snapshot["annotations"]["kind"] == "timer"
    assert snapshot["tags"]["env"] == "test"


def test_restore_missing_optional_fields() -> None:
    timer = Timer(
        value=42,
        name="old",
        description="old description",
        unit="seconds",
        metadata={"old": True},
        annotations={"old": True},
        tags={"old": True},
    )

    snapshot = {
        "value": 10,
    }

    result = timer.restore(snapshot)

    assert result is timer
    assert timer.value == 10
    assert timer.name is None
    assert timer.description is None
    assert timer.unit is None
    assert timer.metadata == {}
    assert timer.annotations == {}
    assert timer.tags == {}


# ==============================================================================
# Part 13. Copy / clone
# ==============================================================================

def test_copy_returns_timer() -> None:
    timer = Timer(
        value=42,
        name=TEST_NAME,
    )

    copied = timer.copy()

    assert isinstance(copied, Timer)


def test_copy_returns_independent_object() -> None:
    timer = Timer(
        value=42,
        metadata={
            "source": "test",
        },
        annotations={
            "kind": "timer",
        },
        tags={
            "env": "test",
        },
    )

    copied = timer.copy()

    assert copied is not timer
    assert copied == timer

    copied.value = 100
    copied.metadata["source"] = "changed"
    copied.annotations["kind"] = "changed"
    copied.tags["env"] = "changed"

    assert timer.value == 42
    assert timer.metadata["source"] == "test"
    assert timer.annotations["kind"] == "timer"
    assert timer.tags["env"] == "test"


def test_clone_returns_timer() -> None:
    timer = Timer(
        value=42,
        name=TEST_NAME,
    )

    cloned = timer.clone()

    assert isinstance(cloned, Timer)


def test_clone_returns_independent_object() -> None:
    timer = Timer(
        value=42,
        metadata={
            "source": "test",
        },
        annotations={
            "kind": "timer",
        },
        tags={
            "env": "test",
        },
    )

    cloned = timer.clone()

    assert cloned is not timer
    assert cloned == timer

    cloned.value = 100
    cloned.metadata["source"] = "changed"
    cloned.annotations["kind"] = "changed"
    cloned.tags["env"] = "changed"

    assert timer.value == 42
    assert timer.metadata["source"] == "test"
    assert timer.annotations["kind"] == "timer"
    assert timer.tags["env"] == "test"


def test_copy_and_clone_are_equivalent() -> None:
    timer = Timer(
        value=42,
        name=TEST_NAME,
        description=TEST_DESCRIPTION,
        unit=TEST_UNIT,
        metadata=TEST_METADATA,
        annotations=TEST_ANNOTATIONS,
        tags=TEST_TAGS,
    )

    copied = timer.copy()
    cloned = timer.clone()

    assert copied == cloned
    assert copied is not cloned
    assert copied is not timer
    assert cloned is not timer


# ==============================================================================
# Part 14. Serialization
# ==============================================================================

def test_to_dict() -> None:
    timer = Timer(
        value=TEST_VALUE,
        name=TEST_NAME,
        description=TEST_DESCRIPTION,
        unit=TEST_UNIT,
        metadata=TEST_METADATA,
        annotations=TEST_ANNOTATIONS,
        tags=TEST_TAGS,
    )

    data = timer.to_dict()

    assert isinstance(data, dict)
    assert data["value"] == TEST_VALUE
    assert data["name"] == TEST_NAME
    assert data["description"] == TEST_DESCRIPTION
    assert data["unit"] == TEST_UNIT
    assert data["metadata"] == TEST_METADATA
    assert data["annotations"] == TEST_ANNOTATIONS
    assert data["tags"] == TEST_TAGS


def test_to_dict_returns_copy_of_containers() -> None:
    timer = Timer(
        metadata={
            "source": "test",
        },
        annotations={
            "kind": "timer",
        },
        tags={
            "env": "test",
        },
    )

    data = timer.to_dict()

    data["metadata"]["source"] = "changed"
    data["annotations"]["kind"] = "changed"
    data["tags"]["env"] = "changed"

    assert timer.metadata["source"] == "test"
    assert timer.annotations["kind"] == "timer"
    assert timer.tags["env"] == "test"


def test_to_json() -> None:
    timer = Timer(
        value=42,
        name=TEST_NAME,
    )

    result = timer.to_json()

    assert isinstance(result, str)
    assert '"value": 42' in result
    assert f'"name": "{TEST_NAME}"' in result


def test_to_json_can_be_parsed() -> None:
    timer = Timer(
        value=42,
        name=TEST_NAME,
        metadata={
            "source": "test",
        },
    )

    result = timer.to_json()

    data = json.loads(result)

    assert isinstance(data, dict)
    assert data["value"] == 42
    assert data["name"] == TEST_NAME
    assert data["metadata"]["source"] == "test"


# ==============================================================================
# Part 15. Validation
# ==============================================================================

def test_validate_default_timer() -> None:
    timer = Timer()

    assert timer.validate() is True


def test_validate_configured_timer() -> None:
    timer = Timer(
        value=42,
        name=TEST_NAME,
        description=TEST_DESCRIPTION,
        unit=TEST_UNIT,
        metadata=TEST_METADATA,
        annotations=TEST_ANNOTATIONS,
        tags=TEST_TAGS,
        state=MetricState(),
    )

    assert timer.validate() is True


def test_validate_after_timer_operations(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    timer = Timer()

    current_time = 100.0

    monkeypatch.setattr(
        timer,
        "_now",
        lambda: current_time,
    )

    timer.start()

    current_time = 105.0

    timer.pause()

    current_time = 110.0

    timer.resume()

    current_time = 115.0

    timer.stop()

    assert timer.validate() is True


def test_validate_invalid_name() -> None:
    timer = Timer()

    timer._name = 123

    with pytest.raises(
        (TimerValidationError, ValueError, TypeError),
    ):
        timer.validate()


def test_validate_invalid_value() -> None:
    timer = Timer()

    timer._value = "invalid"

    with pytest.raises(
        (TimerValidationError, ValueError, TypeError),
    ):
        timer.validate()


def test_validate_invalid_description() -> None:
    timer = Timer()

    timer._description = 123

    with pytest.raises(
        (TimerValidationError, ValueError, TypeError),
    ):
        timer.validate()


def test_validate_invalid_unit() -> None:
    timer = Timer()

    timer._unit = 123

    with pytest.raises(
        (TimerValidationError, ValueError, TypeError),
    ):
        timer.validate()


def test_validate_invalid_metadata() -> None:
    timer = Timer()

    timer._metadata = []

    with pytest.raises(
        (TimerValidationError, ValueError, TypeError),
    ):
        timer.validate()


def test_validate_invalid_annotations() -> None:
    timer = Timer()

    timer._annotations = None

    with pytest.raises(
        (TimerValidationError, ValueError, TypeError),
    ):
        timer.validate()


def test_validate_invalid_tags() -> None:
    timer = Timer()

    timer._tags = None

    with pytest.raises(
        (TimerValidationError, ValueError, TypeError),
    ):
        timer.validate()


# ==============================================================================
# Part 16. Equality
# ==============================================================================

def test_equal_timers() -> None:
    timer_a = Timer(
        value=42,
        name=TEST_NAME,
        description=TEST_DESCRIPTION,
        unit=TEST_UNIT,
        metadata=TEST_METADATA,
        annotations=TEST_ANNOTATIONS,
        tags=TEST_TAGS,
    )

    timer_b = Timer(
        value=42,
        name=TEST_NAME,
        description=TEST_DESCRIPTION,
        unit=TEST_UNIT,
        metadata=TEST_METADATA,
        annotations=TEST_ANNOTATIONS,
        tags=TEST_TAGS,
    )

    assert timer_a == timer_b


def test_unequal_values() -> None:
    timer_a = Timer(value=42)
    timer_b = Timer(value=43)

    assert timer_a != timer_b


def test_unequal_names() -> None:
    timer_a = Timer(name="timer_a")
    timer_b = Timer(name="timer_b")

    assert timer_a != timer_b


def test_unequal_metadata() -> None:
    timer_a = Timer(
        metadata={
            "source": "a",
        },
    )

    timer_b = Timer(
        metadata={
            "source": "b",
        },
    )

    assert timer_a != timer_b


def test_timer_not_equal_to_other_type() -> None:
    timer = Timer(value=42)

    assert timer != 42
    assert timer != "timer"
    assert timer != object()


def test_equal_timers_have_same_hash() -> None:
    timer_a = Timer(
        value=42,
        name=TEST_NAME,
        metadata=TEST_METADATA,
        annotations=TEST_ANNOTATIONS,
        tags=TEST_TAGS,
    )

    timer_b = Timer(
        value=42,
        name=TEST_NAME,
        metadata=TEST_METADATA,
        annotations=TEST_ANNOTATIONS,
        tags=TEST_TAGS,
    )

    assert timer_a == timer_b
    assert hash(timer_a) == hash(timer_b)


def test_timer_is_hashable() -> None:
    timer = Timer(value=42)

    result = hash(timer)

    assert isinstance(result, int)


# ==============================================================================
# Part 17. Representation
# ==============================================================================

def test_repr_contains_class_name() -> None:
    timer = Timer()

    assert "Timer" in repr(timer)


def test_repr_contains_value() -> None:
    timer = Timer(value=42)

    assert "42" in repr(timer)


def test_repr_contains_name() -> None:
    timer = Timer(name=TEST_NAME)

    assert TEST_NAME in repr(timer)


def test_repr_contains_description() -> None:
    timer = Timer(description=TEST_DESCRIPTION)

    assert TEST_DESCRIPTION in repr(timer)


def test_repr_contains_unit() -> None:
    timer = Timer(unit=TEST_UNIT)

    assert TEST_UNIT in repr(timer)


def test_repr_is_string() -> None:
    timer = Timer()

    assert isinstance(repr(timer), str)


def test_str_returns_value() -> None:
    timer = Timer(value=42)

    assert str(timer) == str(timer.value)


# ==============================================================================
# Part 18. Edge / invalid states
# ==============================================================================

def test_invalid_boolean_value() -> None:
    timer = Timer()

    timer._value = True

    with pytest.raises(
        (TimerValidationError, ValueError, TypeError),
    ):
        timer.validate()


def test_invalid_boolean_value_false() -> None:
    timer = Timer()

    timer._value = False

    with pytest.raises(
        (TimerValidationError, ValueError, TypeError),
    ):
        timer.validate()


def test_negative_values_are_allowed() -> None:
    timer = Timer(value=-100)

    assert timer.value == -100
    assert timer.validate() is True


def test_float_values_are_allowed() -> None:
    timer = Timer(value=3.14159)

    assert timer.value == pytest.approx(3.14159)
    assert timer.validate() is True


def test_zero_is_valid() -> None:
    timer = Timer(value=0)

    assert timer.value == 0
    assert timer.validate() is True


def test_invalid_timer_operation() -> None:
    timer = Timer()

    assert timer.stop() is timer
    assert timer.pause() is timer
    assert timer.resume() is timer

    assert timer.is_running() is False
    assert timer.is_paused() is False
    assert timer.validate() is True


def test_stop_before_start() -> None:
    timer = Timer()

    result = timer.stop()

    assert result is timer
    assert timer.elapsed() == pytest.approx(0.0)
    assert timer.is_running() is False


def test_pause_before_start() -> None:
    timer = Timer()

    result = timer.pause()

    assert result is timer
    assert timer.is_running() is False
    assert timer.is_paused() is False


def test_resume_before_pause() -> None:
    timer = Timer()

    result = timer.resume()

    assert result is timer
    assert timer.is_running() is False
    assert timer.is_paused() is False


def test_double_start(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    timer = Timer()

    monkeypatch.setattr(
        timer,
        "_now",
        lambda: 100.0,
    )

    timer.start()

    monkeypatch.setattr(
        timer,
        "_now",
        lambda: 105.0,
    )

    result = timer.start()

    assert result is timer
    assert timer.is_running() is True

    monkeypatch.setattr(
        timer,
        "_now",
        lambda: 110.0,
    )

    assert timer.elapsed() == pytest.approx(10.0)


def test_double_stop(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    timer = Timer()

    current_time = 100.0

    monkeypatch.setattr(
        timer,
        "_now",
        lambda: current_time,
    )

    timer.start()

    current_time = 105.0

    timer.stop()

    current_time = 110.0

    result = timer.stop()

    assert result is timer
    assert timer.is_running() is False
    assert timer.elapsed() == pytest.approx(5.0)


def test_invalid_lifecycle_state() -> None:
    timer = Timer()

    timer._state = None

    assert timer.validate() is True
    assert timer._state is None


def test_large_values() -> None:
    timer = Timer(
        value=10**12,
    )

    timer.set_value(10**15)

    assert timer.value == 10**15
    assert timer.validate() is True