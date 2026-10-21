# ==========================================================
# Part 1. Imports
# ==========================================================

from __future__ import annotations

import pickle

import pytest

from scios.runtime.observability.metrics.core.metrics.core.labels import (
    MetricLabels,
)


# ==========================================================
# Part 2. Fixtures
# ==========================================================

@pytest.fixture
def default_labels() -> MetricLabels:
    return MetricLabels()


@pytest.fixture
def custom_labels() -> MetricLabels:
    return MetricLabels(
        {
            "host": "localhost",
            "service": "runtime",
            "env": "test",
        }
    )


@pytest.fixture
def full_labels() -> MetricLabels:
    return MetricLabels(
        {
            "host": "node-01",
            "service": "metrics",
            "env": "production",
            "region": "ap-southeast-1",
            "version": "1.0.0",
        }
    )


# ==========================================================
# Part 3. Construction
# ==========================================================

class TestConstruction:

    def test_create_default(
        self,
        default_labels: MetricLabels,
    ):
        assert isinstance(default_labels, MetricLabels)

    def test_create_custom(
        self,
        custom_labels: MetricLabels,
    ):
        assert custom_labels["host"] == "localhost"

    def test_create_empty(self):
        labels = MetricLabels()

        assert len(labels) == 0

    def test_create_full(
        self,
        full_labels: MetricLabels,
    ):
        assert full_labels["region"] == "ap-southeast-1"
        assert full_labels["version"] == "1.0.0"


# ==========================================================
# Part 4. Identity
# ==========================================================

class TestIdentity:

    def test_items(
        self,
        custom_labels: MetricLabels,
    ):
        assert ("host", "localhost") in custom_labels.items()

    def test_keys(
        self,
        custom_labels: MetricLabels,
    ):
        assert set(custom_labels.keys()) == {
            "host",
            "service",
            "env",
        }

    def test_values(
        self,
        custom_labels: MetricLabels,
    ):
        assert set(custom_labels.values()) == {
            "localhost",
            "runtime",
            "test",
        }

    def test_length(
        self,
        custom_labels: MetricLabels,
    ):
        assert len(custom_labels) == 3

    def test_contains(
        self,
        custom_labels: MetricLabels,
    ):
        assert "host" in custom_labels
        assert "missing" not in custom_labels
# ==========================================================
# Part 5. Defaults
# ==========================================================

class TestDefaults:

    def test_default_empty(
        self,
        default_labels: MetricLabels,
    ):
        assert len(default_labels) == 0

    def test_default_mutable_independent(self):
        left = MetricLabels()
        right = MetricLabels()

        left["host"] = "node-01"

        assert "host" in left
        assert "host" not in right


# ==========================================================
# Part 6. Mutation
# ==========================================================

class TestMutation:

    def test_set_item(
        self,
        default_labels: MetricLabels,
    ):
        default_labels["host"] = "localhost"

        assert default_labels["host"] == "localhost"

    def test_update(
        self,
        default_labels: MetricLabels,
    ):
        default_labels.update(
            {
                "host": "localhost",
                "service": "runtime",
            }
        )

        assert default_labels["service"] == "runtime"

    def test_remove(
        self,
        custom_labels: MetricLabels,
    ):
        custom_labels.pop("env")

        assert "env" not in custom_labels

    def test_clear(
        self,
        custom_labels: MetricLabels,
    ):
        custom_labels.clear()

        assert len(custom_labels) == 0


# ==========================================================
# Part 7. Serialization
# ==========================================================

class TestSerialization:

    def test_to_dict(
        self,
        custom_labels: MetricLabels,
    ):
        data = custom_labels.to_dict()

        assert isinstance(data, dict)
        assert data["host"] == "localhost"

    def test_from_dict(
        self,
    ):
        labels = MetricLabels.from_dict(
            {
                "host": "localhost",
                "service": "runtime",
            }
        )

        assert labels["service"] == "runtime"

    def test_to_json(
        self,
        custom_labels: MetricLabels,
    ):
        text = custom_labels.to_json()

        assert isinstance(text, str)

    def test_from_json(
        self,
        custom_labels: MetricLabels,
    ):
        restored = MetricLabels.from_json(
            custom_labels.to_json(),
        )

        assert restored == custom_labels

    def test_roundtrip_dict(
        self,
        custom_labels: MetricLabels,
    ):
        restored = MetricLabels.from_dict(
            custom_labels.to_dict(),
        )

        assert restored == custom_labels

    def test_roundtrip_json(
        self,
        custom_labels: MetricLabels,
    ):
        restored = MetricLabels.from_json(
            custom_labels.to_json(),
        )

        assert restored == custom_labels
