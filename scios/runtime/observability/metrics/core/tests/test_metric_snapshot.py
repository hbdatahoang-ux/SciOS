# ==============================================================================
# Part 1. Imports
# ==============================================================================

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from scios.runtime.observability.metrics.core.metric_snapshot import (
    MetricSnapshot,
    SNAPSHOT_VERSION,
)


# ==============================================================================
# Part 2. Construction
# ==============================================================================


def test_default_snapshot():

    snapshot = MetricSnapshot()

    assert snapshot.snapshot == {}
    assert snapshot.version == SNAPSHOT_VERSION
    assert isinstance(snapshot.created_at, datetime)


def test_custom_snapshot():

    now = datetime.now(timezone.utc)

    snapshot = MetricSnapshot(
        snapshot={"a": 1},
        created_at=now,
        version="1.0",
    )

    assert snapshot.snapshot == {"a": 1}
    assert snapshot.created_at == now
    assert snapshot.version == "1.0"


# ==============================================================================
# Part 3. Defaults
# ==============================================================================


def test_empty_snapshot():

    snapshot = MetricSnapshot()

    assert snapshot.is_empty()


# ==============================================================================
# Part 4. Validation
# ==============================================================================


def test_invalid_snapshot():

    with pytest.raises(TypeError):
        MetricSnapshot(snapshot=[])


def test_invalid_payload():

    snapshot = MetricSnapshot()

    assert snapshot.validate()

    snapshot.snapshot = []  # type: ignore

    assert not snapshot.validate()


# ==============================================================================
# Part 5. Properties
# ==============================================================================


def test_snapshot():

    snapshot = MetricSnapshot(
        snapshot={"x": 1},
    )

    payload = snapshot.payload

    assert payload == {"x": 1}

    payload["x"] = 99

    assert snapshot.snapshot["x"] == 1


def test_timestamp():

    snapshot = MetricSnapshot()

    assert snapshot.timestamp == snapshot.created_at


# ==============================================================================
# Part 6. Snapshot Operations
# ==============================================================================


def test_capture():

    snapshot = MetricSnapshot.capture(
        {"a": 1},
    )

    assert snapshot.snapshot == {"a": 1}


def test_restore():

    original = MetricSnapshot.capture(
        {"a": 1},
    )

    restored = original.copy()

    assert restored == original
    assert restored is not original


def test_merge():

    left = MetricSnapshot.capture(
        {"a": 1},
    )

    right = MetricSnapshot.capture(
        {
            "b": 2,
            "c": 3,
        }
    )

    merged = left.merge(right)

    assert merged.snapshot == {
        "a": 1,
        "b": 2,
        "c": 3,
    }


def test_diff():

    left = MetricSnapshot.capture(
        {
            "a": 1,
            "b": 2,
        }
    )

    right = MetricSnapshot.capture(
        {
            "a": 1,
            "b": 3,
            "c": 4,
        }
    )

    diff = left.diff(right)

    assert diff["b"] == (2, 3)
    assert diff["c"] == (None, 4)


def test_clear():

    snapshot = MetricSnapshot.capture(
        {"a": 1},
    )

    snapshot.clear()

    assert snapshot.snapshot == {}


def test_is_empty():

    snapshot = MetricSnapshot()

    assert snapshot.is_empty()

    snapshot.snapshot["x"] = 1

    assert not snapshot.is_empty()


def test_checksum():

    first = MetricSnapshot.capture(
        {"a": 1},
    )

    second = MetricSnapshot.capture(
        {"a": 1},
    )

    assert first.checksum() == second.checksum()

# ==============================================================================
# Part 7. Serialization
# ==============================================================================


def test_to_dict():

    snapshot = MetricSnapshot.capture(
        {"a": 1},
    )

    data = snapshot.to_dict()

    assert data["snapshot"] == {"a": 1}
    assert data["version"] == SNAPSHOT_VERSION
    assert "created_at" in data


