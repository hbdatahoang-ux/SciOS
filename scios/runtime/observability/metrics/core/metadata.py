# ==============================================================================
# Part 1. Imports
# ==============================================================================

from __future__ import annotations

import json

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Mapping, MutableMapping, TypeAlias


# ==============================================================================
# Part 2. Constants
# ==============================================================================

METADATA_VERSION: str = "1.0.0"

DEFAULT_ANNOTATIONS: dict[str, Any] = {}

DEFAULT_TAGS: set[str] = set()


# ==============================================================================
# Part 3. Exceptions
# ==============================================================================


class MetadataError(Exception):
    """Base exception for MetricMetadata."""


class MetadataValidationError(MetadataError):
    """Raised when metadata validation fails."""


# ==============================================================================
# Part 4. Type Aliases
# ==============================================================================

AnnotationMap: TypeAlias = dict[str, Any]

TagSet: TypeAlias = set[str]


# ==============================================================================
# Part 5. Dataclass
# ==============================================================================

@dataclass(slots=True)
class MetricMetadata:
    """
    Runtime metadata attached to a metric.

    Metadata contains optional user-defined information that does not
    affect the metric value itself.

    Examples
    --------
    >>> meta = MetricMetadata()
    >>> meta.annotations
    {}
    >>> meta.tags
    set()
    """

    annotations: AnnotationMap = field(default_factory=dict)

    tags: TagSet = field(default_factory=set)

    version: str = field(default=METADATA_VERSION, init=False)

# ==============================================================================
# Part 6. Constructor Validation
# ==============================================================================

    def __post_init__(self) -> None:
        """
        Validate constructor arguments.
        """

        if not isinstance(self.annotations, Mapping):
            raise TypeError(
                "annotations must be a mapping."
            )

        if isinstance(self.tags, (str, bytes)):
            raise TypeError(
                "tags must be a collection."
            )

        if not isinstance(self.tags, (set, list, tuple)):
            raise TypeError(
                "tags must be a collection."
            )

        # Normalize annotations
        self.annotations = {
            str(key): value
            for key, value in self.annotations.items()
        }

        # Normalize tags
        self.tags = {
            str(tag).strip()
            for tag in self.tags
            if str(tag).strip()
        }

# ==============================================================================
# Part 7. Properties
# ==============================================================================

    @property
    def annotation_count(self) -> int:
        return len(self.annotations)

    @property
    def tag_count(self) -> int:
        return len(self.tags)

    @property
    def is_empty(self) -> bool:
        return not self.annotations and not self.tags


# ==============================================================================
# Part 8. Annotation Management
# ==============================================================================

    def add_annotation(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Add or update an annotation.
        """

        key = str(key).strip()

        if not key:
            raise MetadataValidationError(
                "annotation key cannot be empty."
            )

        self.annotations[key] = value

    def remove_annotation(
        self,
        key: str,
    ) -> None:
        """
        Remove an annotation if present.
        """

        self.annotations.pop(str(key), None)

    def has_annotation(
        self,
        key: str,
    ) -> bool:
        return str(key) in self.annotations

    def get_annotation(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        return self.annotations.get(str(key), default)

    def clear_annotations(self) -> None:
        self.annotations.clear()


# ==============================================================================
# Part 9. Tag Management
# ==============================================================================

    def add_tag(
        self,
        tag: str,
    ) -> None:
        """
        Add a tag.
        """

        tag = str(tag).strip()

        if not tag:
            raise MetadataValidationError(
                "tag cannot be empty."
            )

        self.tags.add(tag)

    def remove_tag(
        self,
        tag: str,
    ) -> None:
        self.tags.discard(str(tag))

    def has_tag(
        self,
        tag: str,
    ) -> bool:
        return str(tag) in self.tags

    def clear_tags(self) -> None:
        self.tags.clear()


# ==============================================================================
# Part 10. Validation
# ==============================================================================

    def validate(self) -> None:
        """
        Validate metadata.
        """

        for key in self.annotations:

            if not isinstance(key, str):
                raise MetadataValidationError(
                    "annotation keys must be strings."
                )

            if not key.strip():
                raise MetadataValidationError(
                    "annotation key cannot be empty."
                )

        for tag in self.tags:

            if not isinstance(tag, str):
                raise MetadataValidationError(
                    "tags must be strings."
                )

            if not tag.strip():
                raise MetadataValidationError(
                    "tag cannot be empty."
                )


# ==============================================================================
# Part 11. Serialization
# ==============================================================================

    def to_dict(self) -> dict[str, Any]:
        """
        Convert metadata into a dictionary.
        """

        return {
            "annotations": dict(self.annotations),
            "tags": sorted(self.tags),
            "version": self.version,
        }

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "MetricMetadata":
        """
        Create metadata from dictionary.
        """

        return cls(
            annotations=data.get("annotations", {}),
            tags=set(data.get("tags", [])),
        )

    def to_json(
        self,
        *,
        indent: int = 2,
    ) -> str:
        """
        Serialize metadata into JSON.
        """

        return json.dumps(
            self.to_dict(),
            indent=indent,
            sort_keys=True,
        )

    @classmethod
    def from_json(
        cls,
        text: str,
    ) -> "MetricMetadata":
        """
        Deserialize metadata from JSON.
        """

        return cls.from_dict(json.loads(text))

# ==============================================================================
# Part 12
# Copy
# ==============================================================================

    def copy(self) -> "MetricMetadata":
        """
        Return a shallow copy.
        """
        return self.__class__(
            annotations=dict(self.annotations),
            tags=set(self.tags),
        )

    def clone(self) -> "MetricMetadata":
        """
        Return a deep clone.
        """
        return deepcopy(self)


# ==============================================================================
# Part 13
# Equality
# ==============================================================================

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MetricMetadata):
            return NotImplemented

        return (
            self.annotations == other.annotations
            and self.tags == other.tags
        )

    def __hash__(self) -> int:
        return hash(
            (
                frozenset(self.annotations.items()),
                frozenset(self.tags),
            )
        )


# ==============================================================================
# Part 14
# Representation
# ==============================================================================

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"annotations={self.annotations!r}, "
            f"tags={sorted(self.tags)!r}"
            f")"
        )

    def __str__(self) -> str:
        return (
            f"MetricMetadata("
            f"{len(self.annotations)} annotations, "
            f"{len(self.tags)} tags)"
        )


# ==============================================================================
# Part 15
# Public API
# ==============================================================================

__all__ = [
    "MetricMetadata",
    "MetadataError",
    "AnnotationMap",
    "TagSet",
]

__version__ = "1.0.0"            