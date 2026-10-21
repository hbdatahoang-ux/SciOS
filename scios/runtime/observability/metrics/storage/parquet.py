"""
SciOS Runtime Metrics Parquet Storage
=====================================

Persistent Parquet-backed storage backend for runtime metrics.

The implementation intentionally keeps the in-memory record model simple::

    {
        "key": <str>,
        "value": <Any>,
    }

The Parquet engine is loaded lazily so that constructing the backend does
not require pandas/pyarrow until an operation actually needs the engine.

Ordering contract
-----------------
The storage maintains deterministic insertion order.

For ``put()``:
    - new keys are appended;
    - existing keys are replaced in-place.

For ``load()``:
    - records are restored in the exact order stored in the Parquet file.

For ``append()``:
    - current in-memory records are written first;
    - existing persisted records follow;
    - duplicate keys are resolved according to the storage invariant:
      the current record wins while its position remains first.

Persistence contract
--------------------
``load()`` requires the configured Parquet file to exist.

A missing file is therefore an error rather than an empty-storage condition.

Python 3.11+
"""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional

from .backend import MetricStorageBackend, StorageError


# ==============================================================================
# Exceptions
# ==============================================================================


class ParquetStorageError(StorageError):
    """Base exception for Parquet storage failures."""


# ==============================================================================
# ParquetStorage
# ==============================================================================


