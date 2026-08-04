# ==========================================================
# Part 1. Imports & Fixtures
# ==========================================================

from __future__ import annotations

import json
import pickle
import threading
from copy import copy, deepcopy
from datetime import UTC, datetime

import pytest

from scios.runtime.observability.metrics.core.metrics.monitor.manager import (
    DEFAULT_CAPACITY,
    DEFAULT_NAME,
    DEFAULT_VERSION,
    ManagerMode,
    ManagerStatus,
    MetricManager,
)


@pytest.fixture()
def manager() -> MetricManager:
    return MetricManager()


@pytest.fixture()
def populated_manager() -> MetricManager:
    m = MetricManager(
        name="runtime",
        version="1.2.0",
        metadata={"env": "test"},
        capacity=16,
    )

    m.add("cpu", 42.5)
    m.add("memory", 1024)

    return m


# ==========================================================
# Part 2. Dummy Data
# ==========================================================


DUMMY_ITEMS = {
    "cpu": 32.5,
    "memory": 1024,
    "disk": 88,
}

DUMMY_METADATA = {
    "env": "test",
    "host": "localhost",
}

DUMMY_DICT = {
    "name": "runtime",
    "version": "1.0.0",
    "metadata": DUMMY_METADATA,
    "items": DUMMY_ITEMS,
    "status": "running",
    "mode": "manual",
    "enabled": True,
    "capacity": 16,
}

DUMMY_JSON = json.dumps(DUMMY_DICT)


# ==========================================================
# Part 3. Construction
# ==========================================================


class TestConstruction:

    def test_create_default(self):

        manager = MetricManager()

        assert manager.name == DEFAULT_NAME
        assert manager.version == DEFAULT_VERSION
        assert manager.enabled is True
        assert manager.capacity == DEFAULT_CAPACITY
        assert manager.status is ManagerStatus.IDLE
        assert manager.mode is ManagerMode.AUTO

    def test_create_custom(self):

        manager = MetricManager(
            name="runtime",
            version="2.0.0",
            metadata=DUMMY_METADATA,
            capacity=32,
            enabled=False,
            status=ManagerStatus.RUNNING,
            mode=ManagerMode.MANUAL,
        )

        assert manager.name == "runtime"
        assert manager.version == "2.0.0"
        assert manager.metadata == DUMMY_METADATA
        assert manager.capacity == 32
        assert manager.enabled is False
        assert manager.status is ManagerStatus.RUNNING
        assert manager.mode is ManagerMode.MANUAL


# ==========================================================
# Part 4. Properties
# ==========================================================


class TestProperties:

    def test_name(self, populated_manager):

        assert populated_manager.name == "runtime"

    def test_timestamp(self, populated_manager):

        assert isinstance(populated_manager.timestamp, datetime)

    def test_version(self, populated_manager):

        assert populated_manager.version == "1.2.0"

    def test_metadata(self, populated_manager):

        assert populated_manager.metadata["env"] == "test"

    def test_items(self, populated_manager):

        assert isinstance(populated_manager.items, dict)
        assert "cpu" in populated_manager.items

    def test_status(self, manager):

        assert manager.status is ManagerStatus.IDLE

    def test_mode(self, manager):

        assert manager.mode is ManagerMode.AUTO

    def test_enabled(self, manager):

        assert manager.enabled is True

    def test_capacity(self, populated_manager):

        assert populated_manager.capacity == 16

    def test_lock(self, populated_manager):

        assert populated_manager.lock is not None
        assert isinstance(populated_manager.lock, type(threading.RLock()))

# ==========================================================
# Part 5. Manager API
# ==========================================================


class TestManagerAPI:

    def test_start(self, manager):

        manager.start()

        assert manager.status is ManagerStatus.RUNNING

    def test_stop(self, manager):

        manager.start()
        manager.stop()

        assert manager.status is ManagerStatus.STOPPED

    def test_reset(self, populated_manager):

        populated_manager.reset()

        assert populated_manager.status is ManagerStatus.IDLE
        assert len(populated_manager.items) == 0
        assert populated_manager.metadata == {}
        assert populated_manager.enabled is True

    def test_clear(self, populated_manager):

        populated_manager.clear()

        assert len(populated_manager.items) == 0

    def test_enable(self, manager):

        manager.disable()
        manager.enable()

        assert manager.enabled is True

    def test_disable(self, manager):

        manager.disable()

        assert manager.enabled is False

    def test_touch(self, manager):

        old = manager.timestamp

        manager.touch()

        assert manager.timestamp >= old


# ==========================================================
# Part 6. Item API
# ==========================================================


class TestItemAPI:

    def test_add(self, manager):

        manager.add("cpu", 50)

        assert manager.items["cpu"] == 50

    def test_update(self, populated_manager):

        populated_manager.update("cpu", 90)

        assert populated_manager.items["cpu"] == 90

    def test_remove(self, populated_manager):

        value = populated_manager.remove("cpu")

        assert value == 42.5
        assert "cpu" not in populated_manager

    def test_get(self, populated_manager):

        assert populated_manager.get("cpu") == 42.5
        assert populated_manager.get("missing", 0) == 0

    def test_contains(self, populated_manager):

        assert populated_manager.contains("cpu")
        assert not populated_manager.contains("gpu")

    def test_count(self, populated_manager):

        assert populated_manager.count() == 2

    def test_keys(self, populated_manager):

        keys = populated_manager.keys()

        assert isinstance(keys, tuple)
        assert "cpu" in keys
        assert "memory" in keys


