from __future__ import annotations

from scios.cognitive_core.memory.core import MemoryRecord, MemoryStore


class EpisodicMemory(MemoryStore):
    """In-memory store for event-oriented episodic memories."""

    def __init__(self, name: str = "EpisodicMemory") -> None:
        super().__init__(name=name)
        self._records: dict[str, MemoryRecord] = {}

    def store(self, record: MemoryRecord) -> MemoryRecord:
        if not isinstance(record, MemoryRecord):
            raise TypeError("record must be a MemoryRecord")

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
