from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

from .errors import MemoryValidationError
from .types import (
    MemoryContent,
    MemoryId,
    MemoryKind,
    MemoryMetadata,
    MemoryTimestamp,
)


@dataclass(frozen=True, slots=True)
class MemoryRecord:
    """Immutable unit of stored memory."""

    content: MemoryContent
    id: MemoryId = field(default_factory=lambda: str(uuid4()))
    metadata: MemoryMetadata = field(default_factory=dict)
    created_at: MemoryTimestamp = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: MemoryTimestamp | None = None
    kind: MemoryKind | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.content, str) or not self.content.strip():
            raise MemoryValidationError(
                "content must be a non-empty string"
            )

        if not isinstance(self.id, str) or not self.id.strip():
            raise MemoryValidationError(
                "id must be a non-empty string"
            )

        if not isinstance(self.metadata, dict):
            raise MemoryValidationError(
                "metadata must be a dictionary"
            )

        if not isinstance(self.created_at, datetime):
            raise MemoryValidationError(
                "created_at must be a datetime"
            )

        if self.updated_at is not None and not isinstance(
            self.updated_at, datetime
        ):
            raise MemoryValidationError(
                "updated_at must be a datetime or None"
            )

        if self.kind is not None and not isinstance(self.kind, MemoryKind):
            raise MemoryValidationError(
                "kind must be a MemoryKind or None"
            )

        object.__setattr__(self, "metadata", dict(self.metadata))

        if self.updated_at is None:
            object.__setattr__(self, "updated_at", self.created_at)
