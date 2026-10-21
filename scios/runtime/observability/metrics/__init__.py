"""
SciOS-NG Metrics System
=======================

Core telemetry and observability framework.

Provides:

- Metric primitives
- Metric registry
- Metric collection
- Recording pipeline
- Aggregation
- Snapshots
- Exporters
- Runtime metrics plugin

Python 3.11+
"""

from __future__ import annotations


__version__ = "0.1.0"


# ==========================================================
# Metric Core
# ==========================================================

try:
    from .metric import (
        Metric,
    )
except ImportError:
    Metric = None


try:
    from .counter import (
        Counter,
    )
except ImportError:
    Counter = None


try:
    from .gauge import (
        Gauge,
    )
except ImportError:
    Gauge = None


try:
    from .histogram import (
        Histogram,
    )
except ImportError:
    Histogram = None


try:
    from .summary import (
        Summary,
    )
except ImportError:
    Summary = None


try:
    from .timer import (
        Timer,
    )
except ImportError:
    Timer = None



# ==========================================================
# Snapshot
# ==========================================================

try:
    from .snapshot import (
        MetricSnapshot,
    )
except ImportError:
    MetricSnapshot = None



# ==========================================================
# Labels
# ==========================================================

try:
    from .labels import (
        MetricLabels,
        Labels,
    )
except ImportError:
    MetricLabels = None
    Labels = None



# ==========================================================
# Registry
# ==========================================================

try:
    from .registry import (
        MetricRegistry,
    )
except ImportError:
    MetricRegistry = None



# ==========================================================
# Recorder
# ==========================================================

try:
    from .recorder import (
        MetricRecorder,
    )
except ImportError:
    MetricRecorder = None



# ==========================================================
# Collector
# ==========================================================

try:
    from .collector import (
        MetricCollector,
    )
except ImportError:
    MetricCollector = None



# ==========================================================
# Aggregator
# ==========================================================

try:
    from .aggregator import (
        MetricAggregator,
    )
except ImportError:
    MetricAggregator = None



# ==========================================================
# Memory Backend
# ==========================================================

try:
    from .memory import (
        MemoryMetricStore,
    )
except ImportError:
    MemoryMetricStore = None



# ==========================================================
# Factory
# ==========================================================

try:
    from .factory import (
        MetricFactory,
    )
except ImportError:
    MetricFactory = None



# ==========================================================
# Builders
# ==========================================================

try:
    from .builders import (
        MetricBuilder,
    )
except ImportError:
    MetricBuilder = None



# ==========================================================
# Export Interface
# ==========================================================

try:
    from .exporter import (
        MetricExporter,
    )
except ImportError:
    MetricExporter = None



# ==========================================================
# Exporters
# ==========================================================

try:
    from .json_exporter import (
        JSONExporter,
    )
except ImportError:
    JSONExporter = None


try:
    from .prometheus import (
        PrometheusExporter,
    )
except ImportError:
    PrometheusExporter = None


try:
    from .otel import (
        OpenTelemetryExporter,
    )
except ImportError:
    OpenTelemetryExporter = None



# ==========================================================
# Runtime Plugin
# ==========================================================

try:
    from .plugin import (
        MetricsPlugin,
    )
except ImportError:
    MetricsPlugin = None



# ==========================================================
# Public API
# ==========================================================

__all__ = [

    # Version
    "__version__",


    # Metric primitives
    "Metric",
    "Counter",
    "Gauge",
    "Histogram",
    "Summary",
    "Timer",


    # Labels
    "MetricLabels",
    "Labels",


    # Snapshot
    "MetricSnapshot",


    # Registry
    "MetricRegistry",


    # Recorder
    "MetricRecorder",


    # Collector
    "MetricCollector",


    # Aggregation
    "MetricAggregator",


    # Storage
    "MemoryMetricStore",


    # Factory
    "MetricFactory",


    # Builder
    "MetricBuilder",


    # Exporter
    "MetricExporter",
    "JSONExporter",
    "PrometheusExporter",
    "OpenTelemetryExporter",


    # Runtime plugin
    "MetricsPlugin",

]