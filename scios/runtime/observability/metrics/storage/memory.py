"""
SciOS Runtime Metrics Memory Storage
====================================

In-memory storage backend for Runtime Metrics.

This backend provides a fast, dependency-free storage implementation
for metrics collection, testing, caching, and ephemeral runtime state.

Python 3.11+
"""

from __future__ import annotations

import copy
import time
from collections.abc import Iterable, Mapping
from typing import Any

from .backend import (
    MetricStorageBackend,
    StorageClosedError,
    StorageError,
)


# ==============================================================================
# MemoryStorage
# ==============================================================================


class MemoryStorage(MetricStorageBackend):
    """
    In-memory metrics storage backend.

    Parameters
    ----------
    enabled:
        Whether the storage starts enabled.

    Notes
    -----
    Values are stored in a regular Python dictionary.

    ``snapshot()`` and ``restore()`` use deep copies so that mutable values
    cannot accidentally mutate a previously captured snapshot.
    """

    def __init__(
        self,
        *,
        enabled: bool = True,
    ) -> None:
        super().__init__(
            enabled=enabled,
        )

        self._data: dict[str, Any] = {}
        self._created_at = time.time()
        self._updated_at = self._created_at
        self._operation_count = 0

    # ==========================================================================
    # Internal helpers
    # ==========================================================================

    def _record_operation(self) -> None:
        """Record a storage operation."""
        self._operation_count += 1
        self._updated_at = time.time()

    def _validate_key(
        self,
        key: str,
    ) -> None:
        """Validate storage keys."""
        if not isinstance(key, str):
            raise TypeError("storage key must be a string")

        if not key:
            raise ValueError("storage key must not be empty")

    # ==========================================================================
    # Primitive CRUD
    # ==========================================================================

    def put(
        self,
        key: str,
        value: Any,
    ) -> None:
        """Store ``value`` under ``key``."""
        self._ensure_active()
        self._validate_key(key)

        self._data[key] = value
        self._record_operation()

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """Return the value stored under ``key``."""
        self._ensure_active()
        self._validate_key(key)

        self._record_operation()

        return self._data.get(
            key,
            default,
        )

    def delete(
        self,
        key: str,
    ) -> bool:
        """Delete ``key`` and return whether it existed."""
        self._ensure_active()
        self._validate_key(key)

        if key not in self._data:
            self._record_operation()
            return False

        del self._data[key]
        self._record_operation()

        return True

    def exists(
        self,
        key: str,
    ) -> bool:
        """Return whether ``key`` exists."""
        self._ensure_active()
        self._validate_key(key)

        self._record_operation()

        return key in self._data

    def clear(self) -> None:
        """Remove all stored values."""
        self._ensure_active()

        self._data.clear()
        self._record_operation()

    def keys(self) -> Iterable[str]:
        """Return a snapshot of stored keys."""
        self._ensure_active()

        self._record_operation()

        return tuple(self._data.keys())

    def values(self) -> Iterable[Any]:
        """Return a snapshot of stored values."""
        self._ensure_active()

        self._record_operation()

        return tuple(self._data.values())

    def items(self) -> Iterable[tuple[str, Any]]:
        """Return a snapshot of stored key/value pairs."""
        self._ensure_active()

        self._record_operation()

        return tuple(self._data.items())

    # ==========================================================================
    # Extended mutation API
    # ==========================================================================

    def update(
        self,
        values: Mapping[str, Any] | None = None,
        /,
        **kwargs: Any,
    ) -> None:
        """
        Update multiple values.

        Both a mapping and keyword arguments may be supplied.

        Examples
        --------
        ``storage.update({"a": 1, "b": 2})``

        ``storage.update(a=1, b=2)``
        """
        self._ensure_active()

        if values is not None:
            if not isinstance(values, Mapping):
                raise TypeError("values must be a mapping")

            for key in values:
                self._validate_key(key)

            for key, value in values.items():
                self._data[key] = value

        for key, value in kwargs.items():
            self._validate_key(key)
            self._data[key] = value

        self._record_operation()

    def get_or_set(
        self,
        key: str,
        default: Any,
    ) -> Any:
        """
        Return an existing value or store and return ``default``.
        """
        self._ensure_active()
        self._validate_key(key)

        if key in self._data:
            self._record_operation()
            return self._data[key]

        self._data[key] = default
        self._record_operation()

        return default

    # ==========================================================================
    # Snapshot / restore
    # ==========================================================================

    def snapshot(self) -> dict[str, Any]:
        """
        Return a deep-copy snapshot of the storage state.
        """
        self._ensure_active()

        self._record_operation()

        return copy.deepcopy(self._data)

    def restore(
        self,
        snapshot: Mapping[str, Any],
    ) -> None:
        """
        Replace storage contents from a snapshot.
        """
        self._ensure_active()

        if not isinstance(snapshot, Mapping):
            raise TypeError("snapshot must be a mapping")

        for key in snapshot:
            self._validate_key(key)

        self._data = copy.deepcopy(
            dict(snapshot)
        )

        self._record_operation()

    # ==========================================================================
    # Size / maintenance
    # ==========================================================================

    def size(self) -> int:
        """Return the number of stored entries."""
        self._ensure_active()

        return len(self._data)

    def compact(self) -> int:
        """
        Compact the storage.

        Python dictionaries do not expose a direct compaction primitive,
        therefore this operation rebuilds the dictionary.

        Returns
        -------
        int
            Number of entries retained.
        """
        self._ensure_active()

        self._data = dict(self._data)
        self._record_operation()

        return len(self._data)

    def cleanup(self) -> int:
        """
        Remove entries whose value is ``None``.

        Returns
        -------
        int
            Number of removed entries.
        """
        self._ensure_active()

        before = len(self._data)

        self._data = {
            key: value
            for key, value in self._data.items()
            if value is not None
        }

        removed = before - len(self._data)

        self._record_operation()

        return removed

    # ==========================================================================
    # Statistics
    # ==========================================================================

    def statistics(self) -> dict[str, Any]:
        """Return memory-storage statistics."""
        self._ensure_active()

        return {
            "backend": self.__class__.__name__,
            "enabled": self.enabled,
            "closed": self.closed,
            "active": self.active,
            "count": len(self._data),
            "size": len(self._data),
            "operations": self._operation_count,
            "created_at": self._created_at,
            "updated_at": self._updated_at,
        }

    # ==========================================================================
    # Lifecycle
    # ==========================================================================

    def close(self) -> None:
        """
        Close the memory storage.

        Data is intentionally retained so that ``reopen()`` can restore
        access to the existing in-memory state.
        """
        super().close()

    def reopen(self) -> None:
        """Reopen the memory storage."""
        super().reopen()

    # ==========================================================================
    # Python protocols
    # ==========================================================================

    def __len__(self) -> int:
        """Return number of stored entries."""
        return len(self._data)

    def __iter__(self):
        """Iterate over stored keys."""
        self._ensure_active()
        return iter(tuple(self._data.keys()))

    def __getitem__(
        self,
        key: str,
    ) -> Any:
        """Support ``storage[key]``."""
        self._ensure_active()
        self._validate_key(key)

        if key not in self._data:
            raise KeyError(key)

        return self._data[key]

    def __setitem__(
        self,
        key: str,
        value: Any,
    ) -> None:
        """Support ``storage[key] = value``."""
        self.put(
            key,
            value,
        )

    def __delitem__(
        self,
        key: str,
    ) -> None:
        """Support ``del storage[key]``."""
        self._ensure_active()
        self._validate_key(key)

        if key not in self._data:
            raise KeyError(key)

        del self._data[key]
        self._record_operation()

    def __contains__(
        self,
        key: object,
    ) -> bool:
        """Support ``key in storage``."""
        if not isinstance(key, str):
            return False

        if not self.active:
            return False

        return key in self._data

    def __repr__(self) -> str:
        """Return a concise representation."""
        return (
            f"{self.__class__.__name__}("
            f"size={len(self._data)!r}, "
            f"enabled={self.enabled!r}, "
            f"closed={self.closed!r}, "
            f"active={self.active!r}"
            f")"
        )


__all__ = [
    "MemoryStorage",
]