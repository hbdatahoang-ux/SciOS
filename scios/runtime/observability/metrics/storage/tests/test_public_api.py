"""
SciOS-NG Runtime Metrics Storage
================================

Public API contract tests.

These tests verify that the storage package exposes a stable and coherent
package-level API.

Python 3.11+
"""

from __future__ import annotations

import pytest


# ==============================================================================
# Part 1. Public Imports
# ==============================================================================


def test_public_imports() -> None:
    """All documented public storage symbols are importable."""
    from scios.runtime.observability.metrics.storage import (
        DuckDBBackend,
        DuckDBStorage,
        MemoryBackend,
        MemoryStorage,
        MetricStorageBackend,
        ParquetBackend,
        ParquetStorage,
        SQLiteBackend,
        SQLiteStorage,
        StorageBackend,
        STORAGE_BACKENDS,
        create_storage,
        default_storage,
    )

    assert MetricStorageBackend is not None
    assert StorageBackend is not None

    assert MemoryStorage is not None
    assert SQLiteStorage is not None
    assert DuckDBStorage is not None
    assert ParquetStorage is not None

    assert MemoryBackend is not None
    assert SQLiteBackend is not None
    assert DuckDBBackend is not None
    assert ParquetBackend is not None

    assert STORAGE_BACKENDS is not None
    assert callable(create_storage)
    assert callable(default_storage)


# ==============================================================================
# Part 2. __all__
# ==============================================================================


def test_public_all() -> None:
    """__all__ contains exactly the documented public API."""
    import scios.runtime.observability.metrics.storage as storage

    expected = {
        "MetricStorageBackend",
        "StorageBackend",
        "MemoryStorage",
        "SQLiteStorage",
        "DuckDBStorage",
        "ParquetStorage",
        "MemoryBackend",
        "SQLiteBackend",
        "DuckDBBackend",
        "ParquetBackend",
        "STORAGE_BACKENDS",
        "create_storage",
        "default_storage",
    }

    assert set(storage.__all__) == expected
    assert len(storage.__all__) == len(expected)


def test_public_all_symbols_exist() -> None:
    """Every symbol listed in __all__ exists on the package."""
    import scios.runtime.observability.metrics.storage as storage

    for name in storage.__all__:
        assert hasattr(storage, name), (
            f"Public symbol {name!r} is listed in __all__ "
            "but is not exposed by the package"
        )


# ==============================================================================
# Part 3. Base Backend Alias
# ==============================================================================


def test_storage_backend_alias() -> None:
    """StorageBackend aliases MetricStorageBackend."""
    from scios.runtime.observability.metrics.storage import (
        MetricStorageBackend,
        StorageBackend,
    )

    assert StorageBackend is MetricStorageBackend


# ==============================================================================
# Part 4. Concrete Backend Aliases
# ==============================================================================


@pytest.mark.parametrize(
    ("alias_name", "storage_name"),
    [
        ("MemoryBackend", "MemoryStorage"),
        ("SQLiteBackend", "SQLiteStorage"),
        ("DuckDBBackend", "DuckDBStorage"),
        ("ParquetBackend", "ParquetStorage"),
    ],
)
def test_backend_aliases(
    alias_name: str,
    storage_name: str,
) -> None:
    """Backend aliases point to their corresponding storage classes."""
    import scios.runtime.observability.metrics.storage as storage

    assert getattr(storage, alias_name) is getattr(
        storage,
        storage_name,
    )


# ==============================================================================
# Part 5. Storage Registry
# ==============================================================================


def test_storage_registry() -> None:
    """STORAGE_BACKENDS contains all supported concrete backends."""
    from scios.runtime.observability.metrics.storage import (
        DuckDBStorage,
        MemoryStorage,
        ParquetStorage,
        SQLiteStorage,
        STORAGE_BACKENDS,
    )

    assert STORAGE_BACKENDS == {
        "memory": MemoryStorage,
        "sqlite": SQLiteStorage,
        "duckdb": DuckDBStorage,
        "parquet": ParquetStorage,
    }


