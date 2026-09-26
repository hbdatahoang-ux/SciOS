"""
Tests for SciOS Runtime Metrics Memory Storage.

SciOS-NG v0.2
"""

from __future__ import annotations

import time

import pytest

from scios.runtime.observability.metrics.storage.backend import (
    StorageClosedError,
    StorageError,
)
from scios.runtime.observability.metrics.storage.memory import (
    MemoryStorage,
)


# ==============================================================================
# Construction
# ==============================================================================


def test_default_construction():

    storage = MemoryStorage()

    assert storage.enabled is True
    assert storage.closed is False
    assert storage.active is True
    assert len(storage) == 0


def test_disabled_construction():

    storage = MemoryStorage(
        enabled=False,
    )

    assert storage.enabled is False
    assert storage.closed is False
    assert storage.active is False


# ==============================================================================
# CRUD
# ==============================================================================


def test_put_and_get():

    storage = MemoryStorage()

    storage.put(
        "temperature",
        25.5,
    )

    assert storage.get(
        "temperature"
    ) == 25.5


def test_get_default():

    storage = MemoryStorage()

    assert storage.get(
        "missing",
        123,
    ) == 123


def test_exists():

    storage = MemoryStorage()

    assert storage.exists("x") is False

    storage.put(
        "x",
        1,
    )

    assert storage.exists("x") is True


def test_delete_existing():

    storage = MemoryStorage()

    storage.put(
        "x",
        1,
    )

    assert storage.delete("x") is True
    assert storage.exists("x") is False


def test_delete_missing():

    storage = MemoryStorage()

    assert storage.delete(
        "missing"
    ) is False


def test_clear():

    storage = MemoryStorage()

    storage.put("a", 1)
    storage.put("b", 2)

    storage.clear()

    assert len(storage) == 0


def test_keys():

    storage = MemoryStorage()

    storage.put("a", 1)
    storage.put("b", 2)

    assert storage.keys() == (
        "a",
        "b",
    )


def test_values():

    storage = MemoryStorage()

    storage.put("a", 1)
    storage.put("b", 2)

    assert storage.values() == (
        1,
        2,
    )


def test_items():

    storage = MemoryStorage()

    storage.put("a", 1)
    storage.put("b", 2)

    assert storage.items() == (
        ("a", 1),
        ("b", 2),
    )


# ==============================================================================
# Batch operations
# ==============================================================================


def test_put_many():

    storage = MemoryStorage()

    storage.put_many(
        {
            "a": 1,
            "b": 2,
            "c": 3,
        }
    )

    assert storage.get_many(
        ["a", "b", "c"]
    ) == {
        "a": 1,
        "b": 2,
        "c": 3,
    }


def test_delete_many():

    storage = MemoryStorage()

    storage.put_many(
        {
            "a": 1,
            "b": 2,
            "c": 3,
        }
    )

    deleted = storage.delete_many(
        [
            "a",
            "missing",
            "c",
        ]
    )

    assert deleted == 2
    assert storage.get("b") == 2
    assert len(storage) == 1


# ==============================================================================
# Extended API
# ==============================================================================


def test_update_mapping():

    storage = MemoryStorage()

    storage.update(
        {
            "a": 1,
            "b": 2,
        }
    )

    assert storage["a"] == 1
    assert storage["b"] == 2


def test_update_kwargs():

    storage = MemoryStorage()

    storage.update(
        a=1,
        b=2,
    )

    assert storage["a"] == 1
    assert storage["b"] == 2


def test_update_mapping_and_kwargs():

    storage = MemoryStorage()

    storage.update(
        {
            "a": 1,
        },
        b=2,
    )

    assert storage["a"] == 1
    assert storage["b"] == 2


def test_update_requires_mapping():

    storage = MemoryStorage()

    with pytest.raises(TypeError):
        storage.update(
            [
                ("a", 1),
            ]
        )


def test_get_or_set_existing():

    storage = MemoryStorage()

    storage.put(
        "x",
        10,
    )

    result = storage.get_or_set(
        "x",
        20,
    )

    assert result == 10
    assert storage.get("x") == 10


def test_get_or_set_missing():

    storage = MemoryStorage()

    result = storage.get_or_set(
        "x",
        20,
    )

    assert result == 20
    assert storage.get("x") == 20


# ==============================================================================
# Snapshot / restore
# ==============================================================================


def test_snapshot():

    storage = MemoryStorage()

    storage.put(
        "a",
        {
            "value": 10,
        },
    )

    snapshot = storage.snapshot()

    assert snapshot == {
        "a": {
            "value": 10,
        },
    }


def test_snapshot_is_deep_copy():

    storage = MemoryStorage()

    storage.put(
        "a",
        {
            "nested": [
                1,
                2,
            ],
        },
    )

    snapshot = storage.snapshot()

    snapshot["a"]["nested"].append(3)

    assert storage.get(
        "a"
    ) == {
        "nested": [
            1,
            2,
        ],
    }


def test_restore():

    storage = MemoryStorage()

    storage.put("a", 1)
    storage.put("b", 2)

    storage.restore(
        {
            "x": 10,
            "y": 20,
        }
    )

    assert storage.items() == (
        ("x", 10),
        ("y", 20),
    )


def test_restore_is_deep_copy():

    source = {
        "a": {
            "values": [
                1,
                2,
            ],
        },
    }

    storage = MemoryStorage()

    storage.restore(source)

    source["a"]["values"].append(3)

    assert storage.get(
        "a"
    ) == {
        "values": [
            1,
            2,
        ],
    }


