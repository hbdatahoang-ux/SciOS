"""Relation retrieval strategy for the Knowledge subsystem."""

from __future__ import annotations

from typing import Iterable

from scios.cognitive_core.knowledge.core.relation import Relation

from .base import RetrievalStrategy


class RelationRetrieval(RetrievalStrategy[Relation, str]):
    """Retrieve relations by source, target, or relation type."""

    def __init__(self, name: str = "relation") -> None:
        super().__init__(name)

    def retrieve(
        self,
        items: Iterable[Relation],
        query: str,
    ) -> list[Relation]:
        if not isinstance(query, str):
            raise TypeError("query must be a string.")

        normalized = query.strip().casefold()

        if not normalized:
            raise ValueError("query must be a non-empty string.")

        return [
            relation
            for relation in items
            if (
                normalized in relation.source.id.casefold()
                or normalized in relation.source.label.casefold()
                or normalized in relation.target.id.casefold()
                or normalized in relation.target.label.casefold()
                or normalized == relation.relation_type.value.casefold()
            )
        ]


__all__ = ["RelationRetrieval"]
