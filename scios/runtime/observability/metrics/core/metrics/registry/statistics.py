# ==============================================================================
# Part 1. Imports & Constants
# ==============================================================================

from __future__ import annotations

from copy import deepcopy

from dataclasses import (
    dataclass,
    field,
)

from typing import (
    Any,
    ClassVar,
    Final,
    TypeAlias,
)

import json


DEFAULT_NAME: Final[str] = ""

DEFAULT_COUNT: Final[int] = 0

DEFAULT_SUM: Final[float] = 0.0

DEFAULT_MINIMUM: Final[float | None] = None

DEFAULT_MAXIMUM: Final[float | None] = None

DEFAULT_AVERAGE: Final[float] = 0.0


StatisticsState: TypeAlias = dict[str, Any]


# ==============================================================================
# Part 2. MetricStatistics
# ==============================================================================

@dataclass(slots=True)
class MetricStatistics:
    """
    Metric statistics.
    """

    name: str = DEFAULT_NAME

    count: int = DEFAULT_COUNT

    sum: float = DEFAULT_SUM

    minimum: float | None = DEFAULT_MINIMUM

    maximum: float | None = DEFAULT_MAXIMUM

    state: StatisticsState = field(
        default_factory=dict,
    )

    _AVERAGE_KEY: ClassVar[str] = "average"

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

        self.count = max(
            0,
            int(self.count),
        )

        self.sum = float(
            self.sum,
        )

        if (
            self.minimum is not None
        ):
            self.minimum = float(
                self.minimum,
            )

        if (
            self.maximum is not None
        ):
            self.maximum = float(
                self.maximum,
            )

        if (
            self.minimum is not None
            and self.maximum is not None
            and self.minimum > self.maximum
        ):
            self.minimum, self.maximum = (
                self.maximum,
                self.minimum,
            )

        if not isinstance(
            self.state,
            dict,
        ):
            self.state = {}

        self.recompute_average()

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate(self) -> None:

        if not isinstance(
            self.name,
            str,
        ):
            raise TypeError(
                "name must be str."
            )

        if not isinstance(
            self.count,
            int,
        ):
            raise TypeError(
                "count must be int."
            )

        if not isinstance(
            self.sum,
            (
                int,
                float,
            ),
        ):
            raise TypeError(
                "sum must be numeric."
            )

        if (
            self.minimum is not None
            and not isinstance(
                self.minimum,
                (
                    int,
                    float,
                ),
            )
        ):
            raise TypeError(
                "minimum must be numeric."
            )

        if (
            self.maximum is not None
            and not isinstance(
                self.maximum,
                (
                    int,
                    float,
                ),
            )
        ):
            raise TypeError(
                "maximum must be numeric."
            )

        if not isinstance(
            self.state,
            dict,
        ):
            raise TypeError(
                "state must be dict."
            )


# ==============================================================================
# Part 3. Properties
# ==============================================================================

    @property
    def average(self) -> float:

        if self.count == 0:
            return DEFAULT_AVERAGE

        return self.sum / self.count


    @property
    def mean(self) -> float:

        return self.average


    @property
    def is_empty(self) -> bool:

        return self.count == 0


    @property
    def has_values(self) -> bool:

        return self.count > 0


    @property
    def size(self) -> int:

        return self.count


    @property
    def range(self) -> float:

        if (
            self.minimum is None
            or self.maximum is None
        ):
            return 0.0

        return self.maximum - self.minimum


    @property
    def statistics(self) -> dict[str, Any]:

        return self.to_dict()


    @property
    def values(self) -> tuple[Any, ...]:

        return (
            self.count,
            self.sum,
            self.minimum,
            self.maximum,
        )


