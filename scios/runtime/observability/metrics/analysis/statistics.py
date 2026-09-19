"""
SciOS-NG Runtime Metrics Analysis
=================================

Descriptive Statistics Engine.

Responsibilities
-----------------
- Store numeric metric observations.
- Compute descriptive statistics.
- Analyze distributions.
- Compute rolling statistics.
- Normalize observations.
- Serialize and restore analysis state.
- Provide thread-safe access.

Python 3.11+
"""

from __future__ import annotations

import copy
import json
import math
import statistics
import threading
import uuid
from collections import Counter
from datetime import datetime, timezone
from typing import Any, Iterable


__all__ = [
    "MetricStatistics",
]


# ==========================================================
# Helpers
# ==========================================================


def _utcnow() -> datetime:
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)


# ==========================================================
# Metric Statistics
# ==========================================================


class MetricStatistics:
    """
    Thread-safe descriptive statistics engine.

    The class intentionally operates on plain numeric observations
    and remains independent from concrete metric implementations.

    Empty-data conventions
    -----------------------
    count       -> 0
    sum         -> 0.0
    mean        -> 0.0
    median      -> 0.0
    mode        -> None
    minimum     -> None
    maximum     -> None
    range       -> 0.0
    variance    -> 0.0
    std         -> 0.0
    percentile  -> None
    IQR         -> 0.0
    """

    VERSION = "0.3"

    # ==========================================================
    # Constructor
    # ==========================================================

    def __init__(
        self,
        values: Iterable[float] | None = None,
        name: str = "MetricStatistics",
        description: str = "",
    ) -> None:

        self._id = str(uuid.uuid4())
        self._name = str(name)
        self._description = str(description)

        self._values: list[float] = []

        self._enabled = True
        self._closed = False

        self._lock = threading.RLock()

        now = _utcnow()

        self._created_at = now
        self._updated_at = now
        self._version = self.VERSION

        if values is not None:
            self.extend(values)

    # ==========================================================
    # Identity
    # ==========================================================

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def version(self) -> str:
        return self._version

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def closed(self) -> bool:
        return self._closed

    # ==========================================================
    # Internal Validation
    # ==========================================================

    def __deepcopy__(
        self,
        memo: dict[int, Any],
    ) -> "MetricStatistics":
        """
        Create an independent deep copy without copying
        the runtime synchronization primitive.
        """

        cls = self.__class__

        obj = cls.__new__(cls)

        memo[id(self)] = obj

        for key, value in self.__dict__.items():

            if key == "_lock":
                setattr(
                    obj,
                    key,
                    threading.RLock(),
                )
                continue

            setattr(
                obj,
                key,
                copy.deepcopy(
                    value,
                    memo,
                ),
            )

        return obj

    @staticmethod
    def _coerce_value(value: float) -> float:
        """
        Convert an observation to float.

        Reject NaN and infinite values because they make the
        statistical contract ambiguous.
        """

        try:
            result = float(value)
        except (TypeError, ValueError) as exc:
            raise TypeError(
                "metric value must be numeric"
            ) from exc

        if not math.isfinite(result):
            raise ValueError(
                "metric value must be finite"
            )

        return result

    @staticmethod
    def _validate_window(window: int) -> None:
        if not isinstance(window, int):
            raise TypeError(
                "window must be an integer"
            )

        if window <= 0:
            raise ValueError(
                "window must be greater than zero"
            )

    # ==========================================================
    # Data API
    # ==========================================================

    def add(
        self,
        value: float,
    ) -> "MetricStatistics":
        """Append one numeric observation."""

        with self._lock:
            self._values.append(
                self._coerce_value(value)
            )
            self._updated_at = _utcnow()

        return self

    def extend(
        self,
        values: Iterable[float],
    ) -> "MetricStatistics":
        """Append multiple numeric observations."""

        if values is None:
            raise TypeError(
                "values cannot be None"
            )

        with self._lock:
            converted = [
                self._coerce_value(value)
                for value in values
            ]

            self._values.extend(converted)

            if converted:
                self._updated_at = _utcnow()

        return self

    def clear(self) -> "MetricStatistics":
        """Remove all observations."""

        with self._lock:
            self._values.clear()
            self._updated_at = _utcnow()

        return self

    def values(self) -> list[float]:
        """Return a detached copy of observations."""

        with self._lock:
            return list(self._values)

    # ==========================================================
    # Basic Statistics
    # ==========================================================

    def count(self) -> int:
        with self._lock:
            return len(self._values)

    def sum(self) -> float:
        with self._lock:
            return float(sum(self._values))

    def mean(self) -> float:
        with self._lock:
            if not self._values:
                return 0.0

            return float(
                statistics.fmean(self._values)
            )

    def median(self) -> float:
        with self._lock:
            if not self._values:
                return 0.0

            return float(
                statistics.median(self._values)
            )

    def mode(self) -> float | None:
        with self._lock:
            if not self._values:
                return None

            counts = Counter(self._values)

            return float(
                counts.most_common(1)[0][0]
            )

    def minimum(self) -> float | None:
        with self._lock:
            if not self._values:
                return None

            return float(min(self._values))

    def maximum(self) -> float | None:
        with self._lock:
            if not self._values:
                return None

            return float(max(self._values))

    def range(self) -> float:
        with self._lock:
            if not self._values:
                return 0.0

            return float(
                max(self._values)
                - min(self._values)
            )

    def variance(self) -> float:
        with self._lock:
            if len(self._values) < 2:
                return 0.0

            return float(
                statistics.variance(self._values)
            )

    def std(self) -> float:
        with self._lock:
            if len(self._values) < 2:
                return 0.0

            return float(
                statistics.stdev(self._values)
            )

    # ==========================================================
    # Percentiles
    # ==========================================================

    def percentile(
        self,
        p: float,
    ) -> float | None:
        """
        Return percentile using linear interpolation.

        Parameters
        ----------
        p:
            Percentile in the inclusive range [0, 100].
        """

        try:
            p = float(p)
        except (TypeError, ValueError) as exc:
            raise TypeError(
                "percentile must be numeric"
            ) from exc

        if not math.isfinite(p):
            raise ValueError(
                "percentile must be finite"
            )

        if not 0.0 <= p <= 100.0:
            raise ValueError(
                "percentile must be between 0 and 100"
            )

        with self._lock:
            if not self._values:
                return None

            data = sorted(self._values)

        index = (len(data) - 1) * p / 100.0

        lower = math.floor(index)
        upper = math.ceil(index)

        if lower == upper:
            return float(data[lower])

        weight = index - lower

        return float(
            data[lower] * (1.0 - weight)
            + data[upper] * weight
        )

    def quantile(
        self,
        q: float,
    ) -> float | None:
        """
        Return quantile using q in [0, 1].
        """

        try:
            q = float(q)
        except (TypeError, ValueError) as exc:
            raise TypeError(
                "quantile must be numeric"
            ) from exc

        if not math.isfinite(q):
            raise ValueError(
                "quantile must be finite"
            )

        if not 0.0 <= q <= 1.0:
            raise ValueError(
                "quantile must be between 0 and 1"
            )

        return self.percentile(q * 100.0)

    def iqr(self) -> float:
        """Return the interquartile range."""

        with self._lock:
            if not self._values:
                return 0.0

        q25 = self.percentile(25.0)
        q75 = self.percentile(75.0)

        return float(q75 - q25)

    # ==========================================================
    # Distribution
    # ==========================================================

    def histogram(self) -> dict[float, int]:
        """Return exact-value frequency counts."""

        with self._lock:
            return dict(
                Counter(self._values)
            )

    def frequency(self) -> dict[float, float]:
        """Return normalized exact-value frequencies."""

        with self._lock:
            total = len(self._values)

            if total == 0:
                return {}

            counts = Counter(self._values)

            return {
                value: count / total
                for value, count in counts.items()
            }

    def cumulative(self) -> list[float]:
        """
        Return cumulative sum over observations sorted
        in ascending order.
        """

        with self._lock:
            values = sorted(self._values)

        total = 0.0
        result: list[float] = []

        for value in values:
            total += value
            result.append(total)

        return result

    def normalize(self) -> list[float]:
        """
        Min-max normalize observations to [0, 1].
        """

        with self._lock:
            values = list(self._values)

        if not values:
            return []

        lo = min(values)
        hi = max(values)

        if lo == hi:
            return [0.0] * len(values)

        span = hi - lo

        return [
            (value - lo) / span
            for value in values
        ]

    # ==========================================================
    # Rolling Statistics
    # ==========================================================

    def moving_average(
        self,
        window: int = 5,
    ) -> list[float]:
        """Return simple moving averages."""

        self._validate_window(window)

        with self._lock:
            values = list(self._values)

        if len(values) < window:
            return []

        return [
            float(
                sum(
                    values[i:i + window]
                ) / window
            )
            for i in range(
                len(values) - window + 1
            )
        ]

    rolling_mean = moving_average

    def rolling_std(
        self,
        window: int = 5,
    ) -> list[float]:
        """
        Return rolling sample standard deviation.

        A window of one has zero dispersion by definition.
        """

        self._validate_window(window)

        with self._lock:
            values = list(self._values)

        if len(values) < window:
            return []

        if window == 1:
            return [
                0.0
                for _ in range(len(values))
            ]

        return [
            float(
                statistics.stdev(
                    values[i:i + window]
                )
            )
            for i in range(
                len(values) - window + 1
            )
        ]

    def exponential_average(
        self,
        alpha: float = 0.2,
    ) -> list[float]:
        """
        Return exponentially weighted averages.

        alpha must satisfy 0 < alpha <= 1.
        """

        try:
            alpha = float(alpha)
        except (TypeError, ValueError) as exc:
            raise TypeError(
                "alpha must be numeric"
            ) from exc

        if not math.isfinite(alpha):
            raise ValueError(
                "alpha must be finite"
            )

        if not 0.0 < alpha <= 1.0:
            raise ValueError(
                "alpha must be greater than 0 and at most 1"
            )

        with self._lock:
            values = list(self._values)

        if not values:
            return []

        result = [float(values[0])]

        for value in values[1:]:
            result.append(
                float(
                    alpha * value
                    + (1.0 - alpha) * result[-1]
                )
            )

        return result

    # ==========================================================
    # Summary
    # ==========================================================

    def describe(self) -> dict[str, Any]:
        """Return descriptive statistics."""

        return {
            "count": self.count(),
            "sum": self.sum(),
            "mean": self.mean(),
            "median": self.median(),
            "mode": self.mode(),
            "min": self.minimum(),
            "max": self.maximum(),
            "range": self.range(),
            "variance": self.variance(),
            "std": self.std(),
            "q25": self.percentile(25.0),
            "q50": self.percentile(50.0),
            "q75": self.percentile(75.0),
            "iqr": self.iqr(),
        }

    summary = describe
    statistics = describe
    report = describe

    # ==========================================================
    # Serialization
    # ==========================================================

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize the complete analysis state.
        """

        with self._lock:
            return {
                "id": self._id,
                "name": self._name,
                "description": self._description,
                "values": list(self._values),
                "statistics": self.describe(),
                "enabled": self._enabled,
                "closed": self._closed,
                "created_at": self._created_at.isoformat(),
                "updated_at": self._updated_at.isoformat(),
                "version": self._version,
            }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "MetricStatistics":
        """
        Restore an analysis object from serialized state.
        """

        if not isinstance(data, dict):
            raise TypeError(
                "data must be a dictionary"
            )

        instance = cls(
            values=data.get("values", []),
            name=data.get(
                "name",
                "MetricStatistics",
            ),
            description=data.get(
                "description",
                "",
            ),
        )

        if "id" in data:
            instance._id = str(data["id"])

        if "enabled" in data:
            instance._enabled = bool(
                data["enabled"]
            )

        if "closed" in data:
            instance._closed = bool(
                data["closed"]
            )

        if "version" in data:
            instance._version = str(
                data["version"]
            )

        for field_name in (
            "_created_at",
            "_updated_at",
        ):
            key = field_name[1:]

            if key not in data:
                continue

            value = data[key]

            if isinstance(value, datetime):
                parsed = value
            else:
                parsed = datetime.fromisoformat(
                    str(value)
                )

            if parsed.tzinfo is None:
                parsed = parsed.replace(
                    tzinfo=timezone.utc
                )

            setattr(
                instance,
                field_name,
                parsed,
            )

        return instance

    def to_json(self) -> str:
        """Serialize to deterministic JSON."""

        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            sort_keys=True,
            indent=4,
        )

    @classmethod
    def from_json(
        cls,
        payload: str,
    ) -> "MetricStatistics":
        """Restore from JSON."""

        if not isinstance(payload, str):
            raise TypeError(
                "payload must be a string"
            )

        try:
            data = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "invalid JSON payload"
            ) from exc

        return cls.from_dict(data)

    # ==========================================================
    # Copy
    # ==========================================================

    def copy(self) -> "MetricStatistics":
        """
        Return an independent shallow-semantic copy.

        Runtime synchronization state is recreated rather than
        shared with the source instance.
        """

        return self.from_dict(
            self.to_dict()
        )

    def clone(self) -> "MetricStatistics":
        """Return an independent deep clone."""

        return self.from_dict(
            copy.deepcopy(
                self.to_dict()
            )
        )

    # ==========================================================
    # Python Protocols
    # ==========================================================

    def __len__(self) -> int:
        return self.count()

    def __iter__(self):
        with self._lock:
            return iter(
                tuple(self._values)
            )

    def __contains__(
        self,
        value: object,
    ) -> bool:
        with self._lock:
            return value in self._values

    def __getitem__(
        self,
        index: int | slice,
    ):
        with self._lock:
            return self._values[index]

    def __call__(self) -> dict[str, Any]:
        return self.describe()

    def __repr__(self) -> str:
        return (
            "MetricStatistics("
            f"count={self.count()}, "
            f"mean={self.mean():.4f}"
            ")"
        )