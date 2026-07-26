"""
SciOS-NG Runtime Observability Package

Provides:
    - Metrics Runtime Engine
    - Monitoring Components
    - Runtime Diagnostics

SciOS-NG v0.2
"""


# ==================================================================
# Runtime Observability Version
# ==================================================================

__version__ = "0.2.0"



# ==================================================================
# Metrics Runtime
# ==================================================================

from .metrics.runtime.registry import (
    MetricRegistry,
)

from .metrics.runtime.collector import (
    MetricCollector,
)

from .metrics.runtime.recorder import (
    MetricRecorder,
)

from .metrics.runtime.aggregator import (
    MetricAggregator,
)

from .metrics.runtime.cache import (
    MetricCache,
)

from .metrics.runtime.pipeline import (
    MetricPipeline,
)

from .metrics.runtime.dispatcher import (
    MetricDispatcher,
)

from .metrics.runtime.scheduler import (
    MetricScheduler,
)

from .metrics.runtime.plugin import (
    MetricPlugin,
)



# ==================================================================
# Public API
# ==================================================================

__all__ = [

    # Registry
    "MetricRegistry",

    # Collection
    "MetricCollector",

    # Recording
    "MetricRecorder",

    # Aggregation
    "MetricAggregator",

    # Cache
    "MetricCache",

    # Pipeline
    "MetricPipeline",

    # Dispatcher
    "MetricDispatcher",

    # Scheduler
    "MetricScheduler",

    # Plugin
    "MetricPlugin",

]