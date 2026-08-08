# ==============================================================================
# test_histogram.py
# ==============================================================================

"""
Tests for SciOS Runtime Histogram.
"""

from __future__ import annotations

# ==============================================================================
# Part 1. Imports
# ==============================================================================

import json

import pytest

from scios.runtime.observability.metrics.core.histogram import (
    Histogram,
    HistogramValidationError,
    DEFAULT_VALUE,
    DEFAULT_NAME,
    DEFAULT_DESCRIPTION,
    DEFAULT_UNIT,
    DEFAULT_BUCKETS,
    DEFAULT_METADATA,
    DEFAULT_ANNOTATIONS,
    DEFAULT_TAGS,
)

from scios.runtime.observability.metrics.core.metric_state import (
    MetricState,
)


# ==============================================================================
# Part 2. Constants
# ==============================================================================

TEST_VALUE = 42.0
TEST_NAME = "requests"
TEST_DESCRIPTION = "Request histogram"
TEST_UNIT = "count"
TEST_BUCKETS = (1.0, 5.0, 10.0, 50.0, 100.0)

TEST_METADATA = {
    "source": "test",
}

TEST_ANNOTATIONS = {
    "kind": "histogram",
}

TEST_TAGS = {
    "env": "test",
}


# ==============================================================================
# Part 3. Construction
# ==============================================================================

def test_histogram_can_be_constructed() -> None:
    histogram = Histogram()

    assert isinstance(histogram, Histogram)


def test_histogram_constructed_with_value() -> None:
    histogram = Histogram(value=TEST_VALUE)

    assert histogram.value == TEST_VALUE


def test_histogram_constructed_with_name() -> None:
    histogram = Histogram(name=TEST_NAME)

    assert histogram.name == TEST_NAME


def test_histogram_constructed_with_buckets() -> None:
    histogram = Histogram(buckets=TEST_BUCKETS)

    assert histogram.buckets == TEST_BUCKETS


def test_histogram_constructed_with_full_configuration() -> None:
    histogram = Histogram(
        value=TEST_VALUE,
        name=TEST_NAME,
        description=TEST_DESCRIPTION,
        unit=TEST_UNIT,
        buckets=TEST_BUCKETS,
        metadata=TEST_METADATA,
        annotations=TEST_ANNOTATIONS,
        tags=TEST_TAGS,
    )

    assert histogram.value == TEST_VALUE
    assert histogram.name == TEST_NAME
    assert histogram.description == TEST_DESCRIPTION
    assert histogram.unit == TEST_UNIT
    assert histogram.buckets == TEST_BUCKETS
    assert histogram.metadata == TEST_METADATA
    assert histogram.annotations == TEST_ANNOTATIONS
    assert histogram.tags == TEST_TAGS


def test_histogram_constructor_copies_metadata() -> None:
    metadata = {"source": "test"}
    histogram = Histogram(metadata=metadata)

    metadata["changed"] = True

    assert "changed" not in histogram.metadata


def test_histogram_constructor_copies_annotations() -> None:
    annotations = {"kind": "histogram"}
    histogram = Histogram(annotations=annotations)

    annotations["changed"] = True

    assert "changed" not in histogram.annotations


def test_histogram_constructor_copies_tags() -> None:
    tags = {"env": "test"}
    histogram = Histogram(tags=tags)

    tags["changed"] = True

    assert "changed" not in histogram.tags


# ==============================================================================
# Part 4. Default values
# ==============================================================================

def test_default_value() -> None:
    histogram = Histogram()

    assert histogram.value == DEFAULT_VALUE


def test_default_name() -> None:
    histogram = Histogram()

    assert histogram.name == DEFAULT_NAME


def test_default_description() -> None:
    histogram = Histogram()

    assert histogram.description == DEFAULT_DESCRIPTION


def test_default_unit() -> None:
    histogram = Histogram()

    assert histogram.unit == DEFAULT_UNIT


def test_default_buckets() -> None:
    histogram = Histogram()

    assert histogram.buckets == DEFAULT_BUCKETS


def test_default_metadata() -> None:
    histogram = Histogram()

    assert histogram.metadata == DEFAULT_METADATA
    assert histogram.metadata is not DEFAULT_METADATA