def test_storage_registry_excludes_base_backend() -> None:
    """The abstract/base backend is not a factory backend."""
    from scios.runtime.observability.metrics.storage import (
        MetricStorageBackend,
        STORAGE_BACKENDS,
    )

    assert "backend" not in STORAGE_BACKENDS
    assert MetricStorageBackend not in STORAGE_BACKENDS.values()


def test_storage_registry_keys_are_strings() -> None:
    """All registry keys are normalized string backend names."""
    from scios.runtime.observability.metrics.storage import (
        STORAGE_BACKENDS,
    )

    assert all(
        isinstance(name, str)
        for name in STORAGE_BACKENDS
    )

    assert all(
        name == name.lower()
        for name in STORAGE_BACKENDS
    )


# ==============================================================================
# Part 6. Factory API
# ==============================================================================


def test_create_storage_default() -> None:
    """create_storage() defaults to MemoryStorage."""
    from scios.runtime.observability.metrics.storage import (
        MemoryStorage,
        create_storage,
    )

    storage = create_storage()

    assert isinstance(storage, MemoryStorage)


@pytest.mark.parametrize(
    ("backend", "expected_type"),
    [
        ("memory", "MemoryStorage"),
        ("sqlite", "SQLiteStorage"),
        ("duckdb", "DuckDBStorage"),
        ("parquet", "ParquetStorage"),
    ],
)
def test_create_storage_backends(
    backend: str,
    expected_type: str,
) -> None:
    """create_storage() creates every registered backend."""
    import scios.runtime.observability.metrics.storage as storage

    instance = storage.create_storage(backend)

    assert type(instance).__name__ == expected_type


@pytest.mark.parametrize(
    ("backend", "expected_type"),
    [
        ("MEMORY", "MemoryStorage"),
        ("Memory", "MemoryStorage"),
        (" memory ", "MemoryStorage"),
        ("SQLITE", "SQLiteStorage"),
        (" sqlite ", "SQLiteStorage"),
        ("DuckDB", "DuckDBStorage"),
        (" duckdb ", "DuckDBStorage"),
        ("PARQUET", "ParquetStorage"),
        (" parquet ", "ParquetStorage"),
    ],
)
def test_create_storage_normalizes_backend_name(
    backend: str,
    expected_type: str,
) -> None:
    """Factory accepts case-insensitive and surrounding whitespace."""
    import scios.runtime.observability.metrics.storage as storage

    instance = storage.create_storage(backend)

    assert type(instance).__name__ == expected_type


def test_create_storage_rejects_non_string_backend() -> None:
    """Factory rejects non-string backend names."""
    from scios.runtime.observability.metrics.storage import (
        create_storage,
    )

    with pytest.raises(
        TypeError,
        match="backend must be a string",
    ):
        create_storage(None)  # type: ignore[arg-type]


def test_create_storage_rejects_empty_backend() -> None:
    """Factory rejects an empty backend name."""
    from scios.runtime.observability.metrics.storage import (
        create_storage,
    )

    with pytest.raises(
        ValueError,
        match="backend must not be empty",
    ):
        create_storage("")


@pytest.mark.parametrize(
    "backend",
    [
        "unknown",
        "redis",
        "backend",
    ],
)
def test_create_storage_rejects_unknown_backend(
    backend: str,
) -> None:
    """Factory rejects unregistered backend names."""
    from scios.runtime.observability.metrics.storage import (
        create_storage,
    )

    with pytest.raises(
        ValueError,
        match="Unknown storage backend",
    ):
        create_storage(backend)


def test_create_storage_rejects_whitespace_backend() -> None:
    """Factory rejects a backend name containing only whitespace."""
    from scios.runtime.observability.metrics.storage import (
        create_storage,
    )

    with pytest.raises(
        ValueError,
        match="backend must not be empty",
    ):
        create_storage("   ")


