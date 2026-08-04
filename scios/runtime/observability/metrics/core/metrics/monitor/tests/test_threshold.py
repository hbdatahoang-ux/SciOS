"""
Unit tests for threshold.py

Part 1. Imports & Fixtures
Part 2. Dummy Data
Part 3. Construction
Part 4. Properties
"""

from __future__ import annotations

import threading
from datetime import UTC, datetime

import pytest

import copy
import pickle

from scios.runtime.observability.metrics.core.metrics.monitor.threshold import (
    DEFAULT_HIGH,
    DEFAULT_LOW,
    DEFAULT_NAME,
    DEFAULT_UNIT,
    DEFAULT_VERSION,
    MetricThreshold,
)


# ==========================================================
# Part 1. Imports & Fixtures
# ==========================================================


@pytest.fixture()
def threshold() -> MetricThreshold:
    return MetricThreshold()


@pytest.fixture()
def custom_threshold() -> MetricThreshold:
    return MetricThreshold(
        low=10.0,
        high=90.0,
        name="cpu",
        unit="%",
        metadata={"node": "A"},
    )


# ==========================================================
# Part 2. Dummy Data
# ==========================================================


class DummyValues:
    LOW = 5.0
    MID = 50.0
    HIGH = 95.0


# ==========================================================
# Part 3. Construction
# ==========================================================


class TestConstruction:

    def test_create_default(self):

        obj = MetricThreshold()

        assert obj.low == DEFAULT_LOW
        assert obj.high == DEFAULT_HIGH
        assert obj.name == DEFAULT_NAME
        assert obj.unit == DEFAULT_UNIT
        assert obj.version == DEFAULT_VERSION

        assert obj.metadata == {}

        assert obj.enabled is True

    def test_create_custom(self):

        obj = MetricThreshold(
            low=1.5,
            high=8.5,
            name="temperature",
            unit="°C",
            metadata={"room": "lab"},
        )

        assert obj.low == 1.5
        assert obj.high == 8.5
        assert obj.name == "temperature"
        assert obj.unit == "°C"
        assert obj.metadata["room"] == "lab"


# ==========================================================
# Part 4. Properties
# ==========================================================


class TestProperties:

    def test_low(self, custom_threshold):

        assert custom_threshold.low == 10.0

    def test_high(self, custom_threshold):

        assert custom_threshold.high == 90.0

    def test_name(self, custom_threshold):

        assert custom_threshold.name == "cpu"

    def test_unit(self, custom_threshold):

        assert custom_threshold.unit == "%"

    def test_timestamp(self, threshold):

        assert isinstance(threshold.timestamp, datetime)
        assert threshold.timestamp.tzinfo is UTC

    def test_version(self, threshold):

        assert threshold.version == DEFAULT_VERSION

    def test_metadata(self, custom_threshold):

        assert isinstance(custom_threshold.metadata, dict)
        assert custom_threshold.metadata["node"] == "A"

    def test_enabled(self, threshold):

        assert threshold.enabled is True

    def test_lock(self, threshold):

        assert isinstance(threshold.lock, type(threading.RLock()))

# ==========================================================
# Part 5. Threshold API
# ==========================================================


class TestThresholdAPI:

    def test_set(self, threshold):

        threshold.set(low=20.0, high=80.0)

        assert threshold.low == 20.0
        assert threshold.high == 80.0

    def test_clear(self, threshold):

        threshold.set(low=1.0, high=9.0)

        threshold.clear()

        assert threshold.low == DEFAULT_LOW
        assert threshold.high == DEFAULT_HIGH

    def test_reset(self, threshold):

        threshold.set(low=5.0, high=95.0)

        threshold.reset()

        assert threshold.low == DEFAULT_LOW
        assert threshold.high == DEFAULT_HIGH
        assert threshold.metadata == {}

    def test_update(self, threshold):

        threshold.update(low=15.0)

        assert threshold.low == 15.0
        assert threshold.high == DEFAULT_HIGH

        threshold.update(high=70.0)

        assert threshold.high == 70.0

    def test_enable(self, threshold):

        threshold.disable()

        threshold.enable()

        assert threshold.enabled is True

    def test_disable(self, threshold):

        threshold.disable()

        assert threshold.enabled is False

    def test_toggle(self, threshold):

        current = threshold.enabled

        threshold.toggle()

        assert threshold.enabled is (not current)


# ==========================================================
# Part 6. Comparison API
# ==========================================================


class TestComparisonAPI:

    def test_exceeded(self, custom_threshold):

        assert custom_threshold.exceeded(DummyValues.HIGH) is True
        assert custom_threshold.exceeded(DummyValues.MID) is False

    def test_below(self, custom_threshold):

        assert custom_threshold.below(DummyValues.LOW) is True
        assert custom_threshold.below(DummyValues.MID) is False

    def test_within(self, custom_threshold):

        assert custom_threshold.within(DummyValues.MID) is True
        assert custom_threshold.within(DummyValues.LOW) is False
        assert custom_threshold.within(DummyValues.HIGH) is False

    def test_compare(self, custom_threshold):

        result = custom_threshold.compare(DummyValues.MID)

        assert result is not None

    def test_evaluate(self, custom_threshold):

        result = custom_threshold.evaluate(DummyValues.HIGH)

        assert result is not None