def test_default_annotations() -> None:
    histogram = Histogram()

    assert histogram.annotations == DEFAULT_ANNOTATIONS
    assert histogram.annotations is not DEFAULT_ANNOTATIONS


def test_default_tags() -> None:
    histogram = Histogram()

    assert histogram.tags == DEFAULT_TAGS
    assert histogram.tags is not DEFAULT_TAGS


# ==============================================================================
# Part 5. Properties
# ==============================================================================

def test_name_property() -> None:
    histogram = Histogram(name="latency")

    assert histogram.name == "latency"


def test_value_property() -> None:
    histogram = Histogram(value=10)

    assert histogram.value == 10


def test_description_property() -> None:
    histogram = Histogram(description="Latency distribution")

    assert histogram.description == "Latency distribution"


def test_unit_property() -> None:
    histogram = Histogram(unit="ms")

    assert histogram.unit == "ms"


def test_buckets_property() -> None:
    histogram = Histogram(buckets=(1, 2, 5, 10))

    assert histogram.buckets == (1, 2, 5, 10)


def test_metadata_property() -> None:
    histogram = Histogram(metadata={"source": "test"})

    assert histogram.metadata["source"] == "test"


def test_annotations_property() -> None:
    histogram = Histogram(annotations={"kind": "histogram"})

    assert histogram.annotations["kind"] == "histogram"


def test_tags_property() -> None:
    histogram = Histogram(tags={"env": "test"})

    assert histogram.tags["env"] == "test"


def test_state_property() -> None:
    histogram = Histogram()

    assert isinstance(histogram.state, MetricState)


def test_state_property_setter() -> None:
    histogram = Histogram()
    state = MetricState()

    histogram.state = state

    assert histogram.state is state



# ==============================================================================
# Part 6. Value operations
# ==============================================================================

def test_set_value() -> None:
    histogram = Histogram()

    result = histogram.set_value(42)

    assert histogram.value == 42
    assert result is histogram


def test_reset() -> None:
    histogram = Histogram(value=100)

    histogram.reset()

    assert histogram.value == DEFAULT_VALUE


def test_add_value() -> None:
    histogram = Histogram(value=10)

    result = histogram.add_value(5)

    assert histogram.value == 15
    assert result is histogram


def test_subtract_value() -> None:
    histogram = Histogram(value=10)

    result = histogram.subtract_value(3)

    assert histogram.value == 7
    assert result is histogram


def test_increment() -> None:
    histogram = Histogram(value=10)

    result = histogram.increment()

    assert histogram.value == 11
    assert result is histogram


def test_increment_by_amount() -> None:
    histogram = Histogram(value=10)

    result = histogram.increment(5)

    assert histogram.value == 15
    assert result is histogram


def test_decrement() -> None:
    histogram = Histogram(value=10)

    result = histogram.decrement()

    assert histogram.value == 9
    assert result is histogram


def test_decrement_by_amount() -> None:
    histogram = Histogram(value=10)

    result = histogram.decrement(5)

    assert histogram.value == 5
    assert result is histogram


def test_negative_values_are_allowed() -> None:
    histogram = Histogram()

    histogram.set_value(-10)

    assert histogram.value == -10


def test_float_values_are_allowed() -> None:
    histogram = Histogram()

    histogram.set_value(3.14)

    assert histogram.value == pytest.approx(3.14)


def test_value_operations_are_chainable() -> None:
    histogram = Histogram()

    result = (
        histogram
        .set_value(10)
        .add_value(5)
        .subtract_value(2)
        .increment()
        .decrement()
    )

    assert result is histogram
    assert histogram.value == 13


# ==============================================================================
# Part 7. Histogram operations
# ==============================================================================

def test_observe_records_value() -> None:
    histogram = Histogram()

    result = histogram.observe(10)

    assert result is histogram
    assert histogram.count() == 1


def test_record_records_value() -> None:
    histogram = Histogram()

    result = histogram.record(20)

    assert result is histogram
    assert histogram.count() == 1


def test_observe_multiple_values() -> None:
    histogram = Histogram()

    histogram.observe(1)
    histogram.observe(2)
    histogram.observe(3)

    assert histogram.count() == 3


def test_count() -> None:
    histogram = Histogram()

    histogram.observe(10)
    histogram.observe(20)

    assert histogram.count() == 2


