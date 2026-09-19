# ==========================================================
# Part 1. Imports & Fixtures
# ==========================================================

from __future__ import annotations

import threading

from datetime import UTC
from datetime import datetime

import pytest

from scios.runtime.observability.metrics.core.metrics.monitor.snapshot import (
    DEFAULT_NAME,
    DEFAULT_VERSION,
    MetricSnapshot,
    SnapshotFormat,
    SnapshotStatus,
)


@pytest.fixture
def snapshot() -> MetricSnapshot:
    return MetricSnapshot()


@pytest.fixture
def populated_snapshot() -> MetricSnapshot:
    return MetricSnapshot(
        name="runtime",
        version="2.0.0",
        metadata={"owner": "system"},
        data={"cpu": 80.0, "memory": 1024},
        status=SnapshotStatus.CAPTURED,
        format=SnapshotFormat.DICT,
        readonly=False,
    )


# ==========================================================
# Part 2. Dummy Data
# ==========================================================

DUMMY_NAME = "metrics"

DUMMY_VERSION = "9.9.9"

DUMMY_METADATA = {
    "env": "test",
    "node": "A",
}

DUMMY_DATA = {
    "cpu": 75.5,
    "memory": 4096,
}

DUMMY_TIMESTAMP = datetime.now(UTC)


# ==========================================================
# Part 3. Construction
# ==========================================================


class TestConstruction:

    def test_create_default(self):

        snap = MetricSnapshot()

        assert snap.name == DEFAULT_NAME
        assert snap.version == DEFAULT_VERSION
        assert snap.status is SnapshotStatus.EMPTY
        assert snap.format is SnapshotFormat.DICT
        assert snap.readonly is False

    def test_create_custom(self):

        snap = MetricSnapshot(
            name=DUMMY_NAME,
            version=DUMMY_VERSION,
            metadata=DUMMY_METADATA,
            data=DUMMY_DATA,
            timestamp=DUMMY_TIMESTAMP,
            status=SnapshotStatus.CAPTURED,
            format=SnapshotFormat.JSON,
            readonly=True,
        )

        assert snap.name == DUMMY_NAME
        assert snap.version == DUMMY_VERSION
        assert snap.metadata == DUMMY_METADATA
        assert snap.data == DUMMY_DATA
        assert snap.timestamp == DUMMY_TIMESTAMP
        assert snap.status is SnapshotStatus.CAPTURED
        assert snap.format is SnapshotFormat.JSON
        assert snap.readonly is True


# ==========================================================
# Part 4. Properties
# ==========================================================


class TestProperties:

    def test_name(self, populated_snapshot):

        assert populated_snapshot.name == "runtime"

    def test_timestamp(self, populated_snapshot):

        assert isinstance(populated_snapshot.timestamp, datetime)

    def test_version(self, populated_snapshot):

        assert populated_snapshot.version == "2.0.0"

    def test_metadata(self, populated_snapshot):

        assert populated_snapshot.metadata["owner"] == "system"

    def test_data(self, populated_snapshot):

        assert populated_snapshot.data["cpu"] == 80.0

    def test_status(self, populated_snapshot):

        assert populated_snapshot.status is SnapshotStatus.CAPTURED

    def test_format(self, populated_snapshot):

        assert populated_snapshot.format is SnapshotFormat.DICT

    def test_readonly(self, populated_snapshot):

        assert populated_snapshot.readonly is False

    def test_lock(self, populated_snapshot):

        assert populated_snapshot.lock is not None
        assert isinstance(populated_snapshot.lock, type(threading.RLock()))

# ==========================================================
# Part 5. Snapshot API
# ==========================================================


