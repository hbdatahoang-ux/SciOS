from __future__ import annotations

import uuid
import time
import copy
import threading

from typing import Any
from pathlib import Path
from contextlib import contextmanager


class OpenTelemetryExporter:
    """
    SciOS-NG OpenTelemetry Exporter.

    Provides:
    - Resource management
    - Attributes
    - Metrics collection
    - OTLP compatible payload
    """


    VERSION = "0.1.0"

    FORMAT = "opentelemetry"


    # ==============================================
    # Constructor
    # ==============================================

    def __init__(
        self,
        *,
        service_name: str = "scios",
        service_version: str = "0.1.0",
    ):

        self._id = str(
            uuid.uuid4()
        )


        self._name = (
            "OpenTelemetryExporter"
        )


        self._version = (
            self.VERSION
        )


        self._service_name = (
            service_name
        )


        self._service_version = (
            service_version
        )


        self._enabled = True


        self._created_at = (
            time.time()
        )


        self._lock = (
            threading.RLock()
        )


        self._metrics = []


        self._attributes = {}


        self._resource = {

            "service.name":
                service_name,

            "service.version":
                service_version,

        }


        self._export_count = 0


        self._error_count = 0


        self._last_payload = None



    # ==============================================
    # UUID API
    # ==============================================

    @property
    def id(
        self,
    ) -> str:
        """
        Exporter UUID.
        """

        return self._id



    # ==============================================
    # Composition
    # ==============================================

    def __repr__(
        self,
    ) -> str:

        return (
            f"<{self._name} "
            f"id={self._id} "
            f"enabled={self._enabled}>"
        )
# ==============================================
# Part 2. Configuration API
# ==============================================


# --------------------------------------------------
# Configure
# --------------------------------------------------

def configure(
    self,
    *,
    service_name: str | None = None,
    service_version: str | None = None,
    enabled: bool | None = None,
) -> "OpenTelemetryExporter":
    """
    Update exporter configuration.
    """

    with self._lock:

        if service_name is not None:

            self._service_name = (
                service_name
            )


            self._resource[
                "service.name"
            ] = service_name



        if service_version is not None:

            self._service_version = (
                service_version
            )


            self._resource[
                "service.version"
            ] = service_version



        if enabled is not None:

            self._enabled = enabled


    return self



# --------------------------------------------------
# Set Service Name
# --------------------------------------------------

def set_service_name(
    self,
    name: str,
) -> "OpenTelemetryExporter":
    """
    Change service identity.
    """

    with self._lock:

        self._service_name = name

        self._resource[
            "service.name"
        ] = name


    return self



# --------------------------------------------------
# Set Service Version
# --------------------------------------------------

def set_service_version(
    self,
    version: str,
) -> "OpenTelemetryExporter":
    """
    Change service version.
    """

    with self._lock:

        self._service_version = version

        self._resource[
            "service.version"
        ] = version


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
# Config Snapshot
# --------------------------------------------------

def config(
    self,
) -> dict[str, Any]:
    """
    Current exporter configuration.
    """

    with self._lock:

        return {

            "id":
                self._id,

            "name":
                self._name,

            "version":
                self._version,

            "format":
                self.FORMAT,

            "service_name":
                self._service_name,

            "service_version":
                self._service_version,

            "enabled":
                self._enabled,

        }



# --------------------------------------------------
# Reset Config
# --------------------------------------------------

def reset_config(
    self,
) -> None:
    """
    Restore default configuration.
    """

    with self._lock:

        self._service_name = "scios"

        self._service_version = "0.1.0"

        self._enabled = True


        self._resource = {

            "service.name":
                "scios",

            "service.version":
                "0.1.0",

        }
# ==============================================
# Part 3. Resource API
# ==============================================


# --------------------------------------------------
# Set Resource
# --------------------------------------------------

