# ==============================================================================
# test_summary.py
# ==============================================================================

"""
Tests for SciOS Runtime Summary.
"""

from __future__ import annotations


# ==============================================================================
# Part 1. Imports
# ==============================================================================

import pytest

from scios.runtime.observability.metrics.core.summary import (
    Summary,
    SummaryValidationError,
    DEFAULT_VALUE,
    DEFAULT_NAME,
    DEFAULT_DESCRIPTION,
    DEFAULT_UNIT,
    DEFAULT_METADATA,
    DEFAULT_ANNOTATIONS,
    DEFAULT_TAGS,
)


# ==============================================================================
# Part 2. Constants
# ==============================================================================

EXPECTED_DEFAULT_VALUE = DEFAULT_VALUE
EXPECTED_DEFAULT_NAME = DEFAULT_NAME
EXPECTED_DEFAULT_DESCRIPTION = DEFAULT_DESCRIPTION
EXPECTED_DEFAULT_UNIT = DEFAULT_UNIT


# ==============================================================================
# Part 3. Construction
# ==============================================================================

def test_summary_can_be_constructed() -> None:
    summary = Summary()

    assert isinstance(summary, Summary)


def test_summary_constructed_with_value() -> None:
    summary = Summary(value=42)

    assert summary.value == 42


def test_summary_constructed_with_name() -> None:
    summary = Summary(name="requests")

    assert summary.name == "requests"


def test_summary_constructed_with_full_configuration() -> None:
    metadata = {"source": "test"}
    annotations = {"kind": "integration"}
    tags = {"env": "test"}

    summary = Summary(
        value=42,
        name="requests",
        description="Request summary",
        unit="count",
        metadata=metadata,
        annotations=annotations,
        tags=tags,
    )

    assert summary.value == 42
    assert summary.name == "requests"
    assert summary.description == "Request summary"
    assert summary.unit == "count"
    assert summary.metadata == metadata
    assert summary.annotations == annotations
    assert summary.tags == tags


def test_summary_constructor_copies_metadata() -> None:
    metadata = {"source": "test"}

    summary = Summary(metadata=metadata)

    metadata["changed"] = True

    assert "changed" not in summary.metadata


def test_summary_constructor_copies_annotations() -> None:
    annotations = {"kind": "test"}

    summary = Summary(annotations=annotations)

    annotations["changed"] = True

    assert "changed" not in summary.annotations


def test_summary_constructor_copies_tags() -> None:
    tags = {"env": "test"}

    summary = Summary(tags=tags)

    tags["changed"] = True

    assert "changed" not in summary.tags


# ==============================================================================
# Part 4. Default values
# ==============================================================================

def test_default_value() -> None:
    summary = Summary()

    assert summary.value == EXPECTED_DEFAULT_VALUE


def test_default_name() -> None:
    summary = Summary()

    assert summary.name == EXPECTED_DEFAULT_NAME


def test_default_description() -> None:
    summary = Summary()

    assert summary.description == EXPECTED_DEFAULT_DESCRIPTION


def test_default_unit() -> None:
    summary = Summary()

    assert summary.unit == EXPECTED_DEFAULT_UNIT


def test_default_metadata() -> None:
    summary = Summary()

    assert summary.metadata == {}
    assert summary.metadata == DEFAULT_METADATA


def test_default_annotations() -> None:
    summary = Summary()

    assert summary.annotations == {}
    assert summary.annotations == DEFAULT_ANNOTATIONS


def test_default_tags() -> None:
    summary = Summary()

    assert summary.tags == {}
    assert summary.tags == DEFAULT_TAGS


# ==============================================================================
# Part 5. Properties
# ==============================================================================

def test_name_property() -> None:
    summary = Summary()

    summary.name = "latency"

    assert summary.name == "latency"


def test_name_property_accepts_none() -> None:
    summary = Summary(name="latency")

    summary.name = None

    assert summary.name is None


def test_value_property() -> None:
    summary = Summary()

    summary.value = 100

    assert summary.value == 100