# ==============================================================================
# Part 7. Factory Keyword Forwarding
# ==============================================================================


def test_create_storage_forwards_kwargs_to_memory() -> None:
    """Factory forwards constructor kwargs to MemoryStorage."""
    from scios.runtime.observability.metrics.storage import (
        MemoryStorage,
        create_storage,
    )

    storage = create_storage(
        "memory",
        enabled=False,
    )

    assert isinstance(storage, MemoryStorage)
    assert storage.enabled is False


def test_create_storage_forwards_kwargs_to_sqlite(
    tmp_path,
) -> None:
    """Factory forwards constructor kwargs to SQLiteStorage."""
    from scios.runtime.observability.metrics.storage import (
        SQLiteStorage,
        create_storage,
    )

    path = tmp_path / "metrics.db"

    storage = create_storage(
        "sqlite",
        path=path,
    )

    assert isinstance(storage, SQLiteStorage)
    assert storage.path == str(path)


def test_create_storage_forwards_kwargs_to_duckdb(
    tmp_path,
) -> None:
    """Factory forwards constructor kwargs to DuckDBStorage."""
    from scios.runtime.observability.metrics.storage import (
        DuckDBStorage,
        create_storage,
    )

    path = tmp_path / "metrics.duckdb"

    storage = create_storage(
        "duckdb",
        path=path,
    )

    assert isinstance(storage, DuckDBStorage)
    assert storage.path == str(path)


def test_create_storage_forwards_kwargs_to_parquet(
    tmp_path,
) -> None:
    """Factory forwards constructor kwargs to ParquetStorage."""
    from scios.runtime.observability.metrics.storage import (
        ParquetStorage,
        create_storage,
    )

    path = tmp_path / "metrics.parquet"

    storage = create_storage(
        "parquet",
        path=path,
    )

    assert isinstance(storage, ParquetStorage)
    assert storage.path == path


# ==============================================================================
# Part 8. Default Storage
# ==============================================================================


def test_default_storage_returns_memory_storage() -> None:
    """default_storage() returns MemoryStorage."""
    from scios.runtime.observability.metrics.storage import (
        MemoryStorage,
        default_storage,
    )

    storage = default_storage()

    assert isinstance(storage, MemoryStorage)


def test_default_storage_forwards_kwargs() -> None:
    """default_storage() forwards constructor kwargs."""
    from scios.runtime.observability.metrics.storage import (
        default_storage,
    )

    storage = default_storage(
        enabled=False,
    )

    assert storage.enabled is False


# ==============================================================================
# Part 9. Public API Identity
# ==============================================================================


def test_registry_matches_public_classes() -> None:
    """Registry entries are the same classes exposed by the package."""
    import scios.runtime.observability.metrics.storage as storage

    assert storage.STORAGE_BACKENDS["memory"] is storage.MemoryStorage
    assert storage.STORAGE_BACKENDS["sqlite"] is storage.SQLiteStorage
    assert storage.STORAGE_BACKENDS["duckdb"] is storage.DuckDBStorage
    assert storage.STORAGE_BACKENDS["parquet"] is storage.ParquetStorage


def test_factory_uses_registry() -> None:
    """Factory returns an instance of the class registered for each backend."""
    import scios.runtime.observability.metrics.storage as storage

    for backend, storage_class in storage.STORAGE_BACKENDS.items():
        instance = storage.create_storage(backend)

        assert isinstance(instance, storage_class)


# ==============================================================================
# Part 10. Package Namespace Hygiene
# ==============================================================================


def test_private_implementation_names_are_not_public() -> None:
    """Implementation helpers are not part of the documented public API."""
    import scios.runtime.observability.metrics.storage as storage

    forbidden = {
        "_path",
        "_records",
        "_find_record_index",
        "_upsert_record",
        "_ensure_parent_directory",
        "_require_engine",
    }

    for name in forbidden:
        assert name not in storage.__all__