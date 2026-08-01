# ==========================================================
# Part 1. Imports
# ==========================================================

from __future__ import annotations

import copy
import inspect
import pickle
import time
from typing import get_type_hints

import pytest

from scios.runtime.observability.metrics.core.metrics.core.metric import (
    Metric,
)


# ==========================================================
# Part 2. Fixtures
# ==========================================================

@pytest.fixture
def empty_metric() -> Metric:
    return Metric()


@pytest.fixture
def custom_metric() -> Metric:
    return Metric(
        name="requests_total",
        value=100,
        unit="count",
        labels={
            "service": "runtime",
        },
        timestamp=123.456,
    )


@pytest.fixture
def full_metric() -> Metric:
    return Metric(
        name="cpu_usage",
        value=87.5,
        unit="%",
        labels={
            "host": "localhost",
            "service": "runtime",
            "region": "local",
        },
        timestamp=999.999,
    )


# ==========================================================
# Part 3. Construction
# ==========================================================

class TestConstruction:

    def test_create_default(self):
        metric = Metric()

        assert isinstance(metric, Metric)

    def test_create_custom(
        self,
        custom_metric: Metric,
    ):
        assert custom_metric.name == "requests_total"
        assert custom_metric.value == 100
        assert custom_metric.unit == "count"

    def test_create_empty(
        self,
        empty_metric: Metric,
    ):
        assert empty_metric.name == ""
        assert empty_metric.labels == {}

    def test_create_full(
        self,
        full_metric: Metric,
    ):
        assert full_metric.name == "cpu_usage"
        assert full_metric.value == 87.5
        assert full_metric.unit == "%"
        assert len(full_metric.labels) == 3

# ==========================================================
# Part 4. Identity
# ==========================================================

class TestIdentity:

    def test_name(
        self,
        custom_metric: Metric,
    ):
        assert custom_metric.name == "requests_total"

    def test_value(
        self,
        custom_metric: Metric,
    ):
        assert custom_metric.value == 100

    def test_unit(
        self,
        custom_metric: Metric,
    ):
        assert custom_metric.unit == "count"

    def test_labels(
        self,
        custom_metric: Metric,
    ):
        assert custom_metric.labels == {
            "service": "runtime",
        }

    def test_timestamp(
        self,
        custom_metric: Metric,
    ):
        assert custom_metric.timestamp == 123.456


# ==========================================================
# Part 5. Defaults
# ==========================================================

class TestDefaults:

    def test_default_value(
        self,
        empty_metric: Metric,
    ):
        assert empty_metric.value == 0

    def test_default_labels(
        self,
        empty_metric: Metric,
    ):
        assert empty_metric.labels == {}

    def test_default_mutable_independent(self):
        a = Metric()
        b = Metric()

        a.labels["x"] = "1"

        assert b.labels == {}


# ==========================================================
# Part 6. Mutation
# ==========================================================

class TestMutation:

    def test_set_value(
        self,
        custom_metric: Metric,
    ):
        custom_metric.value = 999

        assert custom_metric.value == 999

    def test_update_labels(
        self,
        custom_metric: Metric,
    ):
        custom_metric.labels["env"] = "prod"

        assert custom_metric.labels["env"] == "prod"

    def test_clear_labels(
        self,
        custom_metric: Metric,
    ):
        custom_metric.labels.clear()

        assert custom_metric.labels == {}

    def test_touch(
        self,
        custom_metric: Metric,
    ):
        old = custom_metric.timestamp

        time.sleep(0.001)

        custom_metric.touch()

        assert custom_metric.timestamp >= old

# ==========================================================
# Part 7. Serialization
# ==========================================================

class TestSerialization:

    def test_to_dict(
        self,
        full_metric: Metric,
    ):
        data = full_metric.to_dict()

        assert isinstance(data, dict)
        assert data["name"] == full_metric.name
        assert data["value"] == full_metric.value
        assert data["unit"] == full_metric.unit
        assert data["labels"] == full_metric.labels
        assert data["timestamp"] == full_metric.timestamp

    def test_from_dict(
        self,
        full_metric: Metric,
    ):
        restored = Metric.from_dict(
            full_metric.to_dict(),
        )

        assert restored == full_metric

    def test_to_json(
        self,
        full_metric: Metric,
    ):
        payload = full_metric.to_json()

        assert isinstance(payload, str)

    def test_from_json(
        self,
        full_metric: Metric,
    ):
        restored = Metric.from_json(
            full_metric.to_json(),
        )

        assert restored == full_metric

    def test_roundtrip_dict(
        self,
        full_metric: Metric,
    ):
        restored = Metric.from_dict(
            full_metric.to_dict(),
        )

        assert restored == full_metric

    def test_roundtrip_json(
        self,
        full_metric: Metric,
    ):
        restored = Metric.from_json(
            full_metric.to_json(),
        )

        assert restored == full_metric