# ==========================================================
# Part 7. Metadata API
# ==========================================================


class TestMetadataAPI:

    def test_set_metadata(self, threshold):

        threshold.set_metadata("host", "node1")

        assert threshold.metadata["host"] == "node1"

    def test_update_metadata(self, threshold):

        threshold.update_metadata(
            {
                "a": 1,
                "b": 2,
            }
        )

        assert threshold.metadata["a"] == 1
        assert threshold.metadata["b"] == 2

    def test_clear_metadata(self, threshold):

        threshold.update_metadata({"x": 1})

        threshold.clear_metadata()

        assert threshold.metadata == {}


# ==========================================================
# Part 8. Serialization
# ==========================================================


class TestSerialization:

    def test_to_dict(self, custom_threshold):

        data = custom_threshold.to_dict()

        assert isinstance(data, dict)

        assert data["low"] == 10.0
        assert data["high"] == 90.0

    def test_from_dict(self, custom_threshold):

        restored = MetricThreshold.from_dict(
            custom_threshold.to_dict()
        )

        assert restored == custom_threshold

    def test_to_json(self, custom_threshold):

        text = custom_threshold.to_json()

        assert isinstance(text, str)

    def test_from_json(self, custom_threshold):

        restored = MetricThreshold.from_json(
            custom_threshold.to_json()
        )

        assert restored == custom_threshold

    def test_roundtrip_dict(self, custom_threshold):

        restored = MetricThreshold.from_dict(
            custom_threshold.to_dict()
        )

        assert restored.to_dict() == custom_threshold.to_dict()

    def test_roundtrip_json(self, custom_threshold):

        restored = MetricThreshold.from_json(
            custom_threshold.to_json()
        )

        assert restored.to_dict() == custom_threshold.to_dict()


# ==========================================================
# Part 9. Validation
# ==========================================================


class TestValidation:

    def test_validate(self, threshold):

        assert threshold.validate() is True

    def test_is_valid(self, threshold):

        assert threshold.is_valid() is True

# ==========================================================
# Part 10. Snapshot API
# ==========================================================




class TestSnapshot:

    def test_copy(self, threshold: MetricThreshold):

        clone = threshold.copy()

        assert clone == threshold
        assert clone is not threshold

    def test_deepcopy(self, threshold: MetricThreshold):

        clone = copy.deepcopy(threshold)

        assert clone == threshold
        assert clone is not threshold

    def test_clone(self, threshold: MetricThreshold):

        clone = threshold.clone()

        assert clone == threshold
        assert clone is not threshold


# ==========================================================
# Part 11. Python Protocols
# ==========================================================


class TestPythonProtocols:

    def test_repr(self, threshold: MetricThreshold):

        text = repr(threshold)

        assert isinstance(text, str)
        assert "MetricThreshold" in text

    def test_str(self, threshold: MetricThreshold):

        text = str(threshold)

        assert isinstance(text, str)

    def test_bool(self, threshold: MetricThreshold):

        assert bool(threshold) is threshold.enabled

    def test_len(self, threshold: MetricThreshold):

        threshold.update_metadata({"a": 1, "b": 2})

        assert len(threshold) == 2

    def test_eq(self):

        a = MetricThreshold()
        b = MetricThreshold()

        assert a == b

    def test_hash(self):

        value = hash(MetricThreshold())

        assert isinstance(value, int)

    def test_pickle(self, threshold: MetricThreshold):

        restored = pickle.loads(pickle.dumps(threshold))

        assert restored == threshold


# ==========================================================
# Part 12. Diagnostics API
# ==========================================================


class TestDiagnosticsAPI:

    def test_summary(self, threshold: MetricThreshold):

        result = threshold.summary()

        assert isinstance(result, str)

    def test_diagnostics(self, threshold: MetricThreshold):

        result = threshold.diagnostics()

        assert isinstance(result, dict)

    def test_threshold_report(self, threshold: MetricThreshold):

        result = threshold.threshold_report()

        assert isinstance(result, dict)

    def test_overall_status(self, threshold: MetricThreshold):

        result = threshold.overall_status()

        assert result is not None


# ==========================================================
# Part 13. API Freeze
# ==========================================================


class TestAPIFreeze:

    def test_public_api(self):

        expected = {
            "set",
            "clear",
            "reset",
            "update",
            "enable",
            "disable",
            "toggle",
            "exceeded",
            "below",
            "within",
            "compare",
            "evaluate",
            "set_metadata",
            "update_metadata",
            "clear_metadata",
            "to_dict",
            "from_dict",
            "to_json",
            "from_json",
            "validate",
            "is_valid",
            "copy",
            "deepcopy",
            "clone",
            "summary",
            "diagnostics",
            "threshold_report",
            "overall_status",
        }

        for name in expected:
            assert hasattr(MetricThreshold, name)

    def test_annotations(self):

        assert hasattr(MetricThreshold, "__annotations__")

    def test_slots(self):

        assert hasattr(MetricThreshold, "__slots__")

    def test_signature(self):

        import inspect

        sig = inspect.signature(MetricThreshold)

        assert sig is not None                