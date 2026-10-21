"""
SciOS Runtime Observability
===========================

Trace link model.

A Link represents a causal relationship between two spans without
introducing a strict parent-child hierarchy.

Inspired by OpenTelemetry Span Links.

Python 3.11+
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, TypeAlias

import copy

from .attributes import Attributes

__all__: list[str]

# ==============================================================================
# Part 2. Constants & Type Aliases
# ==============================================================================

DEFAULT_TRACE_ID = ""

DEFAULT_SPAN_ID = ""

DEFAULT_LINK_DESCRIPTION: str | None = None

LINK_VERSION = "1.0.0"

LINK_API_VERSION = "1"

DEFAULT_LINK_ATTRIBUTES = Attributes

LinkAttributes: TypeAlias = Attributes

LinkJSON: TypeAlias = dict[str, Any]

# ==============================================================================
# Part 3. Exceptions & Enums
# ==============================================================================


class LinkError(Exception):
    """
    Base exception for Link operations.
    """


class LinkValidationError(LinkError):
    """
    Raised when a Link is invalid.
    """


class LinkSerializationError(LinkError):
    """
    Raised when serialization/deserialization fails.
    """

# ==============================================================================
# Part 4. Dataclass
# ==============================================================================


@dataclass(slots=True)
class Link:
    """
    Immutable trace link.

    Parameters
    ----------
    trace_id:
        Linked trace identifier.

    span_id:
        Linked span identifier.

    attributes:
        Optional link attributes.

    description:
        Human-readable description.
    """

    trace_id: str = DEFAULT_TRACE_ID

    span_id: str = DEFAULT_SPAN_ID

    attributes: LinkAttributes = field(
        default_factory=Attributes
    )

    description: str | None = DEFAULT_LINK_DESCRIPTION
# ==============================================================================
# Part 5. Constructor & Properties
# ==============================================================================

    def __post_init__(self) -> None:
        """
        Validate link.
        """
        self.trace_id = str(self.trace_id).strip()
        self.span_id = str(self.span_id).strip()

        if not self.trace_id:
            raise LinkValidationError(
                "trace_id cannot be empty."
            )

        if not self.span_id:
            raise LinkValidationError(
                "span_id cannot be empty."
            )

        if not isinstance(
            self.attributes,
            Attributes,
        ):
            raise TypeError(
                "attributes must be an Attributes instance."
            )

        if (
            self.description
            is not None
        ):
            self.description = str(
                self.description
            )

    @property
    def identifier(self) -> tuple[str, str]:
        """
        Return unique identifier.
        """
        return (
            self.trace_id,
            self.span_id,
        )

    @property
    def has_attributes(self) -> bool:
        """
        Return True if attributes exist.
        """
        return len(self.attributes) > 0

    @property
    def attribute_count(self) -> int:
        """
        Return attribute count.
        """
        return len(self.attributes)

    @property
    def is_valid(self) -> bool:
        """
        Return validation state.
        """
        return self.validate()

# ==============================================================================
# Part 6. Core API
# ==============================================================================

    def set_trace_id(
        self,
        trace_id: str,
    ) -> "Link":
        """
        Update trace identifier.
        """
        trace_id = str(trace_id).strip()

        if not trace_id:
            raise LinkValidationError(
                "trace_id cannot be empty."
            )

        self.trace_id = trace_id
        return self

    def set_span_id(
        self,
        span_id: str,
    ) -> "Link":
        """
        Update span identifier.
        """
        span_id = str(span_id).strip()

        if not span_id:
            raise LinkValidationError(
                "span_id cannot be empty."
            )

        self.span_id = span_id
        return self

    def set_description(
        self,
        description: str | None,
    ) -> "Link":
        """
        Update description.
        """
        self.description = (
            None
            if description is None
            else str(description)
        )

        return self

    def clear(self) -> "Link":
        """
        Remove all attributes.
        """
        self.attributes.clear()
        return self

    def validate(self) -> bool:
        """
        Validate link integrity.
        """
        return (
            bool(self.trace_id)
            and
            bool(self.span_id)
            and
            isinstance(
                self.attributes,
                Attributes,
            )
        )

# ==============================================================================
# Part 7. Attributes
# ==============================================================================

    def set_attribute(
        self,
        key: str,
        value: Any,
    ) -> "Link":
        """
        Set an attribute.
        """
        self.attributes.set(
            str(key),
            value,
        )
        return self

    def get_attribute(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Get an attribute.
        """
        return self.attributes.get(
            key,
            default,
        )

    def remove_attribute(
        self,
        key: str,
    ) -> "Link":
        """
        Remove an attribute.
        """
        if key in self.attributes:
            del self.attributes[key]
        return self

    def clear_attributes(
        self,
    ) -> "Link":
        """
        Remove all attributes.
        """
        self.attributes.clear()
        return self

    def update_attributes(
        self,
        values: dict[str, Any],
    ) -> "Link":
        """
        Update attributes.
        """
        self.attributes.update(values)
        return self