def set_resource(
    self,
    resource: dict[str, Any],
) -> "OpenTelemetryExporter":
    """
    Replace entire resource.
    """

    with self._lock:

        self._resource = (
            self.normalize_resource(
                resource
            )
        )


    return self



# --------------------------------------------------
# Add Resource
# --------------------------------------------------

def add_resource(
    self,
    key: str,
    value: Any,
) -> "OpenTelemetryExporter":
    """
    Add single resource attribute.
    """

    with self._lock:

        self._resource[
            self.normalize_resource_key(
                key
            )
        ] = value


    return self



# --------------------------------------------------
# Remove Resource
# --------------------------------------------------

def remove_resource(
    self,
    key: str,
) -> None:
    """
    Remove resource field.
    """

    with self._lock:

        self._resource.pop(
            self.normalize_resource_key(
                key
            ),
            None,
        )



# --------------------------------------------------
# Get Resource
# --------------------------------------------------

def get_resource(
    self,
    key: str,
    default=None,
):
    """
    Get resource value.
    """

    return self._resource.get(
        self.normalize_resource_key(
            key
        ),
        default,
    )



# --------------------------------------------------
# Resource Snapshot
# --------------------------------------------------

def resource(
    self,
) -> dict[str, Any]:
    """
    Return current resource.
    """

    with self._lock:

        return dict(
            self._resource
        )



# --------------------------------------------------
# Merge Resource
# --------------------------------------------------

def merge_resource(
    self,
    resource: dict[str, Any],
) -> "OpenTelemetryExporter":
    """
    Merge resource fields.
    """

    with self._lock:

        self._resource.update(
            self.normalize_resource(
                resource
            )
        )


    return self



# --------------------------------------------------
# Clear Resource
# --------------------------------------------------

def clear_resource(
    self,
) -> None:
    """
    Remove custom resources.
    Keep service identity.
    """

    with self._lock:

        self._resource = {

            "service.name":
                self._service_name,

            "service.version":
                self._service_version,

        }



# --------------------------------------------------
# Normalize Resource Key
# --------------------------------------------------

def normalize_resource_key(
    self,
    key: str,
) -> str:
    """
    Normalize resource key.

    Example:

        Node-ID

    becomes:

        node.id
    """

    return (
        key
        .strip()
        .lower()
        .replace(
            "-",
            ".",
        )
        .replace(
            "_",
            ".",
        )
        .replace(
            " ",
            ".",
        )
    )



# --------------------------------------------------
# Normalize Resource
# --------------------------------------------------

def normalize_resource(
    self,
    resource: dict[str, Any],
) -> dict[str, Any]:
    """
    Normalize resource dictionary.
    """

    return {

        self.normalize_resource_key(
            key
        ):
            value

        for key, value
        in resource.items()

    }
# ==============================================
# Part 4. Attributes API
# ==============================================


# --------------------------------------------------
# Set Attributes
# --------------------------------------------------

def set_attributes(
    self,
    attributes: dict[str, Any],
) -> "OpenTelemetryExporter":
    """
    Replace exporter attributes.
    """

    with self._lock:

        self._attributes = (
            self.normalize_attributes(
                attributes
            )
        )


    return self



# --------------------------------------------------
# Add Attribute
# --------------------------------------------------

def add_attribute(
    self,
    key: str,
    value: Any,
) -> "OpenTelemetryExporter":
    """
    Add single attribute.
    """

    with self._lock:

        self._attributes[
            self.normalize_attribute_key(
                key
            )
        ] = value


    return self



# --------------------------------------------------
# Remove Attribute
# --------------------------------------------------

def remove_attribute(
    self,
    key: str,
) -> None:
    """
    Remove attribute.
    """

    with self._lock:

        self._attributes.pop(
            self.normalize_attribute_key(
                key
            ),
            None,
        )



# --------------------------------------------------
# Get Attribute
# --------------------------------------------------

def get_attribute(
    self,
    key: str,
    default=None,
):
    """
    Read attribute.
    """

    return self._attributes.get(
        self.normalize_attribute_key(
            key
        ),
        default,
    )



