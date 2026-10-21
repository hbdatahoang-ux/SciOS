"""
SciOS Metrics Monitoring Subsystem.

Lightweight public package interface.

Modules
-------
- status
- health
- alert
- threshold
- snapshot
- manager
"""

from __future__ import annotations

from .status import (
    MetricStatus,
    MetricStatusInfo,
)

__version__ = "0.1.0"

__all__ = [
    "MetricStatus",
    "MetricStatusInfo",
    "MetricHealth",
    "MetricAlert",
    "MetricThreshold",
    "MetricSnapshot",
    "MetricManager",
]


def __getattr__(name: str):
    """
    Lazy imports to avoid circular dependencies during test collection.
    """

    if name == "MetricHealth":
        from .health import MetricHealth

        return MetricHealth

    if name == "MetricAlert":
        from .alert import MetricAlert

        return MetricAlert

    if name == "MetricThreshold":
        from .threshold import MetricThreshold

        return MetricThreshold

    if name == "MetricSnapshot":
        from .snapshot import MetricSnapshot

        return MetricSnapshot

    if name == "MetricManager":
        from .manager import MetricManager

        return MetricManager

    raise AttributeError(
        f"module {__name__!r} has no attribute {name!r}"
    )