# ==========================================================
# Part 7. Metadata API
# ==========================================================


class TestMetadataAPI:

    def test_set_metadata(self, manager):

        manager.set_metadata("host", "localhost")

        assert manager.metadata["host"] == "localhost"

    def test_update_metadata(self, manager):

        manager.update_metadata({"env": "prod", "region": "vn"})

        assert manager.metadata["env"] == "prod"
        assert manager.metadata["region"] == "vn"

    def test_clear_metadata(self, populated_manager):

        populated_manager.clear_metadata()

        assert populated_manager.metadata == {}


# ==========================================================
# Part 8. Serialization
# ==========================================================


class TestSerialization:

    def test_to_dict(self, populated_manager):

        data = populated_manager.to_dict()

        assert isinstance(data, dict)
        assert data["name"] == "runtime"

    def test_from_dict(self):

        obj = MetricManager.from_dict(DUMMY_DICT)

        assert obj.name == "runtime"
        assert obj.enabled is True

    def test_to_json(self, populated_manager):

        text = populated_manager.to_json()

        assert isinstance(text, str)

    def test_from_json(self):

        obj = MetricManager.from_json(DUMMY_JSON)

        assert obj.name == "runtime"

    def test_roundtrip_dict(self, populated_manager):

        restored = MetricManager.from_dict(
            populated_manager.to_dict()
        )

        assert restored == populated_manager

    def test_roundtrip_json(self, populated_manager):

        restored = MetricManager.from_json(
            populated_manager.to_json()
        )

        assert restored == populated_manager

# ==========================================================
# Part 9. Validation
# ==========================================================


class TestValidation:

    def test_validate(self, populated_manager):

        populated_manager.validate()

    def test_is_valid(self, populated_manager):

        assert populated_manager.is_valid() is True


# ==========================================================
# Part 10. Snapshot API
# ==========================================================


class TestSnapshot:

    def test_copy(self, populated_manager):

        cloned = populated_manager.copy()

        assert cloned == populated_manager
        assert cloned is not populated_manager

    def test_deepcopy(self, populated_manager):

        cloned = populated_manager.deepcopy()

        assert cloned == populated_manager
        assert cloned is not populated_manager
        assert cloned.items is not populated_manager.items

    def test_clone(self, populated_manager):

        cloned = populated_manager.clone()

        assert cloned == populated_manager
        assert cloned is not populated_manager


# ==========================================================
# Part 11. Python Protocols
# ==========================================================


class TestPythonProtocols:

    def test_repr(self, populated_manager):

        assert "MetricManager" in repr(populated_manager)

    def test_str(self, populated_manager):

        assert "runtime" in str(populated_manager)

    def test_bool(self, populated_manager):

        assert bool(populated_manager)

        populated_manager.disable()

        assert not bool(populated_manager)

    def test_len(self, populated_manager):

        assert len(populated_manager) == 2

    def test_contains(self, populated_manager):

        assert "cpu" in populated_manager

    def test_getitem(self, populated_manager):

        assert populated_manager["cpu"] == 42.5

    def test_setitem(self, populated_manager):

        populated_manager["cpu"] = 99

        assert populated_manager["cpu"] == 99

    def test_iter(self, populated_manager):

        keys = list(iter(populated_manager))

        assert "cpu" in keys
        assert "memory" in keys

    def test_eq(self, populated_manager):

        other = populated_manager.clone()

        assert other == populated_manager

    def test_hash(self, populated_manager):

        assert isinstance(hash(populated_manager), int)

    def test_pickle(self, populated_manager):

        restored = pickle.loads(
            pickle.dumps(populated_manager)
        )

        assert restored == populated_manager


# ==========================================================
# Part 12. Diagnostics API
# ==========================================================


class TestDiagnosticsAPI:

    def test_summary(self, populated_manager):

        result = populated_manager.summary()

        assert isinstance(result, dict)
        assert result["name"] == "runtime"

    def test_diagnostics(self, populated_manager):

        result = populated_manager.diagnostics()

        assert isinstance(result, dict)
        assert result["valid"] is True

    def test_manager_report(self, populated_manager):

        report = populated_manager.manager_report()

        assert "manager" in report
        assert "diagnostics" in report

    def test_overall_status(self, populated_manager):

        assert populated_manager.overall_status() == "idle"

        populated_manager.start()

        assert populated_manager.overall_status() == "running"


# ==========================================================
# Part 13. API Freeze
# ==========================================================


class TestAPIFreeze:

    def test_public_api(self):

        exported = set(MetricManager.__module__.split())

        assert MetricManager is not None

    def test_annotations(self):

        assert hasattr(MetricManager, "__annotations__")

    def test_slots(self):

        assert hasattr(MetricManager, "__slots__")

    def test_signature(self):

        import inspect

        sig = inspect.signature(MetricManager.__init__)

        assert "name" in sig.parameters
        assert "capacity" in sig.parameters                