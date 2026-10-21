"""
SciOS Runtime Metrics SQLite Storage
====================================

Persistent SQLite storage backend for Runtime Metrics.

Python 3.11+
"""

from __future__ import annotations

import json
import sqlite3
import time
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

from .backend import (
    MetricStorageBackend,
    StorageClosedError,
    StorageError,
)


# ==============================================================================
# SQLiteStorage
# ==============================================================================


class SQLiteStorage(MetricStorageBackend):
    """
    SQLite-backed persistent metrics storage.

    Parameters
    ----------
    path:
        SQLite database path. ``":memory:"`` creates an in-memory SQLite DB.
    enabled:
        Whether the storage starts enabled.
    timeout:
        SQLite connection timeout in seconds.
    """

    def __init__(
        self,
        path: str | Path = ":memory:",
        *,
        enabled: bool = True,
        timeout: float = 5.0,
    ) -> None:
        super().__init__(
            enabled=enabled,
        )

        # Keep the internal representation compatible with both:
        #   - the SQLite special path ":memory:"
        #   - filesystem-backed paths
        self._path = (
            path
            if isinstance(path, str) and path == ":memory:"
            else Path(path)
        )

        self.timeout = float(timeout)

        self._created_at = time.time()
        self._updated_at = self._created_at
        self._operation_count = 0

        self._connection: sqlite3.Connection | None = None

        self._memory_snapshot: list[tuple[str, object]] | None = None

        self._initialize()

    # ==========================================================================
    # Properties
    # ==========================================================================

    @property
    def path(self) -> str:
        """
        Return the configured SQLite database path.

        The public API intentionally exposes the path as ``str`` so that
        filesystem paths behave consistently across Windows and POSIX
        platforms and remain compatible with the storage backend contract.
        """
        return str(self._path)


    # ==========================================================================
    # Internal helpers
    # ==========================================================================

    def _record_operation(self) -> None:
        self._operation_count += 1
        self._updated_at = time.time()

    # ==========================================================================
    # Internal helpers
    # ==========================================================================

    def _record_operation(self) -> None:
        self._operation_count += 1
        self._updated_at = time.time()

    def _validate_key(
        self,
        key: str,
    ) -> None:
        if not isinstance(key, str):
            raise TypeError("storage key must be a string")

        if not key:
            raise ValueError("storage key must not be empty")

    def _serialize(
        self,
        value: Any,
    ) -> str:
        try:
            return json.dumps(
                value,
                ensure_ascii=False,
                separators=(",", ":"),
            )
        except (TypeError, ValueError) as exc:
            raise StorageError(
                f"value is not JSON serializable: {exc}"
            ) from exc

    def _deserialize(
        self,
        value: str,
    ) -> Any:
        try:
            return json.loads(value)
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            raise StorageError(
                f"invalid stored JSON value: {exc}"
            ) from exc

    def _ensure_connection(self) -> sqlite3.Connection:
        self._ensure_active()

        if self._connection is None:
            raise StorageClosedError(
                "SQLite storage connection is closed"
            )

        return self._connection

    # ==========================================================================
    # Initialization
    # ==========================================================================

    def _initialize(self) -> None:
        """
        Initialize the SQLite database and storage table.
        """
        if not self.enabled:
            return

        if self.path != ":memory:":
            Path(self.path).expanduser().parent.mkdir(
                parents=True,
                exist_ok=True,
            )

        try:
            self._connection = sqlite3.connect(
                self.path,
                timeout=self.timeout,
            )

            self._connection.execute(
                """
                CREATE TABLE IF NOT EXISTS metrics (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
                """
            )

            self._connection.commit()

        except sqlite3.Error as exc:
            self._connection = None
            raise StorageError(
                f"failed to initialize SQLite storage: {exc}"
            ) from exc

    # ==========================================================================
    # CRUD
    # ==========================================================================

    def put(
        self,
        key: str,
        value: Any,
    ) -> None:
        """Store a value under ``key``."""
        connection = self._ensure_connection()
        self._validate_key(key)

        encoded = self._serialize(value)

        try:
            connection.execute(
                """
                INSERT INTO metrics (key, value)
                VALUES (?, ?)
                ON CONFLICT(key)
                DO UPDATE SET value = excluded.value
                """,
                (
                    key,
                    encoded,
                ),
            )
            connection.commit()

        except sqlite3.Error as exc:
            connection.rollback()
            raise StorageError(
                f"failed to store key {key!r}: {exc}"
            ) from exc

        self._record_operation()

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """Return the value stored under ``key``."""
        connection = self._ensure_connection()
        self._validate_key(key)

        try:
            row = connection.execute(
                """
                SELECT value
                FROM metrics
                WHERE key = ?
                """,
                (key,),
            ).fetchone()

        except sqlite3.Error as exc:
            raise StorageError(
                f"failed to read key {key!r}: {exc}"
            ) from exc

        self._record_operation()

        if row is None:
            return default

        return self._deserialize(row[0])

    def delete(
        self,
        key: str,
    ) -> bool:
        """Delete a key and return whether it existed."""
        connection = self._ensure_connection()
        self._validate_key(key)

        try:
            cursor = connection.execute(
                """
                DELETE FROM metrics
                WHERE key = ?
                """,
                (key,),
            )
            connection.commit()

        except sqlite3.Error as exc:
            connection.rollback()
            raise StorageError(
                f"failed to delete key {key!r}: {exc}"
            ) from exc

        self._record_operation()

        return cursor.rowcount > 0

    def exists(
        self,
        key: str,
    ) -> bool:
        """Return whether ``key`` exists."""
        connection = self._ensure_connection()
        self._validate_key(key)

        try:
            row = connection.execute(
                """
                SELECT 1
                FROM metrics
                WHERE key = ?
                LIMIT 1
                """,
                (key,),
            ).fetchone()

        except sqlite3.Error as exc:
            raise StorageError(
                f"failed to check key {key!r}: {exc}"
            ) from exc

        self._record_operation()

        return row is not None

    def clear(self) -> None:
        """Remove all stored values."""
        connection = self._ensure_connection()

        try:
            connection.execute(
                "DELETE FROM metrics"
            )
            connection.commit()

        except sqlite3.Error as exc:
            connection.rollback()
            raise StorageError(
                f"failed to clear SQLite storage: {exc}"
            ) from exc

        self._record_operation()

    def keys(self) -> Iterable[str]:
        """Return all stored keys."""
        connection = self._ensure_connection()

        try:
            rows = connection.execute(
                """
                SELECT key
                FROM metrics
                ORDER BY rowid
                """
            ).fetchall()

        except sqlite3.Error as exc:
            raise StorageError(
                f"failed to retrieve keys: {exc}"
            ) from exc

        self._record_operation()

        return tuple(
            row[0]
            for row in rows
        )

    def values(self) -> Iterable[Any]:
        """Return all stored values."""
        connection = self._ensure_connection()

        try:
            rows = connection.execute(
                """
                SELECT value
                FROM metrics
                ORDER BY rowid
                """
            ).fetchall()

        except sqlite3.Error as exc:
            raise StorageError(
                f"failed to retrieve values: {exc}"
            ) from exc

        self._record_operation()

        return tuple(
            self._deserialize(row[0])
            for row in rows
        )

    def items(self) -> Iterable[tuple[str, Any]]:
        """Return all stored key/value pairs."""
        connection = self._ensure_connection()

        try:
            rows = connection.execute(
                """
                SELECT key, value
                FROM metrics
                ORDER BY rowid
                """
            ).fetchall()

        except sqlite3.Error as exc:
            raise StorageError(
                f"failed to retrieve items: {exc}"
            ) from exc

        self._record_operation()

        return tuple(
            (
                row[0],
                self._deserialize(row[1]),
            )
            for row in rows
        )

    # ==========================================================================
    # Batch operations
    # ==========================================================================

    def put_many(
        self,
        values: Mapping[str, Any],
    ) -> None:
        """Store multiple values atomically."""
        connection = self._ensure_connection()

        if not isinstance(values, Mapping):
            raise TypeError("values must be a mapping")

        rows: list[tuple[str, str]] = []

        for key, value in values.items():
            self._validate_key(key)
            rows.append(
                (
                    key,
                    self._serialize(value),
                )
            )

        try:
            connection.executemany(
                """
                INSERT INTO metrics (key, value)
                VALUES (?, ?)
                ON CONFLICT(key)
                DO UPDATE SET value = excluded.value
                """,
                rows,
            )
            connection.commit()

        except sqlite3.Error as exc:
            connection.rollback()
            raise StorageError(
                f"failed to store multiple values: {exc}"
            ) from exc

        self._record_operation()

    def get_many(
        self,
        keys: Iterable[str],
    ) -> dict[str, Any]:
        """Retrieve multiple keys."""
        self._ensure_connection()

        result: dict[str, Any] = {}

        for key in keys:
            self._validate_key(key)

            value = self.get(
                key,
                None,
            )

            if self.exists(key):
                result[key] = value

        return result

    def delete_many(
        self,
        keys: Iterable[str],
    ) -> int:
        """Delete multiple keys and return the number deleted."""
        connection = self._ensure_connection()

        normalized = tuple(keys)

        for key in normalized:
            self._validate_key(key)

        if not normalized:
            return 0

        try:
            cursor = connection.executemany(
                """
                DELETE FROM metrics
                WHERE key = ?
                """,
                (
                    (key,)
                    for key in normalized
                ),
            )
            connection.commit()

        except sqlite3.Error as exc:
            connection.rollback()
            raise StorageError(
                f"failed to delete multiple values: {exc}"
            ) from exc

        self._record_operation()

        return cursor.rowcount

    # ==========================================================================
    # SQLite-specific API
    # ==========================================================================

    def count(self) -> int:
        """Return the number of stored entries."""
        connection = self._ensure_connection()

        try:
            row = connection.execute(
                "SELECT COUNT(*) FROM metrics"
            ).fetchone()

        except sqlite3.Error as exc:
            raise StorageError(
                f"failed to count metrics: {exc}"
            ) from exc

        self._record_operation()

        return int(row[0])

    def search(
        self,
        pattern: str,
    ) -> dict[str, Any]:
        """
        Search keys using SQLite LIKE semantics.
        """
        connection = self._ensure_connection()

        if not isinstance(pattern, str):
            raise TypeError("pattern must be a string")

        try:
            rows = connection.execute(
                """
                SELECT key, value
                FROM metrics
                WHERE key LIKE ?
                ORDER BY rowid
                """,
                (pattern,),
            ).fetchall()

        except sqlite3.Error as exc:
            raise StorageError(
                f"failed to search metrics: {exc}"
            ) from exc

        self._record_operation()

        return {
            key: self._deserialize(value)
            for key, value in rows
        }

    def vacuum(self) -> None:
        """Run SQLite VACUUM."""
        connection = self._ensure_connection()

        try:
            connection.execute(
                "VACUUM"
            )

        except sqlite3.Error as exc:
            raise StorageError(
                f"failed to vacuum SQLite database: {exc}"
            ) from exc

        self._record_operation()

    # ==========================================================================
    # Lifecycle
    # ==========================================================================

    def close(self) -> None:
        """
        Close the SQLite storage backend.

        For an in-memory database, preserve its logical contents before
        destroying the connection so that ``reopen()`` can restore them.
        """

        if self._connection is not None:

            if self.path == ":memory:":
                rows = self._connection.execute(
                    "SELECT key, value FROM metrics"
                ).fetchall()

                self._memory_snapshot = [
                    (key, value)
                    for key, value in rows
                ]

            self._connection.close()
            self._connection = None

        self._closed = True
        self._enabled = False



    def reopen(self) -> None:
        """
        Reopen the SQLite storage backend.

        For file-backed databases, data is already persisted by SQLite.

        For ``:memory:`` databases, closing the connection destroys the
        database, so the in-memory snapshot captured during ``close()``
        must be restored into the newly created connection.
        """
        # ------------------------------------------------------------------
        # Lifecycle state
        # ------------------------------------------------------------------

        self._closed = False
        self._enabled = True

        # ------------------------------------------------------------------
        # Create a fresh SQLite connection and schema
        # ------------------------------------------------------------------

        self._initialize()

        if self._connection is None:
            raise StorageError(
                "failed to reopen SQLite storage"
            )

        # ------------------------------------------------------------------
        # Restore in-memory database contents
        # ------------------------------------------------------------------

        if self.path == ":memory:":
            snapshot = getattr(
                self,
                "_memory_snapshot",
                None,
            )

            if snapshot:
                try:
                    self._connection.executemany(
                        """
                        INSERT INTO metrics (key, value)
                        VALUES (?, ?)
                        ON CONFLICT(key)
                        DO UPDATE SET value = excluded.value
                        """,
                        snapshot,
                    )

                    self._connection.commit()

                except sqlite3.Error as exc:
                    self._connection.rollback()

                    self._connection = None
                    self._closed = True

                    raise StorageError(
                        f"failed to restore in-memory SQLite storage: {exc}"
                    ) from exc

        # ------------------------------------------------------------------
        # Clear consumed snapshot
        # ------------------------------------------------------------------

        self._memory_snapshot = None

    # ==========================================================================
    # Statistics
    # ==========================================================================

    def statistics(self) -> dict[str, Any]:
        """Return SQLite storage statistics."""
        self._ensure_connection()

        return {
            "backend": self.__class__.__name__,
            "path": self.path,
            "enabled": self.enabled,
            "closed": self.closed,
            "active": self.active,
            "count": self.count(),
            "size": self.count(),
            "operations": self._operation_count,
            "created_at": self._created_at,
            "updated_at": self._updated_at,
        }

    # ==========================================================================
    # Python protocols
    # ==========================================================================

    def __len__(self) -> int:
        return self.count()

    def __iter__(self):
        return iter(self.keys())

    def __getitem__(
        self,
        key: str,
    ) -> Any:
        self._ensure_connection()
        self._validate_key(key)

        value = self.get(
            key,
            None,
        )

        if not self.exists(key):
            raise KeyError(key)

        return value

    def __setitem__(
        self,
        key: str,
        value: Any,
    ) -> None:
        self.put(
            key,
            value,
        )

    def __delitem__(
        self,
        key: str,
    ) -> None:
        if not self.delete(key):
            raise KeyError(key)

    def __contains__(
        self,
        key: object,
    ) -> bool:
        if not isinstance(key, str):
            return False

        if not self.active:
            return False

        return self.exists(key)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"path={self.path!r}, "
            f"size={len(self)!r}, "
            f"enabled={self.enabled!r}, "
            f"closed={self.closed!r}, "
            f"active={self.active!r}"
            f")"
        )


__all__ = [
    "SQLiteStorage",
]