"""
SciOS-NG Prometheus Exporter
============================

Prometheus exposition format exporter
for SciOS Metrics subsystem.
"""

from __future__ import annotations


from threading import RLock
from typing import Any
from pathlib import Path
import json
import copy
from contextlib import contextmanager
import threading

__all__ = [
    "PrometheusExporter",
]


class PrometheusExporter:
    """
    Export SciOS metrics into Prometheus format.

    Responsibilities:
    - metric naming
    - label formatting
    - exposition generation
    - scrape payload creation
    """



    # ==================================================
    # Constants
    # ==================================================

    VERSION = "0.1.0"

    FORMAT = "prometheus"



    # ==================================================
    # Constructor
    # ==================================================

    def __init__(
        self,
        namespace: str = "scios",
        subsystem: str | None = None,
    ) -> None:
        """
        Initialize Prometheus exporter.
        """


        #
        # Identity
        #

        self._name = (
            "PrometheusExporter"
        )


        self._version = (
            self.VERSION
        )


        #
        # Configuration
        #

        self._namespace = namespace

        self._subsystem = subsystem


        #
        # Runtime
        #

        self._enabled = True

        self._export_count = 0

        self._error_count = 0


        #
        # Last state
        #

        self._last_export = None

        self._last_payload = None


        #
        # Thread safety
        #

        self._lock = RLock()



    # ==================================================
    # Identity API
    # ==================================================

    @property
    def name(
        self,
    ) -> str:
        """
        Exporter name.
        """

        return self._name



    @property
    def version(
        self,
    ) -> str:
        """
        Exporter version.
        """

        return self._version



    @property
    def format(
        self,
    ) -> str:
        """
        Export format.
        """

        return self.FORMAT



    # ==================================================
    # Configuration State
    # ==================================================

    @property
    def namespace(
        self,
    ) -> str:
        """
        Metric namespace.
        """

        return self._namespace



    @property
    def subsystem(
        self,
    ) -> str | None:
        """
        Metric subsystem.
        """

        return self._subsystem



    # ==================================================
    # Runtime State
    # ==================================================

    @property
    def enabled(
        self,
    ) -> bool:
        """
        Exporter status.
        """

        return self._enabled



    @property
    def export_count(
        self,
    ) -> int:
        """
        Number of exports.
        """

        return self._export_count



    @property
    def error_count(
        self,
    ) -> int:
        """
        Number of failures.
        """

        return self._error_count



    # ==================================================
    # Lock API
    # ==================================================

    @property
    def lock(
        self,
    ) -> RLock:
        """
        Internal synchronization lock.
        """

        return self._lock
# ==================================================
# Part 2. Configuration API
# ==================================================


# --------------------------------------------------
# Configure
# --------------------------------------------------

def configure(
    self,
    *,
    namespace: str | None = None,
    subsystem: str | None = None,
    enabled: bool | None = None,
) -> "PrometheusExporter":
    """
    Update exporter configuration.
    """

    with self._lock:

        if namespace is not None:

            self._namespace = namespace


        if subsystem is not None:

            self._subsystem = subsystem


        if enabled is not None:

            self._enabled = enabled


    return self



# --------------------------------------------------
# Set Namespace
# --------------------------------------------------

def set_namespace(
    self,
    namespace: str,
) -> "PrometheusExporter":
    """
    Change metric namespace.
    """

    with self._lock:

        self._namespace = namespace


    return self



# --------------------------------------------------
# Set Subsystem
# --------------------------------------------------

def set_subsystem(
    self,
    subsystem: str | None,
) -> "PrometheusExporter":
    """
    Change metric subsystem.
    """

    with self._lock:

        self._subsystem = subsystem


    return self



# --------------------------------------------------
# Enable
# --------------------------------------------------

def enable(
    self,
) -> None:
    """
    Enable exporter.
    """

    with self._lock:

        self._enabled = True



# --------------------------------------------------
# Disable
# --------------------------------------------------

def disable(
    self,
) -> None:
    """
    Disable exporter.
    """

    with self._lock:

        self._enabled = False



# --------------------------------------------------
# Configuration Snapshot
# --------------------------------------------------

def config(
    self,
) -> dict[str, object]:
    """
    Return current configuration.
    """

    with self._lock:

        return {

            "namespace":
                self._namespace,

            "subsystem":
                self._subsystem,

            "enabled":
                self._enabled,

            "format":
                self.FORMAT,

            "version":
                self._version,

        }