def test_sum() -> None:
    histogram = Histogram()

    histogram.observe(10)
    histogram.observe(20)
    histogram.observe(30)

    assert histogram.sum() == 60


def test_min() -> None:
    histogram = Histogram()

    histogram.observe(10)
    histogram.observe(3)
    histogram.observe(20)

    assert histogram.min() == 3


def test_max() -> None:
    histogram = Histogram()

    histogram.observe(10)
    histogram.observe(30)
    histogram.observe(20)

    assert histogram.max() == 30


def test_mean() -> None:
    histogram = Histogram()

    histogram.observe(10)
    histogram.observe(20)
    histogram.observe(30)

    assert histogram.mean() == pytest.approx(20)


def test_percentile_median() -> None:
    histogram = Histogram()

    for value in (1, 2, 3, 4, 5):
        histogram.observe(value)

    assert histogram.percentile(50) == pytest.approx(3)


def test_bucket_counts() -> None:
    histogram = Histogram(
        buckets=(10, 20, 50),
    )

    histogram.observe(5)
    histogram.observe(15)
    histogram.observe(25)
    histogram.observe(60)

    counts = histogram.bucket_counts()

    assert isinstance(counts, dict)


def test_clear_observations() -> None:
    histogram = Histogram()

    histogram.observe(10)
    histogram.observe(20)

    result = histogram.clear_observations()

    assert result is histogram
    assert histogram.count() == 0


def test_reset_clears_value_and_observations() -> None:
    histogram = Histogram(value=100)

    histogram.observe(10)
    histogram.observe(20)
    histogram.reset()

    assert histogram.value == DEFAULT_VALUE
    assert histogram.count() == 0


# ==============================================================================
# Part 8. Lifecycle
# ==============================================================================

def test_enable() -> None:
    histogram = Histogram()

    histogram.disable()
    result = histogram.enable()

    assert result is histogram
    assert histogram.state.enabled is True


def test_disable() -> None:
    histogram = Histogram()

    result = histogram.disable()

    assert result is histogram
    assert histogram.state.enabled is False


def test_activate() -> None:
    histogram = Histogram()

    histogram.deactivate()
    result = histogram.activate()

    assert result is histogram
    assert histogram.state.active is True


def test_deactivate() -> None:
    histogram = Histogram()

    result = histogram.deactivate()

    assert result is histogram
    assert histogram.state.active is False


def test_lifecycle_operations_without_state_do_not_fail() -> None:
    histogram = Histogram()
    histogram._state = None

    histogram.enable()
    histogram.disable()
    histogram.activate()
    histogram.deactivate()


# ==============================================================================
# Part 9. Metadata
# ==============================================================================

def test_set_metadata() -> None:
    histogram = Histogram()

    result = histogram.set_metadata("source", "test")

    assert result is histogram
    assert histogram.metadata["source"] == "test"


def test_get_metadata() -> None:
    histogram = Histogram(metadata={"source": "test"})

    assert histogram.get_metadata("source") == "test"


def test_get_metadata_missing_key() -> None:
    histogram = Histogram()

    assert histogram.get_metadata("missing") is None


def test_get_metadata_default() -> None:
    histogram = Histogram()

    assert histogram.get_metadata("missing", "default") == "default"


def test_remove_metadata() -> None:
    histogram = Histogram(metadata={"source": "test"})

    result = histogram.remove_metadata("source")

    assert result is histogram
    assert "source" not in histogram.metadata


def test_remove_missing_metadata() -> None:
    histogram = Histogram()

    result = histogram.remove_metadata("missing")

    assert result is histogram


def test_clear_metadata() -> None:
    histogram = Histogram(metadata={"source": "test"})

    result = histogram.clear_metadata()

    assert result is histogram
    assert histogram.metadata == {}


# ==============================================================================
# Part 10. Annotations
# ==============================================================================

def test_set_annotation() -> None:
    histogram = Histogram()

    result = histogram.set_annotation("kind", "histogram")

    assert result is histogram
    assert histogram.annotations["kind"] == "histogram"


def test_get_annotation() -> None:
    histogram = Histogram(annotations={"kind": "histogram"})

    assert histogram.get_annotation("kind") == "histogram"


def test_get_annotation_missing_key() -> None:
    histogram = Histogram()

    assert histogram.get_annotation("missing") is None


