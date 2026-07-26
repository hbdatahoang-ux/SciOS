"""
SciOS-NG Metrics Serialization
==============================

Public API for metric serialization subsystem.

Exports:
    - MetricSerializer

Responsibilities:
    - Serialize metrics
    - Deserialize metrics
    - Snapshot persistence
    - JSON conversion
    - File persistence
    - Validation
"""

from __future__ import annotations


from .metric_serializer import (
    MetricSerializer,
)


__all__ = [
    "MetricSerializer",
]


__version__ = "0.1.0"