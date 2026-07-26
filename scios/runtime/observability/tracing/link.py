"""
SciOS Observability - Trace Link
================================

Span links connect traces or spans that have a causal relationship
without introducing a strict parent-child hierarchy.

Inspired by OpenTelemetry Span Links.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .attributes import Attributes

__all__ = [
    "Link",
]


@dataclass(slots=True)
class Link:
    """
    Represents a relationship to another span.

    Parameters
    ----------
    trace_id:
        Linked trace identifier.

    span_id:
        Linked span identifier.

    attributes:
        Optional metadata.

    description:
        Human-readable description.
    """

    trace_id: str

    span_id: str

    attributes: Attributes = field(
        default_factory=Attributes
    )

    description: str | None = None

    # ======================================================

    def set_attribute(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Set an attribute.
        """

        self.attributes.set(
            key,
            value,
        )

    # ------------------------------------------------------

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

    # ------------------------------------------------------

    def remove_attribute(
        self,
        key: str,
    ) -> None:
        """
        Remove an attribute.
        """

        self.attributes.pop(
            key,
            None,
        )

    # ------------------------------------------------------

    def clear_attributes(
        self,
    ) -> None:
        """
        Remove all attributes.
        """

        self.attributes.clear()

    # ------------------------------------------------------

    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Serialize link.
        """

        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "description": self.description,
            "attributes": self.attributes.to_dict(),
        }

    # ------------------------------------------------------

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "Link":
        """
        Deserialize link.
        """

        attrs = Attributes()

        attrs.update(
            data.get(
                "attributes",
                {},
            )
        )

        return cls(
            trace_id=data["trace_id"],
            span_id=data["span_id"],
            description=data.get(
                "description",
            ),
            attributes=attrs,
        )

    # ------------------------------------------------------

    def copy(
        self,
    ) -> "Link":
        """
        Deep copy.
        """

        attrs = Attributes()

        attrs.update(
            self.attributes.to_dict()
        )

        return Link(
            trace_id=self.trace_id,
            span_id=self.span_id,
            description=self.description,
            attributes=attrs,
        )

    # ------------------------------------------------------

    def __hash__(
        self,
    ) -> int:

        return hash(
            (
                self.trace_id,
                self.span_id,
            )
        )

    # ------------------------------------------------------

    def __repr__(
        self,
    ) -> str:

        return (
            f"{self.__class__.__name__}("
            f"trace_id='{self.trace_id}', "
            f"span_id='{self.span_id}')"
        )