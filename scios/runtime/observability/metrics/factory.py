"""
SciOS-NG Metrics Factory
========================

Factory utilities for creating metric instances.

Responsibilities
-----------------
- Create metrics by type.
- Centralize metric construction.
- Avoid direct class coupling.
- Provide registry integration.

Supported metrics
-----------------
- Counter
- Gauge
- Histogram
- Summary
- Timer

Python 3.11+
"""

from __future__ import annotations


from typing import Any, Type


from .counter import Counter
from .gauge import Gauge
from .histogram import Histogram
from .summary import Summary
from .timer import Timer



__all__ = [
    "MetricFactory",
    "create_metric",
]



# ==========================================================
# Metric Factory
# ==========================================================


class MetricFactory:
    """
    Metric object factory.

    Example
    -------

        metric = MetricFactory.create(
            "counter",
            name="requests"
        )

    """



    # ======================================================
    # Type Registry
    # ======================================================


    _types: dict[str, Type[Any]] = {

        "counter":
            Counter,

        "gauge":
            Gauge,

        "histogram":
            Histogram,

        "summary":
            Summary,

        "timer":
            Timer,
    }



    # ======================================================
    # Register
    # ======================================================


    @classmethod
    def register(
        cls,
        name: str,
        metric_type: Type[Any],
    ) -> None:
        """
        Register custom metric type.
        """

        cls._types[
            name.lower()
        ] = metric_type



    # ======================================================
    # Create
    # ======================================================


    @classmethod
    def create(
        cls,
        metric_type: str,
        *,
        name: str,
        **kwargs: Any,
    ) -> Any:
        """
        Create metric instance.

        Parameters
        ----------
        metric_type:
            Metric kind.

        name:
            Metric name.

        """

        metric_cls = cls._types.get(
            metric_type.lower()
        )


        if metric_cls is None:

            raise ValueError(
                f"Unknown metric type: {metric_type}"
            )


        return metric_cls(
            name=name,
            **kwargs,
        )



    # ======================================================
    # Helpers
    # ======================================================


    @classmethod
    def available(
        cls,
    ) -> list[str]:
        """
        Return supported metric types.
        """

        return sorted(
            cls._types.keys()
        )



    @classmethod
    def contains(
        cls,
        metric_type: str,
    ) -> bool:
        """
        Check metric support.
        """

        return (
            metric_type.lower()
            in cls._types
        )



    @classmethod
    def remove(
        cls,
        metric_type: str,
    ) -> None:
        """
        Remove custom metric type.
        """

        cls._types.pop(
            metric_type.lower(),
            None,
        )



    @classmethod
    def reset(
        cls,
    ) -> None:
        """
        Restore default registry.
        """

        cls._types = {

            "counter":
                Counter,

            "gauge":
                Gauge,

            "histogram":
                Histogram,

            "summary":
                Summary,

            "timer":
                Timer,
        }



# ==========================================================
# Shortcut API
# ==========================================================


def create_metric(
    metric_type: str,
    *,
    name: str,
    **kwargs: Any,
) -> Any:
    """
    Shortcut for MetricFactory.create().
    """

    return MetricFactory.create(
        metric_type,
        name=name,
        **kwargs,
    )