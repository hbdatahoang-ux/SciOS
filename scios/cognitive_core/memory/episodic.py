"""
SciOS Episodic Memory
=====================

Concrete implementation of episodic memory.

Responsibilities
----------------
- Store experiences
- Retrieve experiences
- Forget experiences
- Clear memory
- Enumerate records
- Provide compatibility with AbstractMemory
"""

from __future__ import annotations

from datetime import datetime, UTC
from typing import Any, Iterator

from .base import AbstractMemory
from .record import MemoryRecord


class EpisodicMemory(AbstractMemory):
    """
    Episodic memory.

    Stores time-dependent experiences and events.

    This implementation satisfies the complete AbstractMemory API
    while remaining lightweight and backward compatible with
    previous SciOS releases.
    """

    def __init__(
        self,
        name: str = "EpisodicMemory",
    ) -> None:
        super().__init__(name)

        self._records: list[MemoryRecord] = []

    # ==========================================================
    # Store
    # ==========================================================

    def store(
        self,
        record: dict[str, Any],
    ) -> None:
        """
        Store a memory record.
        """

        payload = dict(record)

        payload.setdefault(
            "timestamp",
            datetime.now(UTC).isoformat(),
        )

        self._records.append(
            MemoryRecord(**payload)
        )

    # ==========================================================
    # Retrieve
    # ==========================================================

    def retrieve(
        self,
        query: dict[str, Any],
    ) -> MemoryRecord | None:
        """
        Retrieve the first matching memory.

        Supported query keys
        --------------------
        keyword
        id
        timestamp
        """

        keyword = query.get("keyword")
        record_id = query.get("id")
        timestamp = query.get("timestamp")

        for record in self._records:

            if (
                record_id is not None
                and getattr(record, "id", None) == record_id
            ):
                return record

            if keyword is not None:
                content = str(
                    getattr(record, "content", "")
                )

                if keyword.lower() in content.lower():
                    return record

            if timestamp is not None:

                record_timestamp = getattr(
                    record,
                    "timestamp",
                    None,
                )

                if record_timestamp is None:

                    metadata = getattr(
                        record,
                        "metadata",
                        {},
                    )

                    if isinstance(metadata, dict):
                        record_timestamp = metadata.get(
                            "timestamp"
                        )

                if record_timestamp == timestamp:
                    return record

        return None

    # ==========================================================
    # Forget
    # ==========================================================

    def forget(
        self,
        record_id: str,
    ) -> None:
        """
        Remove a memory by identifier.
        """

        self._records = [
            record
            for record in self._records
            if getattr(record, "id", None) != record_id
        ]

    # ==========================================================
    # Utilities
    # ==========================================================

    def clear(self) -> None:
        """
        Remove every stored memory.
        """

        self._records.clear()

    def reset(self) -> None:
        """
        Alias of clear().
        """

        self.clear()

    def all(self) -> list[MemoryRecord]:
        """
        Return all memories.
        """

        return list(self._records)

    def all_records(self) -> list[MemoryRecord]:
        """
        Required by AbstractMemory.

        Returns every stored memory.
        """

        return self.all()

    # ======================================================
    # Compatibility API
    # ======================================================

    def all_records(self) -> list[MemoryRecord]:
        """
        Return every stored memory.

        Compatibility alias required by AbstractMemory.
        """

        return list(self._records)

    def all_episodes(self) -> list[MemoryRecord]:
        """
        Return all episodic memories.

        Backward-compatible alias used by the reasoning subsystem.
        """

        return self.all_records()

    def snapshot(self) -> list[MemoryRecord]:
        """
        Return an immutable snapshot.
        """

        return self.all_records()

    @property
    def records(self) -> list[MemoryRecord]:
        """
        Read-only access to stored records.
        """

        return self.all_records()
    
    def snapshot(self) -> list[MemoryRecord]:
        """
        Immutable snapshot.
        """

        return self.all()

    def size(self) -> int:
        """
        Number of stored memories.
        """

        return len(self._records)

    def empty(self) -> bool:
        """
        Whether memory contains no records.
        """

        return not self._records

    def status(self) -> dict[str, Any]:
        """
        Runtime status.
        """

        return {
            "component": "EpisodicMemory",
            "records": len(self._records),
        }

    # ==========================================================
    # Python Protocols
    # ==========================================================

    def __len__(self) -> int:
        return len(self._records)

    def __iter__(self) -> Iterator[MemoryRecord]:
        return iter(self._records)

    def __contains__(
        self,
        item: MemoryRecord,
    ) -> bool:
        return item in self._records

    def __getitem__(
        self,
        index: int,
    ) -> MemoryRecord:
        return self._records[index]

    def __bool__(self) -> bool:
        return bool(self._records)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"records={len(self._records)})"
        )

    __str__ = __repr__