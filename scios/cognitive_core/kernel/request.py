"""
SciOS Cognitive Request
=======================

Kernel level request model.

Python 3.11+
"""

from __future__ import annotations


from dataclasses import (
    dataclass,
    field,
)

from uuid import uuid4

from typing import Any


__all__ = [
    "CognitiveRequest",
]



@dataclass
class CognitiveRequest:
    """
    Request object flowing through SciOS cognitive pipeline.

    Features
    --------
    - Automatic request id generation
    - Metadata support
    - Serialization
    - Stable public API
    """


    # ------------------------------------------------------
    # Required payload
    # ------------------------------------------------------

    query: str



    # ------------------------------------------------------
    # Optional identity
    # ------------------------------------------------------

    request_id: str = field(
        default_factory=lambda: str(uuid4())
    )



    # ------------------------------------------------------
    # Context
    # ------------------------------------------------------

    metadata: dict[str, Any] = field(
        default_factory=dict
    )



    # ------------------------------------------------------
    # Helpers
    # ------------------------------------------------------

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "request_id": self.request_id,
            "query": self.query,
            "metadata": self.metadata,
        }



    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "CognitiveRequest":

        return cls(
            query=data.get(
                "query",
                "",
            ),
            request_id=data.get(
                "request_id",
                str(uuid4()),
            ),
            metadata=data.get(
                "metadata",
                {},
            ),
        )



    def __repr__(
        self,
    ) -> str:

        return (
            "CognitiveRequest("
            f"request_id={self.request_id!r}, "
            f"query={self.query!r}"
            ")"
        )