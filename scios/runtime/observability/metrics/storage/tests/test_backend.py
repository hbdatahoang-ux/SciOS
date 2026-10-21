"""
Tests for SciOS Runtime Metrics Storage Backend.

SciOS-NG v0.2
"""

from __future__ import annotations

import pytest

from scios.runtime.observability.metrics.storage.backend import (
    MetricStorageBackend,
    StorageClosedError,
    StorageError,
)


# ==============================================================================
# Test implementation
# ==============================================================================


class DummyStorage(MetricStorageBackend):
    """Minimal concrete backend used to test the abstract contract."""

    def __init__(
        self,
        *,
        enabled: bool = True,
    ) -> None:
        super().__init__(enabled=enabled)
        self.data: dict[str, object] = {}
        self.touch_count = 0

    def put(
        self,
        key: str,
        value: object,
    ) -> None:
        self._ensure_active()
        self.data[key] = value

    def get(
        self,
        key: str,
        default: object = None,
    ) -> object:
        self._ensure_active()
        return self.data.get(key, default)

    def delete(
        self,
        key: str,
    ) -> bool:
        self._ensure_active()

        if key not in self.data:
            return False

        del self.data[key]
        return True

    def exists(
        self,
        key: str,
    ) -> bool:
        self._ensure_active()
        return key in self.data

    def clear(self) -> None:
        self._ensure_active()
        self.data.clear()

    def keys(self):
        self._ensure_active()
        return tuple(self.data.keys())

    def values(self):
        self._ensure_active()
        return tuple(self.data.values())

    def items(self):
        self._ensure_active()
        return tuple(self.data.items())

    def _touch(self) -> None:
        self.touch_count += 1


# ==============================================================================
# Abstract class
# ==============================================================================


def test_backend_is_abstract():

    assert MetricStorageBackend.__abstractmethods__ == {
        "put",
        "get",
        "delete",
        "exists",
        "clear",
        "keys",
        "values",
        "items",
    }


def test_backend_cannot_be_instantiated():

    with pytest.raises(TypeError):
        MetricStorageBackend()


# ==============================================================================
# Constructor / state
# ==============================================================================


def test_default_state():

    storage = DummyStorage()

    assert storage.enabled is True
    assert storage.closed is False
    assert storage.active is True


def test_disabled_state():

    storage = DummyStorage(
        enabled=False,
    )

    assert storage.enabled is False
    assert storage.closed is False
    assert storage.active is False


# ==============================================================================
# Lifecycle
# ==============================================================================


def test_enable():

    storage = DummyStorage(
        enabled=False,
    )

    storage.enable()

    assert storage.enabled is True
    assert storage.closed is False
    assert storage.active is True


def test_disable():

    storage = DummyStorage()

    storage.disable()

    assert storage.enabled is False
    assert storage.closed is False
    assert storage.active is False


def test_close():

    storage = DummyStorage()

    storage.close()

    assert storage.enabled is False
    assert storage.closed is True
    assert storage.active is False


def test_reopen():

    storage = DummyStorage()

    storage.close()
    storage.reopen()

    assert storage.enabled is True
    assert storage.closed is False
    assert storage.active is True


def test_enable_closed_backend_fails():

    storage = DummyStorage()

    storage.close()

    with pytest.raises(StorageClosedError):
        storage.enable()


def test_disable_closed_backend_fails():

    storage = DummyStorage()

    storage.close()

    with pytest.raises(StorageClosedError):
        storage.disable()


# ==============================================================================
# CRUD contract
# ==============================================================================


def test_put_get():

    storage = DummyStorage()

    storage.put(
        "temperature",
        42,
    )

    assert storage.get("temperature") == 42


def test_get_missing_returns_default():

    storage = DummyStorage()

    assert storage.get(
        "missing",
        "fallback",
    ) == "fallback"


def test_exists():

    storage = DummyStorage()

    assert storage.exists("x") is False

    storage.put(
        "x",
        123,
    )

    assert storage.exists("x") is True


def test_delete_existing():

    storage = DummyStorage()

    storage.put(
        "x",
        123,
    )

    assert storage.delete("x") is True
    assert storage.exists("x") is False


def test_delete_missing():

    storage = DummyStorage()

    assert storage.delete("missing") is False


def test_clear():

    storage = DummyStorage()

    storage.put("a", 1)
    storage.put("b", 2)

    storage.clear()

    assert len(storage) == 0