def test_get_annotation_default() -> None:
    histogram = Histogram()

    assert histogram.get_annotation("missing", "default") == "default"


def test_remove_annotation() -> None:
    histogram = Histogram(annotations={"kind": "histogram"})

    result = histogram.remove_annotation("kind")

    assert result is histogram
    assert "kind" not in histogram.annotations


def test_remove_missing_annotation() -> None:
    histogram = Histogram()

    result = histogram.remove_annotation("missing")

    assert result is histogram


def test_clear_annotations() -> None:
    histogram = Histogram(annotations={"kind": "histogram"})

    result = histogram.clear_annotations()

    assert result is histogram
    assert histogram.annotations == {}


# ==============================================================================
# Part 11. Tags
# ==============================================================================

def test_set_tag() -> None:
    histogram = Histogram()

    result = histogram.set_tag("env", "test")

    assert result is histogram
    assert histogram.tags["env"] == "test"


def test_get_tag() -> None:
    histogram = Histogram(tags={"env": "test"})

    assert histogram.get_tag("env") == "test"


def test_get_tag_missing_key() -> None:
    histogram = Histogram()

    assert histogram.get_tag("missing") is None


def test_get_tag_default() -> None:
    histogram = Histogram()

    assert histogram.get_tag("missing", "default") == "default"


def test_remove_tag() -> None:
    histogram = Histogram(tags={"env": "test"})

    result = histogram.remove_tag("env")

    assert result is histogram
    assert "env" not in histogram.tags


def test_remove_missing_tag() -> None:
    histogram = Histogram()

    result = histogram.remove_tag("missing")

    assert result is histogram


def test_clear_tags() -> None:
    histogram = Histogram(tags={"env": "test"})

    result = histogram.clear_tags()

    assert result is histogram
    assert histogram.tags == {}


# ==============================================================================
# Part 12. Snapshot / restore
# ==============================================================================

def test_snapshot_returns_dict() -> None:
    histogram = Histogram(
        value=42,
        name=TEST_NAME,
        description=TEST_DESCRIPTION,
        unit=TEST_UNIT,
        buckets=TEST_BUCKETS,
        metadata=TEST_METADATA,
        annotations=TEST_ANNOTATIONS,
        tags=TEST_TAGS,
    )

    snapshot = histogram.snapshot()

    assert isinstance(snapshot, dict)


def test_snapshot_contains_metric_data() -> None:
    histogram = Histogram(
        value=42,
        name=TEST_NAME,
        description=TEST_DESCRIPTION,
        unit=TEST_UNIT,
        buckets=TEST_BUCKETS,
    )

    snapshot = histogram.snapshot()

    assert snapshot["value"] == 42
    assert snapshot["name"] == TEST_NAME
    assert snapshot["description"] == TEST_DESCRIPTION
    assert snapshot["unit"] == TEST_UNIT
    assert snapshot["buckets"] == TEST_BUCKETS


def test_snapshot_is_independent() -> None:
    histogram = Histogram(
        metadata={"source": "test"},
        annotations={"kind": "histogram"},
        tags={"env": "test"},
    )

    snapshot = histogram.snapshot()

    snapshot["metadata"]["source"] = "changed"
    snapshot["annotations"]["kind"] = "changed"
    snapshot["tags"]["env"] = "changed"

    assert histogram.metadata["source"] == "test"
    assert histogram.annotations["kind"] == "histogram"
    assert histogram.tags["env"] == "test"


def test_restore() -> None:
    source = Histogram(
        value=100,
        name=TEST_NAME,
        description=TEST_DESCRIPTION,
        unit=TEST_UNIT,
        buckets=TEST_BUCKETS,
        metadata=TEST_METADATA,
        annotations=TEST_ANNOTATIONS,
        tags=TEST_TAGS,
    )

    snapshot = source.snapshot()

    target = Histogram(value=1)
    result = target.restore(snapshot)

    assert result is target
    assert target.value == source.value
    assert target.name == source.name
    assert target.description == source.description
    assert target.unit == source.unit
    assert target.buckets == source.buckets
    assert target.metadata == source.metadata
    assert target.annotations == source.annotations
    assert target.tags == source.tags


