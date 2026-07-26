"""
SciOS-NG Metrics Monitor
========================

Public API for metric monitoring subsystem.

Exports:
- MetricMonitor
"""

from __future__ import annotations


from .metric_monitor import MetricMonitor


__all__ = [
    "MetricMonitor",
]


__version__ = "0.1.0"