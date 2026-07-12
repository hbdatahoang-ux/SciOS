"""
SciOS Episodic Memory
=====================

Concrete episodic memory implementation.

Responsibilities
----------------
- Store experiences
- Retrieve experiences
- Forget experiences
- Clear memory
- Enumerate records
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from .base import AbstractMemory
from .record import MemoryRecord


class EpisodicMemory(AbstractMemory):
    """
    Stores episodic memories (events and experiences).
    """

    def __init__(
        self,
        name: str = "EpisodicMemory",
    ) -> None:

        super().__init__(name)

        self._records: list[MemoryRecord] = []

    # ======================================================
    # Store
    # ======================================================

    def store(
        self,
        record: dict[str, Any],
    ) -> None:
        """
        Store a new memory.
        """

        if "timestamp" not in record:
            record["timestamp"] = (
                datetime.utcnow().isoformat()
            )

        self._records.append(
            MemoryRecord(**record)
        )

    # ======================================================
    # Retrieve
    # ======================================================

    def retrieve(
        self,
        query: dict[str, Any],
    ) -> MemoryRecord | None:
        """
        Retrieve the first matching memory.
        """

        keyword = query.get("keyword")
        timestamp = query.get("timestamp")

        for rec in self._records:

            if (
                keyword is not None
                and keyword.lower()
                in rec.content.lower()
            ):
                return rec

            metadata = getattr(rec, "metadata", {})

            if (
                timestamp is not None
                and metadata.get("timestamp")
                == timestamp
            ):
                return rec

        return None

    # ======================================================
    # Forget
    # ======================================================

    def forget(
        self,
        record_id: str,
    ) -> None:
        """
        Remove a memory by ID.
        """

        self._records = [
            rec
            for rec in self._records
            if rec.id != record_id
        ]

    # ======================================================
    # Utilities
    # ======================================================

    def clear(self) -> None:
        """
        Remove every memory.
        """

        self._records.clear()

    def all(self) -> list[MemoryRecord]:
        """
        Return every stored memory.
        """

        return list(self._records)

    def size(self) -> int:
        """
        Number of stored memories.
        """

        return len(self._records)

    # ======================================================
    # Python Protocols
    # ======================================================

    def __len__(self) -> int:
        return len(self._records)

    def __iter__(self):
        return iter(self._records)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(records={len(self._records)})"
        )