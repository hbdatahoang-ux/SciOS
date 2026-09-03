"""Relation model for the Knowledge subsystem."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .entity import Entity
from .types import RelationType


@dataclass(slots=True)
class Relation:
    """A directed semantic relation between two entities."""

    id: str
    source: Entity
    target: Entity
    relation_type: RelationType = RelationType.ASSOCIATED_WITH
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValueError("Relation id must be a non-empty string.")

        if not isinstance(self.source, Entity):
            raise TypeError("source must be an Entity.")

        if not isinstance(self.target, Entity):
            raise TypeError("target must be an Entity.")

        if not isinstance(self.relation_type, RelationType):
            raise TypeError("relation_type must be a RelationType.")

        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary.")

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Relation):
            return NotImplemented
        return self.id == other.id


__all__ = ["Relation"]
