"""
Tests for SciOS Runtime Metrics Processor.

Python 3.11+
"""

from __future__ import annotations

import pytest

from scios.runtime.observability.metrics.processors.processor import (
    MetricProcessor,
)


# ==========================================================
# Construction
# ==========================================================


def test_default_constructor():
    processor = MetricProcessor()

    assert processor.name == "MetricProcessor"
    assert processor.description == ""
    assert processor.enabled is True
    assert processor.processed == 0
    assert processor.failed == 0
    assert processor.dropped == 0


def test_custom_constructor():
    processor = MetricProcessor(
        name="TestProcessor",
        description="test processor",
        enabled=False,
    )

    assert processor.name == "TestProcessor"
    assert processor.description == "test processor"
    assert processor.enabled is False


def test_name_must_be_string():
    with pytest.raises(TypeError):
        MetricProcessor(name=123)


def test_name_must_not_be_empty():
    with pytest.raises(ValueError):
        MetricProcessor(name="")


def test_description_must_be_string():
    with pytest.raises(TypeError):
        MetricProcessor(description=123)


# ==========================================================
# Properties
# ==========================================================


def test_properties_are_read_only():
    processor = MetricProcessor()

    with pytest.raises(AttributeError):
        processor.name = "other"

    with pytest.raises(AttributeError):
        processor.enabled = False


# ==========================================================
# Transform
# ==========================================================


def test_transform_is_identity():
    processor = MetricProcessor()

    metric = {
        "name": "requests",
        "value": 1,
    }

    assert processor.transform(metric) is metric


def test_process_returns_transformed_metric():
    processor = MetricProcessor()

    metric = {
        "name": "requests",
        "value": 1,
    }

    result = processor.process(metric)

    assert result is metric
    assert processor.processed == 1
    assert processor.failed == 0
    assert processor.dropped == 0


def test_process_forwards_kwargs():
    class TestProcessor(MetricProcessor):
        def transform(self, metric, **kwargs):
            metric["extra"] = kwargs["extra"]
            return metric

    processor = TestProcessor()

    metric = {}

    result = processor.process(
        metric,
        extra="value",
    )

    assert result["extra"] == "value"
    assert processor.processed == 1


# ==========================================================
# Disabled Lifecycle
# ==========================================================


def test_disabled_processor_passes_metric_through():
    class TestProcessor(MetricProcessor):
        def transform(self, metric, **kwargs):
            raise AssertionError(
                "transform must not run when disabled"
            )

    processor = TestProcessor(
        enabled=False
    )

    metric = {"value": 1}

    result = processor.process(metric)

    assert result is metric
    assert processor.processed == 0
    assert processor.failed == 0
    assert processor.dropped == 0


def test_enable():
    processor = MetricProcessor(
        enabled=False
    )

    result = processor.enable()

    assert result is processor
    assert processor.enabled is True


def test_disable():
    processor = MetricProcessor()

    result = processor.disable()

    assert result is processor
    assert processor.enabled is False


def test_enable_disable_chain():
    processor = MetricProcessor()

    assert (
        processor
        .disable()
        .enable()
        .disable()
        .enable()
        is processor
    )

    assert processor.enabled is True


# ==========================================================
# Drop Semantics
# ==========================================================


def test_none_result_is_counted_as_dropped():
    class DropProcessor(MetricProcessor):
        def transform(self, metric, **kwargs):
            return None

    processor = DropProcessor()

    assert processor.process({"value": 1}) is None

    assert processor.processed == 1
    assert processor.failed == 0
    assert processor.dropped == 1


def test_multiple_dropped_metrics():
    class DropProcessor(MetricProcessor):
        def transform(self, metric, **kwargs):
            return None

    processor = DropProcessor()

    processor.process(1)
    processor.process(2)
    processor.process(3)

    assert processor.processed == 3
    assert processor.dropped == 3


# ==========================================================
# Failure Semantics
# ==========================================================


