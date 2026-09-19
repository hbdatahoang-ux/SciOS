"""
SciOS Runtime Metrics Snapshot
==============================

Immutable snapshot representation.

Responsibilities
----------------
- Capture metrics state.
- Provide serialization.
- Support exporters.
- Provide stable API.

Python 3.11+
"""

from __future__ import annotations


from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


__all__ = [
    "MetricSnapshot",
]



# ==========================================================
# Helpers
# ==========================================================


def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()



# ==========================================================
# Snapshot Model
# ==========================================================


@dataclass(slots=True)
class MetricSnapshot:
    """
    Immutable runtime metrics snapshot.

    Example:

        snapshot = MetricSnapshot(
            name="runtime",
            values={
                "tasks": 10
            }
        )

    """


    # ======================================================
    # Identity
    # ======================================================


    name: str = "runtime"



    timestamp: str = field(
        default_factory=utc_now
    )



    # ======================================================
    # Metrics payload
    # ======================================================


    values: dict[str, Any] = field(
        default_factory=dict
    )



    labels: dict[str, str] = field(
        default_factory=dict
    )



    metadata: dict[str, Any] = field(
        default_factory=dict
    )



    # ======================================================
    # Initialization
    # ======================================================


    def __post_init__(self):

        self.values = dict(
            self.values
        )

        self.labels = dict(
            self.labels
        )

        self.metadata = dict(
            self.metadata
        )



    # ======================================================
    # Access
    # ======================================================


    def get(
        self,
        key: str,
        default=None,
    ):
        """
        Get metric value.
        """

        return self.values.get(
            key,
            default,
        )



    def has(
        self,
        key: str,
    ) -> bool:

        return key in self.values



    # ======================================================
    # Conversion
    # ======================================================


    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Export snapshot.
        """

        return {

            "name":
                self.name,


            "timestamp":
                self.timestamp,


            "values":
                deepcopy(
                    self.values
                ),


            "labels":
                deepcopy(
                    self.labels
                ),


            "metadata":
                deepcopy(
                    self.metadata
                ),
        }



    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "MetricSnapshot":

        return cls(

            name=data.get(
                "name",
                "runtime",
            ),

            timestamp=data.get(
                "timestamp",
                utc_now(),
            ),

            values=dict(
                data.get(
                    "values",
                    {},
                )
            ),

            labels=dict(
                data.get(
                    "labels",
                    {},
                )
            ),

            metadata=dict(
                data.get(
                    "metadata",
                    {},
                )
            ),
        )



    # ======================================================
    # Copy
    # ======================================================


    def copy(self):

        return MetricSnapshot.from_dict(
            self.to_dict()
        )



    # ======================================================
    # Merge
    # ======================================================


    def merge(
        self,
        other: "MetricSnapshot",
    ) -> "MetricSnapshot":
        """
        Merge two snapshots.
        """

        values = deepcopy(
            self.values
        )

        values.update(
            other.values
        )


        labels = deepcopy(
            self.labels
        )

        labels.update(
            other.labels
        )


        metadata = deepcopy(
            self.metadata
        )

        metadata.update(
            other.metadata
        )


        return MetricSnapshot(

            name=self.name,

            values=values,

            labels=labels,

            metadata=metadata,
        )



    # ======================================================
    # Protocols
    # ======================================================


    def __contains__(
        self,
        key: str,
    ) -> bool:

        return key in self.values



    def __getitem__(
        self,
        key: str,
    ):

        return self.values[key]



    def __repr__(self):

        return (
            "MetricSnapshot("
            f"name={self.name!r}, "
            f"metrics={len(self.values)}"
            ")"
        )