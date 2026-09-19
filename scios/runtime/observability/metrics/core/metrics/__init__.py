"""
SciOS-NG Metrics Core Engine

Core metric primitives.

Exports:

- Metric
- MetricState
- MetricSnapshot
- MetricRegistry
- MetricCollector
- MetricManager
- MetricHooks

"""


from .metric import Metric
from .metric_state import MetricState
from .metric_snapshot import MetricSnapshot
from .metric_registry import MetricRegistry
from .metric_collector import MetricCollector
from .metric_hooks import MetricHooks
from .manager import MetricManager

# Core objects
from .core.descriptor import MetricDescriptor
from .core.metadata import MetricMetadata
from .core.labels import MetricLabels
from .core.attributes import MetricAttributes
from .core.validation import MetricValidator



__all__ = [
    "Metric",
    "MetricState",
    "MetricSnapshot",
    "MetricRegistry",
    "MetricCollector",
    "MetricHooks",
    "MetricManager",

    "MetricDescriptor",
    "MetricMetadata",
    "MetricLabels",
    "MetricAttributes",
    "MetricValidator",
]