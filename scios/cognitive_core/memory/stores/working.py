from __future__ import annotations

from scios.cognitive_core.memory.core import (
    MemoryCapacityError,
    MemoryRecord,
    MemoryStore,
)


class WorkingMemory(MemoryStore):
    """Bounded in-memory store for short-lived working memory."""

    def __init__(
        self,
        name: str = "WorkingMemory",
        capacity: int = 10,
    ) -> None:
        if isinstance(capacity, bool) or not isinstance(capacity, int):
            raise ValueError("capacity must be an integer")

        if capacity <= 0:
            raise ValueError("capacity must be greater than zero")

        super().__init__(name=name)

        self.capacity = capacity
        self._records: dict[str, MemoryRecord] = {}

    def store(self, record: MemoryRecord) -> MemoryRecord:
        if not isinstance(record, MemoryRecord):
            raise TypeError("record must be a MemoryRecord")

        if record.id not in self._records and len(self._records) >= self.capacity:
            raise MemoryCapacityError(
                f"working memory capacity exceeded: {self.capacity}"
            )

        self._records[record.id] = record
        return record

    def get(self, record_id: str) -> MemoryRecord | None:
        if not isinstance(record_id, str):
            raise TypeError("record_id must be a string")

        return self._records.get(record_id)

    def delete(self, record_id: str) -> bool:
        if not isinstance(record_id, str):
            raise TypeError("record_id must be a string")

        return self._records.pop(record_id, None) is not None

    def clear(self) -> None:
        self._records.clear()

    def count(self) -> int:
        return len(self._records)

    def all(self) -> tuple[MemoryRecord, ...]:
        return tuple(self._records.values())