# ==========================================================
# Part 8. Validation
# ==========================================================

class TestValidation:

    def test_validate(
        self,
        full_metric: Metric,
    ):
        full_metric.validate()

    def test_validate_invalid_name(self):
        metric = Metric(
            name="",
        )

        with pytest.raises(Exception):
            metric.validate()

    def test_validate_invalid_value(self):
        metric = Metric(
            value="invalid",  # type: ignore[arg-type]
        )

        with pytest.raises(Exception):
            metric.validate()

    def test_is_valid(
        self,
        full_metric: Metric,
    ):
        assert full_metric.is_valid() is True


# ==========================================================
# Part 9. Comparison
# ==========================================================

class TestComparison:

    def test_equals(
        self,
        full_metric: Metric,
    ):
        copied = full_metric.copy()

        assert copied == full_metric

    def test_not_equals(
        self,
        full_metric: Metric,
    ):
        copied = full_metric.copy()
        copied.value += 1

        assert copied != full_metric

    def test_hash(
        self,
        full_metric: Metric,
    ):
        assert isinstance(
            hash(full_metric),
            int,
        )

    def test_copy_equality(
        self,
        full_metric: Metric,
    ):
        copied = full_metric.copy()

        assert copied == full_metric
        assert copied is not full_metric

# ==========================================================
# Part 10. Snapshot
# ==========================================================

class TestSnapshot:

    def test_copy(
        self,
        full_metric: Metric,
    ):
        copied = full_metric.copy()

        assert copied == full_metric
        assert copied is not full_metric

    def test_deepcopy(
        self,
        full_metric: Metric,
    ):
        copied = copy.deepcopy(full_metric)

        assert copied == full_metric
        assert copied is not full_metric

    def test_clone(
        self,
        full_metric: Metric,
    ):
        cloned = full_metric.clone()

        assert cloned == full_metric
        assert cloned is not full_metric

    def test_replace(
        self,
        full_metric: Metric,
    ):
        replaced = full_metric.replace(
            value=999,
        )

        assert replaced.value == 999
        assert full_metric.value != 999


# ==========================================================
# Part 11. Python Protocols
# ==========================================================

class TestPythonProtocols:

    def test_repr(
        self,
        full_metric: Metric,
    ):
        assert isinstance(repr(full_metric), str)

    def test_str(
        self,
        full_metric: Metric,
    ):
        assert isinstance(str(full_metric), str)

    def test_bool(
        self,
        full_metric: Metric,
    ):
        assert bool(full_metric)

    def test_len(
        self,
        full_metric: Metric,
    ):
        assert len(full_metric) == len(full_metric.labels)

    def test_iter(
        self,
        full_metric: Metric,
    ):
        assert list(iter(full_metric)) == list(full_metric.labels)

    def test_contains(
        self,
        full_metric: Metric,
    ):
        key = next(iter(full_metric.labels))

        assert key in full_metric

    def test_getitem(
        self,
        full_metric: Metric,
    ):
        key = next(iter(full_metric.labels))

        assert full_metric[key] == full_metric.labels[key]

    def test_setitem(
        self,
        full_metric: Metric,
    ):
        full_metric["new"] = "value"

        assert full_metric["new"] == "value"

    def test_delitem(
        self,
        full_metric: Metric,
    ):
        key = next(iter(full_metric.labels))

        del full_metric[key]

        assert key not in full_metric

    def test_hash_protocol(
        self,
        full_metric: Metric,
    ):
        assert isinstance(hash(full_metric), int)


# ==========================================================
# Part 12. API Freeze
# ==========================================================

class TestAPIFreeze:

    def test_public_api(self):
        expected = {
            "copy",
            "clone",
            "deepcopy",
            "replace",
            "validate",
            "is_valid",
            "to_dict",
            "from_dict",
            "to_json",
            "from_json",
            "touch",
        }

        public = {
            name
            for name in dir(Metric)
            if not name.startswith("_")
        }

        assert expected <= public

    def test_annotations(self):
        hints = get_type_hints(Metric)

        assert isinstance(hints, dict)

    def test_slots(self):
        assert hasattr(Metric, "__slots__")

    def test_signature(self):
        signature = inspect.signature(Metric)

        assert signature is not None

    def test_pickle(
        self,
        full_metric: Metric,
    ):
        restored = pickle.loads(
            pickle.dumps(full_metric),
        )

        assert restored == full_metric                        