class ParquetStorage(MetricStorageBackend):
    """
    Persistent metrics storage backed by a Parquet file.

    The storage maintains a deterministic ordered list of records.

    Each key is unique. Putting an existing key replaces its value while
    preserving the key's original position.

    Mutation contract
    -----------------
    - ``put()`` returns the supplied value.
    - ``delete()`` returns ``self``.
    - ``clear()`` returns ``self``.
    - ``restore()`` returns ``self``.

    Persistence contract
    --------------------
    - ``write()`` replaces the target file with current records.
    - ``load()`` requires the target file to exist.
    - ``append()`` places current records before persisted records.
    """

    # ==========================================================================
    # Constructor
    # ==========================================================================

    def __init__(
        self,
        path: str | Path = "metrics.parquet",
        *,
        enabled: bool = True,
        name: str = "metrics",
        description: str = "",
    ) -> None:
        super().__init__(enabled=enabled)

        self._path = Path(path)
        self._name = str(name)
        self._description = str(description)

        self._records: list[dict[str, Any]] = []

    # ==========================================================================
    # Properties
    # ==========================================================================

    @property
    def path(self) -> Path:
        """Return the configured Parquet path."""
        return self._path

    @property
    def name(self) -> str:
        """Return the storage name."""
        return self._name

    @property
    def description(self) -> str:
        """Return the storage description."""
        return self._description

    # ==========================================================================
    # Dependency handling
    # ==========================================================================

    @staticmethod
    def _require_engine() -> tuple[Any, Any]:
        """
        Lazily import pandas and pyarrow.

        Returns
        -------
        tuple
            ``(pandas, pyarrow)``.

        Raises
        ------
        RuntimeError
            If pandas or pyarrow is unavailable.
        """
        try:
            import pandas as pd
            import pyarrow
        except ImportError as exc:
            raise RuntimeError(
                "pandas and pyarrow are required for ParquetStorage; "
                "install them with 'pip install pandas pyarrow'"
            ) from exc

        return pd, pyarrow

    # ==========================================================================
    # Validation
    # ==========================================================================

    @staticmethod
    def _validate_key(key: str) -> str:
        """Validate and normalize a storage key."""
        if not isinstance(key, str):
            raise TypeError("key must be a string")

        if not key:
            raise ValueError("key must not be empty")

        return key

    @staticmethod
    def _validate_record(
        record: Mapping[str, Any],
    ) -> dict[str, Any]:
        """
        Validate and deep-copy one storage record.
        """
        if not isinstance(record, Mapping):
            raise TypeError("each record must be a mapping")

        if "key" not in record:
            raise ValueError("record must contain 'key'")

        if "value" not in record:
            raise ValueError("record must contain 'value'")

        key = ParquetStorage._validate_key(record["key"])

        return {
            "key": key,
            "value": copy.deepcopy(record["value"]),
        }

    @classmethod
    def _validate_records(
        cls,
        records: Iterable[Mapping[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Validate a collection of records and enforce unique keys.

        The returned records are independent deep copies.
        """
        validated: list[dict[str, Any]] = []
        seen: set[str] = set()

        for record in records:
            normalized = cls._validate_record(record)
            key = normalized["key"]

            if key in seen:
                raise ValueError(
                    f"duplicate key in records: {key!r}"
                )

            seen.add(key)
            validated.append(normalized)

        return validated

    # ==========================================================================
    # Internal record helpers
    # ==========================================================================

    def _find_record_index(
        self,
        key: str,
    ) -> Optional[int]:
        """Return the record index for ``key`` or ``None``."""
        for index, record in enumerate(self._records):
            if record["key"] == key:
                return index

        return None

    def _upsert_record(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Insert or replace a record.

        Existing keys retain their original ordering.
        """
        index = self._find_record_index(key)

        record = {
            "key": key,
            "value": copy.deepcopy(value),
        }

        if index is None:
            self._records.append(record)
        else:
            self._records[index] = record

    def _ensure_parent_directory(self) -> None:
        """Create the configured parent directory when necessary."""
        parent = self._path.parent

        if parent != Path("."):
            parent.mkdir(parents=True, exist_ok=True)

    # ==========================================================================
    # Primitive API
    # ==========================================================================

    def put(
        self,
        key: str,
        value: Any,
    ) -> Any:
        """
        Store ``value`` under ``key``.

        Returns the original value supplied by the caller.
        """
        self._ensure_active()

        key = self._validate_key(key)
        self._upsert_record(key, value)

        return value

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """Return the stored value associated with ``key``."""
        self._ensure_active()

        key = self._validate_key(key)

        index = self._find_record_index(key)

        if index is None:
            return default

        return copy.deepcopy(
            self._records[index]["value"]
        )

    def delete(
        self,
        key: str,
    ) -> "ParquetStorage":
        """
        Delete ``key``.

        Returns ``self`` whether or not the key exists.
        """
        self._ensure_active()

        key = self._validate_key(key)

        index = self._find_record_index(key)

        if index is not None:
            del self._records[index]

        return self

    def exists(
        self,
        key: str,
    ) -> bool:
        """Return whether ``key`` exists."""
        self._ensure_active()

        key = self._validate_key(key)

        return self._find_record_index(key) is not None

    def clear(self) -> "ParquetStorage":
        """
        Remove all records.

        Returns ``self``.
        """
        self._ensure_active()

        self._records.clear()

        return self

    # ==========================================================================
    # Collection API
    # ==========================================================================

    def count(self) -> int:
        """Return the number of stored records."""
        self._ensure_active()

        return len(self._records)

    def keys(self) -> list[str]:
        """Return stored keys as a new list."""
        self._ensure_active()

        return [
            record["key"]
            for record in self._records
        ]

    def values(self) -> list[Any]:
        """Return stored values as a new deep-copied list."""
        self._ensure_active()

        return [
            copy.deepcopy(record["value"])
            for record in self._records
        ]

    def items(self) -> list[tuple[str, Any]]:
        """Return stored key/value pairs as a new list."""
        self._ensure_active()

        return [
            (
                record["key"],
                copy.deepcopy(record["value"]),
            )
            for record in self._records
        ]

    # ==========================================================================
    # Statistics
    # ==========================================================================

    def statistics(self) -> dict[str, Any]:
        """
        Return Parquet-specific storage statistics.
        """
        self._ensure_active()

        count = len(self._records)

        return {
            "backend": "parquet",
            "name": self.name,
            "description": self.description,
            "path": str(self._path),
            "enabled": self.enabled,
            "closed": self.closed,
            "active": self.active,
            "count": count,
            "records": count,
            "format": "columnar",
            "engine": "pandas + pyarrow",
        }

    # ==========================================================================
    # Persistence
    # ==========================================================================

    def dataframe(self) -> Any:
        """
        Return the current records as a pandas DataFrame.

        pandas/pyarrow are loaded lazily.
        """
        pd, _ = self._require_engine()

        self._ensure_active()

        return pd.DataFrame(
            [
                {
                    "key": record["key"],
                    "value": copy.deepcopy(record["value"]),
                }
                for record in self._records
            ],
            columns=["key", "value"],
        )

    def write(self) -> "ParquetStorage":
        """
        Write current records to the configured Parquet file.

        Existing file contents are replaced.

        Returns
        -------
        ParquetStorage
            ``self``.
        """
        self._ensure_active()

        self._ensure_parent_directory()

        dataframe = self.dataframe()

        try:
            dataframe.to_parquet(
                self._path,
                index=False,
            )
        except Exception as exc:
            raise ParquetStorageError(
                f"failed to write Parquet storage: {self._path}"
            ) from exc

        return self

    def load(self) -> "ParquetStorage":
        """
        Load records from the configured Parquet file.

        The configured file must exist.

        A missing file is considered a persistence error and raises
        ``ParquetStorageError``.

        Returns
        -------
        ParquetStorage
            ``self``.
        """
        self._ensure_active()

        if not self._path.exists():
            raise ParquetStorageError(
                f"Parquet storage file does not exist: {self._path}"
            )

        if not self._path.is_file():
            raise ParquetStorageError(
                f"Parquet storage path is not a file: {self._path}"
            )

        pd, _ = self._require_engine()

        try:
            dataframe = pd.read_parquet(self._path)
        except Exception as exc:
            raise ParquetStorageError(
                f"failed to load Parquet storage: {self._path}"
            ) from exc

        if "key" not in dataframe.columns:
            raise ParquetStorageError(
                f"invalid Parquet storage schema: missing 'key': "
                f"{self._path}"
            )

        if "value" not in dataframe.columns:
            raise ParquetStorageError(
                f"invalid Parquet storage schema: missing 'value': "
                f"{self._path}"
            )

        try:
            rows = dataframe[
                ["key", "value"]
            ].to_dict(orient="records")

            records = self._validate_records(rows)
        except (TypeError, ValueError) as exc:
            raise ParquetStorageError(
                f"invalid records in Parquet storage: {self._path}"
            ) from exc

        self._records = records

        return self

    def append(self) -> "ParquetStorage":
        """
        Append current records to an existing Parquet file.

        Ordering contract
        -----------------
        Current in-memory records are written first, followed by records
        already persisted in the file.

        Duplicate keys are resolved in favor of current records. This
        preserves the unique-key invariant while ensuring current records
        remain at the front of the resulting sequence.

        If the file does not exist, this behaves like ``write()``.

        Returns
        -------
        ParquetStorage
            ``self``.
        """
        self._ensure_active()

        if not self._path.exists():
            return self.write()

        if not self._path.is_file():
            raise ParquetStorageError(
                f"Parquet storage path is not a file: {self._path}"
            )

        pd, _ = self._require_engine()

        try:
            existing = pd.read_parquet(self._path)
        except Exception as exc:
            raise ParquetStorageError(
                f"failed to read existing Parquet storage: "
                f"{self._path}"
            ) from exc

        if "key" not in existing.columns:
            raise ParquetStorageError(
                f"invalid existing Parquet schema: missing 'key': "
                f"{self._path}"
            )

        if "value" not in existing.columns:
            raise ParquetStorageError(
                f"invalid existing Parquet schema: missing 'value': "
                f"{self._path}"
            )

        try:
            existing_rows = existing[
                ["key", "value"]
            ].to_dict(orient="records")

            existing_records = self._validate_records(
                existing_rows
            )
        except (TypeError, ValueError) as exc:
            raise ParquetStorageError(
                f"invalid records in existing Parquet storage: "
                f"{self._path}"
            ) from exc

        current_records = copy.deepcopy(self._records)

        # Current records win over persisted records with the same key.
        current_keys = {
            record["key"]
            for record in current_records
        }

        merged_records = (
            current_records
            + [
                record
                for record in existing_records
                if record["key"] not in current_keys
            ]
        )

        merged = pd.DataFrame(
            merged_records,
            columns=["key", "value"],
        )

        try:
            merged.to_parquet(
                self._path,
                index=False,
            )
        except Exception as exc:
            raise ParquetStorageError(
                f"failed to append Parquet storage: {self._path}"
            ) from exc

        return self

    # ==========================================================================
    # Snapshot / Restore
    # ==========================================================================

    def snapshot(self) -> list[dict[str, Any]]:
        """
        Return an independent snapshot of all records.
        """
        self._ensure_active()

        return copy.deepcopy(self._records)

    def restore(
        self,
        snapshot: Iterable[Mapping[str, Any]],
    ) -> "ParquetStorage":
        """
        Replace the current record set from ``snapshot``.

        The supplied iterable and all contained values are deep-copied.

        Duplicate keys are rejected because storage keys are unique.
        """
        self._ensure_active()

        if isinstance(snapshot, (str, bytes, Mapping)):
            raise TypeError(
                "snapshot must be an iterable of record mappings"
            )

        records = self._validate_records(snapshot)

        self._records = records

        return self

    # ==========================================================================
    # Python protocols
    # ==========================================================================

    def __len__(self) -> int:
        """Return the number of records."""
        return len(self._records)

    def __iter__(self):
        """
        Iterate over independent raw records.

        Iteration yields records rather than keys.
        """
        self._ensure_active()

        for record in self._records:
            yield copy.deepcopy(record)

    def __contains__(
        self,
        key: object,
    ) -> bool:
        """Support ``key in storage``."""
        if not isinstance(key, str):
            return False

        if not self.active:
            return False

        return self._find_record_index(key) is not None

    def __repr__(self) -> str:
        """Return a concise storage representation."""
        return (
            "ParquetStorage("
            f"path={self.path}, "
            f"count={len(self._records)}, "
            f"enabled={self.enabled}, "
            f"closed={self.closed}, "
            f"active={self.active}"
            ")"
        )


# ==============================================================================
# Public API
# ==============================================================================

__all__ = [
    "ParquetStorage",
    "ParquetStorageError",
]