# --------------------------------------------------
# Attribute Snapshot
# --------------------------------------------------

def attributes(
    self,
) -> dict[str, Any]:
    """
    Return attributes.
    """

    with self._lock:

        return dict(
            self._attributes
        )



# --------------------------------------------------
# Merge Attributes
# --------------------------------------------------

def merge_attributes(
    self,
    attributes: dict[str, Any],
) -> "OpenTelemetryExporter":
    """
    Merge attributes.
    """

    with self._lock:

        self._attributes.update(
            self.normalize_attributes(
                attributes
            )
        )


    return self



# --------------------------------------------------
# Clear Attributes
# --------------------------------------------------

def clear_attributes(
    self,
) -> None:
    """
    Remove all attributes.
    """

    with self._lock:

        self._attributes.clear()



# --------------------------------------------------
# Normalize Attribute Key
# --------------------------------------------------

def normalize_attribute_key(
    self,
    key: str,
) -> str:
    """
    Normalize attribute key.

    Example:

        GPU-ID

    becomes:

        gpu.id
    """

    return (
        key
        .strip()
        .lower()
        .replace(
            "-",
            ".",
        )
        .replace(
            "_",
            ".",
        )
        .replace(
            " ",
            ".",
        )
    )



# --------------------------------------------------
# Normalize Attributes
# --------------------------------------------------

def normalize_attributes(
    self,
    attributes: dict[str, Any],
) -> dict[str, Any]:
    """
    Normalize attributes map.
    """

    return {

        self.normalize_attribute_key(
            key
        ):
            value

        for key, value
        in attributes.items()

    }
# ==============================================
# Part 5. Metric API
# ==============================================


# --------------------------------------------------
# Add Metric
# --------------------------------------------------

def add_metric(
    self,
    metric: dict[str, Any],
) -> "OpenTelemetryExporter":
    """
    Add telemetry metric record.
    """

    with self._lock:

        item = {

            "name":
                metric.get(
                    "name",
                    "unknown",
                ),

            "type":
                metric.get(
                    "type",
                    "gauge",
                ),

            "value":
                metric.get(
                    "value",
                    0,
                ),

            "attributes":
                self.merge_attributes(
                    metric.get(
                        "attributes",
                        {},
                    )
                ),

            "timestamp":
                metric.get(
                    "timestamp",
                    time.time(),
                ),

        }


        self._metrics.append(
            item
        )


    return self



# --------------------------------------------------
# Record Metric
# --------------------------------------------------

def record_metric(
    self,
    name: str,
    value: Any,
    metric_type: str = "gauge",
    attributes: dict[str, Any] | None = None,
) -> "OpenTelemetryExporter":
    """
    Record generic metric.
    """

    return self.add_metric(
        {

            "name":
                name,

            "type":
                metric_type,

            "value":
                value,

            "attributes":
                attributes or {},

        }
    )



# --------------------------------------------------
# Gauge
# --------------------------------------------------

def gauge(
    self,
    name: str,
    value: float,
    attributes: dict[str, Any] | None = None,
):
    """
    Record gauge metric.

    Example:
        cpu_usage = 75
    """

    return self.record_metric(

        name,

        value,

        metric_type="gauge",

        attributes=attributes,

    )



# --------------------------------------------------
# Counter
# --------------------------------------------------

def counter(
    self,
    name: str,
    value: int = 1,
    attributes: dict[str, Any] | None = None,
):
    """
    Record counter metric.
    """

    return self.record_metric(

        name,

        value,

        metric_type="counter",

        attributes=attributes,

    )



# --------------------------------------------------
# Histogram
# --------------------------------------------------

def histogram(
    self,
    name: str,
    value: float,
    attributes: dict[str, Any] | None = None,
):
    """
    Record histogram value.
    """

    return self.record_metric(

        name,

        value,

        metric_type="histogram",

        attributes=attributes,

    )



