"""
SciOS Runtime Metrics Core
==========================

Core metric primitives.

This package is being rebuilt incrementally.

Only stable modules should be exported here.

Python 3.11+
"""

from __future__ import annotations

# ==============================================================================
# Version
# ==============================================================================

__version__ = "0.1.0"

__api_version__ = "1.0"

# ==============================================================================
# Stable Public API
# ==============================================================================

from .descriptor import (
    MetricDescriptor,
    MetricType,
    MetricUnit,
)

# ==============================================================================
# Public API
# ==============================================================================

__all__ = [
    "__version__",
    "__api_version__",
    "MetricDescriptor",
    "MetricType",
    "MetricUnit",
]