def test_description_property() -> None:
    summary = Summary()

    summary.description = "Latency summary"

    assert summary.description == "Latency summary"


def test_description_property_accepts_none() -> None:
    summary = Summary(description="test")

    summary.description = None

    assert summary.description is None


def test_unit_property() -> None:
    summary = Summary()

    summary.unit = "ms"

    assert summary.unit == "ms"


def test_unit_property_accepts_none() -> None:
    summary = Summary(unit="ms")

    summary.unit = None

    assert summary.unit is None


def test_metadata_property() -> None:
    summary = Summary()

    assert isinstance(summary.metadata, dict)


def test_annotations_property() -> None:
    summary = Summary()

    assert isinstance(summary.annotations, dict)


def test_tags_property() -> None:
    summary = Summary()

    assert isinstance(summary.tags, dict)


def test_state_property() -> None:
    state = object()
    summary = Summary(state=state)

    assert summary.state is state


def test_state_property_setter() -> None:
    summary = Summary()
    state = object()

    summary.state = state

    assert summary.state is state


# ==============================================================================
# Part 6. Value operations
# ==============================================================================

def test_set_value() -> None:
    summary = Summary()

    result = summary.set(100)

    assert result is summary
    assert summary.value == 100


def test_reset_value() -> None:
    summary = Summary(value=100)

    result = summary.reset()

    assert result is summary
    assert summary.value == DEFAULT_VALUE


def test_add_value() -> None:
    summary = Summary(value=10)

    result = summary.add(5)

    assert result is summary
    assert summary.value == 15


def test_subtract_value() -> None:
    summary = Summary(value=10)

    result = summary.subtract(3)

    assert result is summary
    assert summary.value == 7


def test_increment_value() -> None:
    summary = Summary(value=10)

    result = summary.increment()

    assert result is summary
    assert summary.value == 11


def test_increment_value_by_amount() -> None:
    summary = Summary(value=10)

    result = summary.increment(5)

    assert result is summary
    assert summary.value == 15


def test_decrement_value() -> None:
    summary = Summary(value=10)

    result = summary.decrement()

    assert result is summary
    assert summary.value == 9


def test_decrement_value_by_amount() -> None:
    summary = Summary(value=10)

    result = summary.decrement(4)

    assert result is summary
    assert summary.value == 6


def test_add_negative_value() -> None:
    summary = Summary(value=10)

    summary.add(-5)

    assert summary.value == 5


def test_subtract_negative_value() -> None:
    summary = Summary(value=10)

    summary.subtract(-5)

    assert summary.value == 15


def test_value_operations_are_chainable() -> None:
    summary = Summary()

    summary.set(10).add(5).subtract(2).increment(3).decrement(1)

    assert summary.value == 15


# ==============================================================================
# Part 7. Lifecycle
# ==============================================================================

def test_enable() -> None:
    summary = Summary()

    result = summary.enable()

    assert result is summary


def test_disable() -> None:
    summary = Summary()

    result = summary.disable()

    assert result is summary


def test_activate() -> None:
    summary = Summary()

    result = summary.activate()

    assert result is summary


def test_deactivate() -> None:
    summary = Summary()

    result = summary.deactivate()

    assert result is summary


def test_lifecycle_with_state_object() -> None:
    class FakeState:
        def __init__(self) -> None:
            self.enabled = False
            self.active = False

        def enable(self) -> None:
            self.enabled = True

        def disable(self) -> None:
            self.enabled = False

        def activate(self) -> None:
            self.active = True

        def deactivate(self) -> None:
            self.active = False

    state = FakeState()
    summary = Summary(state=state)

    summary.enable()
    assert state.enabled is True

    summary.disable()
    assert state.enabled is False

    summary.activate()
    assert state.active is True

    summary.deactivate()
    assert state.active is False


# ==============================================================================
# Part 8. Metadata
# ==============================================================================