class TestSnapshotAPI:

    def test_capture(self, snapshot):

        snapshot.capture({"a": 1})

        assert snapshot.status is SnapshotStatus.CAPTURED
        assert snapshot.data["a"] == 1

    def test_restore(self, snapshot):

        snapshot.restore({"b": 2})

        assert snapshot.status is SnapshotStatus.RESTORED
        assert snapshot.data["b"] == 2

    def test_clear(self, populated_snapshot):

        populated_snapshot.clear()

        assert populated_snapshot.status is SnapshotStatus.EMPTY
        assert populated_snapshot.data == {}

    def test_reset(self, populated_snapshot):

        populated_snapshot.reset()

        assert populated_snapshot.name == DEFAULT_NAME
        assert populated_snapshot.version == DEFAULT_VERSION
        assert populated_snapshot.data == {}
        assert populated_snapshot.metadata == {}
        assert populated_snapshot.status is SnapshotStatus.EMPTY
        assert populated_snapshot.readonly is False

    def test_freeze(self, snapshot):

        snapshot.freeze()

        assert snapshot.readonly is True

    def test_unfreeze(self, snapshot):

        snapshot.freeze()
        snapshot.unfreeze()

        assert snapshot.readonly is False

    def test_touch(self, snapshot):

        old = snapshot.timestamp

        snapshot.touch()

        assert snapshot.timestamp >= old


# ==========================================================
# Part 6. Data API
# ==========================================================


class TestDataAPI:

    def test_set_data(self, snapshot):

        snapshot.set_data("cpu", 99)

        assert snapshot.data["cpu"] == 99

    def test_update_data(self, snapshot):

        snapshot.update_data({"cpu": 10, "mem": 20})

        assert snapshot.data["cpu"] == 10
        assert snapshot.data["mem"] == 20

    def test_merge_data(self, snapshot):

        snapshot.set_data("a", 1)
        snapshot.merge_data({"b": 2})

        assert snapshot.data == {"a": 1, "b": 2}

    def test_remove_data(self, snapshot):

        snapshot.set_data("cpu", 1)
        snapshot.remove_data("cpu")

        assert "cpu" not in snapshot.data

    def test_get(self, snapshot):

        snapshot.set_data("cpu", 123)

        assert snapshot.get("cpu") == 123
        assert snapshot.get("missing", 0) == 0

    def test_contains(self, snapshot):

        snapshot.set_data("cpu", 1)

        assert snapshot.contains("cpu")
        assert not snapshot.contains("memory")


# ==========================================================
# Part 7. Metadata API
# ==========================================================


class TestMetadataAPI:

    def test_set_metadata(self, snapshot):

        snapshot.set_metadata("owner", "admin")

        assert snapshot.metadata["owner"] == "admin"

    def test_update_metadata(self, snapshot):

        snapshot.update_metadata({"a": 1, "b": 2})

        assert snapshot.metadata["a"] == 1
        assert snapshot.metadata["b"] == 2

    def test_clear_metadata(self, snapshot):

        snapshot.set_metadata("x", 1)
        snapshot.clear_metadata()

        assert snapshot.metadata == {}


# ==========================================================
# Part 8. Serialization
# ==========================================================


class TestSerialization:

    def test_to_dict(self, populated_snapshot):

        value = populated_snapshot.to_dict()

        assert value["name"] == "runtime"
        assert value["status"] == SnapshotStatus.CAPTURED.value

    def test_from_dict(self, populated_snapshot):

        restored = MetricSnapshot.from_dict(
            populated_snapshot.to_dict()
        )

        assert restored == populated_snapshot

    def test_to_json(self, populated_snapshot):

        value = populated_snapshot.to_json()

        assert isinstance(value, str)

    def test_from_json(self, populated_snapshot):

        restored = MetricSnapshot.from_json(
            populated_snapshot.to_json()
        )

        assert restored == populated_snapshot

    def test_roundtrip_dict(self, populated_snapshot):

        restored = MetricSnapshot.from_dict(
            populated_snapshot.to_dict()
        )

        assert restored.to_dict() == populated_snapshot.to_dict()

    def test_roundtrip_json(self, populated_snapshot):

        restored = MetricSnapshot.from_json(
            populated_snapshot.to_json()
        )

        assert restored.to_json() == populated_snapshot.to_json()

