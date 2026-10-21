"""
SciOS Runtime Metrics Processor
===============================

Base contract for Runtime Metrics Processing.

Responsibilities
-----------------
- Define the processor lifecycle.
- Transform metric values.
- Track processing statistics.
- Support enable / disable lifecycle.
- Support reset.
- Provide a stable public API for concrete processors.

Python 3.11+
"""

from __future__ import annotations

from typing import Any


__all__ = [
    "MetricProcessor",
]


# ==========================================================
# Metric Processor
# ==========================================================


class MetricProcessor:
    """
    Base class for runtime metric processors.

    A processor receives a metric-like object and returns either:

    - the transformed metric,
    - the original metric,
    - or ``None`` when the metric is intentionally dropped.

    Concrete processors should override :meth:`transform`.

    Example
    -------

    >>> processor = MetricProcessor()
    >>> processor.process({"name": "requests", "value": 1})
    {'name': 'requests', 'value': 1}
    """

    # ======================================================
    # Initialization
    # ======================================================

    def __init__(
        self,
        name: str = "MetricProcessor",
        description: str = "",
        enabled: bool = True,
    ) -> None:
        """
        Create a metric processor.
        """

        if not isinstance(name, str):
            raise TypeError(
                "name must be a string"
            )

        if not name:
            raise ValueError(
                "name must not be empty"
            )

        if not isinstance(description, str):
            raise TypeError(
                "description must be a string"
            )

        self._name = name
        self._description = description
        self._enabled = bool(enabled)

        self._processed = 0
        self._failed = 0
        self._dropped = 0

    # ======================================================
    # Properties
    # ======================================================

    @property
    def name(self) -> str:
        """
        Processor name.
        """

        return self._name

    @property
    def description(self) -> str:
        """
        Processor description.
        """

        return self._description

    @property
    def enabled(self) -> bool:
        """
        Whether the processor is enabled.
        """

        return self._enabled

    @property
    def processed(self) -> int:
        """
        Number of successfully processed metrics.
        """

        return self._processed

    @property
    def failed(self) -> int:
        """
        Number of processing failures.
        """

        return self._failed

    @property
    def dropped(self) -> int:
        """
        Number of metrics dropped by the processor.
        """

        return self._dropped

    # ======================================================
    # Lifecycle
    # ======================================================

    def enable(self) -> "MetricProcessor":
        """
        Enable processor.
        """

        self._enabled = True

        return self

    def disable(self) -> "MetricProcessor":
        """
        Disable processor.

        A disabled processor passes metrics through unchanged.
        """

        self._enabled = False

        return self

    # ======================================================
    # Processing
    # ======================================================

    def transform(
        self,
        metric: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Transform a metric.

        The base implementation is an identity transformation.
        """

        return metric

    def process(
        self,
        metric: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Process a metric through the processor.

        Disabled processors pass the metric through unchanged.

        ``None`` returned by ``transform`` is interpreted as a
        deliberately dropped metric.

        Exceptions are counted as failures and re-raised.
        """

        if not self._enabled:
            return metric

        try:
            result = self.transform(
                metric,
                **kwargs,
            )

        except Exception:
            self._failed += 1
            raise

        self._processed += 1

        if result is None:
            self._dropped += 1

        return result

    # ======================================================
    # Callable Protocol
    # ======================================================

    def __call__(
        self,
        metric: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Allow processor instances to be called directly.
        """

        return self.process(
            metric,
            **kwargs,
        )

    # ======================================================
    # Statistics
    # ======================================================

    def statistics(self) -> dict[str, Any]:
        """
        Return processor statistics.
        """

        return {
            "name": self._name,
            "description": self._description,
            "enabled": self._enabled,
            "processed": self._processed,
            "failed": self._failed,
            "dropped": self._dropped,
        }

    # ======================================================
    # Runtime
    # ======================================================

    def reset(self) -> "MetricProcessor":
        """
        Reset runtime processing statistics.

        Configuration is preserved.
        """

        self._processed = 0
        self._failed = 0
        self._dropped = 0

        return self

    # ======================================================
    # Python Protocols
    # ======================================================

    def __len__(self) -> int:
        """
        Return number of successfully processed metrics.
        """

        return self._processed

    def __bool__(self) -> bool:
        """
        Return whether processing has occurred.
        """

        return self._processed > 0

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name={self._name!r}, "
            f"enabled={self._enabled}, "
            f"processed={self._processed}, "
            f"failed={self._failed}, "
            f"dropped={self._dropped}"
            f")"
        )

    def __str__(self) -> str:
        return self._name