def test_set_metadata() -> None:
    summary = Summary()

    result = summary.set_metadata("source", "test")

    assert result is summary
    assert summary.metadata["source"] == "test"


def test_get_metadata() -> None:
    summary = Summary()

    summary.set_metadata("source", "test")

    assert summary.get_metadata("source") == "test"


def test_get_metadata_missing_key() -> None:
    summary = Summary()

    assert summary.get_metadata("missing") is None


def test_get_metadata_default() -> None:
    summary = Summary()

    assert summary.get_metadata("missing", "fallback") == "fallback"


def test_remove_metadata() -> None:
    summary = Summary(
        metadata={"source": "test"},
    )

    result = summary.remove_metadata("source")

    assert result is summary
    assert "source" not in summary.metadata


def test_remove_missing_metadata() -> None:
    summary = Summary()

    result = summary.remove_metadata("missing")

    assert result is summary


def test_clear_metadata() -> None:
    summary = Summary(
        metadata={
            "a": 1,
            "b": 2,
        },
    )

    result = summary.clear_metadata()

    assert result is summary
    assert summary.metadata == {}


def test_metadata_supports_multiple_values() -> None:
    summary = Summary()

    summary.set_metadata("a", 1)
    summary.set_metadata("b", "two")

    assert summary.metadata == {
        "a": 1,
        "b": "two",
    }


# ==============================================================================
# Part 9. Annotations
# ==============================================================================

def test_set_annotation() -> None:
    summary = Summary()

    result = summary.set_annotation("kind", "test")

    assert result is summary
    assert summary.annotations["kind"] == "test"


def test_get_annotation() -> None:
    summary = Summary()

    summary.set_annotation("kind", "test")

    assert summary.get_annotation("kind") == "test"


def test_get_annotation_missing_key() -> None:
    summary = Summary()

    assert summary.get_annotation("missing") is None


def test_get_annotation_default() -> None:
    summary = Summary()

    assert summary.get_annotation("missing", "fallback") == "fallback"


def test_remove_annotation() -> None:
    summary = Summary(
        annotations={"kind": "test"},
    )

    result = summary.remove_annotation("kind")

    assert result is summary
    assert "kind" not in summary.annotations


def test_remove_missing_annotation() -> None:
    summary = Summary()

    result = summary.remove_annotation("missing")

    assert result is summary


def test_clear_annotations() -> None:
    summary = Summary(
        annotations={
            "a": 1,
            "b": 2,
        },
    )

    result = summary.clear_annotations()

    assert result is summary
    assert summary.annotations == {}


# ==============================================================================
# Part 10. Tags
# ==============================================================================

def test_set_tag() -> None:
    summary = Summary()

    result = summary.set_tag("environment", "test")

    assert result is summary
    assert summary.tags["environment"] == "test"


def test_get_tag() -> None:
    summary = Summary()

    summary.set_tag("environment", "test")

    assert summary.get_tag("environment") == "test"


def test_get_tag_missing_key() -> None:
    summary = Summary()

    assert summary.get_tag("missing") is None


def test_get_tag_default() -> None:
    summary = Summary()

    assert summary.get_tag("missing", "fallback") == "fallback"


def test_remove_tag() -> None:
    summary = Summary(
        tags={"environment": "test"},
    )

    result = summary.remove_tag("environment")

    assert result is summary
    assert "environment" not in summary.tags


def test_remove_missing_tag() -> None:
    summary = Summary()

    result = summary.remove_tag("missing")

    assert result is summary


def test_clear_tags() -> None:
    summary = Summary(
        tags={
            "environment": "test",
            "version": "1",
        },
    )

    result = summary.clear_tags()

    assert result is summary
    assert summary.tags == {}


# ==============================================================================
# Part 11. Snapshot / restore
# ==============================================================================

def test_snapshot_returns_dict() -> None:
    summary = Summary(
        value=42,
        name="requests",
        description="Request summary",
        unit="count",
        metadata={"source": "test"},
        annotations={"kind": "counter"},
        tags={"env": "test"},
    )

    snapshot = summary.snapshot()

    assert isinstance(snapshot, dict)


