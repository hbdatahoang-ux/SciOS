"""Fact retrieval strategy for the Knowledge subsystem."""

from __future__ import annotations

from typing import Iterable

from scios.cognitive_core.knowledge.core.fact import Fact

from .base import RetrievalStrategy


class FactRetrieval(RetrievalStrategy[Fact, str]):
    """Retrieve facts by source, target, relation type, or fact type."""

    def __init__(self, name: str = "fact") -> None:
        super().__init__(name)

    def retrieve(
        self,
        items: Iterable[Fact],
        query: str,
    ) -> list[Fact]:
        if not isinstance(query, str):
            raise TypeError("query must be a string.")

        normalized = query.strip().casefold()

        if not normalized:
            raise ValueError("query must be a non-empty string.")

        return [
            fact
            for fact in items
            if (
                normalized in fact.source.id.casefold()
                or normalized in fact.source.label.casefold()
                or normalized in fact.target.id.casefold()
                or normalized in fact.target.label.casefold()
                or normalized == fact.relation_type.value.casefold()
                or normalized == fact.fact_type.value.casefold()
            )
        ]


__all__ = ["FactRetrieval"]