# ==========================================================
# Part 9. Validation
# ==========================================================


class TestValidation:

    def test_validate(self, populated_snapshot):

        assert populated_snapshot.validate() is True

    def test_is_valid(self, populated_snapshot):

        assert populated_snapshot.is_valid() is True


# ==========================================================
# Part 10. Snapshot Clone API
# ==========================================================


class TestSnapshot:

    def test_copy(self, populated_snapshot):

        clone = populated_snapshot.copy()

        assert clone == populated_snapshot
        assert clone is not populated_snapshot

    def test_deepcopy(self, populated_snapshot):

        import copy

        clone = copy.deepcopy(populated_snapshot)

        assert clone == populated_snapshot
        assert clone is not populated_snapshot

    def test_clone(self, populated_snapshot):

        clone = populated_snapshot.clone()

        assert clone == populated_snapshot
        assert clone is not populated_snapshot


# ==========================================================
# Part 11. Python Protocols
# ==========================================================


class TestPythonProtocols:

    def test_repr(self, populated_snapshot):

        assert "MetricSnapshot" in repr(populated_snapshot)

    def test_str(self, populated_snapshot):

        assert str(populated_snapshot) == populated_snapshot.name

    def test_bool(self, populated_snapshot):

        assert bool(populated_snapshot)

    def test_len(self, populated_snapshot):

        assert len(populated_snapshot) == len(populated_snapshot.data)

    def test_contains(self, populated_snapshot):

        assert "cpu" in populated_snapshot

    def test_getitem(self, populated_snapshot):

        assert populated_snapshot["cpu"] == 80.0

    def test_setitem(self, snapshot):

        snapshot["cpu"] = 10

        assert snapshot["cpu"] == 10

    def test_iter(self, populated_snapshot):

        assert list(iter(populated_snapshot)) == list(
            populated_snapshot.data
        )

    def test_eq(self, populated_snapshot):

        other = populated_snapshot.copy()

        assert populated_snapshot == other

    def test_hash(self, populated_snapshot):

        assert isinstance(hash(populated_snapshot), int)

    def test_pickle(self, populated_snapshot):

        import pickle

        restored = pickle.loads(
            pickle.dumps(populated_snapshot)
        )

        assert restored == populated_snapshot


# ==========================================================
# Part 12. Diagnostics API
# ==========================================================


class TestDiagnosticsAPI:

    def test_summary(self, populated_snapshot):

        result = populated_snapshot.summary()

        assert result["name"] == "runtime"

    def test_diagnostics(self, populated_snapshot):

        result = populated_snapshot.diagnostics()

        assert result["valid"] is True

    def test_snapshot_report(self, populated_snapshot):

        report = populated_snapshot.snapshot_report()

        assert report["name"] == "runtime"

    def test_overall_status(self, populated_snapshot):

        assert (
            populated_snapshot.overall_status()
            == SnapshotStatus.CAPTURED.value
        )


# ==========================================================
# Part 13. API Freeze
# ==========================================================


class TestAPIFreeze:

    def test_public_api(self):

        required = [
            "capture",
            "restore",
            "clear",
            "reset",
            "freeze",
            "unfreeze",
            "touch",
            "set_data",
            "update_data",
            "merge_data",
            "remove_data",
            "get",
            "contains",
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
            "snapshot_report",
            "overall_status",
        ]

        for name in required:
            assert hasattr(MetricSnapshot, name)

    def test_annotations(self):

        assert hasattr(MetricSnapshot, "__annotations__")

    def test_slots(self):

        assert hasattr(MetricSnapshot, "__slots__")

    def test_signature(self):

        import inspect

        sig = inspect.signature(MetricSnapshot)

        assert "name" in sig.parameters                