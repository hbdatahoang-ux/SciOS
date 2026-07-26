"""
SciOS-NG Metrics Registry
=========================

Central registry for runtime metrics.

Responsibilities
-----------------
- Store metric instances.
- Manage metric lifecycle.
- Provide lookup API.
- Provide snapshots.

Python 3.11+
"""

from __future__ import annotations


from copy import deepcopy
from typing import Any


__all__ = [
    "MetricRegistry",
]



# ==========================================================
# Metric Registry
# ==========================================================


class MetricRegistry:
    """
    Global metric registry.

    Example
    -------

        registry = MetricRegistry()

        registry.register(
            cpu_metric
        )

        metric = registry.get(
            "cpu_usage"
        )

    """


    def __init__(self):

        self._metrics: dict[str, Any] = {}



    # ======================================================
    # Register
    # ======================================================


    def register(
        self,
        metric: Any,
    ):
        """
        Register metric instance.
        """

        name = metric.name


        self._metrics[name] = metric


        return metric



    # ======================================================
    # Factory Register
    # ======================================================


    def add(
        self,
        metric: Any,
    ):

        return self.register(
            metric
        )



    # ======================================================
    # Lookup
    # ======================================================


    def get(
        self,
        name: str,
        default: Any = None,
    ):
        """
        Get metric by name.
        """

        return self._metrics.get(
            name,
            default,
        )



    def exists(
        self,
        name: str,
    ) -> bool:
        """
        Check metric existence.
        """

        return name in self._metrics



    # ======================================================
    # Remove
    # ======================================================


    def remove(
        self,
        name: str,
    ):
        """
        Remove metric.
        """

        return self._metrics.pop(
            name,
            None,
        )



    unregister = remove



    # ======================================================
    # Collection API
    # ======================================================


    def all(
        self,
    ) -> dict[str, Any]:
        """
        Return all metrics.
        """

        return dict(
            self._metrics
        )



    def names(
        self,
    ) -> list[str]:
        """
        Return metric names.
        """

        return list(
            self._metrics.keys()
        )



    def values(
        self,
    ):

        return list(
            self._metrics.values()
        )



    def __len__(
        self,
    ) -> int:

        return len(
            self._metrics
        )



    def __contains__(
        self,
        name: str,
    ) -> bool:

        return name in self._metrics



    # ======================================================
    # Snapshot
    # ======================================================


    def snapshot(
        self,
    ) -> dict[str, Any]:
        """
        Export registry snapshot.
        """

        result = {}


        for name, metric in self._metrics.items():

            if hasattr(
                metric,
                "snapshot",
            ):

                result[name] = metric.snapshot()


            elif hasattr(
                metric,
                "to_dict",
            ):

                result[name] = metric.to_dict()


            else:

                result[name] = deepcopy(
                    metric
                )


        return result



    # ======================================================
    # Reset
    # ======================================================


    def reset(
        self,
    ):
        """
        Reset all metrics.
        """

        for metric in self._metrics.values():

            if hasattr(
                metric,
                "reset",
            ):

                metric.reset()



    # ======================================================
    # Clear
    # ======================================================


    def clear(
        self,
    ):
        """
        Remove all metrics.
        """

        self._metrics.clear()



    # ======================================================
    # Export
    # ======================================================


    def to_dict(
        self,
    ) -> dict[str, Any]:

        return self.snapshot()



    # ======================================================
    # Debug
    # ======================================================


    def __repr__(
        self,
    ) -> str:

        return (
            "MetricRegistry("
            f"metrics={len(self._metrics)}"
            ")"
        )