# --------------------------------------------------
# Reset Configuration
# --------------------------------------------------

def reset_config(
    self,
) -> None:
    """
    Restore default configuration.
    """

    with self._lock:

        self._namespace = "scios"

        self._subsystem = None

        self._enabled = True
# ==================================================
# Part 3. Metric Formatting API
# ==================================================


# --------------------------------------------------
# Format Metric Name
# --------------------------------------------------

def format_name(
    self,
    name: str,
) -> str:
    """
    Create Prometheus metric name.

    Example:
        cpu_usage

    becomes:

        scios_cpu_usage
    """

    parts = []


    if self._namespace:

        parts.append(
            self._namespace
        )


    if self._subsystem:

        parts.append(
            self._subsystem
        )


    parts.append(
        name
    )


    return "_".join(
        parts
    )



# --------------------------------------------------
# Normalize Metric Name
# --------------------------------------------------

def normalize_metric(
    self,
    name: str,
) -> str:
    """
    Normalize metric name.

    Prometheus rules:
    - lowercase
    - underscore separator
    """

    return (
        name
        .strip()
        .lower()
        .replace(
            "-",
            "_",
        )
        .replace(
            " ",
            "_",
        )
    )



# --------------------------------------------------
# Format Value
# --------------------------------------------------

def format_value(
    self,
    value,
) -> str:
    """
    Convert metric value.

    Supports:
    - int
    - float
    - bool
    """

    if isinstance(
        value,
        bool,
    ):

        return (
            "1"
            if value
            else "0"
        )


    return str(
        value
    )



# --------------------------------------------------
# Format Sample
# --------------------------------------------------

def format_sample(
    self,
    name: str,
    value,
    labels: dict[str, str] | None = None,
    timestamp: int | None = None,
) -> str:
    """
    Create Prometheus sample line.

    Example:

    scios_cpu_usage{node="01"} 70
    """

    metric_name = self.format_name(
        self.normalize_metric(name)
    )


    label_text = ""


    if labels:

        pairs = [

            f'{k}="{v}"'

            for k, v in labels.items()

        ]

        label_text = (
            "{"
            +
            ",".join(pairs)
            +
            "}"
        )


    line = (
        f"{metric_name}"
        f"{label_text} "
        f"{self.format_value(value)}"
    )


    if timestamp is not None:

        line += (
            f" {timestamp}"
        )


    return line



# --------------------------------------------------
# Format Metric Object
# --------------------------------------------------

def format_metric(
    self,
    metric,
) -> str:
    """
    Convert Metric object into
    Prometheus sample.
    """

    if hasattr(
        metric,
        "name",
    ):

        name = metric.name


    else:

        name = "unknown"



    if hasattr(
        metric,
        "value",
    ):

        value = metric.value


    elif isinstance(
        metric,
        dict,
    ):

        value = metric.get(
            "value",
            0,
        )


    else:

        value = metric



    return self.format_sample(
        name,
        value,
    )
# ==================================================
# Part 4. Labels API
# ==================================================


# --------------------------------------------------
# Initialize Labels
# --------------------------------------------------

def _init_labels(
    self,
) -> None:
    """
    Initialize exporter labels.
    """

    self._labels = {}



# --------------------------------------------------
# Set Labels
# --------------------------------------------------

def set_labels(
    self,
    labels: dict[str, str],
) -> "PrometheusExporter":
    """
    Replace exporter labels.
    """

    with self._lock:

        self._labels = (
            self.normalize_labels(
                labels
            )
        )


    return self



# --------------------------------------------------
# Add Label
# --------------------------------------------------

def add_label(
    self,
    key: str,
    value: str,
) -> "PrometheusExporter":
    """
    Add single label.
    """

    with self._lock:

        self._labels[
            self.normalize_label_key(key)
        ] = str(value)


    return self



# --------------------------------------------------
# Remove Label
# --------------------------------------------------

def remove_label(
    self,
    key: str,
) -> None:
    """
    Remove label.
    """

    with self._lock:

        self._labels.pop(
            self.normalize_label_key(key),
            None,
        )



# --------------------------------------------------
# Get Labels
# --------------------------------------------------