def test_snapshot_contains_metric_data() -> None:
    summary = Summary(
        value=42,
        name="requests",
        description="Request summary",
        unit="count",
        metadata={"source": "test"},
        annotations={"kind": "summary"},
        tags={"env": "test"},
    )

    snapshot = summary.snapshot()

    assert snapshot["name"] == "requests"
    assert snapshot["value"] == 42
    assert snapshot["description"] == "Request summary"
    assert snapshot["unit"] == "count"
    assert snapshot["metadata"] == {"source": "test"}
    assert snapshot["annotations"] == {"kind": "summary"}
    assert snapshot["tags"] == {"env": "test"}


def test_snapshot_is_independent() -> None:
    summary = Summary(
        metadata={"source": "test"},
        annotations={"kind": "summary"},
        tags={"env": "test"},
    )

    snapshot = summary.snapshot()

    snapshot["metadata"]["source"] = "changed"
    snapshot["annotations"]["kind"] = "changed"
    snapshot["tags"]["env"] = "changed"

    assert summary.metadata["source"] == "test"
    assert summary.annotations["kind"] == "summary"
    assert summary.tags["env"] == "test"


def test_restore() -> None:
    source = Summary(
        value=100,
        name="requests",
        description="Request summary",
        unit="count",
        metadata={"source": "test"},
        annotations={"kind": "summary"},
        tags={"env": "test"},
    )

    snapshot = source.snapshot()

    target = Summary(
        value=0,
        name="old",
    )

    result = target.restore(snapshot)

    assert result is target
    assert target.value == 100
    assert target.name == "requests"
    assert target.description == "Request summary"
    assert target.unit == "count"
    assert target.metadata == {"source": "test"}
    assert target.annotations == {"kind": "summary"}
    assert target.tags == {"env": "test"}


def test_restore_does_not_alias_snapshot_containers() -> None:
    summary = Summary()

    snapshot = {
        "name": "test",
        "value": 10,
        "description": None,
        "unit": None,
        "metadata": {"a": 1},
        "annotations": {"b": 2},
        "tags": {"c": 3},
    }

    summary.restore(snapshot)

    snapshot["metadata"]["a"] = 99
    snapshot["annotations"]["b"] = 99
    snapshot["tags"]["c"] = 99

    assert summary.metadata["a"] == 1
    assert summary.annotations["b"] == 2
    assert summary.tags["c"] == 3


# ==============================================================================
# Part 12. Copy / clone
# ==============================================================================

def test_copy_returns_summary() -> None:
    summary = Summary(value=42)

    copied = summary.copy()

    assert isinstance(copied, Summary)


def test_copy_returns_independent_object() -> None:
    summary = Summary(
        value=42,
        metadata={"source": "test"},
    )

    copied = summary.copy()

    assert copied is not summary
    assert copied == summary

    copied.set(100)
    copied.set_metadata("changed", True)

    assert summary.value == 42
    assert "changed" not in summary.metadata


def test_clone_returns_summary() -> None:
    summary = Summary(value=42)

    cloned = summary.clone()

    assert isinstance(cloned, Summary)


def test_clone_returns_independent_object() -> None:
    summary = Summary(
        value=42,
        metadata={"source": "test"},
    )

    cloned = summary.clone()

    assert cloned is not summary
    assert cloned == summary

    cloned.set(100)

    assert summary.value == 42


def test_copy_and_clone_are_equivalent() -> None:
    summary = Summary(
        value=42,
        name="test",
    )

    copied = summary.copy()
    cloned = summary.clone()

    assert copied == cloned


# ==============================================================================
# Part 13. Serialization
# ==============================================================================

def test_to_dict() -> None:
    summary = Summary(
        value=42,
        name="requests",
        description="Request summary",
        unit="count",
        metadata={"source": "test"},
        annotations={"kind": "summary"},
        tags={"env": "test"},
    )

    data = summary.to_dict()

    assert data["name"] == "requests"
    assert data["value"] == 42
    assert data["description"] == "Request summary"
    assert data["unit"] == "count"
    assert data["metadata"] == {"source": "test"}
    assert data["annotations"] == {"kind": "summary"}
    assert data["tags"] == {"env": "test"}


