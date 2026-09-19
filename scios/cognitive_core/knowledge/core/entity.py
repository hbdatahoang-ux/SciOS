"""Entity model for the Knowledge subsystem."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .types import EntityType


@dataclass(slots=True)
class Entity:
    """A semantic entity represented in the Knowledge subsystem."""

    id: str
    label: str
    entity_type: EntityType = EntityType.CONCEPT
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValueError("Entity id must be a non-empty string.")

        if not isinstance(self.label, str) or not self.label.strip():
            raise ValueError("Entity label must be a non-empty string.")

        if not isinstance(self.entity_type, EntityType):
            raise TypeError("entity_type must be an EntityType.")

        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary.")

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return NotImplemented
        return self.id == other.id


__all__ = ["Entity"]