# --------------------------------------------------
# Get Metric
# --------------------------------------------------

def get_metric(
    self,
    name: str,
) -> list[dict[str, Any]]:
    """
    Query metrics by name.
    """

    with self._lock:

        return [

            metric

            for metric
            in self._metrics

            if metric["name"] == name

        ]



# --------------------------------------------------
# Metrics Snapshot
# --------------------------------------------------

def metrics(
    self,
) -> list[dict[str, Any]]:
    """
    Return all metrics.
    """

    with self._lock:

        return copy.deepcopy(
            self._metrics
        )



# --------------------------------------------------
# Clear Metrics
# --------------------------------------------------

def clear_metrics(
    self,
) -> None:
    """
    Remove all metrics.
    """

    with self._lock:

        self._metrics.clear()



# --------------------------------------------------
# Metric Snapshot
# --------------------------------------------------

def metric_snapshot(
    self,
) -> dict[str, Any]:
    """
    Metric state snapshot.
    """

    with self._lock:

        return {

            "count":
                len(
                    self._metrics
                ),

            "metrics":
                copy.deepcopy(
                    self._metrics
                ),

        }
# ==============================================
# Part 6. Export API
# ==============================================


# --------------------------------------------------
# Export Single Metric
# --------------------------------------------------

def export_metric(
    self,
    metric: dict[str, Any],
) -> dict[str, Any]:
    """
    Convert metric into OTLP record.
    """

    return {

        "name":
            metric.get(
                "name",
                "unknown",
            ),

        "type":
            metric.get(
                "type",
                "gauge",
            ),

        "value":
            metric.get(
                "value",
                0,
            ),

        "attributes":
            self.merge_attributes(
                metric.get(
                    "attributes",
                    {},
                )
            ),

        "timestamp":
            metric.get(
                "timestamp",
                time.time(),
            ),

    }



# --------------------------------------------------
# Export Batch
# --------------------------------------------------

