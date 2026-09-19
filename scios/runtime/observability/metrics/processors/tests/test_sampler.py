"""
Tests for SciOS Runtime Metrics Sampling Processor.
"""

from __future__ import annotations

import subprocess
import sys

import pytest

from ..sampler import (
    SamplingProcessor,
    SamplerProcessor,
)


# ==============================================================
# Construction
# ==============================================================


def test_default_construction():
    processor = SamplingProcessor()

    assert processor.name == "SamplingProcessor"
    assert processor.rate() == 1.0
    assert processor.sampler() is None


def test_custom_construction():
    processor = SamplingProcessor(
        rate=0.25,
        name="custom",
        description="test",
    )

    assert processor.name == "custom"
    assert processor.description == "test"
    assert processor.rate() == 0.25


def test_invalid_rate_type():
    with pytest.raises(TypeError):
        SamplingProcessor(rate="0.5")


@pytest.mark.parametrize(
    "rate",
    [-0.1, 1.1, 2, -1],
)
def test_invalid_rate_value(rate):
    with pytest.raises(ValueError):
        SamplingProcessor(rate=rate)


def test_bool_rate_rejected():
    with pytest.raises(TypeError):
        SamplingProcessor(rate=True)


# ==============================================================
# Sampling Logic
# ==============================================================


def test_rate_one_always_samples():
    processor = SamplingProcessor(rate=1.0)

    for value in range(10):
        assert processor.transform(value) == value


def test_rate_zero_never_samples():
    processor = SamplingProcessor(rate=0.0)

    for value in range(10):
        assert processor.transform(value) is None


def test_should_sample_rate_one():
    processor = SamplingProcessor(rate=1.0)

    assert processor.should_sample("metric") is True


def test_should_sample_rate_zero():
    processor = SamplingProcessor(rate=0.0)

    assert processor.should_sample("metric") is False


# ==============================================================
# Configuration
# ==============================================================


def test_set_rate():
    processor = SamplingProcessor()

    result = processor.set_rate(0.25)

    assert result is processor
    assert processor.rate() == 0.25


def test_set_rate_invalid():
    processor = SamplingProcessor()

    with pytest.raises(ValueError):
        processor.set_rate(1.5)


def test_set_rate_invalid_type():
    processor = SamplingProcessor()

    with pytest.raises(TypeError):
        processor.set_rate("0.5")


def test_set_sampler():
    processor = SamplingProcessor(
        rate=0.0
    )

    sampler = lambda metric: metric == "keep"

    result = processor.set_sampler(sampler)

    assert result is processor
    assert processor.sampler() is sampler
    assert processor.transform("keep") == "keep"
    assert processor.transform("drop") is None


def test_set_sampler_requires_callable():
    processor = SamplingProcessor()

    with pytest.raises(TypeError):
        processor.set_sampler("invalid")


def test_remove_sampler():
    processor = SamplingProcessor(
        rate=1.0
    )

    processor.set_sampler(
        lambda metric: False
    )

    assert processor.transform("x") is None

    processor.remove_sampler()

    assert processor.sampler() is None
    assert processor.transform("x") == "x"


# ==============================================================
# Built-in Strategies
# ==============================================================


def test_always():
    processor = SamplingProcessor(
        rate=0.0
    )

    result = processor.always()

    assert result is processor
    assert processor.rate() == 1.0
    assert processor.sampler() is None
    assert processor.transform("x") == "x"


def test_never():
    processor = SamplingProcessor(
        rate=1.0
    )

    result = processor.never()

    assert result is processor
    assert processor.rate() == 0.0
    assert processor.sampler() is None
    assert processor.transform("x") is None


def test_half():
    processor = SamplingProcessor(
        rate=1.0
    )

    result = processor.half()

    assert result is processor
    assert processor.rate() == 0.5
    assert processor.sampler() is None


# ==============================================================
# Deterministic Sampling
# ==============================================================