# ==========================================================
# Part 8. Validation
# ==========================================================

class TestValidation:

    def test_validate(
        self,
        custom_labels: MetricLabels,
    ):
        custom_labels.validate()

    def test_validate_invalid_key(self):
        labels = MetricLabels(
            {
                123: "value",
            }
        )

        with pytest.raises(Exception):
            labels.validate()

    def test_validate_invalid_value(self):
        labels = MetricLabels(
            {
                "host": 123,
            }
        )

        with pytest.raises(Exception):
            labels.validate()

    def test_is_valid(
        self,
        custom_labels: MetricLabels,
    ):
        assert custom_labels.is_valid() is True


# ==========================================================
# Part 9. Comparison
# ==========================================================

class TestComparison:

    def test_equals(
        self,
        custom_labels: MetricLabels,
    ):
        other = MetricLabels.from_dict(
            custom_labels.to_dict(),
        )

        assert custom_labels == other

    def test_not_equals(
        self,
        custom_labels: MetricLabels,
    ):
        other = MetricLabels(
            {
                "host": "other",
            }
        )

        assert custom_labels != other

    def test_hash(
        self,
        custom_labels: MetricLabels,
    ):
        assert isinstance(
            hash(custom_labels),
            int,
        )

    def test_copy_equality(
        self,
        custom_labels: MetricLabels,
    ):
        assert custom_labels.copy() == custom_labels


# ==========================================================
# Part 10. Snapshot
# ==========================================================

class TestSnapshot:

    def test_copy(
        self,
        custom_labels: MetricLabels,
    ):
        copied = custom_labels.copy()

        assert copied == custom_labels
        assert copied is not custom_labels

    def test_deepcopy(
        self,
        custom_labels: MetricLabels,
    ):
        copied = custom_labels.deepcopy()

        assert copied == custom_labels
        assert copied is not custom_labels

    def test_clone(
        self,
        custom_labels: MetricLabels,
    ):
        cloned = custom_labels.clone()

        assert cloned == custom_labels
        assert cloned is not custom_labels

    def test_replace(
        self,
        custom_labels: MetricLabels,
    ):
        replaced = custom_labels.replace(
            host="node-01",
        )

        assert replaced["host"] == "node-01"
        assert custom_labels["host"] == "localhost"
# ==========================================================
# Part 11. Python Protocols
# ==========================================================

class TestPythonProtocols:

    def test_repr(
        self,
        custom_labels: MetricLabels,
    ):
        assert isinstance(
            repr(custom_labels),
            str,
        )

    def test_str(
        self,
        custom_labels: MetricLabels,
    ):
        assert isinstance(
            str(custom_labels),
            str,
        )

    def test_bool(
        self,
        default_labels: MetricLabels,
        custom_labels: MetricLabels,
    ):
        assert bool(default_labels) is False
        assert bool(custom_labels) is True

    def test_len(
        self,
        custom_labels: MetricLabels,
    ):
        assert len(custom_labels) == 3

    def test_iter(
        self,
        custom_labels: MetricLabels,
    ):
        assert set(iter(custom_labels)) == {
            "host",
            "service",
            "env",
        }

    def test_contains(
        self,
        custom_labels: MetricLabels,
    ):
        assert "host" in custom_labels

    def test_getitem(
        self,
        custom_labels: MetricLabels,
    ):
        assert custom_labels["host"] == "localhost"

    def test_setitem(
        self,
        default_labels: MetricLabels,
    ):
        default_labels["host"] = "node"

        assert default_labels["host"] == "node"

    def test_delitem(
        self,
        custom_labels: MetricLabels,
    ):
        del custom_labels["env"]

        assert "env" not in custom_labels

    def test_hash_protocol(
        self,
        custom_labels: MetricLabels,
    ):
        assert isinstance(
            hash(custom_labels),
            int,
        )


# ==========================================================
# Part 12. API Freeze
# ==========================================================

class TestAPIFreeze:

    def test_public_api(self):
        assert hasattr(
            MetricLabels,
            "to_dict",
        )
        assert hasattr(
            MetricLabels,
            "from_dict",
        )
        assert hasattr(
            MetricLabels,
            "to_json",
        )
        assert hasattr(
            MetricLabels,
            "from_json",
        )

    def test_annotations(self):
        assert isinstance(
            MetricLabels.__annotations__,
            dict,
        )

    def test_slots(self):
        assert hasattr(
            MetricLabels,
            "__slots__",
        )

    def test_signature(self):
        assert callable(
            MetricLabels,
        )

    def test_pickle(
        self,
        custom_labels: MetricLabels,
    ):
        restored = pickle.loads(
            pickle.dumps(custom_labels),
        )

        assert restored == custom_labels                        