def test_transform_exception_is_counted_and_reraised():
    class FailingProcessor(MetricProcessor):
        def transform(self, metric, **kwargs):
            raise RuntimeError("processing failed")

    processor = FailingProcessor()

    with pytest.raises(RuntimeError, match="processing failed"):
        processor.process({"value": 1})

    assert processor.processed == 0
    assert processor.failed == 1
    assert processor.dropped == 0


def test_failed_processing_is_not_counted_as_processed():
    class FailingProcessor(MetricProcessor):
        def transform(self, metric, **kwargs):
            raise ValueError("invalid metric")

    processor = FailingProcessor()

    with pytest.raises(ValueError):
        processor.process(1)

    assert processor.processed == 0
    assert processor.failed == 1


# ==========================================================
# Callable Protocol
# ==========================================================


def test_processor_is_callable():
    processor = MetricProcessor()

    metric = {"value": 10}

    result = processor(metric)

    assert result is metric
    assert processor.processed == 1


def test_callable_forwards_kwargs():
    class TestProcessor(MetricProcessor):
        def transform(self, metric, **kwargs):
            return metric + kwargs["amount"]

    processor = TestProcessor()

    assert processor(10, amount=5) == 15
    assert processor.processed == 1


# ==========================================================
# Statistics
# ==========================================================


def test_statistics_initial_state():
    processor = MetricProcessor(
        name="TestProcessor",
        description="test",
    )

    assert processor.statistics() == {
        "name": "TestProcessor",
        "description": "test",
        "enabled": True,
        "processed": 0,
        "failed": 0,
        "dropped": 0,
    }


def test_statistics_after_processing():
    class DropProcessor(MetricProcessor):
        def transform(self, metric, **kwargs):
            if metric < 0:
                return None

            return metric

    processor = DropProcessor(
        name="TestProcessor"
    )

    processor.process(1)
    processor.process(-1)

    statistics = processor.statistics()

    assert statistics["name"] == "TestProcessor"
    assert statistics["processed"] == 2
    assert statistics["failed"] == 0
    assert statistics["dropped"] == 1


# ==========================================================
# Reset
# ==========================================================


def test_reset_clears_runtime_statistics():
    class TestProcessor(MetricProcessor):
        def transform(self, metric, **kwargs):
            if metric is None:
                return None

            return metric

    processor = TestProcessor(
        name="TestProcessor",
        description="persistent configuration",
    )

    processor.process(1)
    processor.process(None)

    assert processor.processed == 2
    assert processor.dropped == 1

    result = processor.reset()

    assert result is processor

    assert processor.processed == 0
    assert processor.failed == 0
    assert processor.dropped == 0

    assert processor.name == "TestProcessor"
    assert processor.description == "persistent configuration"
    assert processor.enabled is True


# ==========================================================
# Python Protocols
# ==========================================================


def test_len():
    processor = MetricProcessor()

    assert len(processor) == 0

    processor.process(1)
    processor.process(2)

    assert len(processor) == 2


def test_bool():
    processor = MetricProcessor()

    assert bool(processor) is False

    processor.process(1)

    assert bool(processor) is True


def test_repr():
    processor = MetricProcessor(
        name="TestProcessor"
    )

    representation = repr(processor)

    assert "TestProcessor" in representation
    assert "processed=0" in representation
    assert "failed=0" in representation
    assert "dropped=0" in representation


def test_str():
    processor = MetricProcessor(
        name="TestProcessor"
    )

    assert str(processor) == "TestProcessor"


# ==========================================================
# Reset After Failure
# ==========================================================


def test_reset_clears_failure_statistics():
    class FailingProcessor(MetricProcessor):
        def transform(self, metric, **kwargs):
            raise RuntimeError("failure")

    processor = FailingProcessor()

    with pytest.raises(RuntimeError):
        processor.process(1)

    assert processor.failed == 1

    processor.reset()

    assert processor.failed == 0
    assert processor.processed == 0
    assert processor.dropped == 0