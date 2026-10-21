"""
Tests for SciOS Runtime Metrics Normalizer.
"""

from __future__ import annotations

import pytest

from ..normalizer import NormalizerProcessor


# ==============================================================
# Construction
# ==============================================================


def test_default_constructor():
    processor = NormalizerProcessor()

    assert processor.strategy() == "minmax"
    assert len(processor) == 0
    assert processor.statistics()["normalized"] == 0


def test_constructor_strategy():
    processor = NormalizerProcessor(
        strategy="zscore"
    )

    assert processor.strategy() == "zscore"


def test_invalid_strategy():
    with pytest.raises(ValueError):
        NormalizerProcessor(
            strategy="unknown"
        )


def test_strategy_is_case_insensitive():
    processor = NormalizerProcessor(
        strategy="ZSCORE"
    )

    assert processor.strategy() == "zscore"


# ==============================================================
# Strategy Configuration
# ==============================================================


def test_set_strategy():
    processor = NormalizerProcessor()

    result = processor.set_strategy(
        "zscore"
    )

    assert result is processor
    assert processor.strategy() == "zscore"


def test_set_invalid_strategy():
    processor = NormalizerProcessor()

    with pytest.raises(ValueError):
        processor.set_strategy(
            "invalid"
        )


# ==============================================================
# Min-Max
# ==============================================================


def test_normalize_minmax():
    result = (
        NormalizerProcessor.normalize_minmax(
            5,
            0,
            10,
        )
    )

    assert result == pytest.approx(0.5)


def test_normalize_minmax_lower_bound():
    assert (
        NormalizerProcessor.normalize_minmax(
            0,
            0,
            10,
        )
        == 0.0
    )


def test_normalize_minmax_upper_bound():
    assert (
        NormalizerProcessor.normalize_minmax(
            10,
            0,
            10,
        )
        == 1.0
    )


def test_normalize_minmax_equal_range():
    assert (
        NormalizerProcessor.normalize_minmax(
            10,
            10,
            10,
        )
        == 0.0
    )


def test_minmax_transform():
    processor = NormalizerProcessor()

    processor.set_range(
        0,
        100,
    )

    assert processor.transform(
        50
    ) == pytest.approx(0.5)


def test_minmax_requires_range():
    processor = NormalizerProcessor()

    with pytest.raises(RuntimeError):
        processor.transform(50)


def test_set_range():
    processor = NormalizerProcessor()

    result = processor.set_range(
        0,
        10,
    )

    assert result is processor


def test_invalid_range():
    processor = NormalizerProcessor()

    with pytest.raises(ValueError):
        processor.set_range(
            10,
            10,
        )

    with pytest.raises(ValueError):
        processor.set_range(
            20,
            10,
        )


# ==============================================================
# Z-Score
# ==============================================================


def test_normalize_zscore():
    result = (
        NormalizerProcessor.normalize_zscore(
            15,
            10,
            5,
        )
    )

    assert result == pytest.approx(1.0)


def test_normalize_zscore_zero_std():
    assert (
        NormalizerProcessor.normalize_zscore(
            15,
            10,
            0,
        )
        == 0.0
    )


def test_zscore_transform():
    processor = NormalizerProcessor(
        strategy="zscore"
    )

    processor.set_distribution(
        mean=10,
        std=5,
    )

    assert processor.transform(
        15
    ) == pytest.approx(1.0)


def test_zscore_requires_distribution():
    processor = NormalizerProcessor(
        strategy="zscore"
    )

    with pytest.raises(RuntimeError):
        processor.transform(15)


def test_set_distribution():
    processor = NormalizerProcessor(
        strategy="zscore"
    )

    result = processor.set_distribution(
        mean=10,
        std=2,
    )

    assert result is processor


def test_negative_std():
    processor = NormalizerProcessor(
        strategy="zscore"
    )

    with pytest.raises(ValueError):
        processor.set_distribution(
            mean=0,
            std=-1,
        )


# ==============================================================
# Field Mapping
# ==============================================================


def test_map_field():
    processor = NormalizerProcessor()

    result = processor.map_field(
        "latency"
    )

    assert result is processor
    assert processor.fields() == {
        "latency": "latency"
    }


def test_map_field_with_target():
    processor = NormalizerProcessor()

    processor.map_field(
        "latency",
        "latency_normalized",
    )

    assert processor.fields() == {
        "latency": "latency_normalized"
    }


def test_remove_field():
    processor = NormalizerProcessor()

    processor.map_field(
        "latency"
    )

    result = processor.remove_field(
        "latency"
    )

    assert result is processor
    assert len(processor) == 0


def test_fields_returns_copy():
    processor = NormalizerProcessor()

    processor.map_field(
        "latency"
    )

    fields = processor.fields()

    fields["other"] = "other"

    assert "other" not in processor.fields()


def test_dictionary_field_normalization():
    processor = NormalizerProcessor()

    processor.set_range(
        0,
        100,
    )

    processor.map_field(
        "latency",
        "latency_normalized",
    )

    metric = {
        "name": "request",
        "latency": 50,
    }

    result = processor.transform(
        metric
    )

    assert result["name"] == "request"
    assert result["latency"] == 50
    assert result["latency_normalized"] == pytest.approx(
        0.5
    )


def test_dictionary_is_not_mutated():
    processor = NormalizerProcessor()

    processor.set_range(
        0,
        100,
    )

    processor.map_field(
        "value"
    )

    metric = {
        "value": 50
    }

    result = processor.transform(
        metric
    )

    assert result is not metric
    assert metric["value"] == 50
    assert result["value"] == pytest.approx(
        0.5
    )


def test_missing_field_is_ignored():
    processor = NormalizerProcessor()

    processor.set_range(
        0,
        100,
    )

    processor.map_field(
        "missing"
    )

    metric = {
        "value": 50
    }

    result = processor.transform(
        metric
    )

    assert result == metric


# ==============================================================
# Custom Normalizer
# ==============================================================


def test_custom_normalizer():
    processor = NormalizerProcessor(
        strategy="custom"
    )

    processor.set_normalizer(
        lambda value: value * 2
    )

    assert processor.transform(
        5
    ) == 10


def test_custom_normalizer_changes_strategy():
    processor = NormalizerProcessor()

    processor.set_normalizer(
        lambda value: value + 1
    )

    assert processor.strategy() == "custom"


def test_invalid_custom_normalizer():
    processor = NormalizerProcessor(
        strategy="custom"
    )

    with pytest.raises(RuntimeError):
        processor.transform(10)


def test_set_normalizer_requires_callable():
    processor = NormalizerProcessor()

    with pytest.raises(TypeError):
        processor.set_normalizer(
            "not-callable"
        )


# ==============================================================
# Statistics / Reset
# ==============================================================


def test_statistics():
    processor = NormalizerProcessor()

    processor.set_range(
        0,
        10,
    )

    processor.map_field(
        "value"
    )

    processor.transform(
        {"value": 5}
    )

    data = processor.statistics()

    assert data["normalized"] == 1
    assert data["strategy"] == "minmax"
    assert data["mappings"] == 1


def test_reset():
    processor = NormalizerProcessor()

    processor.set_range(
        0,
        10,
    )

    processor.transform(5)

    assert processor.statistics()[
        "normalized"
    ] == 1

    result = processor.reset()

    assert result is processor
    assert processor.statistics()[
        "normalized"
    ] == 0


def test_repr():
    processor = NormalizerProcessor()

    text = repr(processor)

    assert "NormalizerProcessor" in text
    assert "minmax" in text