def export_batch(
    self,
    metrics: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Convert metric batch.
    """

    return [

        self.export_metric(
            metric
        )

        for metric in metrics

    ]



# --------------------------------------------------
# Build Payload
# --------------------------------------------------

def build_payload(
    self,
    metrics=None,
) -> dict[str, Any]:
    """
    Build OpenTelemetry payload.
    """

    if metrics is None:

        metrics = self.metrics()



    return {

        "resource":
            self.resource(),


        "scope": {

            "name":
                self._name,

            "version":
                self._version,

        },


        "metrics":
            self.export_batch(
                metrics
            ),

    }



# --------------------------------------------------
# Export
# --------------------------------------------------

def export(
    self,
) -> dict[str, Any]:
    """
    Main export API.
    """

    if not self._enabled:

        return {}


    with self._lock:

        payload = (
            self.build_payload()
        )


        self._export_count += 1


        self._last_payload = payload


        return payload



# --------------------------------------------------
# Flush
# --------------------------------------------------

def flush(
    self,
) -> dict[str, Any]:
    """
    Export and clear metrics.
    """

    with self._lock:

        payload = self.export()

        self.clear_metrics()


        return payload



# --------------------------------------------------
# Push
# --------------------------------------------------

def push(
    self,
    endpoint: str,
) -> dict[str, Any]:
    """
    Prepare OTLP push request.

    HTTP transport is delegated
    to collector layer.
    """

    payload = self.export()


    return {

        "endpoint":
            endpoint,

        "status":
            "prepared",

        "metric_count":
            len(
                payload.get(
                    "metrics",
                    []
                )
            ),

        "payload":
            payload,

    }
# ==============================================
# Part 7. Batch API
# ==============================================


# --------------------------------------------------
# Create Batch
# --------------------------------------------------

def create_batch(
    self,
    name: str = "default",
) -> "OpenTelemetryExporter":
    """
    Create metric batch.
    """

    with self._lock:

        if name not in self._batches:

            self._batches[name] = []


    return self



# --------------------------------------------------
# Add To Batch
# --------------------------------------------------

def add_to_batch(
    self,
    metric: dict[str, Any],
    batch: str = "default",
) -> "OpenTelemetryExporter":
    """
    Add metric to batch buffer.
    """

    with self._lock:

        if batch not in self._batches:

            self._batches[batch] = []


        self._batches[batch].append(
            self.export_metric(
                metric
            )
        )


    return self



# --------------------------------------------------
# Add Current Metrics To Batch
# --------------------------------------------------

def collect_to_batch(
    self,
    batch: str = "default",
) -> "OpenTelemetryExporter":
    """
    Move current metrics into batch.
    """

    with self._lock:

        for metric in self._metrics:

            self.add_to_batch(
                metric,
                batch,
            )


    return self



# --------------------------------------------------
# Get Batch
# --------------------------------------------------

def get_batch(
    self,
    name: str = "default",
) -> list[dict[str, Any]]:
    """
    Read batch content.
    """

    with self._lock:

        return list(
            self._batches.get(
                name,
                [],
            )
        )



# --------------------------------------------------
# Batch Size
# --------------------------------------------------

def batch_size(
    self,
    name: str = "default",
) -> int:
    """
    Return batch length.
    """

    return len(
        self._batches.get(
            name,
            [],
        )
    )



# --------------------------------------------------
# Export Batch Buffer
# --------------------------------------------------

def export_batch_buffer(
    self,
    name: str = "default",
) -> dict[str, Any]:
    """
    Export existing batch.
    """

    with self._lock:

        metrics = (
            self.get_batch(
                name
            )
        )


        return {

            "resource":
                self.resource(),

            "metrics":
                metrics,

            "batch":
                name,

            "size":
                len(metrics),

        }



# --------------------------------------------------
# Flush Batch
# --------------------------------------------------

def flush_batch(
    self,
    name: str = "default",
) -> dict[str, Any]:
    """
    Export and clear batch.
    """

    with self._lock:

        payload = (
            self.export_batch_buffer(
                name
            )
        )


        self._batches[name] = []


        self._export_count += 1


        return payload



# --------------------------------------------------
# Remove Batch
# --------------------------------------------------

def remove_batch(
    self,
    name: str,
) -> None:
    """
    Delete batch buffer.
    """

    with self._lock:

        self._batches.pop(
            name,
            None,
        )



# --------------------------------------------------
# Clear All Batches
# --------------------------------------------------

def clear_batches(
    self,
) -> None:
    """
    Clear all batch buffers.
    """

    with self._lock:

        self._batches.clear()



# --------------------------------------------------
# Batch Snapshot
# --------------------------------------------------

def batch_snapshot(
    self,
) -> dict[str, Any]:
    """
    Snapshot batch state.
    """

    with self._lock:

        return {

            name:
                list(metrics)

            for name, metrics
            in self._batches.items()

        }
# ==============================================
# Part 8. Snapshot API
# ==============================================


# --------------------------------------------------
# Create Snapshot
# --------------------------------------------------

def snapshot(
    self,
) -> dict[str, Any]:
    """
    Create full exporter snapshot.
    """

    with self._lock:

        return {

            "version":
                self.VERSION,


            "id":
                self._id,


            "configuration":
                self.config(),


            "resource":
                self.resource(),


            "attributes":
                self.attributes(),


            "metrics":
                copy.deepcopy(
                    self._metrics
                ),


            "batches":
                copy.deepcopy(
                    self._batches
                ),


            "statistics":
            {

                "export_count":
                    self._export_count,


                "error_count":
                    self._error_count,

            },


            "created_at":
                self._created_at,


        }



# --------------------------------------------------
# Restore Snapshot
# --------------------------------------------------

def restore(
    self,
    state: dict[str, Any],
) -> "OpenTelemetryExporter":
    """
    Restore exporter state.
    """

    with self._lock:

        config = (
            state.get(
                "configuration",
                {}
            )
        )


        self.configure(

            service_name =
                config.get(
                    "service_name",
                    self._service_name,
                ),

            service_version =
                config.get(
                    "service_version",
                    self._service_version,
                ),

            enabled =
                config.get(
                    "enabled",
                    True,
                ),

        )


        self._resource = (
            copy.deepcopy(
                state.get(
                    "resource",
                    {}
                )
            )
        )


        self._attributes = (
            copy.deepcopy(
                state.get(
                    "attributes",
                    {}
                )
            )
        )


        self._metrics = (
            copy.deepcopy(
                state.get(
                    "metrics",
                    []
                )
            )
        )


        self._batches = (
            copy.deepcopy(
                state.get(
                    "batches",
                    {}
                )
            )
        )


        stats = (
            state.get(
                "statistics",
                {}
            )
        )


        self._export_count = (
            stats.get(
                "export_count",
                0,
            )
        )


        self._error_count = (
            stats.get(
                "error_count",
                0,
            )
        )


    return self



# --------------------------------------------------
# Clone
# --------------------------------------------------

def clone(
    self,
) -> "OpenTelemetryExporter":
    """
    Create independent exporter copy.
    """

    new = (
        OpenTelemetryExporter(
            service_name=
                self._service_name,

            service_version=
                self._service_version,

        )
    )


    new.restore(
        self.snapshot()
    )


    return new



# --------------------------------------------------
# Copy State
# --------------------------------------------------

def copy(
    self,
) -> dict[str, Any]:
    """
    Return detached state copy.
    """

    return copy.deepcopy(
        self.snapshot()
    )



# --------------------------------------------------
# Save Snapshot
# --------------------------------------------------

def save_snapshot(
    self,
    path: str | Path,
) -> None:
    """
    Save snapshot JSON file.
    """

    state = self.snapshot()


    Path(
        path
    ).write_text(
        json.dumps(
            state,
            indent=2,
        ),
        encoding="utf-8",
    )



# --------------------------------------------------
# Load Snapshot
# --------------------------------------------------

def load_snapshot(
    self,
    path: str | Path,
) -> "OpenTelemetryExporter":
    """
    Load snapshot JSON file.
    """

    data = json.loads(

        Path(
            path
        )
        .read_text(
            encoding="utf-8"
        )

    )


    return self.restore(
        data
    )



# --------------------------------------------------
# Clear Snapshot State
# --------------------------------------------------

def clear_snapshot(
    self,
) -> None:
    """
    Remove runtime telemetry state.
    """

    with self._lock:

        self._metrics.clear()

        self._batches.clear()

        self._attributes.clear()



# --------------------------------------------------
# Snapshot Info
# --------------------------------------------------

def snapshot_info(
    self,
) -> dict[str, Any]:
    """
    Snapshot metadata.
    """

    state = self.snapshot()


    return {

        "version":
            state["version"],


        "metrics":
            len(
                state["metrics"]
            ),


        "batches":
            len(
                state["batches"]
            ),


        "attributes":
            len(
                state["attributes"]
            ),

    }
# ==============================================
# Part 9. Debug Helpers
# ==============================================


# --------------------------------------------------
# Info
# --------------------------------------------------

def info(
    self,
) -> dict[str, Any]:
    """
    Exporter information.
    """

    with self._lock:

        return {

            "name":
                self._name,


            "id":
                self._id,


            "version":
                self._version,


            "format":
                self.FORMAT,


            "service_name":
                self._service_name,


            "service_version":
                self._service_version,


            "enabled":
                self._enabled,


            "created_at":
                self._created_at,

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

            "metrics":
                len(
                    self._metrics
                ),


            "batches":
                len(
                    self._batches
                ),


            "attributes":
                len(
                    self._attributes
                ),


            "exports":
                self._export_count,


            "errors":
                self._error_count,

        }



# --------------------------------------------------
# Health Check
# --------------------------------------------------

def health(
    self,
) -> dict[str, Any]:
    """
    Runtime health status.
    """

    with self._lock:

        healthy = (
            self._enabled
            and self._error_count == 0
        )


        return {

            "status":
                "healthy"
                if healthy
                else "degraded",


            "enabled":
                self._enabled,


            "metric_count":
                len(
                    self._metrics
                ),


            "error_count":
                self._error_count,

        }



# --------------------------------------------------
# Diagnostics
# --------------------------------------------------

def diagnostics(
    self,
) -> dict[str, Any]:
    """
    Full runtime diagnostics.
    """

    return {

        "info":
            self.info(),


        "stats":
            self.stats(),


        "health":
            self.health(),


        "resource":
            self.resource(),


        "attributes":
            self.attributes(),


        "batch":
            self.batch_snapshot(),

    }



# --------------------------------------------------
# Dump
# --------------------------------------------------

def dump(
    self,
) -> str:
    """
    Human readable debug dump.
    """

    data = self.diagnostics()


    return (
        "\n"
        "=== OpenTelemetryExporter ===\n"
        f"Service: "
        f"{data['info']['service_name']}\n"
        f"Enabled: "
        f"{data['info']['enabled']}\n"
        f"Metrics: "
        f"{data['stats']['metrics']}\n"
        f"Batches: "
        f"{data['stats']['batches']}\n"
        f"Errors: "
        f"{data['stats']['errors']}\n"
    )



# --------------------------------------------------
# Metric Summary
# --------------------------------------------------

def metric_summary(
    self,
) -> dict[str, Any]:
    """
    Summarize metric types.
    """

    summary = {}


    with self._lock:

        for metric in self._metrics:

            kind = (
                metric.get(
                    "type",
                    "unknown",
                )
            )


            summary[kind] = (
                summary.get(
                    kind,
                    0,
                )
                + 1
            )


    return summary



# --------------------------------------------------
# Reset Statistics
# --------------------------------------------------

def reset_stats(
    self,
) -> None:
    """
    Reset counters.
    """

    with self._lock:

        self._export_count = 0

        self._error_count = 0
# ==============================================
# Part 10. Thread Safety
# ==============================================


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
# Locked Context
# --------------------------------------------------

@contextmanager
def locked(
    self,
):
    """
    Thread-safe context.

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
# Synchronized Decorator
# --------------------------------------------------

def synchronized(
    self,
    func,
):
    """
    Decorator for synchronized execution.
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
# Safe Record Metric
# --------------------------------------------------

def safe_record_metric(
    self,
    name: str,
    value: Any,
    metric_type: str = "gauge",
    attributes=None,
):
    """
    Thread-safe metric recording.
    """

    with self.locked():

        return self.record_metric(
            name,
            value,
            metric_type,
            attributes,
        )



# --------------------------------------------------
# Safe Export
# --------------------------------------------------

def safe_export(
    self,
) -> dict[str, Any]:
    """
    Thread-safe export.
    """

    with self.locked():

        try:

            return self.export()


        except Exception:

            self._error_count += 1

            return {}



# --------------------------------------------------
# Safe Snapshot
# --------------------------------------------------

def safe_snapshot(
    self,
) -> dict[str, Any]:
    """
    Thread-safe snapshot.
    """

    with self.locked():

        return self.snapshot()



# --------------------------------------------------
# Thread Information
# --------------------------------------------------

def thread_info(
    self,
) -> dict[str, Any]:
    """
    Current thread metadata.
    """

    thread = (
        threading.current_thread()
    )


    return {

        "name":
            thread.name,


        "id":
            thread.ident,


        "daemon":
            thread.daemon,

    }



# --------------------------------------------------
# Lock Status
# --------------------------------------------------

def lock_status(
    self,
) -> dict[str, Any]:
    """
    Lock diagnostics.
    """

    return {

        "lock_type":
            type(
                self._lock
            ).__name__,


        "thread":
            self.thread_info(),

    }
                                                            