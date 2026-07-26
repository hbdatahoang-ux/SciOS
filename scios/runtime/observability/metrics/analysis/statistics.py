"""
SciOS-NG Runtime Metrics Analysis

Descriptive Statistics Engine

SciOS/scios/runtime/observability/metrics/analysis/statistics.py
"""

from __future__ import annotations

import copy
import json
import math
import statistics
import threading
import uuid

from collections import Counter
from datetime import datetime
from typing import Any, Iterable


class MetricStatistics:
    """
    Descriptive Statistics Engine.

    Features
    --------
    • Descriptive Statistics
    • Distribution Analysis
    • Rolling Statistics
    • Summary / Reporting
    • Serialization
    """

    # ==========================================================
    # Constructor
    # ==========================================================

    def __init__(
        self,
        values: Iterable[float] | None = None,
        name: str = "MetricStatistics",
        description: str = "",
    ) -> None:

        # Identity
        self._id = str(uuid.uuid4())
        self._name = name
        self._description = description

        # Data
        self._values = list(values or [])

        # Runtime
        self._enabled = True
        self._closed = False

        # Synchronization
        self._lock = threading.RLock()

        # Metadata
        self._created_at = datetime.utcnow()
        self._updated_at = self._created_at
        self._version = "0.2"

    # ==========================================================
    # Data API
    # ==========================================================

    def add(
        self,
        value: float,
    ):

        with self._lock:

            self._values.append(float(value))
            self._updated_at = datetime.utcnow()

        return self

    def extend(
        self,
        values: Iterable[float],
    ):

        with self._lock:

            self._values.extend(
                float(v)
                for v in values
            )

            self._updated_at = datetime.utcnow()

        return self

    def clear(self):

        self._values.clear()
        return self

    def values(self):

        return list(self._values)

    # ==========================================================
    # Basic Statistics
    # ==========================================================

    def count(self):

        return len(self._values)

    def sum(self):

        return sum(self._values)

    def mean(self):

        if not self._values:
            return 0.0

        return statistics.fmean(self._values)

    def median(self):

        if not self._values:
            return 0.0

        return statistics.median(self._values)

    def mode(self):

        if not self._values:
            return None

        try:
            return statistics.mode(self._values)

        except statistics.StatisticsError:

            return Counter(
                self._values
            ).most_common(1)[0][0]

    def minimum(self):

        return min(self._values) if self._values else None

    def maximum(self):

        return max(self._values) if self._values else None

    def range(self):

        if len(self._values) < 2:
            return 0.0

        return self.maximum() - self.minimum()

    def variance(self):

        if len(self._values) < 2:
            return 0.0

        return statistics.variance(
            self._values
        )

    def std(self):

        if len(self._values) < 2:
            return 0.0

        return statistics.stdev(
            self._values
        )

    # ==========================================================
    # Percentiles
    # ==========================================================

    def percentile(
        self,
        p: float,
    ):

        if not self._values:
            return None

        data = sorted(self._values)

        index = (len(data) - 1) * p / 100

        lower = math.floor(index)
        upper = math.ceil(index)

        if lower == upper:
            return data[int(index)]

        weight = index - lower

        return (
            data[lower] * (1 - weight)
            + data[upper] * weight
        )

    def quantile(
        self,
        q: float,
    ):

        return self.percentile(
            q * 100
        )

    def iqr(self):

        return (
            self.percentile(75)
            - self.percentile(25)
        )

    # ==========================================================
    # Distribution
    # ==========================================================

    def histogram(self):

        return dict(
            Counter(self._values)
        )

    def frequency(self):

        total = self.count()

        if total == 0:
            return {}

        hist = self.histogram()

        return {

            k: v / total

            for k, v in hist.items()

        }

    def cumulative(self):

        total = 0

        result = []

        for value in sorted(self._values):

            total += value

            result.append(total)

        return result

    def normalize(self):

        if not self._values:
            return []

        lo = self.minimum()
        hi = self.maximum()

        if lo == hi:
            return [0.0] * len(self._values)

        return [

            (x - lo) / (hi - lo)

            for x in self._values

        ]

    # ==========================================================
    # Rolling Statistics
    # ==========================================================

    def moving_average(
        self,
        window: int = 5,
    ):

        if window <= 0:
            raise ValueError("window > 0")

        values = self._values

        if len(values) < window:
            return []

        return [

            sum(values[i:i + window]) / window

            for i in range(
                len(values) - window + 1
            )

        ]

    rolling_mean = moving_average

    def rolling_std(
        self,
        window: int = 5,
    ):

        if len(self._values) < window:
            return []

        return [

            statistics.stdev(
                self._values[i:i + window]
            )

            for i in range(
                len(self._values) - window + 1
            )

        ]

    def exponential_average(
        self,
        alpha: float = 0.2,
    ):

        if not self._values:
            return []

        result = [self._values[0]]

        for value in self._values[1:]:

            result.append(

                alpha * value
                + (1 - alpha) * result[-1]

            )

        return result

    # ==========================================================
    # Summary
    # ==========================================================

    def describe(self):

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
            "q25": self.percentile(25),
            "q50": self.percentile(50),
            "q75": self.percentile(75),
            "iqr": self.iqr(),

        }

    summary = describe
    statistics = describe
    report = describe

    # ==========================================================
    # Serialization
    # ==========================================================

    def to_dict(self):

        return {

            "id": self._id,
            "name": self._name,
            "description": self._description,
            "values": self.values(),
            "statistics": self.describe(),

        }

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ):

        return cls(

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

    def to_json(self):

        return json.dumps(
            self.to_dict(),
            indent=4,
        )

    # ==========================================================
    # Copy
    # ==========================================================

    def copy(self):

        return copy.copy(self)

    def clone(self):

        return copy.deepcopy(self)

    # ==========================================================
    # Python Protocols
    # ==========================================================

    def __len__(self):

        return len(self._values)

    def __iter__(self):

        return iter(self._values)

    def __contains__(
        self,
        value,
    ):

        return value in self._values

    def __getitem__(
        self,
        index,
    ):

        return self._values[index]

    def __call__(self):

        return self.describe()

    def __repr__(self):

        return (
            f"MetricStatistics("
            f"count={self.count()}, "
            f"mean={self.mean():.4f})"
        )