def test_from_dict():

    original = MetricSnapshot.capture(
        {"a": 1},
    )

    restored = MetricSnapshot.from_dict(
        original.to_dict(),
    )

    assert restored == original


def test_to_json():

    snapshot = MetricSnapshot.capture(
        {"a": 1},
    )

    payload = snapshot.to_json()

    assert isinstance(payload, str)
    assert '"snapshot"' in payload


def test_from_json():

    original = MetricSnapshot.capture(
        {"a": 1},
    )

    restored = MetricSnapshot.from_json(
        original.to_json(),
    )

    assert restored == original


# ==============================================================================
# Part 8. Copy
# ==============================================================================


def test_copy():

    snapshot = MetricSnapshot.capture(
        {"a": 1},
    )

    copied = snapshot.copy()

    assert copied == snapshot
    assert copied is not snapshot


def test_clone():

    snapshot = MetricSnapshot.capture(
        {"a": 1},
    )

    cloned = snapshot.clone()

    assert cloned == snapshot
    assert cloned is not snapshot


# ==============================================================================
# Part 9. Equality
# ==============================================================================


def test_eq():

    left = MetricSnapshot.capture(
        {"a": 1},
    )

    right = MetricSnapshot.from_dict(
        left.to_dict(),
    )

    assert left == right


def test_hash():

    snapshot = MetricSnapshot.capture(
        {"a": 1},
    )

    assert isinstance(hash(snapshot), int)


# ==============================================================================
# Part 10. Representation
# ==============================================================================


def test_repr():

    snapshot = MetricSnapshot.capture(
        {"a": 1},
    )

    assert "MetricSnapshot" in repr(snapshot)


def test_str():

    snapshot = MetricSnapshot.capture(
        {"a": 1},
    )

    assert "MetricSnapshot" in str(snapshot)


# ==============================================================================
# Part 11. Public API
# ==============================================================================


def test_all():

    from scios.runtime.observability.metrics.core.metric_snapshot import (
        __all__,
    )

    assert "MetricSnapshot" in __all__
    assert "SNAPSHOT_VERSION" in __all__


def test_version():

    assert SNAPSHOT_VERSION == "0.1.0"


# ==============================================================================
# Part 12. Regression
# ==============================================================================


def test_snapshot_is_copied():

    payload = {"a": 1}

    snapshot = MetricSnapshot.capture(
        payload,
    )

    payload["a"] = 100

    assert snapshot.snapshot["a"] == 1


def test_json_roundtrip():

    snapshot = MetricSnapshot.capture(
        {
            "a": 1,
            "b": 2,
        }
    )

    restored = MetricSnapshot.from_json(
        snapshot.to_json(),
    )

    assert restored == snapshot


def test_dict_roundtrip():

    snapshot = MetricSnapshot.capture(
        {
            "a": 1,
            "b": 2,
        }
    )

    restored = MetricSnapshot.from_dict(
        snapshot.to_dict(),
    )

    assert restored == snapshot


def test_restore_recovers_original_state():

    original = MetricSnapshot.capture(
        {
            "a": 1,
            "b": 2,
        }
    )

    restored = original.copy()

    restored.snapshot["b"] = 99

    restored = MetricSnapshot.from_dict(
        original.to_dict(),
    )

    assert restored == original


def test_merge_preserves_original_snapshot():

    left = MetricSnapshot.capture(
        {"a": 1},
    )

    right = MetricSnapshot.capture(
        {"b": 2},
    )

    merged = left.merge(right)

    assert left.snapshot == {"a": 1}
    assert right.snapshot == {"b": 2}
    assert merged.snapshot == {
        "a": 1,
        "b": 2,
    }


def test_diff_detects_changes():

    left = MetricSnapshot.capture(
        {
            "a": 1,
            "b": 2,
        }
    )

    right = MetricSnapshot.capture(
        {
            "a": 3,
            "b": 2,
            "c": 5,
        }
    )

    diff = left.diff(right)

    assert "a" in diff
    assert "c" in diff
    assert "b" not in diff    