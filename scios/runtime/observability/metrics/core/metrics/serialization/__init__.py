"""
SciOS Runtime Metrics Serialization
===================================

Serialization subsystem for the Metrics runtime.

Exports
-------
- MetricSerializer

Responsibilities
----------------
- Dictionary serialization
- JSON serialization
- File persistence
- Snapshot persistence
- Object restoration
- Validation utilities
"""

from __future__ import annotations

from .metric_serializer import MetricSerializer

__all__ = [
    "MetricSerializer",
]

__version__ = "1.0.0"