# ==============================================================================
# Part 8. Serialization
# ==============================================================================

    def to_dict(
        self,
    ) -> LinkJSON:
        """
        Serialize link.
        """
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "description": self.description,
            "attributes": self.attributes.to_dict(),
        }

    def to_json(
        self,
    ) -> str:
        """
        Serialize to JSON.
        """
        try:
            import json

            return json.dumps(
                self.to_dict(),
                ensure_ascii=False,
            )

        except Exception as exc:
            raise LinkSerializationError(
                "Failed to serialize Link."
            ) from exc

    @classmethod
    def from_dict(
        cls,
        data: LinkJSON,
    ) -> "Link":
        """
        Restore from dictionary.
        """
        attrs = Attributes()
        attrs.update(
            data.get(
                "attributes",
                {},
            )
        )

        return cls(
            trace_id=data.get(
                "trace_id",
                DEFAULT_TRACE_ID,
            ),
            span_id=data.get(
                "span_id",
                DEFAULT_SPAN_ID,
            ),
            description=data.get(
                "description",
            ),
            attributes=attrs,
        )

    @classmethod
    def from_json(
        cls,
        value: str,
    ) -> "Link":
        """
        Restore from JSON.
        """
        try:
            import json

            return cls.from_dict(
                json.loads(value)
            )

        except Exception as exc:
            raise LinkSerializationError(
                "Failed to deserialize Link."
            ) from exc
# ==============================================================================
# Part 9. Snapshot / Clone
# ==============================================================================

    def snapshot(
        self,
    ) -> LinkJSON:
        """
        Create a serializable snapshot.
        """
        return self.to_dict()

    @classmethod
    def restore(
        cls,
        snapshot: LinkJSON,
    ) -> "Link":
        """
        Restore from snapshot.
        """
        return cls.from_dict(snapshot)

    def clone(
        self,
    ) -> "Link":
        """
        Create a deep clone.
        """
        return copy.deepcopy(self)

    def copy(
        self,
    ) -> "Link":
        """
        Create a shallow copy.
        """
        return copy.copy(self)

# ==============================================================================
# Part 10. Diagnostics
# ==============================================================================

    def diagnostics(
        self,
    ) -> dict[str, Any]:
        """
        Return detailed diagnostics.
        """
        return {
            "valid": self.validate(),
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "description": self.description,
            "attribute_count": len(self.attributes),
        }

    def summary(
        self,
    ) -> dict[str, Any]:
        """
        Return compact summary.
        """
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "attributes": len(self.attributes),
        }

# ==============================================================================
# Part 11. Python Protocols
# ==============================================================================

    def __repr__(
        self,
    ) -> str:
        return (
            f"{self.__class__.__name__}("
            f"trace_id={self.trace_id!r}, "
            f"span_id={self.span_id!r})"
        )

    def __str__(
        self,
    ) -> str:
        return (
            f"{self.trace_id}"
            f":{self.span_id}"
        )

    def __len__(
        self,
    ) -> int:
        return len(self.attributes)

    def __contains__(
        self,
        key: str,
    ) -> bool:
        return key in self.attributes

    def __getitem__(
        self,
        key: str,
    ) -> Any:
        return self.attributes[key]

    def __setitem__(
        self,
        key: str,
        value: Any,
    ) -> None:
        self.attributes.set(
            key,
            value,
        )

    def __eq__(
        self,
        other: object,
    ) -> bool:
        if not isinstance(
            other,
            Link,
        ):
            return NotImplemented

        return (
            self.trace_id == other.trace_id
            and
            self.span_id == other.span_id
            and
            self.description == other.description
            and
            self.attributes.to_dict()
            ==
            other.attributes.to_dict()
        )

    def __hash__(
        self,
    ) -> int:
        return hash(
            (
                self.trace_id,
                self.span_id,
                self.description,
                tuple(
                    sorted(
                        self.attributes.to_dict().items()
                    )
                ),
            )
        )

    def __copy__(
        self,
    ) -> "Link":
        return self.__class__.from_dict(
            self.to_dict()
        )

    def __deepcopy__(
        self,
        memo: dict[int, Any],
    ) -> "Link":
        result = self.__class__.from_dict(
            copy.deepcopy(
                self.to_dict(),
                memo,
            )
        )

        memo[id(self)] = result

        return result

# ==============================================================================
# Part 12. Public API
# ==============================================================================

__all__ = [

    # ------------------------------------------------------------------
    # Constants
    # ------------------------------------------------------------------

    "DEFAULT_TRACE_ID",
    "DEFAULT_SPAN_ID",
    "DEFAULT_LINK_DESCRIPTION",
    "DEFAULT_LINK_ATTRIBUTES",
    "LINK_VERSION",
    "LINK_API_VERSION",

    # ------------------------------------------------------------------
    # Type Aliases
    # ------------------------------------------------------------------

    "LinkAttributes",
    "LinkJSON",

    # ------------------------------------------------------------------
    # Exceptions
    # ------------------------------------------------------------------

    "LinkError",
    "LinkValidationError",
    "LinkSerializationError",

    # ------------------------------------------------------------------
    # Core Model
    # ------------------------------------------------------------------

    "Link",
]                