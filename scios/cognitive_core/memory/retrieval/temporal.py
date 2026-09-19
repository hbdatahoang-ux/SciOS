from __future__ import annotations

from datetime import datetime
from typing import Iterable

from scios.cognitive_core.memory.core import MemoryRecord
from scios.cognitive_core.memory.retrieval.base import RetrievalStrategy


class TemporalRetrieval(RetrievalStrategy):
    """Retrieve memory records created at or after a given timestamp."""

    def __init__(self, name: str = "TemporalRetrieval") -> None:
        super().__init__(name=name)

    def retrieve(
        self,
        records: Iterable[MemoryRecord],
        query: datetime,
    ) -> tuple[MemoryRecord, ...]:
        if not isinstance(query, datetime):
            raise TypeError("query must be a datetime")

        return tuple(
            record
            for record in records
            if record.created_at >= query
        )
