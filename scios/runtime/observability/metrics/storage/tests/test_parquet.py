"""
SciOS Runtime Metrics Parquet Storage Tests
============================================

Tests for ``ParquetStorage``.

Python 3.11+
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scios.runtime.observability.metrics.storage.parquet import (
    ParquetStorage,
    ParquetStorageError,
)


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def storage(tmp_path: Path) -> ParquetStorage:
    """Return a temporary Parquet storage backend."""
    return ParquetStorage(
        path=str(tmp_path / "metrics.parquet"),
    )


# ==============================================================================
# Construction
# ==============================================================================


def test_constructor(storage: ParquetStorage) -> None:
    """Storage initializes with an empty record set."""
    assert len(storage) == 0
    assert storage.count() == 0
    assert storage._records == []


def test_constructor_path(tmp_path: Path) -> None:
    """Storage preserves the configured Parquet path."""
    path = tmp_path / "custom.parquet"

    storage = ParquetStorage(path=str(path))

    assert storage._path == path


# ==============================================================================
# CRUD
# ==============================================================================


def test_put(storage: ParquetStorage) -> None:
    """put() stores a metric value."""
    result = storage.put("cpu", 42)

    assert result == 42
    assert storage.get("cpu") == 42
    assert storage.exists("cpu")
    assert len(storage) == 1


def test_put_multiple(storage: ParquetStorage) -> None:
    """Multiple records can be stored."""
    storage.put("cpu", 42)
    storage.put("memory", 73)

    assert storage.get("cpu") == 42
    assert storage.get("memory") == 73
    assert storage.count() == 2


def test_get_missing_returns_none(storage: ParquetStorage) -> None:
    """get() returns None for a missing key."""
    assert storage.get("missing") is None


def test_get_returns_latest_value(storage: ParquetStorage) -> None:
    """get() returns the most recently stored value for duplicate keys."""
    storage.put("cpu", 10)
    storage.put("cpu", 20)

    assert storage.get("cpu") == 20


def test_exists(storage: ParquetStorage) -> None:
    """exists() reports whether a key is present."""
    storage.put("cpu", 42)

    assert storage.exists("cpu")
    assert not storage.exists("memory")


def test_delete(storage: ParquetStorage) -> None:
    """delete() removes matching records."""
    storage.put("cpu", 42)
    storage.put("memory", 73)

    result = storage.delete("cpu")

    assert result is storage
    assert not storage.exists("cpu")
    assert storage.exists("memory")
    assert storage.count() == 1


def test_delete_missing(storage: ParquetStorage) -> None:
    """Deleting a missing key leaves the storage unchanged."""
    storage.put("cpu", 42)

    storage.delete("missing")

    assert storage.count() == 1
    assert storage.get("cpu") == 42


def test_clear(storage: ParquetStorage) -> None:
    """clear() removes all records."""
    storage.put("cpu", 42)
    storage.put("memory", 73)

    result = storage.clear()

    assert result is storage
    assert storage.count() == 0
    assert storage.keys() == []


# ==============================================================================
# Enumeration
# ==============================================================================


def test_keys(storage: ParquetStorage) -> None:
    """keys() returns stored keys."""
    storage.put("cpu", 42)
    storage.put("memory", 73)

    assert storage.keys() == ["cpu", "memory"]


def test_values(storage: ParquetStorage) -> None:
    """values() returns stored values."""
    storage.put("cpu", 42)
    storage.put("memory", 73)

    assert storage.values() == [42, 73]


def test_items(storage: ParquetStorage) -> None:
    """items() returns key/value pairs."""
    storage.put("cpu", 42)
    storage.put("memory", 73)

    assert storage.items() == [
        ("cpu", 42),
        ("memory", 73),
    ]


# ==============================================================================
# Data Types
# ==============================================================================


def test_put_complex_value(storage: ParquetStorage) -> None:
    """Complex Python values can be kept in the in-memory representation."""
    value = {
        "timestamp": 123.45,
        "labels": {
            "host": "node-1",
            "service": "runtime",
        },
        "values": [1, 2, 3],
    }

    storage.put("metric", value)

    assert storage.get("metric") == value


def test_put_none(storage: ParquetStorage) -> None:
    """None is a valid in-memory metric value."""
    storage.put("metric", None)

    assert storage.exists("metric")
    assert storage.get("metric") is None


# ==============================================================================
# Persistence
# ==============================================================================


def test_write_and_load(
    storage: ParquetStorage,
) -> None:
    """Records can be written to and loaded from Parquet."""
    pytest.importorskip("pandas")
    pytest.importorskip("pyarrow")

    storage.put("cpu", 42)
    storage.put("memory", 73)

    storage.write()

    assert storage._path.exists()

    restored = ParquetStorage(
        path=str(storage._path),
    )

    restored.load()

    assert restored.items() == [
        ("cpu", 42),
        ("memory", 73),
    ]


def test_write_empty_storage(
    storage: ParquetStorage,
) -> None:
    """An empty storage can be written to Parquet."""
    pytest.importorskip("pandas")
    pytest.importorskip("pyarrow")

    storage.write()

    assert storage._path.exists()

    restored = ParquetStorage(
        path=str(storage._path),
    )

    restored.load()

    assert restored.count() == 0


def test_load_missing_file(
    storage: ParquetStorage,
) -> None:
    """Loading a missing file raises ParquetStorageError."""
    pytest.importorskip("pandas")
    pytest.importorskip("pyarrow")

    with pytest.raises(
        ParquetStorageError,
        match="does not exist",
    ):
        storage.load()


def test_load_invalid_file(
    storage: ParquetStorage,
) -> None:
    """Loading an invalid Parquet file raises ParquetStorageError."""
    pytest.importorskip("pandas")
    pytest.importorskip("pyarrow")

    storage._path.write_bytes(b"not-a-parquet-file")

    with pytest.raises(
        ParquetStorageError,
        match="failed to load Parquet storage",
    ):
        storage.load()


def test_load_invalid_schema_missing_key(
    storage: ParquetStorage,
) -> None:
    """A Parquet file without the key column is rejected."""
    pytest.importorskip("pandas")
    pytest.importorskip("pyarrow")

    import pandas as pd

    pd.DataFrame(
        {
            "value": [42],
        }
    ).to_parquet(
        storage._path,
        index=False,
    )

    with pytest.raises(
        ParquetStorageError,
        match="missing 'key'",
    ):
        storage.load()


def test_load_invalid_schema_missing_value(
    storage: ParquetStorage,
) -> None:
    """A Parquet file without the value column is rejected."""
    pytest.importorskip("pandas")
    pytest.importorskip("pyarrow")

    import pandas as pd

    pd.DataFrame(
        {
            "key": ["cpu"],
        }
    ).to_parquet(
        storage._path,
        index=False,
    )

    with pytest.raises(
        ParquetStorageError,
        match="missing 'value'",
    ):
        storage.load()


# ==============================================================================
# Append
# ==============================================================================


def test_append_without_existing_file(
    storage: ParquetStorage,
) -> None:
    """append() writes records when no previous file exists."""
    pytest.importorskip("pandas")
    pytest.importorskip("pyarrow")

    storage.put("cpu", 42)

    result = storage.append()

    assert result is storage
    assert storage._path.exists()

    restored = ParquetStorage(
        path=str(storage._path),
    )

    restored.load()

    assert restored.items() == [
        ("cpu", 42),
    ]


def test_append_existing_file(
    storage: ParquetStorage,
) -> None:
    """
    append() places current records before existing persisted records.
    """
    pytest.importorskip("pandas")
    pytest.importorskip("pyarrow")

    storage.put("cpu", 42)
    storage.write()

    storage._records = [
        {
            "key": "memory",
            "value": 73,
        },
    ]

    result = storage.append()

    assert result is storage

    restored = ParquetStorage(
        path=str(storage._path),
    )

    restored.load()

    assert restored.count() == 2
    assert restored.items() == [
        ("memory", 73),
        ("cpu", 42),
    ]


def test_append_current_records_win_on_duplicate_key(
    storage: ParquetStorage,
) -> None:
    """
    append() gives current in-memory records precedence over persisted
    records with the same key.
    """
    pytest.importorskip("pandas")
    pytest.importorskip("pyarrow")

    storage.put("cpu", 42)
    storage.put("memory", 73)
    storage.write()

    storage._records = [
        {
            "key": "memory",
            "value": 99,
        },
        {
            "key": "disk",
            "value": 11,
        },
    ]

    storage.append()

    restored = ParquetStorage(
        path=str(storage._path),
    )

    restored.load()

    assert restored.items() == [
        ("memory", 99),
        ("disk", 11),
        ("cpu", 42),
    ]


def test_append_preserves_current_order(
    storage: ParquetStorage,
) -> None:
    """append() preserves the insertion order of current records."""
    pytest.importorskip("pandas")
    pytest.importorskip("pyarrow")

    storage.put("old", 1)
    storage.write()

    storage._records = [
        {
            "key": "z",
            "value": 3,
        },
        {
            "key": "a",
            "value": 2,
        },
    ]

    storage.append()

    restored = ParquetStorage(
        path=str(storage._path),
    )

    restored.load()

    assert restored.items() == [
        ("z", 3),
        ("a", 2),
        ("old", 1),
    ]


# ==============================================================================
# DataFrame
# ==============================================================================


def test_dataframe(
    storage: ParquetStorage,
) -> None:
    """dataframe() returns a pandas DataFrame."""
    pytest.importorskip("pandas")
    pytest.importorskip("pyarrow")

    storage.put("cpu", 42)
    storage.put("memory", 73)

    frame = storage.dataframe()

    assert list(frame.columns) == [
        "key",
        "value",
    ]

    assert len(frame) == 2
    assert frame["key"].tolist() == [
        "cpu",
        "memory",
    ]
    assert frame["value"].tolist() == [
        42,
        73,
    ]


# ==============================================================================
# Snapshot / Restore
# ==============================================================================


def test_snapshot(
    storage: ParquetStorage,
) -> None:
    """snapshot() captures the current records."""
    storage.put("cpu", 42)
    storage.put("memory", 73)

    snapshot = storage.snapshot()

    assert snapshot == [
        {
            "key": "cpu",
            "value": 42,
        },
        {
            "key": "memory",
            "value": 73,
        },
    ]


def test_restore(
    storage: ParquetStorage,
) -> None:
    """restore() replaces the current record set."""
    storage.put("old", 1)

    snapshot = [
        {
            "key": "cpu",
            "value": 42,
        },
        {
            "key": "memory",
            "value": 73,
        },
    ]

    result = storage.restore(snapshot)

    assert result is storage
    assert storage.items() == [
        ("cpu", 42),
        ("memory", 73),
    ]


def test_snapshot_is_independent(
    storage: ParquetStorage,
) -> None:
    """Snapshot must not share the outer list with storage."""
    storage.put("cpu", 42)

    snapshot = storage.snapshot()

    snapshot.append(
        {
            "key": "memory",
            "value": 73,
        }
    )

    assert storage.count() == 1


def test_snapshot_nested_value_is_independent(
    storage: ParquetStorage,
) -> None:
    """Snapshot must deep-copy nested values."""
    value = {
        "labels": {
            "host": "node-1",
        },
    }

    storage.put("metric", value)

    snapshot = storage.snapshot()

    snapshot[0]["value"]["labels"]["host"] = "node-2"

    assert storage.get("metric") == {
        "labels": {
            "host": "node-1",
        },
    }


# ==============================================================================
# Statistics
# ==============================================================================


def test_statistics(
    storage: ParquetStorage,
) -> None:
    """statistics() exposes Parquet-specific metadata."""
    storage.put("cpu", 42)
    storage.put("memory", 73)

    stats = storage.statistics()

    assert stats["backend"] == "parquet"
    assert stats["path"] == str(storage._path)
    assert stats["records"] == 2
    assert stats["format"] == "columnar"


# ==============================================================================
# Python Protocols
# ==============================================================================


def test_len(
    storage: ParquetStorage,
) -> None:
    """len(storage) returns the number of records."""
    storage.put("cpu", 42)
    storage.put("memory", 73)

    assert len(storage) == 2


def test_iter(
    storage: ParquetStorage,
) -> None:
    """Iteration yields raw records."""
    storage.put("cpu", 42)
    storage.put("memory", 73)

    records = list(storage)

    assert records == [
        {
            "key": "cpu",
            "value": 42,
        },
        {
            "key": "memory",
            "value": 73,
        },
    ]


def test_iter_is_independent(
    storage: ParquetStorage,
) -> None:
    """Iteration must return independent record copies."""
    storage.put(
        "metric",
        {
            "labels": {
                "host": "node-1",
            },
        },
    )

    records = list(storage)

    records[0]["value"]["labels"]["host"] = "node-2"

    assert storage.get("metric") == {
        "labels": {
            "host": "node-1",
        },
    }


def test_contains(
    storage: ParquetStorage,
) -> None:
    """The ``in`` operator checks metric keys."""
    storage.put("cpu", 42)

    assert "cpu" in storage
    assert "memory" not in storage


def test_repr(
    storage: ParquetStorage,
) -> None:
    """repr() identifies the backend and path."""
    text = repr(storage)

    assert "ParquetStorage" in text
    assert str(storage._path) in text


# ==============================================================================
# Lifecycle / Validation
# ==============================================================================


def test_key_validation_non_string(
    storage: ParquetStorage,
) -> None:
    """Non-string keys should be rejected by the backend contract."""
    with pytest.raises(TypeError):
        storage.put(123, 42)  # type: ignore[arg-type]


def test_key_validation_empty_string(
    storage: ParquetStorage,
) -> None:
    """Empty keys should be rejected by the backend contract."""
    with pytest.raises(ValueError):
        storage.put("", 42)


def test_get_requires_valid_key(
    storage: ParquetStorage,
) -> None:
    """get() should validate its key."""
    with pytest.raises(TypeError):
        storage.get(123)  # type: ignore[arg-type]


# ==============================================================================
# Dependency Check
# ==============================================================================


def test_require_engine_without_dependencies(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Dependency failures are converted to RuntimeError."""
    import builtins

    original_import = builtins.__import__

    def fake_import(
        name,
        globals=None,
        locals=None,
        fromlist=(),
        level=0,
    ):
        if name in {"pandas", "pyarrow"}:
            raise ImportError(name)

        return original_import(
            name,
            globals,
            locals,
            fromlist,
            level,
        )

    monkeypatch.setattr(
        builtins,
        "__import__",
        fake_import,
    )

    storage = ParquetStorage()

    with pytest.raises(RuntimeError, match="pandas and pyarrow"):
        storage._require_engine()
