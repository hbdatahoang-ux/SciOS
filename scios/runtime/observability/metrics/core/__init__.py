"""
SciOS-NG Observability
======================

Metric Core Package

Core metric implementations used by the SciOS runtime.

Available Metrics
-----------------

- Metric
- Counter
- Gauge
- Histogram
- Summary
- Timer

Core Components
---------------

- MetricDescriptor
- MetricSnapshot
- MetricMetadata
- MetricLabels
- MetricAttributes

These classes form the canonical runtime metric model
used throughout SciOS Observability.
"""

from .attributes import MetricAttributes
from .counter import Counter
from .descriptor import MetricDescriptor
from .gauge import Gauge
from .histogram import Histogram
from .labels import MetricLabels
from .metadata import MetricMetadata
from .metric import Metric
from .snapshot import MetricSnapshot
from .summary import Summary
from .timer import Timer

__all__ = [
    # Base
    "Metric",

    # Metric types
    "Counter",
    "Gauge",
    "Histogram",
    "Summary",
    "Timer",

    # Supporting types
    "MetricDescriptor",
    "MetricSnapshot",
    "MetricMetadata",
    "MetricLabels",
    "MetricAttributes",
]

__version__ = "0.1.0"