@property
def labels(
    self,
) -> dict[str, str]:
    """
    Current exporter labels.
    """

    with self._lock:

        return dict(
            self._labels
        )



# --------------------------------------------------
# Normalize Label Key
# --------------------------------------------------

def normalize_label_key(
    self,
    key: str,
) -> str:
    """
    Normalize label key.

    Example:

        Node-ID

    becomes:

        node_id
    """

    return (
        key
        .strip()
        .lower()
        .replace(
            "-",
            "_",
        )
        .replace(
            " ",
            "_",
        )
    )



# --------------------------------------------------
# Normalize Labels
# --------------------------------------------------

def normalize_labels(
    self,
    labels: dict[str, str],
) -> dict[str, str]:
    """
    Normalize all labels.
    """

    return {

        self.normalize_label_key(k):
            str(v)

        for k, v in labels.items()

    }



# --------------------------------------------------
# Merge Labels
# --------------------------------------------------

def merge_labels(
    self,
    *labels: dict[str, str],
) -> dict[str, str]:
    """
    Merge multiple label sets.
    """

    result = {}


    for item in labels:

        result.update(
            self.normalize_labels(
                item
            )
        )


    return result



# --------------------------------------------------
# Format Labels
# --------------------------------------------------

def format_labels(
    self,
    labels: dict[str, str] | None = None,
) -> str:
    """
    Convert labels to Prometheus format.

    Example:

    {
        node="edge01",
        gpu="0"
    }
    """

    merged = self.merge_labels(
        self._labels,
        labels or {},
    )


    if not merged:

        return ""


    values = [

        f'{key}="{value}"'

        for key, value
        in merged.items()

    ]


    return (
        "{"
        +
        ",".join(values)
        +
        "}"
    )
# ==================================================
# Part 5. Collection API
# ==================================================


# --------------------------------------------------
# Initialize Collection
# --------------------------------------------------

def _init_collection(
    self,
) -> None:
    """
    Initialize metric collection storage.
    """

    self._metrics = []



# --------------------------------------------------
# Add Metric
# --------------------------------------------------

def add_metric(
    self,
    metric: Any,
) -> "PrometheusExporter":
    """
    Add metric into collection.
    """

    with self._lock:

        self._metrics.append(
            metric
        )


    return self



# --------------------------------------------------
# Collect One
# --------------------------------------------------

def collect_one(
    self,
    metric: Any,
) -> dict[str, Any]:
    """
    Normalize single metric.

    Returns internal representation.
    """

    if isinstance(
        metric,
        dict,
    ):

        return {

            "name":
                metric.get(
                    "name",
                    "unknown",
                ),

            "value":
                metric.get(
                    "value",
                    0,
                ),

            "labels":
                metric.get(
                    "labels",
                    {},
                ),

            "timestamp":
                metric.get(
                    "timestamp"
                ),

        }



    return {

        "name":
            getattr(
                metric,
                "name",
                "unknown",
            ),

        "value":
            getattr(
                metric,
                "value",
                metric,
            ),

        "labels":
            getattr(
                metric,
                "labels",
                {},
            ),

        "timestamp":
            getattr(
                metric,
                "timestamp",
                None,
            ),

    }



# --------------------------------------------------
# Collect Many
# --------------------------------------------------

def collect_many(
    self,
    metrics,
) -> list[dict[str, Any]]:
    """
    Normalize metric batch.
    """

    return [

        self.collect_one(
            metric
        )

        for metric in metrics

    ]



# --------------------------------------------------
# Collect
# --------------------------------------------------

def collect(
    self,
    source=None,
) -> list[dict[str, Any]]:
    """
    Collect metrics.

    Source can be:
    - list
    - registry
    - collector
    - None
    """

    with self._lock:


        if source is None:

            data = self._metrics


        elif isinstance(
            source,
            list,
        ):

            data = source


        elif hasattr(
            source,
            "snapshot",
        ):

            data = source.snapshot()


        elif hasattr(
            source,
            "metrics",
        ):

            data = source.metrics


        else:

            data = []


        return self.collect_many(
            data
        )



# --------------------------------------------------
# Clear Collection
# --------------------------------------------------

def clear(
    self,
) -> None:
    """
    Remove collected metrics.
    """

    with self._lock:

        self._metrics.clear()



# --------------------------------------------------
# Collection Snapshot
# --------------------------------------------------

