"""Relation store for the Knowledge subsystem."""

from __future__ import annotations

from scios.cognitive_core.knowledge.core.errors import RelationError
from scios.cognitive_core.knowledge.core.relation import Relation


class RelationStore:
    """In-memory store for directed semantic relations."""

    def __init__(self) -> None:
        self._relations: dict[str, Relation] = {}

    def add(self, relation: Relation) -> Relation:
        """Add a relation to the store."""
        if not isinstance(relation, Relation):
            raise TypeError("relation must be a Relation.")

        if relation.id in self._relations:
            raise RelationError(
                f"Relation already exists: {relation.id}"
            )

        self._relations[relation.id] = relation
        return relation

    def get(self, relation_id: str) -> Relation | None:
        """Return a relation by ID."""
        return self._relations.get(relation_id)

    def remove(self, relation_id: str) -> Relation | None:
        """Remove and return a relation by ID."""
        return self._relations.pop(relation_id, None)

    def all(self) -> list[Relation]:
        """Return all stored relations as a snapshot."""
        return list(self._relations.values())

    def count(self) -> int:
        """Return the number of stored relations."""
        return len(self._relations)

    def clear(self) -> None:
        """Remove all relations."""
        self._relations.clear()


__all__ = ["RelationStore"]
