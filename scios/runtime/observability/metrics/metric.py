"""
SciOS Runtime Metric Core
=========================

Base metric abstraction.

Responsibilities
-----------------
- Define common metric metadata.
- Manage metric identity.
- Attach labels.
- Provide serialization.
- Provide lifecycle state.

Python 3.11+
"""

from __future__ import annotations


from copy import deepcopy
from dataclasses import dataclass, field
from time import time
from typing import Any


from .labels import MetricLabels


__all__ = [
    "Metric",
]



# ==========================================================
# Helpers
# ==========================================================


def timestamp() -> float:
    """
    Current unix timestamp.
    """

    return time()



# ==========================================================
# Metric
# ==========================================================


@dataclass(slots=True)
class Metric:
    """
    Base runtime metric object.

    Example
    -------

    metric = Metric(
        name="runtime_tasks",
        description="Executed tasks",
    )

    """


    # ======================================================
    # Identity
    # ======================================================


    name: str


    description: str = ""


    namespace: str = "scios"


    unit: str = ""



    # ======================================================
    # Labels
    # ======================================================


    labels: MetricLabels = field(
        default_factory=MetricLabels
    )



    # ======================================================
    # Metadata
    # ======================================================


    metadata: dict[str, Any] = field(
        default_factory=dict
    )



    # ======================================================
    # State
    # ======================================================


    enabled: bool = True



    created_at: float = field(
        default_factory=timestamp
    )


    updated_at: float = field(
        default_factory=timestamp
    )



    # ======================================================
    # Initialization
    # ======================================================


    def __post_init__(self):

        if not isinstance(
            self.labels,
            MetricLabels,
        ):

            self.labels = MetricLabels(
                **self.labels
            )


        self.metadata = dict(
            self.metadata
        )


        self.validate()



    # ======================================================
    # Validation
    # ======================================================


    def validate(
        self,
    ) -> None:
        """
        Validate metric definition.
        """

        if not self.name:
            raise ValueError(
                "metric name cannot be empty"
            )

        if " " in self.name:
            raise ValueError(
                "metric name cannot contain spaces"
            )

        if not isinstance(self.unit, str):
            raise TypeError(
                "metric unit must be a string"
            )


    # ======================================================
    # Identity
    # ======================================================


    @property
    def full_name(
        self,
    ) -> str:
        """
        Full metric name.

        Example:

        scios.runtime.tasks
        """

        if self.namespace:

            return (
                f"{self.namespace}."
                f"{self.name}"
            )


        return self.name



    # ======================================================
    # Labels
    # ======================================================


    def set_label(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Add metric label.
        """

        self.labels.set(
            key,
            value,
        )


        self.touch()



    def remove_label(
        self,
        key: str,
    ) -> None:

        self.labels.remove(
            key
        )


        self.touch()



    # ======================================================
    # Metadata
    # ======================================================


    def set_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Add metadata.
        """

        self.metadata[key] = value

        self.touch()



    def get_metadata(
        self,
        key: str,
        default: Any = None,
    ) -> Any:

        return self.metadata.get(
            key,
            default,
        )



    # ======================================================
    # Lifecycle
    # ======================================================


    def enable(
        self,
    ) -> None:
        """
        Enable metric collection.
        """

        self.enabled = True

        self.touch()



    def disable(
        self,
    ) -> None:
        """
        Disable metric collection.
        """

        self.enabled = False

        self.touch()



    def touch(
        self,
    ) -> None:
        """
        Update modification time.
        """

        self.updated_at = timestamp()



    # ======================================================
    # Snapshot
    # ======================================================


    def snapshot(
        self,
    ) -> dict[str, Any]:
        """
        Serialize metric definition.
        """

        return {
            "name": self.name,
            "full_name": self.full_name,
            "description": self.description,
            "namespace": self.namespace,
            "unit": self.unit,
            "labels": self.labels.to_dict(),
            "metadata": deepcopy(self.metadata),
            "enabled": self.enabled,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


    # ======================================================
    # Restore
    # ======================================================

    def restore(
        self,
        snapshot: dict[str, Any],
    ) -> None:
        """
        Restore common metric state from a snapshot.

        Subclasses are responsible for restoring their own
        metric-specific state such as numeric values,
        buckets, samples, or timing state.
        """

        if not isinstance(snapshot, dict):
            raise TypeError(
                "snapshot must be a dictionary"
            )

        if "name" in snapshot:
            self.name = snapshot["name"]

        if "description" in snapshot:
            self.description = snapshot["description"]

        if "namespace" in snapshot:
            self.namespace = snapshot["namespace"]

        if "unit" in snapshot:
            self.unit = snapshot["unit"]

        if "labels" in snapshot:
            labels = snapshot["labels"]

            if isinstance(labels, MetricLabels):
                self.labels = labels
            else:
                self.labels = MetricLabels(
                    **dict(labels)
                )

        if "metadata" in snapshot:
            self.metadata = deepcopy(
                snapshot["metadata"]
            )

        if "enabled" in snapshot:
            self.enabled = bool(
                snapshot["enabled"]
            )

        if "created_at" in snapshot:
            self.created_at = float(
                snapshot["created_at"]
            )

        if "updated_at" in snapshot:
            self.updated_at = float(
                snapshot["updated_at"]
            )

        self.validate()

    # ======================================================
    # Copy
    # ======================================================


    def copy(
        self,
    ) -> "Metric":
        """
        Clone metric.
        """

        return deepcopy(
            self
        )



    # ======================================================
    # Protocols
    # ======================================================


    def __hash__(
        self,
    ) -> int:

        return hash(
            self.full_name
        )



    def __repr__(
        self,
    ) -> str:

        return (
            "Metric("
            f"name={self.name!r}, "
            f"namespace={self.namespace!r}, "
            f"enabled={self.enabled}"
            ")"
        )
        