def collection_snapshot(
    self,
) -> dict[str, Any]:
    """
    Return collection state.
    """

    with self._lock:

        return {

            "count":
                len(
                    self._metrics
                ),

            "metrics":
                self.collect(),

        }
# ==================================================
# Part 6. Export API
# ==================================================


# --------------------------------------------------
# Export Single Metric
# --------------------------------------------------

def export_metric(
    self,
    metric: dict[str, Any],
) -> str:
    """
    Export single normalized metric.

    Returns:
        Prometheus sample line
    """

    if not self._enabled:

        return ""


    try:

        return self.format_sample(

            metric.get(
                "name",
                "unknown",
            ),

            metric.get(
                "value",
                0,
            ),

            labels=metric.get(
                "labels",
                {},
            ),

            timestamp=metric.get(
                "timestamp"
            ),

        )


    except Exception:

        self._error_count += 1

        return ""



# --------------------------------------------------
# Export Batch
# --------------------------------------------------

def export_batch(
    self,
    metrics: list[dict[str, Any]],
) -> str:
    """
    Export multiple metrics.
    """

    if not self._enabled:

        return ""


    lines = []


    for metric in metrics:

        line = self.export_metric(
            metric
        )

        if line:

            lines.append(
                line
            )


    return "\n".join(
        lines
    )



# --------------------------------------------------
# Export All
# --------------------------------------------------

def export(
    self,
    source=None,
) -> str:
    """
    Collect and export metrics.

    Main public API.
    """

    with self._lock:

        metrics = self.collect(
            source
        )


        payload = self.export_batch(
            metrics
        )


        self._export_count += 1


        self._last_payload = payload


        return payload



# --------------------------------------------------
# Flush
# --------------------------------------------------

def flush(
    self,
) -> str:
    """
    Export current buffer
    and clear collection.
    """

    with self._lock:

        payload = self.export()


        self.clear()


        return payload



# --------------------------------------------------
# Push
# --------------------------------------------------

def push(
    self,
    endpoint: str,
) -> dict[str, Any]:
    """
    Push payload to remote endpoint.

    Placeholder for:
    - HTTP push
    - remote write
    - gateway
    """

    payload = self.export()


    return {

        "endpoint":
            endpoint,

        "size":
            len(payload),

        "payload":
            payload,

        "status":
            "prepared",

    }
# ==================================================
# Part 7. Text API
# ==================================================


# --------------------------------------------------
# Content Type
# --------------------------------------------------

def content_type(
    self,
) -> str:
    """
    Prometheus exposition content type.
    """

    return (
        "text/plain; "
        "version=0.0.4"
    )



# --------------------------------------------------
# Headers
# --------------------------------------------------

def headers(
    self,
) -> dict[str, str]:
    """
    HTTP headers for /metrics endpoint.
    """

    return {

        "Content-Type":
            self.content_type()

    }



# --------------------------------------------------
# Format HELP
# --------------------------------------------------

def format_help(
    self,
    name: str,
    description: str,
) -> str:
    """
    Generate HELP line.

    Example:

    # HELP scios_cpu CPU usage
    """

    metric_name = self.format_name(
        self.normalize_metric(name)
    )


    return (
        f"# HELP "
        f"{metric_name} "
        f"{description}"
    )



# --------------------------------------------------
# Format TYPE
# --------------------------------------------------

def format_type(
    self,
    name: str,
    metric_type: str = "gauge",
) -> str:
    """
    Generate TYPE line.

    Example:

    # TYPE scios_cpu gauge
    """

    metric_name = self.format_name(
        self.normalize_metric(name)
    )


    return (
        f"# TYPE "
        f"{metric_name} "
        f"{metric_type}"
    )



# --------------------------------------------------
# Render Metric
# --------------------------------------------------

def render(
    self,
    metric: dict[str, Any],
) -> str:
    """
    Render full metric block.

    Includes:
    - HELP
    - TYPE
    - SAMPLE
    """

    name = metric.get(
        "name",
        "unknown",
    )


    description = metric.get(
        "description",
        name,
    )


    metric_type = metric.get(
        "type",
        "gauge",
    )


    sample = self.format_sample(
        name,

        metric.get(
            "value",
            0,
        ),

        labels=metric.get(
            "labels",
            {},
        ),

        timestamp=metric.get(
            "timestamp"
        ),
    )


    return "\n".join(
        [
            self.format_help(
                name,
                description,
            ),

            self.format_type(
                name,
                metric_type,
            ),

            sample,
        ]
    )



