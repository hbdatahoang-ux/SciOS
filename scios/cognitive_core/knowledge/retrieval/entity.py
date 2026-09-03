"""Entity retrieval strategy for the Knowledge subsystem."""

from __future__ import annotations

from typing import Iterable

from scios.cognitive_core.knowledge.core.entity import Entity
from .base import RetrievalStrategy


class EntityRetrieval(RetrievalStrategy[Entity, str]):
    """Retrieve entities by ID or case-insensitive label."""

    def __init__(self, name: str = "entity") -> None:
        super().__init__(name)

    def retrieve(
        self,
        items: Iterable[Entity],
        query: str,
    ) -> list[Entity]:
        if not isinstance(query, str):
            raise TypeError("query must be a string.")

        normalized = query.casefold()

        return [
            entity
            for entity in items
            if entity.id.casefold() == normalized
            or normalized in entity.label.casefold()
        ]


__all__ = ["EntityRetrieval"]