def test_to_dict_returns_copy_of_containers() -> None:
    summary = Summary(
        metadata={"source": "test"},
        annotations={"kind": "summary"},
        tags={"env": "test"},
    )

    data = summary.to_dict()

    data["metadata"]["source"] = "changed"
    data["annotations"]["kind"] = "changed"
    data["tags"]["env"] = "changed"

    assert summary.metadata["source"] == "test"
    assert summary.annotations["kind"] == "summary"
    assert summary.tags["env"] == "test"


def test_to_json() -> None:
    summary = Summary(
        value=42,
        name="requests",
    )

    payload = summary.to_json()

    assert isinstance(payload, str)
    assert '"value": 42' in payload
    assert '"name": "requests"' in payload


def test_to_json_can_be_parsed() -> None:
    import json

    summary = Summary(
        value=42,
        name="requests",
    )

    payload = summary.to_json()
    data = json.loads(payload)

    assert data["value"] == 42
    assert data["name"] == "requests"


# ==============================================================================
# Part 14. Validation
# ==============================================================================

def test_validate_default_summary() -> None:
    summary = Summary()

    assert summary.validate() is True


def test_validate_configured_summary() -> None:
    summary = Summary(
        value=100,
        name="requests",
        description="Request summary",
        unit="count",
        metadata={"source": "test"},
        annotations={"kind": "summary"},
        tags={"env": "test"},
    )

    assert summary.validate() is True


def test_validate_after_value_operations() -> None:
    summary = Summary()

    summary.set(10)
    summary.increment(5)
    summary.decrement(2)
    summary.add(10)
    summary.subtract(3)

    assert summary.validate() is True


def test_validate_invalid_name() -> None:
    summary = Summary()

    summary._name = 123

    with pytest.raises(SummaryValidationError):
        summary.validate()


def test_validate_invalid_value() -> None:
    summary = Summary()

    summary._value = "invalid"

    with pytest.raises(SummaryValidationError):
        summary.validate()


def test_validate_invalid_description() -> None:
    summary = Summary()

    summary._description = 123

    with pytest.raises(SummaryValidationError):
        summary.validate()


def test_validate_invalid_unit() -> None:
    summary = Summary()

    summary._unit = 123

    with pytest.raises(SummaryValidationError):
        summary.validate()


def test_validate_invalid_metadata() -> None:
    summary = Summary()

    summary._metadata = None

    with pytest.raises(SummaryValidationError):
        summary.validate()


def test_validate_invalid_annotations() -> None:
    summary = Summary()

    summary._annotations = None

    with pytest.raises(SummaryValidationError):
        summary.validate()


def test_validate_invalid_tags() -> None:
    summary = Summary()

    summary._tags = None

    with pytest.raises(SummaryValidationError):
        summary.validate()


# ==============================================================================
# Part 15. Equality
# ==============================================================================

def test_equal_summaries() -> None:
    left = Summary(
        value=42,
        name="requests",
        metadata={"source": "test"},
    )

    right = Summary(
        value=42,
        name="requests",
        metadata={"source": "test"},
    )

    assert left == right


def test_unequal_values() -> None:
    left = Summary(value=42)
    right = Summary(value=100)

    assert left != right


def test_unequal_names() -> None:
    left = Summary(
        value=42,
        name="a",
    )

    right = Summary(
        value=42,
        name="b",
    )

    assert left != right


def test_unequal_metadata() -> None:
    left = Summary(
        value=42,
        metadata={"source": "a"},
    )

    right = Summary(
        value=42,
        metadata={"source": "b"},
    )

    assert left != right


def test_summary_not_equal_to_other_type() -> None:
    summary = Summary(value=42)

    assert summary != 42
    assert summary != None


