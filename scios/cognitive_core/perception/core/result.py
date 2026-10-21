"""Standard perception result for the SciOS Cognitive Core Perception subsystem."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .errors import PerceptionValidationError
from .types import (
    Embedding,
    Entities,
    Entity,
    Features,
    Metadata,
    Modality,
    PerceptionStatus,
    Relations,
    Relation,
)


@dataclass
class PerceptionResult:
    """Standardized result produced by a perception operation."""

    status: PerceptionStatus
    modality: Modality
    content: Any = None
    features: Features = field(default_factory=dict)
    entities: Entities = field(default_factory=list)
    relations: Relations = field(default_factory=list)
    embedding: Embedding | None = None
    confidence: float = 0.0
    metadata: Metadata = field(default_factory=dict)

    def validate(self) -> None:
        """Validate the structural invariants of the result."""

        if not isinstance(self.status, PerceptionStatus):
            raise PerceptionValidationError(
                "status must be a PerceptionStatus"
            )

        if not isinstance(self.modality, Modality):
            raise PerceptionValidationError(
                "modality must be a Modality"
            )

        if not 0.0 <= self.confidence <= 1.0:
            raise PerceptionValidationError(
                "confidence must be between 0.0 and 1.0"
            )

        if not isinstance(self.features, dict):
            raise PerceptionValidationError(
                "features must be a dictionary"
            )

        if not isinstance(self.entities, list):
            raise PerceptionValidationError(
                "entities must be a list"
            )

        if not isinstance(self.relations, list):
            raise PerceptionValidationError(
                "relations must be a list"
            )

        if not isinstance(self.metadata, dict):
            raise PerceptionValidationError(
                "metadata must be a dictionary"
            )

    @property
    def successful(self) -> bool:
        """Return whether perception completed successfully."""

        return self.status is PerceptionStatus.SUCCESS

    @property
    def partial(self) -> bool:
        """Return whether perception completed partially."""

        return self.status is PerceptionStatus.PARTIAL

    @property
    def failed(self) -> bool:
        """Return whether perception failed."""

        return self.status is PerceptionStatus.FAILED

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable structural representation."""

        return {
            "status": self.status.value,
            "modality": self.modality.value,
            "content": self.content,
            "features": self.features,
            "entities": self.entities,
            "relations": self.relations,
            "embedding": self.embedding,
            "confidence": self.confidence,
            "metadata": self.metadata,
        }


__all__ = ["PerceptionResult"]