def test_deterministic_returns_self():
    processor = SamplingProcessor(
        rate=0.5
    )

    result = processor.deterministic()

    assert result is processor
    assert processor.sampler() is not None


def test_deterministic_requires_string_key():
    processor = SamplingProcessor()

    with pytest.raises(TypeError):
        processor.deterministic(key=123)


def test_deterministic_is_stable():
    processor = SamplingProcessor(
        rate=0.5
    ).deterministic()

    first = [
        processor.should_sample({"id": str(i)})
        for i in range(100)
    ]

    second = [
        processor.should_sample({"id": str(i)})
        for i in range(100)
    ]

    assert first == second


def test_deterministic_uses_configured_key():
    processor = SamplingProcessor(
        rate=0.5
    ).deterministic(
        key="name"
    )

    first = processor.should_sample(
        {"name": "alpha", "id": "one"}
    )

    second = processor.should_sample(
        {"name": "alpha", "id": "two"}
    )

    assert first == second


def test_deterministic_different_values_can_differ():
    processor = SamplingProcessor(
        rate=0.5
    ).deterministic()

    results = {
        processor.should_sample({"id": str(i)})
        for i in range(100)
    }

    assert results == {True, False}


def test_deterministic_non_dict_metric():
    processor = SamplingProcessor(
        rate=0.5
    ).deterministic()

    result = processor.should_sample(
        "metric-123"
    )

    assert isinstance(result, bool)


def test_deterministic_is_stable_across_processes():
    code = """
from scios.runtime.observability.metrics.processors.sampler import SamplingProcessor
p = SamplingProcessor(rate=0.5).deterministic()
print(p.should_sample({"id": "stable-key"}))
"""

    result_one = subprocess.check_output(
        [sys.executable, "-c", code],
        text=True,
    ).strip()

    result_two = subprocess.check_output(
        [sys.executable, "-c", code],
        text=True,
    ).strip()

    assert result_one == result_two


# ==============================================================
# Statistics
# ==============================================================


def test_statistics():
    processor = SamplingProcessor(
        rate=1.0
    )

    processor.transform("a")
    processor.transform("b")

    stats = processor.statistics()

    assert stats["rate"] == 1.0
    assert stats["total"] == 2
    assert stats["sampled"] == 2
    assert stats["dropped"] == 0
    assert stats["efficiency"] == 1.0


def test_statistics_with_drops():
    processor = SamplingProcessor(
        rate=0.0
    )

    processor.transform("a")
    processor.transform("b")
    processor.transform("c")

    stats = processor.statistics()

    assert stats["total"] == 3
    assert stats["sampled"] == 0
    assert stats["dropped"] == 3
    assert stats["efficiency"] == 0.0


def test_statistics_empty():
    processor = SamplingProcessor()

    stats = processor.statistics()

    assert stats["total"] == 0
    assert stats["sampled"] == 0
    assert stats["dropped"] == 0
    assert stats["efficiency"] == 0.0


# ==============================================================
# Reset
# ==============================================================


def test_reset_preserves_configuration():
    processor = SamplingProcessor(
        rate=0.25
    )

    processor.transform("a")
    processor.transform("b")

    processor.reset()

    stats = processor.statistics()

    assert stats["total"] == 0
    assert stats["sampled"] == 0
    assert stats["dropped"] == 0
    assert processor.rate() == 0.25


def test_reset_returns_self():
    processor = SamplingProcessor()

    assert processor.reset() is processor


# ==============================================================
# Representation
# ==============================================================


def test_repr():
    processor = SamplingProcessor(
        rate=1.0
    )

    processor.transform("metric")

    text = repr(processor)

    assert "SamplingProcessor" in text
    assert "rate=1.0" in text
    assert "sampled=1" in text
    assert "dropped=0" in text


# ==============================================================
# Alias
# ==============================================================


def test_sampler_processor_alias():
    assert SamplerProcessor is SamplingProcessor