def test_equal_summaries_have_same_hash() -> None:
    left = Summary(
        value=42,
        name="requests",
        metadata={"source": "test"},
    )

    right = Summary(
        value=42,
        name="requests",
        metadata={"source": "test"},
    )

    assert hash(left) == hash(right)


def test_summary_is_hashable() -> None:
    summary = Summary(value=42)

    assert isinstance(hash(summary), int)


# ==============================================================================
# Part 16. Representation
# ==============================================================================

def test_repr_contains_class_name() -> None:
    summary = Summary()

    result = repr(summary)

    assert "Summary" in result


def test_repr_contains_value() -> None:
    summary = Summary(value=42)

    result = repr(summary)

    assert "42" in result


def test_repr_contains_name() -> None:
    summary = Summary(name="requests")

    result = repr(summary)

    assert "requests" in result


def test_repr_contains_description() -> None:
    summary = Summary(
        description="Request summary",
    )

    result = repr(summary)

    assert "Request summary" in result


def test_repr_contains_unit() -> None:
    summary = Summary(unit="count")

    result = repr(summary)

    assert "count" in result


def test_str_returns_value() -> None:
    summary = Summary(value=42)

    assert str(summary) == "42"


def test_repr_is_string() -> None:
    summary = Summary()

    assert isinstance(repr(summary), str)


# ==============================================================================
# Part 17. Edge / invalid states
# ==============================================================================

def test_invalid_boolean_value() -> None:
    summary = Summary()

    summary._value = True

    with pytest.raises(SummaryValidationError):
        summary.validate()


def test_invalid_boolean_value_false() -> None:
    summary = Summary()

    summary._value = False

    with pytest.raises(SummaryValidationError):
        summary.validate()


def test_invalid_name_type() -> None:
    summary = Summary()

    summary._name = 123

    with pytest.raises(SummaryValidationError):
        summary.validate()


def test_invalid_description_type() -> None:
    summary = Summary()

    summary._description = 123

    with pytest.raises(SummaryValidationError):
        summary.validate()


def test_invalid_unit_type() -> None:
    summary = Summary()

    summary._unit = 123

    with pytest.raises(SummaryValidationError):
        summary.validate()


def test_invalid_metadata_type() -> None:
    summary = Summary()

    summary._metadata = []

    with pytest.raises(SummaryValidationError):
        summary.validate()


def test_invalid_annotations_state() -> None:
    summary = Summary()

    summary._annotations = None

    with pytest.raises(SummaryValidationError):
        summary.validate()


def test_invalid_tags_state() -> None:
    summary = Summary()

    summary._tags = None

    with pytest.raises(SummaryValidationError):
        summary.validate()


def test_none_state_is_allowed_by_validation_contract() -> None:
    summary = Summary(state=None)

    assert summary.validate() is True


def test_lifecycle_operations_without_state_do_not_fail() -> None:
    summary = Summary(state=None)

    summary.enable()
    summary.disable()
    summary.activate()
    summary.deactivate()

    assert summary.validate() is True


def test_restore_missing_optional_fields() -> None:
    summary = Summary(
        value=100,
        name="old",
    )

    summary.restore(
        {
            "value": 10,
        }
    )

    assert summary.value == 10
    assert summary.name is None
    assert summary.description is None
    assert summary.unit is None
    assert summary.metadata == {}
    assert summary.annotations == {}
    assert summary.tags == {}


def test_reset_from_large_value() -> None:
    summary = Summary(value=10_000_000)

    summary.reset()

    assert summary.value == DEFAULT_VALUE


def test_negative_values_are_allowed() -> None:
    summary = Summary(value=-100)

    assert summary.value == -100
    assert summary.validate() is True


def test_float_values_are_allowed() -> None:
    summary = Summary(value=3.14159)

    assert summary.value == 3.14159
    assert summary.validate() is True


def test_zero_is_valid() -> None:
    summary = Summary(value=0)

    assert summary.value == 0
    assert summary.validate() is True
