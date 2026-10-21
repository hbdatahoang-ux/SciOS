"""Entity store for the Knowledge subsystem."""

from __future__ import annotations

from scios.cognitive_core.knowledge.core.entity import Entity
from scios.cognitive_core.knowledge.core.errors import EntityError


class EntityStore:
    """In-memory store for semantic entities."""

    def __init__(self) -> None:
        self._entities: dict[str, Entity] = {}

    def add(self, entity: Entity) -> Entity:
        """Add an entity to the store."""
        if not isinstance(entity, Entity):
            raise TypeError("entity must be an Entity.")

        if entity.id in self._entities:
            raise EntityError(f"Entity already exists: {entity.id}")

        self._entities[entity.id] = entity
        return entity

    def get(self, entity_id: str) -> Entity | None:
        """Return an entity by ID."""
        return self._entities.get(entity_id)

    def remove(self, entity_id: str) -> Entity | None:
        """Remove and return an entity by ID."""
        return self._entities.pop(entity_id, None)

    def all(self) -> list[Entity]:
        """Return all stored entities as a snapshot."""
        return list(self._entities.values())

    def count(self) -> int:
        """Return the number of stored entities."""
        return len(self._entities)

    def clear(self) -> None:
        """Remove all entities."""
        self._entities.clear()


__all__ = ["EntityStore"]
