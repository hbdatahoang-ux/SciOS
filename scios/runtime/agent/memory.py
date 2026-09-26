"""
SciOS Runtime Agent Memory
==========================

Agent memory abstraction layer.

Responsibilities
-----------------
- Store information
- Retrieve memories
- Search memories
- Maintain diagnostics
- Support snapshots

Python 3.11+
"""

from __future__ import annotations

import copy
from typing import Any


__all__ = [
    "Memory",
]


class Memory:
    """
    Deterministic in-memory store for SciOS Runtime Agent.

    The current implementation intentionally uses simple key/value
    storage. Vector retrieval, embeddings, and external persistence
    belong to higher-level integrations.
    """

    def __init__(self) -> None:
        self._storage: dict[str, Any] = {}
        self._writes = 0
        self._reads = 0
        self._anonymous_counter = 0
        self._next_memory_id = 0

    @property
    def size(self) -> int:
        return len(self._storage)


    @property
    def writes(self) -> int:
        return self._writes


    @property
    def reads(self) -> int:
        return self._reads
    # ======================================================
    # Write API
    # ======================================================

    def store(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Store memory by key.

        Contract:
            key must be a string.
        """

        if not isinstance(key, str):
            raise TypeError(
                "key must be a string"
            )

        self._storage[key] = value

        self._writes += 1

    def add(
        self,
        value: Any,
    ) -> str:
        """
        Add anonymous memory.

        Generated keys are never reused.
        """

        key = (
            f"memory-{self._next_memory_id}"
        )

        self._next_memory_id += 1

        self.store(
            key,
            value,
        )

        return key

    def update(
        self,
        values: dict[str, Any],
    ) -> None:
        """
        Batch update memory.
        """

        if not isinstance(values, dict):
            raise TypeError(
                "values must be a dict"
            )

        for key, value in values.items():

            self.store(
                key,
                value,
            )

    # ======================================================
    # Read API
    # ======================================================

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve memory.
        """

        if not isinstance(key, str):
            raise TypeError(
                "key must be a string"
            )

        self._reads += 1

        return self._storage.get(
            key,
            default,
        )

    def recall(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """Alias for get()."""

        return self.get(
            key,
            default,
        )

    def last(self) -> Any:
        """Return the most recently stored value."""

        self._reads += 1

        if not self._storage:
            return None

        key = next(
            reversed(self._storage)
        )

        return self._storage[key]

    def search(
        self,
        query: str,
    ) -> list[Any]:
        """
        Search memory values.
        """

        if not isinstance(query, str):
            raise TypeError(
                "query must be a string"
            )

        query = query.lower()

        return [
            value
            for key, value
            in self._storage.items()
            if (
                query in key.lower()
                or query in str(value).lower()
            )
        ]

    # ======================================================
    # Management
    # ======================================================

    def exists(
        self,
        key: str,
    ) -> bool:
        """Return whether a key exists."""

        return key in self._storage

    def remove(
        self,
        key: str,
    ) -> bool:
        """Remove a memory entry."""

        if key not in self._storage:
            return False

        del self._storage[key]

        return True

    def clear(
        self,
    ) -> None:

        self._storage.clear()

    # ======================================================
    # Collection API
    # ======================================================

    def keys(self) -> list[str]:
        """Return a snapshot of stored keys."""

        return list(
            self._storage.keys()
        )

    def values(self) -> list[Any]:
        """Return a deep-copied snapshot of stored values."""

        return copy.deepcopy(
            list(self._storage.values())
        )

    def items(self) -> list[tuple[str, Any]]:
        """Return a deep-copied snapshot of stored entries."""

        return copy.deepcopy(
            list(self._storage.items())
        )

    # ======================================================
    # Snapshot
    # ======================================================

    def snapshot(self) -> dict[str, Any]:
        """Return a deep-copy checkpoint of memory."""

        return copy.deepcopy(
            self._storage
        )

    def restore(
        self,
        snapshot: dict[str, Any],
    ) -> None:
        """
        Restore memory checkpoint.

        Diagnostics are preserved.
        """

        if not isinstance(snapshot, dict):
            raise TypeError(
                "snapshot must be a dict"
            )

        self._storage = copy.deepcopy(
            snapshot
        )

    # ======================================================
    # Serialization
    # ======================================================

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return copy.deepcopy(
            self._storage
        )

    # ======================================================
    # Diagnostics
    # ======================================================

    @property
    def writes(self) -> int:
        return self._writes

    @property
    def reads(self) -> int:
        return self._reads

    @property
    def size(self) -> int:
        return len(self._storage)

    def status(self) -> dict[str, Any]:
        """Return runtime diagnostics."""

        return {
            "size": len(self._storage),
            "keys": self.keys(),
            "writes": self._writes,
            "reads": self._reads,
        }

    # ======================================================
    # Protocol
    # ======================================================

    def __len__(self) -> int:
        return len(self._storage)

    def __contains__(
        self,
        key: str,
    ) -> bool:
        return self.exists(key)

    def __iter__(self):
        return iter(self._storage)

    def __getitem__(
        self,
        key: str,
    ) -> Any:
        return self._storage[key]

    def __setitem__(
        self,
        key: str,
        value: Any,
    ) -> None:
        self.store(
            key,
            value,
        )

    def __repr__(self) -> str:
        return (
            "Memory("
            f"size={len(self)}, "
            f"writes={self._writes}, "
            f"reads={self._reads}"
            ")"
        )