# ==============================================================================
# Part 4. Statistics Operations
# ==============================================================================

    def merge(
        self,
        other: "MetricStatistics",
    ) -> "MetricStatistics":

        if not isinstance(
            other,
            MetricStatistics,
        ):
            return self

        self.count += other.count
        self.sum += other.sum

        if other.minimum is not None:
            if (
                self.minimum is None
                or other.minimum < self.minimum
            ):
                self.minimum = other.minimum

        if other.maximum is not None:
            if (
                self.maximum is None
                or other.maximum > self.maximum
            ):
                self.maximum = other.maximum

        self.state.update(
            other.state,
        )

        self.recompute_average()

        return self


    def update(
        self,
        other: "MetricStatistics",
    ) -> None:

        self.merge(
            other,
        )


    def reset(self) -> None:

        self.count = 0
        self.sum = 0.0
        self.minimum = 0.0
        self.maximum = 0.0
        self.state.clear()


    def snapshot(self) -> dict[str, Any]:

        return self.to_dict()


    def restore(
        self,
        snapshot: dict[str, Any],
    ) -> None:

        restored = self.from_dict(
            snapshot,
        )

        self.name = restored.name
        self.count = restored.count
        self.sum = restored.sum
        self.minimum = restored.minimum
        self.maximum = restored.maximum
        self.state = restored.state


    def increment(
        self,
        value: float,
    ) -> None:

        value = float(value)

        self.count += 1
        self.sum += value

        self.set_minimum(
            value,
        )

        self.set_maximum(
            value,
        )

        self.recompute_average()


    def decrement(
        self,
        value: float,
    ) -> None:

        self.sum -= float(value)

        if self.count:
            self.count -= 1

        self.recompute_average()


    def set_minimum(
        self,
        value: float,
    ) -> None:

        if (
            self.minimum is None
            or value < self.minimum
        ):
            self.minimum = float(
                value,
            )


    def set_maximum(
        self,
        value: float,
    ) -> None:

        if (
            self.maximum is None
            or value > self.maximum
        ):
            self.maximum = float(
                value,
            )


    def recompute_average(self) -> None:

        if self.state:

            self.state[self._AVERAGE_KEY] = self.average


    def normalize(self) -> None:

        self._normalize()


# ==============================================================================
# Part 5. Serialization
# ==============================================================================

    def to_dict(self) -> dict[str, Any]:

        return {
            "name": self.name,
            "count": self.count,
            "sum": self.sum,
            "minimum": self.minimum,
            "maximum": self.maximum,
            "state": deepcopy(
                self.state,
            ),
        }


    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "MetricStatistics":

        return cls(
            name=data.get(
                "name",
                DEFAULT_NAME,
            ),
            count=data.get(
                "count",
                DEFAULT_COUNT,
            ),
            sum=data.get(
                "sum",
                DEFAULT_SUM,
            ),
            minimum=data.get(
                "minimum",
                DEFAULT_MINIMUM,
            ),
            maximum=data.get(
                "maximum",
                DEFAULT_MAXIMUM,
            ),
            state=deepcopy(
                data.get(
                    "state",
                    {},
                ),
            ),
        )


    def to_tuple(
        self,
    ) -> tuple[Any, ...]:

        return (
            self.name,
            self.count,
            self.sum,
            self.minimum,
            self.maximum,
            deepcopy(
                self.state,
            ),
        )


    @classmethod
    def from_tuple(
        cls,
        data: tuple[Any, ...],
    ) -> "MetricStatistics":

        return cls(
            name=data[0],
            count=data[1],
            sum=data[2],
            minimum=data[3],
            maximum=data[4],
            state=deepcopy(
                data[5],
            ),
        )


    def to_json(self) -> str:

        return json.dumps(
            self.to_dict(),
        )


    @classmethod
    def from_json(
        cls,
        value: str,
    ) -> "MetricStatistics":

        return cls.from_dict(
            json.loads(value),
        )

