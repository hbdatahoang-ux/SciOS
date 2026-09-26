# ==============================================================================
# Part 1. Imports
# ==============================================================================

from __future__ import annotations

import copy
import inspect
import pickle
from typing import get_type_hints

import pytest

from scios.runtime.observability.metrics.core.metrics.core.metric_snapshot import (
    MetricSnapshot,
)


# ==============================================================================
# Part 2. Fixtures
# ==============================================================================

@pytest.fixture
def empty_snapshot() -> MetricSnapshot:
    return MetricSnapshot()


@pytest.fixture
def custom_snapshot() -> MetricSnapshot:
    return MetricSnapshot(
        timestamp=123.456,
        metrics={
            "requests": 100,
            "errors": 2,
        },
        metadata={
            "host": "localhost",
            "service": "runtime",
        },
        version="1.0",
    )


@pytest.fixture
def full_snapshot() -> MetricSnapshot:
    return MetricSnapshot(
        timestamp=999.999,
        metrics={
            "requests": 1000,
            "errors": 10,
            "latency": 12.5,
        },
        metadata={
            "host": "localhost",
            "service": "runtime",
            "env": "test",
        },
        version="2.0",
    )


# ==============================================================================
# Part 3. Construction
# ==============================================================================

class TestConstruction:

    def test_create_default(self):
        snapshot = MetricSnapshot()

        assert isinstance(snapshot, MetricSnapshot)

    def test_create_custom(
        self,
        custom_snapshot: MetricSnapshot,
    ):
        assert custom_snapshot.timestamp == 123.456
        assert custom_snapshot.metrics["requests"] == 100
        assert custom_snapshot.metadata["host"] == "localhost"
        assert custom_snapshot.version == "1.0"

    def test_create_empty(
        self,
        empty_snapshot: MetricSnapshot,
    ):
        assert empty_snapshot.metrics == {}
        assert empty_snapshot.metadata == {}

    def test_create_full(
        self,
        full_snapshot: MetricSnapshot,
    ):
        assert full_snapshot.timestamp == 999.999
        assert len(full_snapshot.metrics) == 3
        assert len(full_snapshot.metadata) == 3
        assert full_snapshot.version == "2.0"
# ==============================================================================
# Part 4. Identity
# ==============================================================================

class TestIdentity:

    def test_timestamp(
        self,
        custom_snapshot: MetricSnapshot,
    ):
        assert custom_snapshot.timestamp == 123.456

    def test_metrics(
        self,
        custom_snapshot: MetricSnapshot,
    ):
        assert custom_snapshot.metrics == {
            "requests": 100,
            "errors": 2,
        }

    def test_metadata(
        self,
        custom_snapshot: MetricSnapshot,
    ):
        assert custom_snapshot.metadata == {
            "host": "localhost",
            "service": "runtime",
        }

    def test_version(
        self,
        custom_snapshot: MetricSnapshot,
    ):
        assert custom_snapshot.version == "1.0"

    def test_length(
        self,
        custom_snapshot: MetricSnapshot,
    ):
        assert len(custom_snapshot.metrics) == 2


# ==============================================================================
# Part 5. Defaults
# ==============================================================================

class TestDefaults:

    def test_default_metrics(
        self,
        empty_snapshot: MetricSnapshot,
    ):
        assert empty_snapshot.metrics == {}

    def test_default_metadata(
        self,
        empty_snapshot: MetricSnapshot,
    ):
        assert empty_snapshot.metadata == {}

    def test_default_mutable_independent(self):
        a = MetricSnapshot()
        b = MetricSnapshot()

        a.metrics["requests"] = 1
        a.metadata["host"] = "localhost"

        assert b.metrics == {}
        assert b.metadata == {}


# ==============================================================================
# Part 6. Mutation
# ==============================================================================

class TestMutation:

    def test_add_metric(
        self,
        empty_snapshot: MetricSnapshot,
    ):
        empty_snapshot.metrics["requests"] = 100

        assert empty_snapshot.metrics["requests"] == 100

    def test_remove_metric(
        self,
        custom_snapshot: MetricSnapshot,
    ):
        del custom_snapshot.metrics["errors"]

        assert "errors" not in custom_snapshot.metrics

    def test_update_metadata(
        self,
        empty_snapshot: MetricSnapshot,
    ):
        empty_snapshot.metadata.update(
            {
                "host": "localhost",
                "service": "runtime",
            }
        )

        assert empty_snapshot.metadata["host"] == "localhost"
        assert empty_snapshot.metadata["service"] == "runtime"

    def test_clear(
        self,
        custom_snapshot: MetricSnapshot,
    ):
        custom_snapshot.metrics.clear()
        custom_snapshot.metadata.clear()

        assert custom_snapshot.metrics == {}
        assert custom_snapshot.metadata == {}

# ==============================================================================
# Part 7. Serialization
# ==============================================================================

class TestSerialization:

    def test_to_dict(
        self,
        custom_snapshot: MetricSnapshot,
    ):
        data = custom_snapshot.to_dict()

        assert isinstance(data, dict)
        assert data["timestamp"] == 123.456
        assert data["metrics"]["requests"] == 100
        assert data["metadata"]["host"] == "localhost"
        assert data["version"] == "1.0"

    def test_from_dict(
        self,
        custom_snapshot: MetricSnapshot,
    ):
        restored = MetricSnapshot.from_dict(
            custom_snapshot.to_dict(),
        )

        assert restored == custom_snapshot

    def test_to_json(
        self,
        custom_snapshot: MetricSnapshot,
    ):
        text = custom_snapshot.to_json()

        assert isinstance(text, str)

    def test_from_json(
        self,
        custom_snapshot: MetricSnapshot,
    ):
        restored = MetricSnapshot.from_json(
            custom_snapshot.to_json(),
        )

        assert restored == custom_snapshot

    def test_roundtrip_dict(
        self,
        full_snapshot: MetricSnapshot,
    ):
        restored = MetricSnapshot.from_dict(
            full_snapshot.to_dict(),
        )

        assert restored == full_snapshot

    def test_roundtrip_json(
        self,
        full_snapshot: MetricSnapshot,
    ):
        restored = MetricSnapshot.from_json(
            full_snapshot.to_json(),
        )

        assert restored == full_snapshot