def test_restore_does_not_alias_snapshot_containers() -> None:
    histogram = Histogram()

    snapshot = {
        "value": 42,
        "name": "test",
        "description": None,
        "unit": None,
        "buckets": (1, 2, 3),
        "metadata": {"source": "test"},
        "annotations": {"kind": "histogram"},
        "tags": {"env": "test"},
    }

    histogram.restore(snapshot)

    snapshot["metadata"]["source"] = "changed"
    snapshot["annotations"]["kind"] = "changed"
    snapshot["tags"]["env"] = "changed"

    assert histogram.metadata["source"] == "test"
    assert histogram.annotations["kind"] == "histogram"
    assert histogram.tags["env"] == "test"


def test_restore_missing_optional_fields() -> None:
    histogram = Histogram(
        value=42,
        name="test",
    )

    histogram.restore({
        "value": 10,
    })

    assert histogram.value == 10


# ==============================================================================
# Part 13. Copy / clone
# ==============================================================================

def test_copy_returns_histogram() -> None:
    histogram = Histogram(value=42)

    copied = histogram.copy()

    assert isinstance(copied, Histogram)


def test_copy_returns_independent_object() -> None:
    histogram = Histogram(
        value=42,
        metadata={"source": "test"},
    )

    copied = histogram.copy()

    assert copied is not histogram

    copied.metadata["source"] = "changed"

    assert histogram.metadata["source"] == "test"


def test_clone_returns_histogram() -> None:
    histogram = Histogram(value=42)

    cloned = histogram.clone()

    assert isinstance(cloned, Histogram)


def test_clone_returns_independent_object() -> None:
    histogram = Histogram(
        value=42,
        metadata={"source": "test"},
    )

    cloned = histogram.clone()

    assert cloned is not histogram

    cloned.metadata["source"] = "changed"

    assert histogram.metadata["source"] == "test"


def test_copy_and_clone_are_equivalent() -> None:
    histogram = Histogram(
        value=42,
        name="test",
        buckets=(1, 2, 3),
    )

    copied = histogram.copy()
    cloned = histogram.clone()

    assert copied == cloned


# ==============================================================================
# Part 14. Serialization
# ==============================================================================

def test_to_dict() -> None:
    histogram = Histogram(
        value=42,
        name=TEST_NAME,
        buckets=TEST_BUCKETS,
    )

    payload = histogram.to_dict()

    assert isinstance(payload, dict)
    assert payload["value"] == 42
    assert payload["name"] == TEST_NAME


def test_to_dict_returns_copy_of_containers() -> None:
    histogram = Histogram(
        metadata={"source": "test"},
        annotations={"kind": "histogram"},
        tags={"env": "test"},
    )

    payload = histogram.to_dict()

    payload["metadata"]["source"] = "changed"
    payload["annotations"]["kind"] = "changed"
    payload["tags"]["env"] = "changed"

    assert histogram.metadata["source"] == "test"
    assert histogram.annotations["kind"] == "histogram"
    assert histogram.tags["env"] == "test"


def test_to_json() -> None:
    histogram = Histogram(
        value=42,
        name=TEST_NAME,
    )

    payload = histogram.to_json()

    assert isinstance(payload, str)


def test_to_json_can_be_parsed() -> None:
    histogram = Histogram(
        value=42,
        name=TEST_NAME,
    )

    payload = histogram.to_json()
    parsed = json.loads(payload)

    assert parsed["value"] == 42
    assert parsed["name"] == TEST_NAME


# ==============================================================================
# Part 15. Validation
# ==============================================================================

def test_validate_default_histogram() -> None:
    histogram = Histogram()

    assert histogram.validate() is True


def test_validate_configured_histogram() -> None:
    histogram = Histogram(
        value=42,
        name=TEST_NAME,
        description=TEST_DESCRIPTION,
        unit=TEST_UNIT,
        buckets=TEST_BUCKETS,
        metadata=TEST_METADATA,
        annotations=TEST_ANNOTATIONS,
        tags=TEST_TAGS,
    )

    assert histogram.validate() is True


def test_validate_after_value_operations() -> None:
    histogram = Histogram()

    histogram.set_value(10)
    histogram.add_value(5)
    histogram.increment()
    histogram.decrement()

    assert histogram.validate() is True


def test_validate_invalid_name() -> None:
    histogram = Histogram()
    histogram._name = 123

    with pytest.raises((HistogramValidationError, ValueError, TypeError)):
        histogram.validate()


