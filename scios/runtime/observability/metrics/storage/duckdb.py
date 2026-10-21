"""
SciOS Runtime Metrics DuckDB Storage
====================================

DuckDB-backed persistent storage for runtime metrics.

The implementation follows the same lifecycle and storage contract as
``MetricStorageBackend`` while exposing a small DuckDB-specific query API.

Python 3.11+
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

from .backend import (
    MetricStorageBackend,
    StorageClosedError,
    StorageError,
)


try:
    import duckdb
except ImportError:  # pragma: no cover - handled by runtime checks
    duckdb = None


# ==============================================================================
# DuckDBStorage
# ==============================================================================


class DuckDBStorage(MetricStorageBackend):
    """
    DuckDB implementation of the SciOS metrics storage backend.

    Parameters
    ----------
    path:
        Database path. ``":memory:"`` creates an in-memory database.

    enabled:
        Whether the backend starts enabled.

    timeout:
        Connection timeout in seconds.

        DuckDB does not use this value directly in ``duckdb.connect()``.
        It is retained as part of the backend API for compatibility.

    Notes
    -----
    Values are serialized as JSON strings.

    File-backed databases persist naturally through DuckDB.

    In-memory databases normally disappear when their connection is closed.
    To preserve the backend lifecycle contract, ``DuckDBStorage`` maintains
    a serialized snapshot for ``:memory:`` databases so that:

        close()
        reopen()

    preserves the stored values.
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

        self.path = str(path)
        self.timeout = float(timeout)

        self._connection: Any = None

        # DuckDB :memory: databases disappear when the connection closes.
        # Keep a serialized snapshot to preserve data across reopen().
        self._memory_snapshot: list[tuple[str, str]] = []

        if self.enabled:
            self._initialize()

    # ==========================================================================
    # Representation
    # ==========================================================================

    def __repr__(self) -> str:
        """
        Return a concise representation of the backend.

        ``repr()`` must remain safe even when the storage is closed or
        initialization is incomplete.
        """
        try:
            size = self.count()
        except Exception:
            size = 0

        return (
            f"DuckDBStorage("
            f"path={self.path!r}, "
            f"size={size}, "
            f"enabled={self.enabled}, "
            f"closed={self.closed}, "
            f"active={self.active}"
            f")"
        )

    # ==========================================================================
    # Internal helpers
    # ==========================================================================

    def _validate_key(
        self,
        key: str,
    ) -> None:
        """
        Validate a storage key.

        Storage keys must be non-empty strings.
        """
        if not isinstance(key, str):
            raise TypeError(
                "storage key must be a string"
            )

        if not key:
            raise ValueError(
                "storage key must not be empty"
            )

    def _serialize(
        self,
        value: Any,
    ) -> str:
        """
        Serialize a Python value into JSON.

        ``default=str`` provides a deterministic fallback for values that
        are not natively JSON serializable.
        """
        try:
            return json.dumps(
                value,
                ensure_ascii=False,
                separators=(",", ":"),
                default=str,
            )
        except (TypeError, ValueError) as exc:
            raise StorageError(
                f"failed to serialize value: {exc}"
            ) from exc

    def _deserialize(
        self,
        value: str,
    ) -> Any:
        """
        Deserialize a JSON value.
        """
        try:
            return json.loads(value)
        except (
            TypeError,
            ValueError,
            json.JSONDecodeError,
        ) as exc:
            raise StorageError(
                f"invalid stored JSON value: {exc}"
            ) from exc

    def _record_operation(self) -> None:
        """
        Record a backend operation.

        ``MetricStorageBackend`` versions that already expose an operation
        counter can override this behavior. This local implementation keeps
        DuckDBStorage compatible with the existing storage contract.
        """
        operation_count = getattr(
            self,
            "_operation_count",
            0,
        )

        self._operation_count = operation_count + 1

    # ==========================================================================
    # DuckDB engine / connection
    # ==========================================================================

    def _require_engine(self) -> None:
        """
        Ensure that the DuckDB dependency is installed.
        """
        if duckdb is None:
            raise StorageError(
                "DuckDB is not installed; install it with "
                "'pip install duckdb'"
            )

    def _ensure_connection(self) -> Any:
        """
        Return the active DuckDB connection.

        Raises
        ------
        StorageClosedError
            If the backend has been closed.

        StorageError
            If the backend has been disabled.
        """
        self._ensure_active()

        if self._connection is None:
            raise StorageClosedError(
                "DuckDB storage connection is closed"
            )

        return self._connection

    # ==========================================================================
    # Initialization
    # ==========================================================================

    def _initialize(self) -> None:
        """
        Initialize the DuckDB database and metrics table.
        """
        if not self.enabled:
            return

        self._require_engine()

        if self.path != ":memory:":
            database_path = Path(
                self.path
            ).expanduser()

            database_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

        try:
            self._connection = duckdb.connect(
                database=self.path,
            )

            self._connection.execute(
                """
                CREATE TABLE IF NOT EXISTS metrics (
                    key VARCHAR PRIMARY KEY,
                    value VARCHAR NOT NULL
                )
                """
            )

            # Restore an in-memory snapshot created before close().
            if (
                self.path == ":memory:"
                and self._memory_snapshot
            ):
                self._connection.executemany(
                    """
                    INSERT INTO metrics (key, value)
                    VALUES (?, ?)
                    ON CONFLICT (key)
                    DO UPDATE SET value = excluded.value
                    """,
                    self._memory_snapshot,
                )

        except Exception as exc:
            self._connection = None

            raise StorageError(
                f"failed to initialize DuckDB storage: {exc}"
            ) from exc

    # ==========================================================================
    # Primitive CRUD
    # ==========================================================================

    def put(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Store ``value`` under ``key``.

        Existing keys are updated.
        """
        connection = self._ensure_connection()

        self._validate_key(key)

        encoded = self._serialize(value)

        try:
            connection.execute(
                """
                INSERT INTO metrics (key, value)
                VALUES (?, ?)
                ON CONFLICT (key)
                DO UPDATE SET value = excluded.value
                """,
                [key, encoded],
            )
        except Exception as exc:
            raise StorageError(
                f"failed to store key {key!r}: {exc}"
            ) from exc

        self._record_operation()

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Return the value stored under ``key``.

        ``default`` is returned when the key does not exist.
        """
        connection = self._ensure_connection()

        self._validate_key(key)

        try:
            row = connection.execute(
                """
                SELECT value
                FROM metrics
                WHERE key = ?
                """,
                [key],
            ).fetchone()
        except Exception as exc:
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
        """
        Delete ``key``.

        Returns
        -------
        bool
            ``True`` if the key existed and was deleted,
            otherwise ``False``.
        """
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
                [key],
            ).fetchone()

            if row is None:
                self._record_operation()
                return False

            connection.execute(
                """
                DELETE FROM metrics
                WHERE key = ?
                """,
                [key],
            )
        except Exception as exc:
            raise StorageError(
                f"failed to delete key {key!r}: {exc}"
            ) from exc

        self._record_operation()

        return True

    def exists(
        self,
        key: str,
    ) -> bool:
        """
        Return whether ``key`` exists.
        """
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
                [key],
            ).fetchone()
        except Exception as exc:
            raise StorageError(
                f"failed to check key {key!r}: {exc}"
            ) from exc

        self._record_operation()

        return row is not None

    def clear(self) -> None:
        """
        Remove all stored metrics.
        """
        connection = self._ensure_connection()

        try:
            connection.execute(
                """
                DELETE FROM metrics
                """
            )
        except Exception as exc:
            raise StorageError(
                f"failed to clear DuckDB storage: {exc}"
            ) from exc

        self._record_operation()

    # ==========================================================================
    # Collection API
    # ==========================================================================

    def keys(self) -> list[str]:
        """
        Return all metric keys.

        Keys are returned in deterministic key order.
        """
        connection = self._ensure_connection()

        try:
            rows = connection.execute(
                """
                SELECT key
                FROM metrics
                ORDER BY key
                """
            ).fetchall()
        except Exception as exc:
            raise StorageError(
                f"failed to read keys: {exc}"
            ) from exc

        self._record_operation()

        return [
            row[0]
            for row in rows
        ]

    def values(self) -> list[Any]:
        """
        Return all metric values.

        Values follow the same deterministic key ordering as ``keys()``.
        """
        connection = self._ensure_connection()

        try:
            rows = connection.execute(
                """
                SELECT value
                FROM metrics
                ORDER BY key
                """
            ).fetchall()
        except Exception as exc:
            raise StorageError(
                f"failed to read values: {exc}"
            ) from exc

        self._record_operation()

        return [
            self._deserialize(row[0])
            for row in rows
        ]

    def items(self) -> list[tuple[str, Any]]:
        """
        Return all key/value pairs.

        Items are returned in deterministic key order.
        """
        connection = self._ensure_connection()

        try:
            rows = connection.execute(
                """
                SELECT key, value
                FROM metrics
                ORDER BY key
                """
            ).fetchall()
        except Exception as exc:
            raise StorageError(
                f"failed to read items: {exc}"
            ) from exc

        self._record_operation()

        return [
            (
                key,
                self._deserialize(value),
            )
            for key, value in rows
        ]

    # ==========================================================================
    # Batch API
    # ==========================================================================

    def put_many(
        self,
        values: Mapping[str, Any] | Iterable[tuple[str, Any]],
    ) -> None:
        """
        Store multiple values.

        Existing keys are updated.
        """
        connection = self._ensure_connection()

        if isinstance(values, Mapping):
            values = values.items()

        normalized: list[tuple[str, str]] = []

        for key, value in values:
            self._validate_key(key)

            normalized.append(
                (
                    key,
                    self._serialize(value),
                )
            )

        if not normalized:
            return

        try:
            connection.executemany(
                """
                INSERT INTO metrics (key, value)
                VALUES (?, ?)
                ON CONFLICT (key)
                DO UPDATE SET value = excluded.value
                """,
                normalized,
            )
        except Exception as exc:
            raise StorageError(
                f"failed to store multiple values: {exc}"
            ) from exc

        self._record_operation()

    def get_many(
        self,
        keys: Iterable[str],
    ) -> dict[str, Any]:
        """
        Return multiple values.

        Missing keys map to ``None``.
        """
        result: dict[str, Any] = {}

        for key in keys:
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
            Number of keys actually deleted.
        """
        connection = self._ensure_connection()

        normalized: list[str] = []

        for key in keys:
            self._validate_key(key)
            normalized.append(key)

        if not normalized:
            return 0

        deleted = 0

        try:
            for key in normalized:
                row = connection.execute(
                    """
                    SELECT 1
                    FROM metrics
                    WHERE key = ?
                    LIMIT 1
                    """,
                    [key],
                ).fetchone()

                if row is None:
                    continue

                connection.execute(
                    """
                    DELETE FROM metrics
                    WHERE key = ?
                    """,
                    [key],
                )

                deleted += 1

        except Exception as exc:
            raise StorageError(
                f"failed to delete multiple values: {exc}"
            ) from exc

        self._record_operation()

        return deleted

    # ==========================================================================
    # DuckDB-specific API
    # ==========================================================================

    def query(
        self,
        sql: str,
        parameters: Iterable[Any] | None = None,
    ) -> Any:
        """
        Execute a DuckDB query.

        The native DuckDB result object is returned directly.
        """
        connection = self._ensure_connection()

        if not isinstance(sql, str):
            raise TypeError(
                "sql must be a string"
            )

        if not sql.strip():
            raise ValueError(
                "sql must not be empty"
            )

        try:
            if parameters is None:
                result = connection.execute(
                    sql
                )
            else:
                result = connection.execute(
                    sql,
                    list(parameters),
                )
        except Exception as exc:
            raise StorageError(
                f"failed to execute DuckDB query: {exc}"
            ) from exc

        self._record_operation()

        return result


    def dataframe(self):
        """
        Return the metrics table as a pandas DataFrame.

        Pandas is an optional dependency and is imported lazily so that
        DuckDBStorage remains fully usable without pandas for all other
        storage operations.
        """
        connection = self._ensure_connection()

        try:
            import pandas as pd
        except ImportError as exc:
            raise StorageError(
                "pandas is required for dataframe(); "
                "install it with 'pip install pandas'"
            ) from exc

        try:
            rows = connection.execute(
                """
                SELECT key, value
                FROM metrics
                ORDER BY key
                """
            ).fetchall()

            frame = pd.DataFrame(
                rows,
                columns=["key", "value"],
            )

        except Exception as exc:
            raise StorageError(
                f"failed to create DataFrame: {exc}"
            ) from exc

        self._record_operation()

        return frame


    def count(self) -> int:
        """
        Return the number of stored entries.
        """
        connection = self._ensure_connection()

        try:
            row = connection.execute(
                """
                SELECT COUNT(*)
                FROM metrics
                """
            ).fetchone()
        except Exception as exc:
            raise StorageError(
                f"failed to count metrics: {exc}"
            ) from exc

        self._record_operation()

        return int(row[0])

    def aggregate(
        self,
        expression: str,
    ) -> Any:
        """
        Execute a scalar aggregate expression over ``metrics``.

        Examples
        --------
        ``storage.aggregate("COUNT(*)")``

        ``storage.aggregate("MAX(CAST(value AS DOUBLE))")``
        """
        connection = self._ensure_connection()

        if not isinstance(expression, str):
            raise TypeError(
                "expression must be a string"
            )

        if not expression.strip():
            raise ValueError(
                "expression must not be empty"
            )

        try:
            row = connection.execute(
                f"""
                SELECT {expression}
                FROM metrics
                """
            ).fetchone()
        except Exception as exc:
            raise StorageError(
                f"failed to aggregate metrics: {exc}"
            ) from exc

        self._record_operation()

        return None if row is None else row[0]

    def optimize(self) -> None:
        """
        Run DuckDB checkpoint/maintenance operation.
        """
        connection = self._ensure_connection()

        try:
            connection.execute(
                """
                CHECKPOINT
                """
            )
        except Exception as exc:
            raise StorageError(
                f"failed to optimize DuckDB storage: {exc}"
            ) from exc

        self._record_operation()

    # ==========================================================================
    # Lifecycle
    # ==========================================================================

    def close(self) -> None:
        """
        Close the DuckDB connection.

        For ``:memory:``, snapshot the current table before closing so that
        ``reopen()`` can restore the data.
        """
        if self.closed:
            return

        if self._connection is not None:
            if self.path == ":memory:":
                try:
                    self._memory_snapshot = (
                        self._connection.execute(
                            """
                            SELECT key, value
                            FROM metrics
                            ORDER BY key
                            """
                        ).fetchall()
                    )
                except Exception as exc:
                    raise StorageError(
                        "failed to snapshot in-memory "
                        f"DuckDB storage: {exc}"
                    ) from exc

            try:
                self._connection.close()
            except Exception as exc:
                raise StorageError(
                    f"failed to close DuckDB storage: {exc}"
                ) from exc

            self._connection = None

        # Keep enabled=True so reopen() remains possible.
        self._closed = True

    def reopen(self) -> None:
        """
        Reopen the storage backend.

        Closing a backend is reversible.
        """
        if self._connection is not None:
            return

        self._closed = False

        try:
            self._initialize()
        except Exception:
            self._closed = True
            raise

    # ==========================================================================
    # Inspection
    # ==========================================================================

    def statistics(self) -> dict[str, Any]:
        """
        Return DuckDB storage statistics.
        """
        connection = self._ensure_connection()

        try:
            row = connection.execute(
                """
                SELECT COUNT(*)
                FROM metrics
                """
            ).fetchone()
        except Exception as exc:
            raise StorageError(
                f"failed to collect statistics: {exc}"
            ) from exc

        self._record_operation()

        return {
            "backend": "duckdb",
            "path": self.path,
            "count": int(row[0]),
            "enabled": self.enabled,
            "closed": self.closed,
            "active": self.active,
        }

    # ==========================================================================
    # Python protocol API
    # ==========================================================================

    def __len__(self) -> int:
        """
        Return the number of stored entries.
        """
        return self.count()

    def __contains__(
        self,
        key: object,
    ) -> bool:
        """
        Support ``key in storage``.
        """
        if not isinstance(key, str):
            return False

        if not self.active:
            return False

        return self.exists(key)