from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable

from scios.cognitive_core.memory.core import MemoryQuery, MemoryRecord


class RetrievalStrategy(ABC):
    """Abstract contract for retrieving memory records."""

    def __init__(self, *, name: str) -> None:
        if not isinstance(name, str) or not name.strip():
            raise ValueError("name must be a non-empty string")

        self.name = name

    @abstractmethod
    def retrieve(
        self,
        records: Iterable[MemoryRecord],
        query: MemoryQuery,
    ) -> tuple[MemoryRecord, ...]:
        """Return records matching the retrieval query."""
        raise NotImplementedError
