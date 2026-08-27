"""
SciOS-NG Runtime Metrics Storage
================================

Public API for the Runtime Metrics Storage subsystem.

This module defines the stable package-level API for:

- MetricStorageBackend
- MemoryStorage
- SQLiteStorage
- DuckDBStorage
- ParquetStorage
- backend aliases
- storage registry
- storage factory
- default storage factory

SciOS-NG v0.2
Python 3.11+
"""

from __future__ import annotations

from typing import Any


# ==============================================================================
# Part 1. Base Storage
# ==============================================================================

from .backend import (
    MetricStorageBackend,
)


# ==============================================================================
# Part 2. Storage Backends
# ==============================================================================

from .memory import (
    MemoryStorage,
)

from .sqlite import (
    SQLiteStorage,
)

from .duckdb import (
    DuckDBStorage,
)

from .parquet import (
    ParquetStorage,
)


# ==============================================================================
# Part 3. Backend Aliases
# ==============================================================================

StorageBackend = MetricStorageBackend

MemoryBackend = MemoryStorage

SQLiteBackend = SQLiteStorage

DuckDBBackend = DuckDBStorage

ParquetBackend = ParquetStorage


# ==============================================================================
# Part 4. Storage Registry
# ==============================================================================

STORAGE_BACKENDS: dict[str, type[MetricStorageBackend]] = {
    "memory": MemoryStorage,
    "sqlite": SQLiteStorage,
    "duckdb": DuckDBStorage,
    "parquet": ParquetStorage,
}


# ==============================================================================
# Part 5. Factory API
# ==============================================================================


def create_storage(
    backend: str = "memory",
    **kwargs: Any,
) -> MetricStorageBackend:
    """
    Create a Runtime Metrics Storage backend.

    Parameters
    ----------
    backend:
        Registered backend name.

        Supported values:

        - ``"memory"``
        - ``"sqlite"``
        - ``"duckdb"``
        - ``"parquet"``

    **kwargs:
        Keyword arguments forwarded to the selected storage constructor.

    Returns
    -------
    MetricStorageBackend
        A newly created storage backend.

    Raises
    ------
    TypeError
        If ``backend`` is not a string.

    ValueError
        If ``backend`` is not registered.

    Examples
    --------
    >>> storage = create_storage("memory")

    >>> storage = create_storage(
    ...     "sqlite",
    ...     path="metrics.db",
    ... )
    """
    if not isinstance(backend, str):
        raise TypeError("backend must be a string")

    backend_name = backend.strip().lower()

    if not backend_name:
        raise ValueError("backend must not be empty")

    try:
        storage_class = STORAGE_BACKENDS[backend_name]
    except KeyError as exc:
        supported = ", ".join(
            sorted(STORAGE_BACKENDS)
        )

        raise ValueError(
            f"Unknown storage backend: {backend!r}; "
            f"supported backends: {supported}"
        ) from exc

    return storage_class(**kwargs)


# ==============================================================================
# Part 6. Default Storage
# ==============================================================================


def default_storage(
    **kwargs: Any,
) -> MemoryStorage:
    """
    Create the default Runtime Metrics Storage backend.

    The default backend is ``MemoryStorage``.

    Parameters
    ----------
    **kwargs:
        Keyword arguments forwarded to ``MemoryStorage``.

    Returns
    -------
    MemoryStorage
        A newly created in-memory storage backend.

    Examples
    --------
    >>> storage = default_storage()
    """
    return MemoryStorage(**kwargs)


# ==============================================================================
# Part 7. Public Namespace
# ==============================================================================


__all__ = [
    # --------------------------------------------------------------------------
    # Base
    # --------------------------------------------------------------------------

    "MetricStorageBackend",
    "StorageBackend",

    # --------------------------------------------------------------------------
    # Concrete Backends
    # --------------------------------------------------------------------------

    "MemoryStorage",
    "SQLiteStorage",
    "DuckDBStorage",
    "ParquetStorage",

    # --------------------------------------------------------------------------
    # Backend Aliases
    # --------------------------------------------------------------------------

    "MemoryBackend",
    "SQLiteBackend",
    "DuckDBBackend",
    "ParquetBackend",

    # --------------------------------------------------------------------------
    # Registry
    # --------------------------------------------------------------------------

    "STORAGE_BACKENDS",

    # --------------------------------------------------------------------------
    # Factory API
    # --------------------------------------------------------------------------

    "create_storage",
    "default_storage",
]