def test_validate_invalid_value() -> None:
    histogram = Histogram()
    histogram._value = "invalid"

    with pytest.raises((HistogramValidationError, ValueError, TypeError)):
        histogram.validate()


def test_validate_invalid_description() -> None:
    histogram = Histogram()
    histogram._description = 123

    with pytest.raises((HistogramValidationError, ValueError, TypeError)):
        histogram.validate()


def test_validate_invalid_unit() -> None:
    histogram = Histogram()
    histogram._unit = 123

    with pytest.raises((HistogramValidationError, ValueError, TypeError)):
        histogram.validate()


def test_validate_invalid_buckets() -> None:
    histogram = Histogram()
    histogram._buckets = "invalid"

    with pytest.raises((HistogramValidationError, ValueError, TypeError)):
        histogram.validate()


def test_validate_invalid_metadata() -> None:
    histogram = Histogram()
    histogram._metadata = None

    with pytest.raises((HistogramValidationError, ValueError, TypeError)):
        histogram.validate()


def test_validate_invalid_annotations() -> None:
    histogram = Histogram()
    histogram._annotations = None

    with pytest.raises((HistogramValidationError, ValueError, TypeError)):
        histogram.validate()


def test_validate_invalid_tags() -> None:
    histogram = Histogram()
    histogram._tags = None

    with pytest.raises((HistogramValidationError, ValueError, TypeError)):
        histogram.validate()


def test_invalid_boolean_value() -> None:
    histogram = Histogram()

    histogram._value = True

    with pytest.raises((HistogramValidationError, ValueError, TypeError)):
        histogram.validate()


def test_invalid_boolean_value_false() -> None:
    histogram = Histogram()

    histogram._value = False

    with pytest.raises((HistogramValidationError, ValueError, TypeError)):
        histogram.validate()


def test_none_state_is_allowed_by_validation_contract() -> None:
    histogram = Histogram()

    histogram._state = None

    assert histogram.validate() is True


# ==============================================================================
# Part 16. Equality
# ==============================================================================

def test_equal_histograms() -> None:
    left = Histogram(
        value=42,
        name=TEST_NAME,
        buckets=TEST_BUCKETS,
        metadata=TEST_METADATA,
        annotations=TEST_ANNOTATIONS,
        tags=TEST_TAGS,
    )

    right = Histogram(
        value=42,
        name=TEST_NAME,
        buckets=TEST_BUCKETS,
        metadata=TEST_METADATA,
        annotations=TEST_ANNOTATIONS,
        tags=TEST_TAGS,
    )

    assert left == right


def test_unequal_values() -> None:
    left = Histogram(value=42)
    right = Histogram(value=43)

    assert left != right


def test_unequal_names() -> None:
    left = Histogram(name="left")
    right = Histogram(name="right")

    assert left != right


def test_unequal_buckets() -> None:
    left = Histogram(buckets=(1, 2, 3))
    right = Histogram(buckets=(1, 2, 4))

    assert left != right


def test_unequal_metadata() -> None:
    left = Histogram(metadata={"source": "left"})
    right = Histogram(metadata={"source": "right"})

    assert left != right


def test_histogram_not_equal_to_other_type() -> None:
    histogram = Histogram(value=42)

    assert histogram != 42


def test_equal_histograms_have_same_hash() -> None:
    left = Histogram(
        value=42,
        name=TEST_NAME,
        buckets=TEST_BUCKETS,
        metadata=TEST_METADATA,
    )

    right = Histogram(
        value=42,
        name=TEST_NAME,
        buckets=TEST_BUCKETS,
        metadata=TEST_METADATA,
    )

    assert hash(left) == hash(right)


def test_histogram_is_hashable() -> None:
    histogram = Histogram(value=42)

    assert isinstance(hash(histogram), int)


# ==============================================================================

# Part 17. Representation

# ==============================================================================

def test_repr_contains_class_name() -> None:
    histogram = Histogram()


    assert "Histogram" in repr(histogram)


def test_repr_contains_value() -> None:
    histogram = Histogram(value=42)


    assert "42" in repr(histogram)


def test_repr_contains_name() -> None:
    histogram = Histogram(name="requests")


    assert "requests" in repr(histogram)


def test_repr_contains_description() -> None:
    histogram = Histogram(description="Request histogram")


    assert "Request histogram" in repr(histogram)