def test_snapshot_restore_roundtrip():

    storage = MemoryStorage()

    storage.put("a", 1)
    storage.put("b", 2)

    snapshot = storage.snapshot()

    storage.clear()

    assert len(storage) == 0

    storage.restore(snapshot)

    assert storage.items() == (
        ("a", 1),
        ("b", 2),
    )


# ==============================================================================
# Size / maintenance
# ==============================================================================


def test_size():

    storage = MemoryStorage()

    storage.put("a", 1)
    storage.put("b", 2)

    assert storage.size() == 2


def test_compact():

    storage = MemoryStorage()

    storage.put("a", 1)
    storage.put("b", 2)

    retained = storage.compact()

    assert retained == 2
    assert len(storage) == 2


def test_cleanup():

    storage = MemoryStorage()

    storage.put("a", 1)
    storage.put("b", None)
    storage.put("c", 3)
    storage.put("d", None)

    removed = storage.cleanup()

    assert removed == 2
    assert storage.items() == (
        ("a", 1),
        ("c", 3),
    )


def test_cleanup_without_none():

    storage = MemoryStorage()

    storage.put("a", 1)
    storage.put("b", 2)

    assert storage.cleanup() == 0
    assert len(storage) == 2


# ==============================================================================
# Python protocols
# ==============================================================================


def test_len():

    storage = MemoryStorage()

    storage.put("a", 1)
    storage.put("b", 2)

    assert len(storage) == 2


def test_iteration():

    storage = MemoryStorage()

    storage.put("a", 1)
    storage.put("b", 2)

    assert tuple(storage) == (
        "a",
        "b",
    )


def test_getitem():

    storage = MemoryStorage()

    storage["x"] = 42

    assert storage["x"] == 42


def test_getitem_missing():

    storage = MemoryStorage()

    with pytest.raises(KeyError):
        storage["missing"]


def test_setitem():

    storage = MemoryStorage()

    storage["x"] = 42

    assert storage.get("x") == 42


def test_delitem():

    storage = MemoryStorage()

    storage["x"] = 42

    del storage["x"]

    assert "x" not in storage


def test_delitem_missing():

    storage = MemoryStorage()

    with pytest.raises(KeyError):
        del storage["missing"]


def test_contains():

    storage = MemoryStorage()

    storage["x"] = 42

    assert "x" in storage
    assert "missing" not in storage


# ==============================================================================
# Validation
# ==============================================================================


@pytest.mark.parametrize(
    "key",
    [
        "",
        None,
        123,
        [],
    ],
)
def test_invalid_key_put(
    key,
):

    storage = MemoryStorage()

    with pytest.raises(
        ValueError if key == "" else TypeError
    ):
        storage.put(
            key,
            1,
        )


@pytest.mark.parametrize(
    "method",
    [
        "get",
        "delete",
        "exists",
    ],
)
def test_invalid_key_operations(
    method,
):

    storage = MemoryStorage()

    with pytest.raises(
        ValueError
        if method == "get" and False
        else TypeError
    ):
        getattr(
            storage,
            method,
        )(123)


def test_empty_key_get():

    storage = MemoryStorage()

    with pytest.raises(ValueError):
        storage.get(
            "",
        )


def test_restore_requires_mapping():

    storage = MemoryStorage()

    with pytest.raises(TypeError):
        storage.restore(
            [
                ("a", 1),
            ]
        )


# ==============================================================================
# Lifecycle
# ==============================================================================


def test_disabled_storage_rejects_operations():

    storage = MemoryStorage(
        enabled=False,
    )

    with pytest.raises(StorageError):
        storage.put(
            "x",
            1,
        )

    with pytest.raises(StorageError):
        storage.get(
            "x",
        )

    with pytest.raises(StorageError):
        storage.clear()


def test_close_rejects_operations():

    storage = MemoryStorage()

    storage.put(
        "x",
        1,
    )

    storage.close()

    assert storage.closed is True
    assert storage.active is False

    with pytest.raises(StorageClosedError):
        storage.get(
            "x",
        )


def test_reopen_preserves_data():

    storage = MemoryStorage()

    storage.put(
        "x",
        1,
    )

    storage.close()
    storage.reopen()

    assert storage.active is True
    assert storage.get("x") == 1


def test_enable_disable():

    storage = MemoryStorage()

    storage.disable()

    assert storage.active is False

    storage.enable()

    assert storage.active is True


# ==============================================================================
# Statistics
# ==============================================================================


def test_statistics():

    storage = MemoryStorage()

    storage.put("a", 1)
    storage.put("b", 2)

    stats = storage.statistics()

    assert stats["backend"] == "MemoryStorage"
    assert stats["enabled"] is True
    assert stats["closed"] is False
    assert stats["active"] is True
    assert stats["count"] == 2
    assert stats["size"] == 2
    assert stats["operations"] > 0
    assert isinstance(
        stats["created_at"],
        float,
    )
    assert isinstance(
        stats["updated_at"],
        float,
    )


def test_statistics_timestamps():

    storage = MemoryStorage()

    before = time.time()

    storage.put(
        "x",
        1,
    )

    stats = storage.statistics()

    after = time.time()

    assert before <= stats["created_at"] <= after
    assert before <= stats["updated_at"] <= after


# ==============================================================================
# Representation
# ==============================================================================


def test_repr():

    storage = MemoryStorage()

    representation = repr(storage)

    assert representation == (
        "MemoryStorage("
        "size=0, "
        "enabled=True, "
        "closed=False, "
        "active=True"
        ")"
    )


def test_repr_after_data():

    storage = MemoryStorage()

    storage.put(
        "a",
        1,
    )

    assert repr(storage) == (
        "MemoryStorage("
        "size=1, "
        "enabled=True, "
        "closed=False, "
        "active=True"
        ")"
    )