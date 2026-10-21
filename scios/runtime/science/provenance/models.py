# ==============================================================================
# SciOS Runtime Science
# Provenance Models
# ==============================================================================

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Mapping


# ==============================================================================
# Exceptions
# ==============================================================================


class ProvenanceError(RuntimeError):
    """Base exception for provenance model failures."""


class InvalidProvenanceError(ProvenanceError, ValueError):
    """Raised when a provenance record is invalid."""


# ==============================================================================
# Provenance Record
# ==============================================================================


@dataclass(frozen=True, slots=True)
class ProvenanceRecord:
    """
    Immutable scientific provenance record.

    A record identifies one entity in the scientific knowledge lineage.

    Examples:
        H001 -> hypothesis
        E001 -> experiment
        O001 -> observation
        R001 -> revision
    """

    id: str
    entity_type: str
    created_at: datetime
    parent_ids: tuple[str, ...]
    metadata: Mapping[str, Any]

    def __init__(
        self,
        id: str,
        entity_type: str,
        created_at: datetime | None = None,
        parent_ids: tuple[str, ...] | list[str] | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        # ------------------------------------------------------------------
        # ID
        # ------------------------------------------------------------------

        if not isinstance(id, str) or not id.strip():
            raise InvalidProvenanceError(
                "id must be a non-empty string"
            )

        # ------------------------------------------------------------------
        # Entity type
        # ------------------------------------------------------------------

        if not isinstance(entity_type, str) or not entity_type.strip():
            raise InvalidProvenanceError(
                "entity_type must be a non-empty string"
            )

        # ------------------------------------------------------------------
        # Timestamp
        # ------------------------------------------------------------------

        if created_at is None:
            created_at = datetime.now(timezone.utc)

        if not isinstance(created_at, datetime):
            raise InvalidProvenanceError(
                "created_at must be a datetime"
            )

        if created_at.tzinfo is None:
            raise InvalidProvenanceError(
                "created_at must be timezone-aware"
            )

        # ------------------------------------------------------------------
        # Parent IDs
        # ------------------------------------------------------------------

        if parent_ids is None:
            parent_ids = ()

        try:
            normalized_parent_ids = tuple(parent_ids)
        except TypeError as exc:
            raise InvalidProvenanceError(
                "parent_ids must be an iterable of strings"
            ) from exc

        if any(
            not isinstance(parent_id, str) or not parent_id.strip()
            for parent_id in normalized_parent_ids
        ):
            raise InvalidProvenanceError(
                "parent_ids must contain non-empty strings"
            )

        if len(normalized_parent_ids) != len(set(normalized_parent_ids)):
            raise InvalidProvenanceError(
                "parent_ids must not contain duplicates"
            )

        # ------------------------------------------------------------------
        # Metadata
        # ------------------------------------------------------------------

        if metadata is None:
            metadata = {}

        if not isinstance(metadata, Mapping):
            raise InvalidProvenanceError(
                "metadata must be a mapping"
            )

        # ------------------------------------------------------------------
        # Immutable storage
        # ------------------------------------------------------------------

        object.__setattr__(self, "id", id)
        object.__setattr__(self, "entity_type", entity_type)
        object.__setattr__(self, "created_at", created_at)
        object.__setattr__(
            self,
            "parent_ids",
            normalized_parent_ids,
        )
        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(dict(metadata)),
        )

    # ==========================================================================
    # Query API
    # ==========================================================================

    def has_parent(self, parent_id: str) -> bool:
        """
        Return True if this record directly references parent_id.
        """

        return parent_id in self.parent_ids

    # ==========================================================================
    # Functional update API
    # ==========================================================================

    def with_parent(self, parent_id: str) -> ProvenanceRecord:
        """
        Return a new record with parent_id added.

        If the parent already exists, return this record unchanged.
        """

        if not isinstance(parent_id, str) or not parent_id.strip():
            raise InvalidProvenanceError(
                "parent_id must be a non-empty string"
            )

        if parent_id in self.parent_ids:
            return self

        return ProvenanceRecord(
            id=self.id,
            entity_type=self.entity_type,
            created_at=self.created_at,
            parent_ids=self.parent_ids + (parent_id,),
            metadata=self.metadata,
        )