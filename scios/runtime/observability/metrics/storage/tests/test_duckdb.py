"""
Tests for DuckDB metrics storage.

SciOS-NG v0.2
"""

from __future__ import annotations

import pytest

from scios.runtime.observability.metrics.storage.backend import (
    StorageClosedError,
    StorageError,
)

duckdb = pytest.importorskip("duckdb")

from scios.runtime.observability.metrics.storage.duckdb import (
    DuckDBStorage,
)


# ==============================================================================
# Construction
# ==============================================================================


def test_default_construction():

    storage = DuckDBStorage()

    assert storage.enabled is True
    assert storage.closed is False
    assert storage.active is True
    assert storage.path == ":memory:"

    storage.close()


def test_file_construction(tmp_path):

    path = tmp_path / "metrics.duckdb"

    storage = DuckDBStorage(path)

    assert storage.active is True
    assert storage.path == str(path)

    storage.close()


# ==============================================================================
# CRUD
# ==============================================================================


def test_put_get():

    storage = DuckDBStorage()

    storage.put(
        "temperature",
        25.5,
    )

    assert storage.get(
        "temperature"
    ) == 25.5

    storage.close()


def test_put_update():

    storage = DuckDBStorage()

    storage.put(
        "x",
        1,
    )

    storage.put(
        "x",
        2,
    )

    assert storage.get("x") == 2
    assert storage.count() == 1

    storage.close()


def test_get_missing():

    storage = DuckDBStorage()

    assert storage.get(
        "missing"
    ) is None

    assert storage.get(
        "missing",
        42,
    ) == 42

    storage.close()


def test_delete():

    storage = DuckDBStorage()

    storage.put(
        "x",
        1,
    )

    assert storage.delete("x") is True
    assert storage.exists("x") is False
    assert storage.delete("x") is False

    storage.close()


def test_exists():

    storage = DuckDBStorage()

    assert storage.exists("x") is False

    storage.put(
        "x",
        1,
    )

    assert storage.exists("x") is True

    storage.close()


def test_clear():

    storage = DuckDBStorage()

    storage.put("a", 1)
    storage.put("b", 2)

    assert storage.count() == 2

    storage.clear()

    assert storage.count() == 0

    storage.close()


# ==============================================================================
# Collection API
# ==============================================================================


def test_keys():

    storage = DuckDBStorage()

    storage.put("a", 1)
    storage.put("b", 2)

    assert storage.keys() == [
        "a",
        "b",
    ]

    storage.close()


def test_values():

    storage = DuckDBStorage()

    storage.put("a", 1)
    storage.put("b", 2)

    assert storage.values() == [
        1,
        2,
    ]

    storage.close()


def test_items():

    storage = DuckDBStorage()

    storage.put("a", 1)
    storage.put("b", {"x": 2})

    assert storage.items() == [
        ("a", 1),
        ("b", {"x": 2}),
    ]

    storage.close()


# ==============================================================================
# Batch API
# ==============================================================================


def test_put_many():

    storage = DuckDBStorage()

    storage.put_many(
        {
            "a": 1,
            "b": 2,
        }
    )

    assert storage.get("a") == 1
    assert storage.get("b") == 2

    storage.close()


def test_get_many():

    storage = DuckDBStorage()

    storage.put_many(
        {
            "a": 1,
            "b": 2,
        }
    )

    result = storage.get_many(
        ["a", "b"]
    )

    assert result == {
        "a": 1,
        "b": 2,
    }

    storage.close()


def test_delete_many():

    storage = DuckDBStorage()

    storage.put_many(
        {
            "a": 1,
            "b": 2,
            "c": 3,
        }
    )

    deleted = storage.delete_many(
        ["a", "c"]
    )

    assert deleted == 2
    assert storage.count() == 1
    assert storage.get("b") == 2

    storage.close()


# ==============================================================================
# Complex values
# ==============================================================================


def test_complex_values():

    storage = DuckDBStorage()

    value = {
        "name": "experiment",
        "values": [1, 2, 3],
        "nested": {
            "enabled": True,
        },
        "none": None,
    }

    storage.put(
        "experiment",
        value,
    )

    assert storage.get(
        "experiment"
    ) == value

    storage.close()