# --------------------------------------------------
# Generate Text
# --------------------------------------------------

def generate_text(
    self,
    metrics=None,
) -> str:
    """
    Generate complete Prometheus text.

    Used by:
    /metrics endpoint
    """

    if metrics is None:

        metrics = self.collect()



    blocks = []


    for metric in metrics:

        blocks.append(
            self.render(
                metric
            )
        )


    return (
        "\n\n".join(
            blocks
        )
        +
        "\n"
    )
# --------------------------------------------------
# Create Snapshot
# --------------------------------------------------

def snapshot(
    self,
) -> dict[str, Any]:
    """
    Create exporter state snapshot.
    """

    with self._lock:

        return {

            "name":
                self._name,

            "version":
                self._version,

            "namespace":
                self._namespace,

            "subsystem":
                self._subsystem,

            "enabled":
                self._enabled,

            "labels":
                dict(
                    self._labels
                ),

            "metrics":
                copy.deepcopy(
                    self._metrics
                ),

            "statistics": {

                "exports":
                    self._export_count,

                "errors":
                    self._error_count,

            },

        }



# --------------------------------------------------
# Restore Snapshot
# --------------------------------------------------

def restore(
    self,
    state: dict[str, Any],
) -> "PrometheusExporter":
    """
    Restore exporter state.
    """

    with self._lock:

        self._namespace = (
            state.get(
                "namespace",
                "scios",
            )
        )


        self._subsystem = (
            state.get(
                "subsystem"
            )
        )


        self._enabled = (
            state.get(
                "enabled",
                True,
            )
        )


        self._labels = dict(
            state.get(
                "labels",
                {},
            )
        )


        self._metrics = copy.deepcopy(
            state.get(
                "metrics",
                [],
            )
        )


        statistics = state.get(
            "statistics",
            {},
        )


        self._export_count = (
            statistics.get(
                "exports",
                0,
            )
        )


        self._error_count = (
            statistics.get(
                "errors",
                0,
            )
        )


    return self



# --------------------------------------------------
# Save Snapshot
# --------------------------------------------------

def save_snapshot(
    self,
    path: str | Path,
) -> Path:
    """
    Save snapshot to JSON file.
    """

    file_path = Path(
        path
    )


    file_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )


    file_path.write_text(

        json.dumps(
            self.snapshot(),
            indent=2,
            default=str,
        ),

        encoding="utf-8",
    )


    return file_path



# --------------------------------------------------
# Load Snapshot
# --------------------------------------------------

def load_snapshot(
    self,
    path: str | Path,
) -> "PrometheusExporter":
    """
    Load snapshot from JSON.
    """

    file_path = Path(
        path
    )


    state = json.loads(

        file_path.read_text(
            encoding="utf-8"
        )

    )


    return self.restore(
        state
    )



# --------------------------------------------------
# Clone
# --------------------------------------------------

def clone(
    self,
) -> "PrometheusExporter":
    """
    Clone exporter instance.
    """

    new_exporter = (
        PrometheusExporter(
            namespace=self._namespace,
            subsystem=self._subsystem,
        )
    )


    new_exporter.restore(
        self.snapshot()
    )


    return new_exporter



# --------------------------------------------------
# Copy State
# --------------------------------------------------

def copy_state(
    self,
) -> dict[str, Any]:
    """
    Return independent state copy.
    """

    return copy.deepcopy(
        self.snapshot()
    )    
# ==================================================
# Part 9. Debug Helpers
# ==================================================


# --------------------------------------------------
# Info
# --------------------------------------------------

def info(
    self,
) -> dict[str, Any]:
    """
    Exporter identity information.
    """

    return {

        "name":
            self._name,

        "version":
            self._version,

        "format":
            self.FORMAT,

        "namespace":
            self._namespace,

        "subsystem":
            self._subsystem,

        "enabled":
            self._enabled,

    }



# --------------------------------------------------
# Statistics
# --------------------------------------------------

