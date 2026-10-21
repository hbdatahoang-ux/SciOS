"""
SciOS Vector Metadata
=====================

Metadata abstraction for the SciOS VectorStore.

Responsibilities
----------------
- Immutable metadata representation
- Rich document descriptors
- Filtering support
- Serialization
- Versioning
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
import uuid

__all__ = [
    "Metadata",
]


# ==========================================================
# Metadata
# ==========================================================

@dataclass(slots=True)
class Metadata:
    """
    Metadata associated with a stored vector.

    Metadata is intentionally backend-independent and
    can be serialized into JSON-compatible structures.
    """

    # ======================================================
    # Identity
    # ======================================================

    id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    # ======================================================
    # Human-readable information
    # ======================================================

    title: str | None = None

    source: str | None = None

    author: str | None = None

    language: str = "en"

    # ======================================================
    # Temporal information
    # ======================================================

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: datetime | None = None

    # ======================================================
    # Categorization
    # ======================================================

    tags: list[str] = field(default_factory=list)

    category: str | None = None

    # ======================================================
    # Retrieval
    # ======================================================

    score: float | None = None

    namespace: str = "default"

    # ======================================================
    # User-defined attributes
    # ======================================================

    attributes: dict[str, Any] = field(default_factory=dict)

    # ======================================================
    # Methods
    # ======================================================

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve a custom attribute.
        """

        return self.attributes.get(
            key,
            default,
        )

    def set(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Set a custom attribute.
        """

        self.attributes[key] = value

    def update(
        self,
        values: dict[str, Any],
    ) -> None:
        """
        Update custom attributes.
        """

        self.attributes.update(values)

    # ======================================================
    # Serialization
    # ======================================================

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize metadata.
        """

        return {

            "id": self.id,

            "title": self.title,

            "source": self.source,

            "author": self.author,

            "language": self.language,

            "created_at": self.created_at.isoformat(),

            "updated_at": (
                self.updated_at.isoformat()
                if self.updated_at
                else None
            ),

            "tags": self.tags,

            "category": self.category,

            "score": self.score,

            "namespace": self.namespace,

            "attributes": self.attributes,
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "Metadata":
        """
        Construct Metadata from a dictionary.
        """

        metadata = cls()

        metadata.id = data.get("id", metadata.id)

        metadata.title = data.get("title")

        metadata.source = data.get("source")

        metadata.author = data.get("author")

        metadata.language = data.get(
            "language",
            "en",
        )

        if data.get("created_at"):
            metadata.created_at = datetime.fromisoformat(
                data["created_at"]
            )

        if data.get("updated_at"):
            metadata.updated_at = datetime.fromisoformat(
                data["updated_at"]
            )

        metadata.tags = list(
            data.get("tags", [])
        )

        metadata.category = data.get(
            "category"
        )

        metadata.score = data.get(
            "score"
        )

        metadata.namespace = data.get(
            "namespace",
            "default",
        )

        metadata.attributes = dict(
            data.get("attributes", {})
        )

        return metadata

    # ======================================================
    # Representation
    # ======================================================

    def __repr__(self) -> str:

        return (

            "Metadata("

            f"id='{self.id}', "

            f"title={self.title!r}, "

            f"namespace='{self.namespace}')"

        )