# ==============================================================================
# DuckDB-specific API
# ==============================================================================


def test_query():

    storage = DuckDBStorage()

    storage.put("a", 1)
    storage.put("b", 2)

    result = storage.query(
        "SELECT COUNT(*) FROM metrics"
    )

    assert result.fetchone()[0] == 2

    storage.close()


def test_count():

    storage = DuckDBStorage()

    storage.put("a", 1)
    storage.put("b", 2)

    assert storage.count() == 2

    storage.close()


def test_aggregate():

    storage = DuckDBStorage()

    storage.put("a", 1)
    storage.put("b", 2)

    assert storage.aggregate(
        "COUNT(*)"
    ) == 2

    storage.close()


def test_dataframe():

    storage = DuckDBStorage()

    storage.put("a", 1)
    storage.put("b", 2)

    frame = storage.dataframe()

    assert list(frame.columns) == [
        "key",
        "value",
    ]

    assert len(frame) == 2

    storage.close()


def test_optimize():

    storage = DuckDBStorage()

    storage.put(
        "x",
        1,
    )

    storage.optimize()

    assert storage.get("x") == 1

    storage.close()


# ==============================================================================
# Lifecycle
# ==============================================================================


def test_close():

    storage = DuckDBStorage()

    storage.put(
        "x",
        1,
    )

    storage.close()

    assert storage.closed is True
    assert storage.active is False
    assert storage._connection is None


def test_closed_storage_rejects_operations():

    storage = DuckDBStorage()

    storage.close()

    with pytest.raises(StorageClosedError):
        storage.get("x")


def test_reopen_after_close():

    storage = DuckDBStorage()

    storage.put(
        "x",
        1,
    )

    storage.close()

    assert storage.closed is True

    storage.reopen()

    assert storage.closed is False
    assert storage.active is True
    assert storage.get("x") == 1

    storage.close()


def test_reopen_preserves_data(tmp_path):

    path = tmp_path / "metrics.duckdb"

    storage = DuckDBStorage(path)

    storage.put(
        "x",
        42,
    )

    storage.close()

    storage.reopen()

    assert storage.active is True
    assert storage.get("x") == 42

    storage.close()


def test_memory_reopen_preserves_data():

    storage = DuckDBStorage()

    storage.put(
        "x",
        1,
    )

    storage.close()

    storage.reopen()

    assert storage.get("x") == 1

    storage.close()


# ==============================================================================
# Persistence
# ==============================================================================


def test_file_persistence(tmp_path):

    path = tmp_path / "metrics.duckdb"

    first = DuckDBStorage(path)

    first.put(
        "temperature",
        {
            "value": 25.5,
        },
    )

    first.close()

    second = DuckDBStorage(path)

    assert second.get(
        "temperature"
    ) == {
        "value": 25.5,
    }

    second.close()


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
def test_invalid_key(key):

    storage = DuckDBStorage()

    with pytest.raises(
        (TypeError, ValueError)
    ):
        storage.put(
            key,
            1,
        )

    storage.close()


def test_invalid_query():

    storage = DuckDBStorage()

    with pytest.raises(TypeError):
        storage.query(123)

    storage.close()


# ==============================================================================
# Statistics
# ==============================================================================


def test_statistics():

    storage = DuckDBStorage()

    storage.put("a", 1)
    storage.put("b", 2)

    statistics = storage.statistics()

    assert statistics["backend"] == "duckdb"
    assert statistics["count"] == 2
    assert statistics["enabled"] is True
    assert statistics["closed"] is False
    assert statistics["active"] is True

    storage.close()


# ==============================================================================
# Protocol API
# ==============================================================================


def test_len():

    storage = DuckDBStorage()

    storage.put("a", 1)
    storage.put("b", 2)

    assert len(storage) == 2

    storage.close()


def test_contains():

    storage = DuckDBStorage()

    storage.put(
        "x",
        1,
    )

    assert "x" in storage
    assert "missing" not in storage

    storage.close()