def test_keys():

    storage = DummyStorage()

    storage.put("a", 1)
    storage.put("b", 2)

    assert storage.keys() == (
        "a",
        "b",
    )


def test_values():

    storage = DummyStorage()

    storage.put("a", 1)
    storage.put("b", 2)

    assert storage.values() == (
        1,
        2,
    )


def test_items():

    storage = DummyStorage()

    storage.put("a", 1)
    storage.put("b", 2)

    assert storage.items() == (
        ("a", 1),
        ("b", 2),
    )


# ==============================================================================
# Batch API
# ==============================================================================


def test_put_many():

    storage = DummyStorage()

    storage.put_many(
        {
            "a": 1,
            "b": 2,
            "c": 3,
        }
    )

    assert len(storage) == 3
    assert storage.get("a") == 1
    assert storage.get("b") == 2
    assert storage.get("c") == 3


def test_put_many_requires_mapping():

    storage = DummyStorage()

    with pytest.raises(TypeError):
        storage.put_many(
            [
                ("a", 1),
            ]
        )


def test_get_many():

    storage = DummyStorage()

    storage.put("a", 1)
    storage.put("b", 2)

    result = storage.get_many(
        [
            "a",
            "b",
            "missing",
        ]
    )

    assert result == {
        "a": 1,
        "b": 2,
    }


def test_delete_many():

    storage = DummyStorage()

    storage.put("a", 1)
    storage.put("b", 2)
    storage.put("c", 3)

    deleted = storage.delete_many(
        [
            "a",
            "missing",
            "b",
        ]
    )

    assert deleted == 2
    assert len(storage) == 1
    assert storage.exists("c") is True


# ==============================================================================
# Active-state enforcement
# ==============================================================================


def test_disabled_backend_rejects_batch_operations():

    storage = DummyStorage(
        enabled=False,
    )

    with pytest.raises(StorageError):
        storage.put_many(
            {"a": 1}
        )

    with pytest.raises(StorageError):
        storage.get_many(
            ["a"]
        )

    with pytest.raises(StorageError):
        storage.delete_many(
            ["a"]
        )


def test_closed_backend_rejects_batch_operations():

    storage = DummyStorage()

    storage.close()

    with pytest.raises(StorageClosedError):
        storage.put_many(
            {"a": 1}
        )

    with pytest.raises(StorageClosedError):
        storage.get_many(
            ["a"]
        )

    with pytest.raises(StorageClosedError):
        storage.delete_many(
            ["a"]
        )


# ==============================================================================
# Inspection
# ==============================================================================


def test_statistics():

    storage = DummyStorage()

    storage.put("a", 1)
    storage.put("b", 2)

    stats = storage.statistics()

    assert stats["backend"] == "DummyStorage"
    assert stats["enabled"] is True
    assert stats["closed"] is False
    assert stats["active"] is True
    assert stats["count"] == 2


def test_status():

    storage = DummyStorage()

    status = storage.status()

    assert status == {
        "backend": "DummyStorage",
        "enabled": True,
        "closed": False,
        "active": True,
    }


def test_status_after_close():

    storage = DummyStorage()

    storage.close()

    status = storage.status()

    assert status == {
        "backend": "DummyStorage",
        "enabled": False,
        "closed": True,
        "active": False,
    }


# ==============================================================================
# Protocol helpers
# ==============================================================================


def test_len():

    storage = DummyStorage()

    storage.put("a", 1)
    storage.put("b", 2)

    assert len(storage) == 2


def test_contains():

    storage = DummyStorage()

    storage.put("a", 1)

    assert "a" in storage
    assert "missing" not in storage


def test_contains_non_string():

    storage = DummyStorage()

    assert 123 not in storage


def test_contains_disabled_backend():

    storage = DummyStorage()

    storage.put("a", 1)
    storage.disable()

    assert "a" not in storage


def test_contains_closed_backend():

    storage = DummyStorage()

    storage.put("a", 1)
    storage.close()

    assert "a" not in storage


def test_repr():

    storage = DummyStorage()

    representation = repr(storage)

    assert representation == (
        "DummyStorage("
        "enabled=True, "
        "closed=False, "
        "active=True"
        ")"
    )


# ==============================================================================
# Internal hook
# ==============================================================================


def test_touch_hook_is_called():

    storage = DummyStorage()

    storage.put("a", 1)

    assert storage.touch_count >= 1


def test_reopen_after_close():

    storage = DummyStorage()

    storage.put("a", 1)
    storage.close()
    storage.reopen()

    assert storage.active is True
    assert storage.get("a") == 1