"""
SciOS Cognitive Request
=======================

Kernel-level request model.

Python 3.11+
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4


__all__ = [
    "CognitiveRequest",
]


@dataclass
class CognitiveRequest:
    """
    Request object flowing through the SciOS cognitive pipeline.

    Public contract
    ---------------
    - query
    - request_id
    - inputs
    - metadata
    - created_at
    - to_dict()
    - from_dict()
    """

    # ------------------------------------------------------
    # Core query
    # ------------------------------------------------------

    query: str = ""

    # ------------------------------------------------------
    # Identity
    # ------------------------------------------------------

    request_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    # ------------------------------------------------------
    # Input payload
    # ------------------------------------------------------

    inputs: dict[str, Any] = field(
        default_factory=dict
    )

    # ------------------------------------------------------
    # Metadata
    # ------------------------------------------------------

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    # ------------------------------------------------------
    # Creation timestamp
    # ------------------------------------------------------

    created_at: datetime = field(
        default_factory=datetime.now
    )

    # ======================================================
    # Serialization
    # ======================================================

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize the request into a dictionary.

        The returned dictionary contains the complete
        public request contract.
        """

        return {
            "request_id": self.request_id,
            "query": self.query,
            "inputs": dict(self.inputs),
            "metadata": dict(self.metadata),
            "created_at": self.created_at,
        }

    # ======================================================
    # Deserialization
    # ======================================================

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "CognitiveRequest":
        """
        Restore a CognitiveRequest from a dictionary.

        Missing optional fields fall back to their
        normal defaults.
        """

        created_at = data.get("created_at")

        if created_at is None:
            created_at = datetime.now()

        return cls(
            query=data.get(
                "query",
                "",
            ),
            request_id=data.get(
                "request_id",
                str(uuid4()),
            ),
            inputs=dict(
                data.get(
                    "inputs",
                    {},
                )
            ),
            metadata=dict(
                data.get(
                    "metadata",
                    {},
                )
            ),
            created_at=created_at,
        )

    # ======================================================
    # Representation
    # ======================================================

    def __repr__(self) -> str:
        return (
            "CognitiveRequest("
            f"request_id={self.request_id!r}, "
            f"query={self.query!r}"
            ")"
        )