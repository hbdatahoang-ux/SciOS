"""Fact model for the Knowledge subsystem."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .relation import Relation
from .types import FactType


@dataclass(slots=True)
class Fact:
    """A semantic fact represented in the Knowledge subsystem."""

    id: str
    relation: Relation
    fact_type: FactType = FactType.ASSERTION
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValueError("Fact id must be a non-empty string.")

        if not isinstance(self.relation, Relation):
            raise TypeError("relation must be a Relation.")

        if not isinstance(self.fact_type, FactType):
            raise TypeError("fact_type must be a FactType.")

        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary.")

    @property
    def source(self):
        """Return the source entity of the underlying relation."""
        return self.relation.source

    @property
    def target(self):
        """Return the target entity of the underlying relation."""
        return self.relation.target

    @property
    def relation_type(self):
        """Return the type of the underlying relation."""
        return self.relation.relation_type

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Fact):
            return NotImplemented
        return self.id == other.id


__all__ = ["Fact"]