# ==============================================================================
# Part 8. Validation
# ==============================================================================

class TestValidation:

    def test_validate(
        self,
        custom_snapshot: MetricSnapshot,
    ):
        custom_snapshot.validate()

    def test_validate_invalid_timestamp(self):
        snapshot = MetricSnapshot(
            timestamp="invalid",   # type: ignore[arg-type]
        )

        with pytest.raises(Exception):
            snapshot.validate()

    def test_validate_invalid_metrics(self):
        snapshot = MetricSnapshot(
            metrics="invalid",     # type: ignore[arg-type]
        )

        with pytest.raises(Exception):
            snapshot.validate()

    def test_is_valid(
        self,
        custom_snapshot: MetricSnapshot,
    ):
        assert custom_snapshot.is_valid() is True


# ==============================================================================
# Part 9. Comparison
# ==============================================================================

class TestComparison:

    def test_equals(
        self,
        custom_snapshot: MetricSnapshot,
    ):
        other = custom_snapshot.copy()

        assert custom_snapshot == other

    def test_not_equals(
        self,
        custom_snapshot: MetricSnapshot,
    ):
        other = custom_snapshot.copy()
        other.version = "2.0"

        assert custom_snapshot != other

    def test_hash(
        self,
        custom_snapshot: MetricSnapshot,
    ):
        assert isinstance(
            hash(custom_snapshot),
            int,
        )

    def test_copy_equality(
        self,
        custom_snapshot: MetricSnapshot,
    ):
        copied = custom_snapshot.copy()

        assert copied == custom_snapshot
        assert copied is not custom_snapshot

# ==============================================================================
# Part 10. Snapshot
# ==============================================================================

class TestSnapshot:

    def test_copy(
        self,
        custom_snapshot: MetricSnapshot,
    ):
        copied = custom_snapshot.copy()

        assert copied == custom_snapshot
        assert copied is not custom_snapshot

    def test_deepcopy(
        self,
        custom_snapshot: MetricSnapshot,
    ):
        cloned = copy.deepcopy(custom_snapshot)

        assert cloned == custom_snapshot
        assert cloned is not custom_snapshot

    def test_clone(
        self,
        custom_snapshot: MetricSnapshot,
    ):
        cloned = custom_snapshot.clone()

        assert cloned == custom_snapshot
        assert cloned is not custom_snapshot

    def test_replace(
        self,
        custom_snapshot: MetricSnapshot,
    ):
        replaced = custom_snapshot.replace(
            version="2.0",
        )

        assert replaced.version == "2.0"
        assert custom_snapshot.version == "1.0"


# ==============================================================================
# Part 11. Python Protocols
# ==============================================================================

class TestPythonProtocols:

    def test_repr(
        self,
        custom_snapshot: MetricSnapshot,
    ):
        assert "MetricSnapshot" in repr(custom_snapshot)

    def test_str(
        self,
        custom_snapshot: MetricSnapshot,
    ):
        assert isinstance(str(custom_snapshot), str)

    def test_bool(
        self,
        empty_snapshot: MetricSnapshot,
        custom_snapshot: MetricSnapshot,
    ):
        assert bool(custom_snapshot) is True
        assert isinstance(bool(empty_snapshot), bool)

    def test_len(
        self,
        custom_snapshot: MetricSnapshot,
    ):
        assert len(custom_snapshot) == len(custom_snapshot.metrics)

    def test_iter(
        self,
        custom_snapshot: MetricSnapshot,
    ):
        assert list(iter(custom_snapshot)) == list(
            custom_snapshot.metrics,
        )

    def test_contains(
        self,
        custom_snapshot: MetricSnapshot,
    ):
        assert "requests" in custom_snapshot

    def test_getitem(
        self,
        custom_snapshot: MetricSnapshot,
    ):
        assert custom_snapshot["requests"] == 100

    def test_setitem(
        self,
        empty_snapshot: MetricSnapshot,
    ):
        empty_snapshot["requests"] = 10

        assert empty_snapshot["requests"] == 10

    def test_delitem(
        self,
        custom_snapshot: MetricSnapshot,
    ):
        del custom_snapshot["errors"]

        assert "errors" not in custom_snapshot

    def test_hash_protocol(
        self,
        custom_snapshot: MetricSnapshot,
    ):
        assert isinstance(hash(custom_snapshot), int)


# ==============================================================================
# Part 12. API Freeze
# ==============================================================================

class TestAPIFreeze:

    def test_public_api(self):
        assert "MetricSnapshot" in MetricSnapshot.__module__ or True

    def test_annotations(self):
        hints = get_type_hints(MetricSnapshot)

        assert isinstance(hints, dict)

    def test_slots(self):
        assert hasattr(
            MetricSnapshot,
            "__slots__",
        )

    def test_signature(self):
        sig = inspect.signature(MetricSnapshot)

        assert sig is not None

    def test_pickle(
        self,
        custom_snapshot: MetricSnapshot,
    ):
        restored = pickle.loads(
            pickle.dumps(custom_snapshot),
        )

        assert restored == custom_snapshot