# ==============================================================================
# Part 6. Validation
# ==============================================================================

    @staticmethod
    def validate_name(
        value: Any,
    ) -> bool:

        return isinstance(
            value,
            str,
        )


    @staticmethod
    def validate_count(
        value: Any,
    ) -> bool:

        return (
            isinstance(
                value,
                int,
            )
            and value >= 0
        )


    @staticmethod
    def validate_sum(
        value: Any,
    ) -> bool:

        return isinstance(
            value,
            (
                int,
                float,
            ),
        )


    @staticmethod
    def validate_minimum(
        value: Any,
    ) -> bool:

        return (
            value is None
            or isinstance(
                value,
                (
                    int,
                    float,
                ),
            )
        )


    @staticmethod
    def validate_maximum(
        value: Any,
    ) -> bool:

        return (
            value is None
            or isinstance(
                value,
                (
                    int,
                    float,
                ),
            )
        )


    @staticmethod
    def validate_state(
        value: Any,
    ) -> bool:

        return isinstance(
            value,
            dict,
        )


    @classmethod
    def validate_statistics(
        cls,
        statistics: "MetricStatistics",
    ) -> bool:

        return (
            isinstance(
                statistics,
                cls,
            )
            and cls.validate_name(
                statistics.name,
            )
            and cls.validate_count(
                statistics.count,
            )
            and cls.validate_sum(
                statistics.sum,
            )
            and cls.validate_minimum(
                statistics.minimum,
            )
            and cls.validate_maximum(
                statistics.maximum,
            )
            and cls.validate_state(
                statistics.state,
            )
        )


    def validate(self) -> bool:

        return self.validate_statistics(
            self,
        )


# ==============================================================================
# Part 7. Utilities
# ==============================================================================

    def clone(self) -> "MetricStatistics":

        return deepcopy(
            self,
        )


    def copy(self) -> "MetricStatistics":

        return self.clone()


    def clear(self) -> None:

        self.reset()


    def summary(self) -> dict[str, Any]:

        return {
            "name": self.name,
            "count": self.count,
            "sum": self.sum,
            "minimum": self.minimum,
            "maximum": self.maximum,
            "average": self.average,
            "valid": self.validate(),
        }


    def statistics_report(self) -> dict[str, Any]:

        return {
            "summary": self.summary(),
            "diagnostics": self.diagnostics(),
        }


    def overall_status(self) -> str:

        if not self.validate():
            return "invalid"

        return "healthy"


# ==============================================================================
# Part 8. Protocols
# ==============================================================================

    def __hash__(self) -> int:

        return hash(
            (
                self.name,
                self.count,
                self.sum,
                self.minimum,
                self.maximum,
            )
        )


    def __eq__(
        self,
        other: object,
    ) -> bool:

        if not isinstance(
            other,
            MetricStatistics,
        ):
            return False

        return self.to_dict() == other.to_dict()


    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}"
            f"(name={self.name!r}, "
            f"count={self.count}, "
            f"sum={self.sum})"
        )


    def __str__(self) -> str:

        return self.__repr__()


    def __bool__(self) -> bool:

        return self.count > 0


    def __len__(self) -> int:

        return self.count


    def __contains__(
        self,
        key: str,
    ) -> bool:

        return key in self.state


    def __iter__(self):

        return iter(
            self.state.items(),
        )


    def __getitem__(
        self,
        key: str,
    ) -> Any:

        return self.state[key]


    def __setitem__(
        self,
        key: str,
        value: Any,
    ) -> None:

        self.state[key] = value


# ==============================================================================
# Part 9. Diagnostics
# ==============================================================================

    def diagnostics(self) -> dict[str, Any]:

        return {
            "valid": self.validate(),
            "statistics": self.summary(),
            "state": deepcopy(
                self.state,
            ),
        }


    def health(self) -> str:

        return self.overall_status()


    def issues(self) -> list[str]:

        issues: list[str] = []

        if not self.validate():
            issues.append(
                "validation_failed",
            )

        return issues


    def warnings(self) -> list[str]:

        warnings: list[str] = []

        if self.count == 0:
            warnings.append(
                "no_samples",
            )

        return warnings


    def status(self) -> dict[str, Any]:

        return {
            "health": self.health(),
            "issues": self.issues(),
            "warnings": self.warnings(),
        }


# ==============================================================================
# Part 10. Public API
# ==============================================================================

__all__ = [
    "MetricStatistics",
    "StatisticsState",
    "DEFAULT_NAME",
    "DEFAULT_COUNT",
    "DEFAULT_SUM",
    "DEFAULT_MINIMUM",
    "DEFAULT_MAXIMUM",
    "DEFAULT_AVERAGE",
]        