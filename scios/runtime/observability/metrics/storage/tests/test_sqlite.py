"""
Tests for SciOS Runtime Metrics SQLite Storage.

SciOS-NG v0.2
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scios.runtime.observability.metrics.storage.backend import (
    StorageClosedError,
    StorageError,
)
from scios.runtime.observability.metrics.storage.sqlite import (
    SQLiteStorage,
)


# ==============================================================================
# Construction
# ==============================================================================


def test_default_construction():

    storage = SQLiteStorage()

    assert storage.enabled is True
    assert storage.closed is False
    assert storage.active is True
    assert len(storage) == 0


def test_file_construction(tmp_path):

    path = tmp_path / "metrics.db"

    storage = SQLiteStorage(path)

    assert Path(storage.path) == path
    assert path.exists()


def test_disabled_construction(tmp_path):

    path = tmp_path / "metrics.db"

    storage = SQLiteStorage(
        path,
        enabled=False,
    )

    assert storage.enabled is False
    assert storage.active is False
    assert storage._connection is None


# ==============================================================================
# CRUD
# ==============================================================================


def test_put_and_get():

    storage = SQLiteStorage()

    storage.put(
        "temperature",
        25.5,
    )

    assert storage.get(
        "temperature"
    ) == 25.5


def test_get_default():

    storage = SQLiteStorage()

    assert storage.get(
        "missing",
        123,
    ) == 123


def test_overwrite():

    storage = SQLiteStorage()

    storage.put("x", 1)
    storage.put("x", 2)

    assert storage.get("x") == 2
    assert len(storage) == 1


def test_exists():

    storage = SQLiteStorage()

    assert storage.exists("x") is False

    storage.put("x", 1)

    assert storage.exists("x") is True


def test_delete():

    storage = SQLiteStorage()

    storage.put("x", 1)

    assert storage.delete("x") is True
    assert storage.delete("x") is False


def test_clear():

    storage = SQLiteStorage()

    storage.put("a", 1)
    storage.put("b", 2)

    storage.clear()

    assert len(storage) == 0


def test_keys():

    storage = SQLiteStorage()

    storage.put("a", 1)
    storage.put("b", 2)

    assert storage.keys() == (
        "a",
        "b",
    )


def test_values():

    storage = SQLiteStorage()

    storage.put("a", 1)
    storage.put("b", 2)

    assert storage.values() == (
        1,
        2,
    )


def test_items():

    storage = SQLiteStorage()

    storage.put("a", 1)
    storage.put("b", 2)

    assert storage.items() == (
        ("a", 1),
        ("b", 2),
    )


# ==============================================================================
# JSON values
# ==============================================================================


@pytest.mark.parametrize(
    "value",
    [
        1,
        1.5,
        "hello",
        True,
        False,
        None,
        [1, 2, 3],
        {"a": 1, "b": 2},
    ],
)
def test_json_values(value):

    storage = SQLiteStorage()

    storage.put(
        "value",
        value,
    )

    assert storage.get(
        "value"
    ) == value


def test_non_serializable_value():

    storage = SQLiteStorage()

    with pytest.raises(StorageError):
        storage.put(
            "bad",
            {
                "invalid": object(),
            },
        )


# ==============================================================================
# Batch operations
# ==============================================================================


def test_put_many():

    storage = SQLiteStorage()

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


def test_put_many_overwrites():

    storage = SQLiteStorage()

    storage.put("a", 1)

    storage.put_many(
        {
            "a": 10,
            "b": 20,
        }
    )

    assert storage.items() == (
        ("a", 10),
        ("b", 20),
    )


def test_get_many_missing():

    storage = SQLiteStorage()

    storage.put("a", 1)

    assert storage.get_many(
        ["a", "missing"]
    ) == {
        "a": 1,
    }


def test_delete_many():

    storage = SQLiteStorage()

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
    assert storage.items() == (
        ("b", 2),
    )


# ==============================================================================
# SQLite-specific operations
# ==============================================================================


def test_count():

    storage = SQLiteStorage()

    storage.put_many(
        {
            "a": 1,
            "b": 2,
        }
    )

    assert storage.count() == 2


def test_search():

    storage = SQLiteStorage()

    storage.put_many(
        {
            "temperature:1": 10,
            "temperature:2": 20,
            "pressure:1": 30,
        }
    )

    assert storage.search(
        "temperature:%"
    ) == {
        "temperature:1": 10,
        "temperature:2": 20,
    }


def test_vacuum():

    storage = SQLiteStorage()

    storage.put("x", 1)
    storage.delete("x")

    storage.vacuum()


# ==============================================================================
# Persistence
# ==============================================================================


def test_persistence(tmp_path):

    path = tmp_path / "metrics.db"

    first = SQLiteStorage(path)

    first.put(
        "temperature",
        {
            "value": 25.5,
        },
    )

    first.close()

    second = SQLiteStorage(path)

    assert second.get(
        "temperature"
    ) == {
        "value": 25.5,
    }


def test_reopen_preserves_data(tmp_path):

    path = tmp_path / "metrics.db"

    storage = SQLiteStorage(path)

    storage.put(
        "x",
        42,
    )

    storage.close()

    assert storage.closed is True

    storage.reopen()

    assert storage.active is True
    assert storage.get("x") == 42


# ==============================================================================
# Lifecycle
# ==============================================================================


def test_close():

    storage = SQLiteStorage()

    storage.put(
        "x",
        1,
    )

    storage.close()

    assert storage.closed is True
    assert storage.active is False
    assert storage._connection is None


def test_closed_storage_rejects_operations():

    storage = SQLiteStorage()

    storage.close()

    with pytest.raises(StorageClosedError):
        storage.get("x")


def test_disabled_storage_rejects_operations():

    storage = SQLiteStorage(
        enabled=False,
    )

    with pytest.raises(StorageError):
        storage.get("x")


def test_reopen_after_close():

    storage = SQLiteStorage()

    storage.put(
        "x",
        1,
    )

    storage.close()
    storage.reopen()

    assert storage.get("x") == 1


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
def test_invalid_key(
    key,
):

    storage = SQLiteStorage()

    with pytest.raises(
        ValueError if key == "" else TypeError
    ):
        storage.put(
            key,
            1,
        )


def test_invalid_search_pattern():

    storage = SQLiteStorage()

    with pytest.raises(TypeError):
        storage.search(123)


# ==============================================================================
# Python protocols
# ==============================================================================


def test_len():

    storage = SQLiteStorage()

    storage.put("a", 1)
    storage.put("b", 2)

    assert len(storage) == 2


def test_iteration():

    storage = SQLiteStorage()

    storage.put("a", 1)
    storage.put("b", 2)

    assert tuple(storage) == (
        "a",
        "b",
    )


def test_getitem():

    storage = SQLiteStorage()

    storage["x"] = 42

    assert storage["x"] == 42


def test_getitem_missing():

    storage = SQLiteStorage()

    with pytest.raises(KeyError):
        storage["missing"]


def test_setitem():

    storage = SQLiteStorage()

    storage["x"] = 42

    assert storage.get("x") == 42


def test_delitem():

    storage = SQLiteStorage()

    storage["x"] = 42

    del storage["x"]

    assert "x" not in storage


def test_delitem_missing():

    storage = SQLiteStorage()

    with pytest.raises(KeyError):
        del storage["missing"]


def test_contains():

    storage = SQLiteStorage()

    storage["x"] = 42

    assert "x" in storage
    assert "missing" not in storage


# ==============================================================================
# Statistics / repr
# ==============================================================================


def test_statistics():

    storage = SQLiteStorage()

    storage.put("a", 1)
    storage.put("b", 2)

    stats = storage.statistics()

    assert stats["backend"] == "SQLiteStorage"
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


def test_repr():

    storage = SQLiteStorage()

    assert repr(storage) == (
        "SQLiteStorage("
        "path=':memory:', "
        "size=0, "
        "enabled=True, "
        "closed=False, "
        "active=True"
        ")"
    )