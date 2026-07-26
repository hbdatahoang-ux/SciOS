"""
SciOS-NG Metrics Builders
=========================

Fluent builders for creating runtime metrics.

Responsibilities
-----------------
- Simplify metric construction.
- Provide readable metric configuration.
- Build metrics consistently.
- Support custom labels and metadata.

Python 3.11+
"""

from __future__ import annotations


from typing import Any


from .factory import MetricFactory



__all__ = [
    "MetricBuilder",
    "CounterBuilder",
    "GaugeBuilder",
    "HistogramBuilder",
    "SummaryBuilder",
    "TimerBuilder",
]



# ==========================================================
# Base Metric Builder
# ==========================================================


class MetricBuilder:
    """
    Generic metric builder.

    Example
    -------

        metric = (
            MetricBuilder("gauge")
            .name("cpu")
            .label("host", "node1")
            .build()
        )

    """



    def __init__(
        self,
        metric_type: str,
    ):

        self.metric_type = metric_type


        self._name: str | None = None


        self._options: dict[str, Any] = {}



    # ======================================================
    # Name
    # ======================================================


    def name(
        self,
        value: str,
    ) -> "MetricBuilder":

        self._name = value

        return self



    # ======================================================
    # Options
    # ======================================================


    def option(
        self,
        key: str,
        value: Any,
    ) -> "MetricBuilder":

        self._options[key] = value

        return self



    def labels(
        self,
        **labels: str,
    ) -> "MetricBuilder":

        self._options.setdefault(
            "labels",
            {},
        ).update(
            labels
        )

        return self



    def metadata(
        self,
        **metadata: Any,
    ) -> "MetricBuilder":

        self._options.setdefault(
            "metadata",
            {},
        ).update(
            metadata
        )

        return self



    # ======================================================
    # Build
    # ======================================================


    def build(
        self,
    ):

        if self._name is None:

            raise ValueError(
                "Metric name is required"
            )


        return MetricFactory.create(
            self.metric_type,
            name=self._name,
            **self._options,
        )



# ==========================================================
# Counter Builder
# ==========================================================


class CounterBuilder(MetricBuilder):
    """
    Builder for Counter metrics.
    """

    def __init__(self):

        super().__init__(
            "counter"
        )



# ==========================================================
# Gauge Builder
# ==========================================================


class GaugeBuilder(MetricBuilder):
    """
    Builder for Gauge metrics.
    """

    def __init__(self):

        super().__init__(
            "gauge"
        )



# ==========================================================
# Histogram Builder
# ==========================================================


class HistogramBuilder(MetricBuilder):
    """
    Builder for Histogram metrics.
    """

    def __init__(self):

        super().__init__(
            "histogram"
        )



    def buckets(
        self,
        values: list[float],
    ) -> "HistogramBuilder":

        return self.option(
            "buckets",
            values,
        )



# ==========================================================
# Summary Builder
# ==========================================================


class SummaryBuilder(MetricBuilder):
    """
    Builder for Summary metrics.
    """

    def __init__(self):

        super().__init__(
            "summary"
        )



    def quantiles(
        self,
        values: list[float],
    ) -> "SummaryBuilder":

        return self.option(
            "quantiles",
            values,
        )



# ==========================================================
# Timer Builder
# ==========================================================


class TimerBuilder(MetricBuilder):
    """
    Builder for Timer metrics.
    """

    def __init__(self):

        super().__init__(
            "timer"
        )