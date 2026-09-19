"""
Metric Snapshot
===============

Immutable-style runtime snapshot container.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from ..metric import Metric

__all__ = [
    "MetricSnapshot",
]

# ==============================================================================
# Type Aliases
# ==============================================================================

MetricStorage = dict[str, Metric]

MetricSnapshotState = dict[str, Any]

# ==============================================================================
# Constants
# ==============================================================================

DEFAULT_NAME = ""

DEFAULT_TIMESTAMP: datetime | None = None

DEFAULT_METRICS: MetricStorage = {}

DEFAULT_STATE: MetricSnapshotState = {}


# ==============================================================================
# Part 2. MetricSnapshot
# ==============================================================================


@dataclass(slots=True)
class MetricSnapshot:
    """
    Runtime metrics snapshot.
    """

    name: str = DEFAULT_NAME

    timestamp: str = field(
        default_factory=lambda:
            datetime.utcnow().isoformat()
    )

    metrics: MetricStorage = field(
        default_factory=dict,
    )

    state: MetricSnapshotState = field(
        default_factory=dict,
    )


    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------

    def __post_init__(self) -> None:

        self._normalize()

        self._validate()



    # ------------------------------------------------------------------
    # Normalization
    # ------------------------------------------------------------------

    def _normalize(self) -> None:

        if isinstance(
            self.name,
            str,
        ):
            self.name = (
                self.name
                .strip()
                .lower()
            )

        else:

            self.name = DEFAULT_NAME


        if not isinstance(
            self.metrics,
            dict,
        ):

            self.metrics = {}


        normalized = {}


        for key, value in self.metrics.items():

            if isinstance(
                value,
                Metric,
            ):

                normalized[
                    value.name
                ] = value


        self.metrics = normalized


        if not isinstance(
            self.state,
            dict,
        ):

            self.state = {}



    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate(self) -> None:


        if not isinstance(
            self.name,
            str,
        ):
            raise TypeError(
                "name must be string"
            )


        if not isinstance(
            self.timestamp,
            str,
        ):
            raise TypeError(
                "timestamp must be string"
            )


        if not isinstance(
            self.metrics,
            dict,
        ):
            raise TypeError(
                "metrics must be dict"
            )


        if not all(
            isinstance(v, Metric)
            for v in self.metrics.values()
        ):
            raise TypeError(
                "metrics must contain Metric"
            )


        if not isinstance(
            self.state,
            dict,
        ):
            raise TypeError(
                "state must be dict"
            )



# ==============================================================================
# Part 3. Properties
# ==============================================================================


    @property
    def size(self) -> int:

        return len(
            self.metrics
        )



# ==============================================================================
# Part 4. Operations
# ==============================================================================


    def add(
        self,
        metric: Metric,
    ) -> "MetricSnapshot":

        if isinstance(
            metric,
            Metric,
        ):

            self.metrics[
                metric.name
            ] = metric


        return self



    def remove(
        self,
        metric: Metric | str,
    ) -> "MetricSnapshot":

        name = (
            metric.name
            if isinstance(metric, Metric)
            else metric
        )


        self.metrics.pop(
            name,
            None,
        )


        return self



    def get(
        self,
        name: str,
    ) -> Metric | None:

        return self.metrics.get(
            name
        )



    def contains(
        self,
        metric: Metric | str,
    ) -> bool:

        name = (
            metric.name
            if isinstance(metric, Metric)
            else metric
        )

        return name in self.metrics



    def clear(self):

        self.metrics.clear()

        return self



    def normalize(self):

        self._normalize()

        return self



# ==============================================================================
# Part 5. Serialization
# ==============================================================================


    def to_dict(self) -> dict:


        return {

            "name":
                self.name,

            "timestamp":
                self.timestamp,

            "metrics":
                {
                    k:v.to_dict()
                    for k,v in self.metrics.items()
                },

            "state":
                dict(self.state),

        }



    @classmethod
    def from_dict(
        cls,
        data: dict,
    ) -> "MetricSnapshot":


        snapshot = cls(

            name=data.get(
                "name",
                "",
            ),

            timestamp=data.get(
                "timestamp",
                "",
            ),

        )


        snapshot.metrics = {

            k:
            Metric.from_dict(v)

            for k,v in data.get(
                "metrics",
                {},
            ).items()

        }


        snapshot.state = dict(
            data.get(
                "state",
                {},
            )
        )


        return snapshot



    def to_tuple(self) -> tuple:


        return (

            self.name,

            self.timestamp,

            tuple(
                self.metrics.items()
            ),

            dict(self.state),

        )



    @classmethod
    def from_tuple(
        cls,
        value: tuple,
    ) -> "MetricSnapshot":


        (
            name,
            timestamp,
            metrics,
            state,
        ) = value


        obj = cls(
            name=name,
            timestamp=timestamp,
        )


        obj.metrics = dict(
            metrics
        )

        obj.state = dict(
            state
        )


        return obj



    def snapshot(self):

        return self.to_dict()



    def restore(
        self,
        value: dict,
    ):

        restored = self.from_dict(
            value
        )


        self.name = restored.name
        self.timestamp = restored.timestamp
        self.metrics = restored.metrics
        self.state = restored.state


        return self

# ==============================================================================
# Part 6. Validation
# ==============================================================================

    @staticmethod
    def validate_name(
        value: object,
    ) -> bool:
        """
        Validate snapshot name.
        """
        return isinstance(value, str)


    @staticmethod
    def validate_metrics(
        value: object,
    ) -> bool:
        """
        Validate metric storage.
        """
        if not isinstance(value, dict):
            return False

        return all(
            isinstance(v, Metric)
            for v in value.values()
        )


    @classmethod
    def validate_snapshot(
        cls,
        value: object,
    ) -> bool:
        """
        Validate snapshot instance.
        """
        return (
            isinstance(value, cls)
            and cls.validate_name(value.name)
            and cls.validate_metrics(value.metrics)
            and isinstance(value.state, dict)
            and isinstance(value.timestamp, str)
        )


    def validate(self) -> bool:
        """
        Validate current snapshot.
        """
        return self.validate_snapshot(self)


# ==============================================================================
# Part 7. Utilities
# ==============================================================================

    def clone(self) -> "MetricSnapshot":
        """
        Deep clone.
        """
        return self.from_dict(
            self.to_dict()
        )


    def copy(self) -> "MetricSnapshot":
        """
        Alias of clone().
        """
        return self.clone()


    def merge(
        self,
        other: "MetricSnapshot",
    ) -> "MetricSnapshot":
        """
        Merge another snapshot.
        """
        if not isinstance(
            other,
            MetricSnapshot,
        ):
            return self

        self.metrics.update(
            other.metrics
        )

        self.state.update(
            other.state
        )

        return self


    def update(
        self,
        other: "MetricSnapshot",
    ) -> "MetricSnapshot":
        """
        Update from another snapshot.
        """
        return self.merge(other)


    def reset(self) -> "MetricSnapshot":
        """
        Reset snapshot.
        """
        self.metrics.clear()
        self.state.clear()
        self.name = DEFAULT_NAME

        return self


# ==============================================================================
# Part 8. Protocols
# ==============================================================================

    def __hash__(self) -> int:

        return hash(
            (
                self.name,
                tuple(
                    sorted(
                        self.metrics.items()
                    )
                )
                if isinstance(self.metrics, dict)
                else tuple(self.metrics),
            )
        )


    def __eq__(
        self,
        other: object,
    ) -> bool:

        if self is other:
            return True

        if not isinstance(
            other,
            MetricSnapshot,
        ):
            return NotImplemented

        return (
            self.name
            == other.name
            and self.metrics
            == other.metrics
            and self.state
            == other.state
        )


    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, "
            f"size={self.size})"
        )


    def __str__(self) -> str:

        return (
            f"{self.name}"
            f" ({self.size} metrics)"
        )


    def __bool__(self) -> bool:

        return self.size > 0


# ==============================================================================
# Part 9. Diagnostics
# ==============================================================================

    def summary(self) -> dict:
        """
        Snapshot summary.
        """
        return {
            "name": self.name,
            "timestamp": self.timestamp,
            "size": self.size,
        }


    def diagnostics(self) -> dict:
        """
        Snapshot diagnostics.
        """
        return {
            "valid": self.validate(),
            "summary": self.summary(),
            "state_size": len(self.state),
        }


    def snapshot_report(self) -> dict:
        """
        Complete snapshot report.
        """
        return {
            "summary": self.summary(),
            "diagnostics": self.diagnostics(),
            "metrics": list(
                self.metrics.keys()
            ),
        }


    def overall_status(self) -> str:
        """
        Overall snapshot status.
        """
        return (
            "healthy"
            if self.validate()
            else "invalid"
        )


# ==============================================================================
# Part 10. Public API
# ==============================================================================

__all__ = [
    "MetricSnapshot",
]        