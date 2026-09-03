from __future__ import annotations

from typing import Iterable

from scios.cognitive_core.memory.core import (
    MemoryKind,
    MemoryRecord,
    MemoryStore,
)
from scios.cognitive_core.memory.retrieval.base import RetrievalStrategy


class MemoryManager:
    """Coordinate multiple memory stores and retrieval strategies."""

    def __init__(
        self,
        *,
        working: MemoryStore,
        episodic: MemoryStore,
        semantic: MemoryStore,
    ) -> None:
        if not isinstance(working, MemoryStore):
            raise TypeError("working must be a MemoryStore")

        if not isinstance(episodic, MemoryStore):
            raise TypeError("episodic must be a MemoryStore")

        if not isinstance(semantic, MemoryStore):
            raise TypeError("semantic must be a MemoryStore")

        self.working = working
        self.episodic = episodic
        self.semantic = semantic

    def _store_for(self, kind: MemoryKind) -> MemoryStore:
        if not isinstance(kind, MemoryKind):
            raise TypeError("kind must be a MemoryKind")

        if kind is MemoryKind.WORKING:
            return self.working

        if kind is MemoryKind.EPISODIC:
            return self.episodic

        if kind is MemoryKind.SEMANTIC:
            return self.semantic

        raise ValueError(f"unsupported memory kind: {kind}")

    def store(
        self,
        record: MemoryRecord,
        kind: MemoryKind,
    ) -> MemoryRecord:
        if not isinstance(record, MemoryRecord):
            raise TypeError("record must be a MemoryRecord")

        return self._store_for(kind).store(record)

    def get(
        self,
        record_id: str,
        kind: MemoryKind,
    ) -> MemoryRecord | None:
        if not isinstance(record_id, str):
            raise TypeError("record_id must be a string")

        return self._store_for(kind).get(record_id)

    def delete(
        self,
        record_id: str,
        kind: MemoryKind,
    ) -> bool:
        if not isinstance(record_id, str):
            raise TypeError("record_id must be a string")

        return self._store_for(kind).delete(record_id)

    def clear(self, kind: MemoryKind) -> None:
        self._store_for(kind).clear()

    def count(self, kind: MemoryKind) -> int:
        return self._store_for(kind).count()

    def all(self, kind: MemoryKind) -> tuple[MemoryRecord, ...]:
        return self._store_for(kind).all()

    def retrieve(
        self,
        strategy: RetrievalStrategy,
        query: object,
        kind: MemoryKind,
    ) -> tuple[MemoryRecord, ...]:
        if not isinstance(strategy, RetrievalStrategy):
            raise TypeError("strategy must be a RetrievalStrategy")

        records: Iterable[MemoryRecord] = self._store_for(kind).all()

        return strategy.retrieve(records, query)