def stats(
    self,
) -> dict[str, Any]:
    """
    Runtime statistics.
    """

    with self._lock:

        return {

            "export_count":
                self._export_count,

            "error_count":
                self._error_count,

            "metric_count":
                len(
                    self._metrics
                ),

            "label_count":
                len(
                    self._labels
                ),

        }



# --------------------------------------------------
# Summary
# --------------------------------------------------

def summary(
    self,
) -> dict[str, Any]:
    """
    Human readable summary.
    """

    return {

        "info":
            self.info(),

        "stats":
            self.stats(),

    }



# --------------------------------------------------
# Health Check
# --------------------------------------------------

def health(
    self,
) -> dict[str, Any]:
    """
    Exporter health status.
    """

    with self._lock:

        healthy = (
            self._error_count == 0
            and self._enabled
        )


        return {

            "status":
                (
                    "healthy"
                    if healthy
                    else "degraded"
                ),

            "enabled":
                self._enabled,

            "errors":
                self._error_count,

        }



# --------------------------------------------------
# Dump
# --------------------------------------------------

def dump(
    self,
) -> dict[str, Any]:
    """
    Full debug dump.
    """

    return {

        "info":
            self.info(),

        "stats":
            self.stats(),

        "health":
            self.health(),

        "snapshot":
            self.snapshot(),

    }



# --------------------------------------------------
# Diagnostics
# --------------------------------------------------

def diagnostics(
    self,
) -> dict[str, Any]:
    """
    Runtime diagnostics.
    """

    return {

        "summary":
            self.summary(),

        "health":
            self.health(),

        "collection":

            {
                "metrics":
                    len(
                        self._metrics
                    ),

                "labels":
                    self._labels,

            },

        "last_export":
            self._last_export,

        "last_payload_size":
            (
                len(
                    self._last_payload
                )
                if self._last_payload
                else 0
            ),

    }



# --------------------------------------------------
# Reset Statistics
# --------------------------------------------------

def reset_stats(
    self,
) -> None:
    """
    Reset runtime counters.
    """

    with self._lock:

        self._export_count = 0

        self._error_count = 0
# ==================================================
# Part 10. Thread Safety
# ==================================================


# --------------------------------------------------
# Acquire Lock
# --------------------------------------------------

def acquire(
    self,
    blocking: bool = True,
) -> bool:
    """
    Acquire exporter lock.
    """

    return self._lock.acquire(
        blocking
    )



# --------------------------------------------------
# Release Lock
# --------------------------------------------------

def release(
    self,
) -> None:
    """
    Release exporter lock.
    """

    self._lock.release()



# --------------------------------------------------
# Context Lock
# --------------------------------------------------

@contextmanager
def locked(
    self,
):
    """
    Context manager lock.

    Example:

        with exporter.locked():
            exporter.export()
    """

    self.acquire()

    try:

        yield self


    finally:

        self.release()



# --------------------------------------------------
# Synchronized Wrapper
# --------------------------------------------------

def synchronized(
    self,
    func,
):
    """
    Decorator for thread-safe methods.
    """

    def wrapper(
        *args,
        **kwargs,
    ):

        with self.locked():

            return func(
                *args,
                **kwargs,
            )


    return wrapper



# --------------------------------------------------
# Safe Export
# --------------------------------------------------

def safe_export(
    self,
    source=None,
) -> str:
    """
    Thread-safe export.
    """

    with self.lock:

        try:

            return self.export(
                source
            )


        except Exception:

            self._error_count += 1

            return ""



# --------------------------------------------------
# Safe Snapshot
# --------------------------------------------------

def safe_snapshot(
    self,
) -> dict[str, Any]:
    """
    Thread-safe snapshot.
    """

    with self.lock:

        return self.snapshot()



# --------------------------------------------------
# Thread Information
# --------------------------------------------------

def thread_info(
    self,
) -> dict[str, Any]:
    """
    Current thread diagnostics.
    """

    current = (
        threading.current_thread()
    )


    return {

        "thread_name":
            current.name,

        "thread_id":
            current.ident,

        "daemon":
            current.daemon,

    }



# --------------------------------------------------
# Lock Status
# --------------------------------------------------

def lock_status(
    self,
) -> dict[str, Any]:
    """
    Lock diagnostics.

    Note:
    Python RLock does not expose
    public locked state in all versions.
    """

    return {

        "lock_type":
            type(
                self._lock
            ).__name__,

        "thread":
            self.thread_info(),

    }