def test_repr_contains_unit() -> None:
    histogram = Histogram(unit="count")


    assert "count" in repr(histogram)


def test_repr_is_string() -> None:
    histogram = Histogram()


    assert isinstance(repr(histogram), str)


def test_str_returns_value() -> None:
    histogram = Histogram(value=42)


    assert str(histogram) == str(histogram.value)


    # ==============================================================================

    # Part 18. Edge / invalid states

    # ==============================================================================

def test_zero_is_valid() -> None:
    histogram = Histogram(value=0)


    assert histogram.validate() is True


def test_negative_values_are_valid() -> None:
    histogram = Histogram(value=-10)


    assert histogram.validate() is True


def test_float_values_are_allowed() -> None:
    histogram = Histogram(value=3.14)


    assert histogram.validate() is True


def test_empty_histogram_statistics() -> None:
    histogram = Histogram()


    assert histogram.count() == 0
    assert histogram.sum() == 0


def test_observations_accept_zero() -> None:
    histogram = Histogram()


    histogram.observe(0)

    assert histogram.count() == 1
    assert histogram.min() == 0
    assert histogram.max() == 0


def test_observations_accept_negative_values() -> None:
    histogram = Histogram()


    histogram.observe(-10)
    histogram.observe(-5)

    assert histogram.count() == 2
    assert histogram.min() == -10
    assert histogram.max() == -5


def test_observe_returns_histogram() -> None:
    histogram = Histogram()


    assert histogram.observe(10) is histogram


def test_record_returns_histogram() -> None:
    histogram = Histogram()


    assert histogram.record(10) is histogram


def test_multiple_observations_preserve_statistics() -> None:
    histogram = Histogram()


    for value in (1, 2, 3, 4, 5):
        histogram.observe(value)

    assert histogram.count() == 5
    assert histogram.sum() == 15
    assert histogram.min() == 1
    assert histogram.max() == 5
    assert histogram.mean() == pytest.approx(3)


def test_histogram_reset_from_large_value() -> None:
    histogram = Histogram(value=1_000_000)


    histogram.observe(100)
    histogram.reset()

    assert histogram.value == DEFAULT_VALUE
    assert histogram.count() == 0


# ==============================================================================

# Part 18. Edge / invalid states

# ==============================================================================

def test_invalid_boolean_value() -> None:
    histogram = Histogram()


    histogram._value = True

    with pytest.raises((HistogramValidationError, ValueError, TypeError)):
        histogram.validate()


def test_invalid_boolean_value_false() -> None:
    histogram = Histogram()


    histogram._value = False

    with pytest.raises((HistogramValidationError, ValueError, TypeError)):
        histogram.validate()


def test_negative_values_are_allowed() -> None:
    histogram = Histogram(value=-100)


    assert histogram.value == -100
    assert histogram.validate() is True


def test_float_values_are_allowed() -> None:
    histogram = Histogram(value=3.14159)


    assert histogram.value == pytest.approx(3.14159)
    assert histogram.validate() is True


def test_zero_is_valid() -> None:
    histogram = Histogram(value=0)


    assert histogram.value == 0
    assert histogram.validate() is True


def test_empty_buckets() -> None:
    histogram = Histogram(buckets=())


    assert histogram.buckets == ()


def test_unsorted_buckets() -> None:
    histogram = Histogram(
    buckets=(50, 10, 20),
    )


    with pytest.raises((HistogramValidationError, ValueError, TypeError)):
        histogram.validate()


def test_duplicate_buckets() -> None:
    histogram = Histogram(
    buckets=(10, 20, 20, 50),
    )

    with pytest.raises((HistogramValidationError, ValueError, TypeError)):
        histogram.validate()


def test_invalid_observation() -> None:
    histogram = Histogram()

    with pytest.raises((HistogramValidationError, ValueError, TypeError)):
        histogram.observe("invalid")


def test_invalid_lifecycle_state() -> None:
    histogram = Histogram()

    histogram._state = None

    assert histogram.validate() is True
    assert histogram._state is None


def test_large_values() -> None:
    histogram = Histogram(
    value=10**12,
    )


    histogram.observe(10**15)

    assert histogram.value == 10**12
    assert histogram.count() == 1
    assert histogram.max() == 10**15
    assert histogram.validate() is True
