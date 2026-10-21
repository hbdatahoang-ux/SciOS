"""
SciOS Runtime Metrics Storage Backend
=====================================

Abstract contract for Runtime Metrics Storage backends.

The storage backend defines the common lifecycle, CRUD, batch, inspection,
and statistics API shared by all concrete metrics storage implementations.

Python 3.11+
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable, Mapping
from typing import Any


# ==============================================================================
# Part 1. Exceptions
# ==============================================================================


class StorageError(RuntimeError):
    """Base exception for metrics storage failures."""


class StorageClosedError(StorageError):
    """Raised when an operation requires an active storage backend."""


# ==============================================================================
# Part 2. MetricStorageBackend
# ==============================================================================


class MetricStorageBackend(ABC):
    """
    Abstract base class for SciOS Runtime Metrics storage.

    Concrete implementations must provide the primitive CRUD operations:

    - put()
    - get()
    - delete()
    - exists()
    - clear()
    - keys()
    - values()
    - items()

    Batch operations and lifecycle helpers are implemented here in terms of
    those primitives so that all storage backends expose a consistent API.
    """

    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------

    def __init__(
        self,
        *,
        enabled: bool = True,
    ) -> None:
        self._enabled = bool(enabled)
        self._closed = False

    # ------------------------------------------------------------------
    # Lifecycle state
    # ------------------------------------------------------------------

    @property
    def enabled(self) -> bool:
        """Return whether the backend is enabled."""
        return self._enabled

    @property
    def closed(self) -> bool:
        """Return whether the backend has been closed."""
        return self._closed

    @property
    def active(self) -> bool:
        """Return whether the backend is enabled and open."""
        return self._enabled and not self._closed

    # ------------------------------------------------------------------
    # Primitive storage API
    # ------------------------------------------------------------------

    @abstractmethod
    def put(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Store a value under ``key``.
        """

    @abstractmethod
    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve a value by key.

        ``default`` is returned when the key does not exist.
        """

    @abstractmethod
    def delete(
        self,
        key: str,
    ) -> bool:
        """
        Delete a key.

        Returns
        -------
        bool
            ``True`` when an item was removed, otherwise ``False``.
        """

    @abstractmethod
    def exists(
        self,
        key: str,
    ) -> bool:
        """Return whether ``key`` exists."""

    @abstractmethod
    def clear(self) -> None:
        """Remove all stored values."""

    @abstractmethod
    def keys(self) -> Iterable[str]:
        """Return an iterable of stored keys."""

    @abstractmethod
    def values(self) -> Iterable[Any]:
        """Return an iterable of stored values."""

    @abstractmethod
    def items(self) -> Iterable[tuple[str, Any]]:
        """Return an iterable of ``(key, value)`` pairs."""

    # ------------------------------------------------------------------
    # Batch API
    # ------------------------------------------------------------------

    def put_many(
        self,
        values: Mapping[str, Any],
    ) -> None:
        """
        Store multiple values.

        Parameters
        ----------
        values:
            Mapping of keys to values.
        """
        if not isinstance(values, Mapping):
            raise TypeError("values must be a mapping")

        self._ensure_active()

        for key, value in values.items():
            self.put(key, value)

    def get_many(
        self,
        keys: Iterable[str],
    ) -> dict[str, Any]:
        """
        Retrieve multiple values.

        Missing keys are omitted from the result.
        """
        self._ensure_active()

        result: dict[str, Any] = {}

        for key in keys:
            if self.exists(key):
                result[key] = self.get(key)

        return result

    def delete_many(
        self,
        keys: Iterable[str],
    ) -> int:
        """
        Delete multiple values.

        Returns
        -------
        int
            Number of deleted entries.
        """
        self._ensure_active()

        deleted = 0

        for key in keys:
            if self.delete(key):
                deleted += 1

        return deleted

    # ------------------------------------------------------------------
    # Lifecycle API
    # ------------------------------------------------------------------

    def enable(self) -> None:
        """Enable the backend."""
        if self._closed:
            raise StorageClosedError(
                "cannot enable a closed storage backend"
            )

        self._enabled = True

    def disable(self) -> None:
        """Disable the backend."""
        if self._closed:
            raise StorageClosedError(
                "cannot disable a closed storage backend"
            )

        self._enabled = False

    def close(self) -> None:
        """Close the backend."""
        self._closed = True
        self._enabled = False

    def reopen(self) -> None:
        """
        Reopen the backend.

        Concrete persistent backends may override this method if they need
        to recreate a database connection or file handle.
        """
        self._closed = False
        self._enabled = True

    # ------------------------------------------------------------------
    # Inspection API
    # ------------------------------------------------------------------

    def statistics(self) -> dict[str, Any]:
        """
        Return basic backend statistics.
        """
        self._ensure_active()

        try:
            count = len(self)
        except (TypeError, NotImplementedError):
            count = sum(1 for _ in self.items())

        return {
            "backend": self.__class__.__name__,
            "enabled": self.enabled,
            "closed": self.closed,
            "active": self.active,
            "count": count,
        }

    def status(self) -> dict[str, Any]:
        """
        Return backend lifecycle status.
        """
        return {
            "backend": self.__class__.__name__,
            "enabled": self.enabled,
            "closed": self.closed,
            "active": self.active,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _touch(self) -> None:
        """
        Hook for concrete backends.

        Concrete implementations may override this when an operation should
        update timestamps, access metadata, or connection state.
        """

    def _ensure_active(self) -> None:
        """Raise when the backend is unavailable for normal operations."""
        if self._closed:
            raise StorageClosedError(
                "storage backend is closed"
            )

        if not self._enabled:
            raise StorageError(
                "storage backend is disabled"
            )

        self._touch()

    # ------------------------------------------------------------------
    # Python protocol helpers
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        """Return the number of stored entries."""
        return sum(1 for _ in self.items())

    def __contains__(
        self,
        key: object,
    ) -> bool:
        """Support ``key in storage``."""
        if not isinstance(key, str):
            return False

        if not self.active:
            return False

        return self.exists(key)

    def __repr__(self) -> str:
        """Return a concise backend representation."""
        return (
            f"{self.__class__.__name__}("
            f"enabled={self.enabled!r}, "
            f"closed={self.closed!r}, "
            f"active={self.active!r}"
            f")"
        )


__all__ = [
    "StorageError",
    "StorageClosedError",
    "MetricStorageBackend",
]