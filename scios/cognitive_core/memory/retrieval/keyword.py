from __future__ import annotations

from typing import Iterable

from scios.cognitive_core.memory.core import MemoryRecord
from scios.cognitive_core.memory.retrieval.base import RetrievalStrategy


class KeywordRetrieval(RetrievalStrategy):
    """Retrieve memory records whose content contains the query."""

    def __init__(self, name: str = "KeywordRetrieval") -> None:
        super().__init__(name=name)

    def retrieve(
        self,
        records: Iterable[MemoryRecord],
        query: str,
    ) -> tuple[MemoryRecord, ...]:
        if not isinstance(query, str):
            raise TypeError("query must be a string")

        if not query.strip():
            return ()

        normalized_query = query.casefold()

        return tuple(
            record
            for record in records
            if normalized_query in record.content.casefold()
        )
