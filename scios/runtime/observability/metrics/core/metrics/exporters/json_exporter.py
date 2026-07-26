from __future__ import annotations

import uuid
import json
import time
import copy
import threading

from pathlib import Path
from typing import Any
from contextlib import contextmanager


class JSONExporter:
    """
    SciOS-NG JSON Metrics Exporter.

    Features:
    - JSON serialization
    - Metric export
    - Snapshot support
    - File persistence
    """


    VERSION = "0.1.0"

    FORMAT = "json"


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
            "JSONExporter"
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


        self._resource = {

            "service.name":
                service_name,

            "service.version":
                service_version,

        }


        self._attributes = {}


        self._metrics = []


        self._export_count = 0


        self._error_count = 0


        self._last_export = None



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
) -> "JSONExporter":
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
) -> "JSONExporter":
    """
    Update service name.
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
) -> "JSONExporter":
    """
    Update service version.
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
    Return configuration state.
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

        self._service_name = (
            "scios"
        )


        self._service_version = (
            "0.1.0"
        )


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
) -> "JSONExporter":
    """
    Replace resource metadata.
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
) -> "JSONExporter":
    """
    Add resource field.
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
    Read resource value.
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
    Return resource metadata.
    """

    with self._lock:

        return copy.deepcopy(
            self._resource
        )



# --------------------------------------------------
# Merge Resource
# --------------------------------------------------

def merge_resource(
    self,
    resource: dict[str, Any],
) -> "JSONExporter":
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
    Clear custom resource.

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
) -> "JSONExporter":
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
) -> "JSONExporter":
    """
    Add one attribute.
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
    Get attribute value.
    """

    return self._attributes.get(
        self.normalize_attribute_key(
            key
        ),
        default,
    )



# --------------------------------------------------
# Attributes Snapshot
# --------------------------------------------------

def attributes(
    self,
) -> dict[str, Any]:
    """
    Return attributes.
    """

    with self._lock:

        return copy.deepcopy(
            self._attributes
        )



# --------------------------------------------------
# Merge Attributes
# --------------------------------------------------

def merge_attributes(
    self,
    attributes: dict[str, Any],
) -> "JSONExporter":
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
    Clear attributes.
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
    Normalize attribute name.

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
    Normalize attribute dictionary.
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
# Part 5. Metric Formatting API
# ==============================================


# --------------------------------------------------
# Format Generic Metric
# --------------------------------------------------

def format_metric(
    self,
    name: str,
    value: Any,
    metric_type: str = "gauge",
    attributes: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Create normalized JSON metric.
    """

    return {

        "name":
            name,


        "type":
            metric_type,


        "value":
            value,


        "timestamp":
            time.time(),


        "attributes":
            self.normalize_attributes(
                attributes or {}
            ),

    }



# --------------------------------------------------
# Format Gauge
# --------------------------------------------------

def format_gauge(
    self,
    name: str,
    value: float,
    attributes=None,
) -> dict[str, Any]:
    """
    Format gauge metric.
    """

    return self.format_metric(

        name,

        value,

        metric_type="gauge",

        attributes=attributes,

    )



# --------------------------------------------------
# Format Counter
# --------------------------------------------------

def format_counter(
    self,
    name: str,
    value: int = 1,
    attributes=None,
) -> dict[str, Any]:
    """
    Format counter metric.
    """

    return self.format_metric(

        name,

        value,

        metric_type="counter",

        attributes=attributes,

    )



# --------------------------------------------------
# Format Histogram
# --------------------------------------------------

def format_histogram(
    self,
    name: str,
    value: float,
    attributes=None,
) -> dict[str, Any]:
    """
    Format histogram metric.
    """

    return self.format_metric(

        name,

        value,

        metric_type="histogram",

        attributes=attributes,

    )



# --------------------------------------------------
# Normalize Metric
# --------------------------------------------------

def normalize_metric(
    self,
    metric: dict[str, Any],
) -> dict[str, Any]:
    """
    Normalize metric dictionary.
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


        "timestamp":
            metric.get(
                "timestamp",
                time.time(),
            ),


        "attributes":
            self.normalize_attributes(
                metric.get(
                    "attributes",
                    {}
                )
            ),

    }



# --------------------------------------------------
# Add Metric
# --------------------------------------------------

def add_metric(
    self,
    metric: dict[str, Any],
) -> "JSONExporter":
    """
    Store metric.
    """

    with self._lock:

        self._metrics.append(

            self.normalize_metric(
                metric
            )

        )

    return self



# --------------------------------------------------
# Get Metrics
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
# Query Metric
# --------------------------------------------------

def get_metric(
    self,
    name: str,
) -> list[dict[str, Any]]:
    """
    Find metrics by name.
    """

    with self._lock:

        return [

            metric

            for metric
            in self._metrics

            if metric["name"] == name

        ]



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
    Prepare one metric export record.
    """

    return self.normalize_metric(
        metric
    )



# --------------------------------------------------
# Export Multiple Metrics
# --------------------------------------------------

def export_metrics(
    self,
    metrics: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Prepare metric collection.
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
    Build complete JSON payload.
    """

    if metrics is None:

        metrics = self.metrics()


    return {

        "format":
            self.FORMAT,


        "version":
            self.VERSION,


        "exporter":
        {

            "id":
                self._id,

            "name":
                self._name,

        },


        "resource":
            self.resource(),


        "attributes":
            self.attributes(),


        "metrics":
            self.export_metrics(
                metrics
            ),


        "timestamp":
            time.time(),

    }



# --------------------------------------------------
# To Dictionary
# --------------------------------------------------

def to_dict(
    self,
) -> dict[str, Any]:
    """
    Return JSON-ready dictionary.
    """

    return self.build_payload()



# --------------------------------------------------
# To JSON String
# --------------------------------------------------

def to_json(
    self,
    *,
    indent: int = 2,
) -> str:
    """
    Convert payload to JSON.
    """

    return json.dumps(

        self.build_payload(),

        indent=indent,

        ensure_ascii=False,

    )



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


        self._last_export = payload


        return payload



# --------------------------------------------------
# Last Export
# --------------------------------------------------

def last_export(
    self,
):
    """
    Return latest exported payload.
    """

    return copy.deepcopy(
        self._last_export
    )
# ==============================================
# Part 7. File API
# ==============================================


# --------------------------------------------------
# Write JSON
# --------------------------------------------------

def write_json(
    self,
    path: str | Path,
    data: dict[str, Any] | None = None,
) -> Path:
    """
    Write JSON document.
    """

    if data is None:

        data = self.export()


    file_path = Path(
        path
    )


    file_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )


    file_path.write_text(

        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        ),

        encoding="utf-8",

    )


    return file_path



# --------------------------------------------------
# Read JSON
# --------------------------------------------------

def read_json(
    self,
    path: str | Path,
) -> dict[str, Any]:
    """
    Read JSON document.
    """

    file_path = Path(
        path
    )


    return json.loads(

        file_path.read_text(
            encoding="utf-8"
        )

    )



# --------------------------------------------------
# Save
# --------------------------------------------------

def save(
    self,
    path: str | Path,
) -> Path:
    """
    Export and save.
    """

    with self._lock:

        return self.write_json(
            path,
            self.export(),
        )



# --------------------------------------------------
# Load
# --------------------------------------------------

def load(
    self,
    path: str | Path,
) -> dict[str, Any]:
    """
    Load JSON telemetry.
    """

    return self.read_json(
        path
    )



# --------------------------------------------------
# Append
# --------------------------------------------------

def append(
    self,
    path: str | Path,
    metric: dict[str, Any],
) -> Path:
    """
    Append metric record.

    Stored as JSON array.
    """

    file_path = Path(
        path
    )


    records = []


    if file_path.exists():

        try:

            records = json.loads(

                file_path.read_text(
                    encoding="utf-8"
                )

            )

        except Exception:

            records = []



    records.append(

        self.normalize_metric(
            metric
        )

    )


    file_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )


    file_path.write_text(

        json.dumps(
            records,
            indent=2,
            ensure_ascii=False,
        ),

        encoding="utf-8",

    )


    return file_path



# --------------------------------------------------
# File Exists
# --------------------------------------------------

def file_exists(
    self,
    path: str | Path,
) -> bool:
    """
    Check file.
    """

    return Path(
        path
    ).exists()



# --------------------------------------------------
# File Size
# --------------------------------------------------

def file_size(
    self,
    path: str | Path,
) -> int:
    """
    Return file size bytes.
    """

    return Path(
        path
    ).stat().st_size



# --------------------------------------------------
# Delete File
# --------------------------------------------------

def delete_file(
    self,
    path: str | Path,
) -> None:
    """
    Remove file.
    """

    file_path = Path(
        path
    )


    if file_path.exists():

        file_path.unlink()



# --------------------------------------------------
# Rotate File
# --------------------------------------------------

def rotate_file(
    self,
    path: str | Path,
    backup_suffix: str = ".bak",
) -> Path:
    """
    Rename current file.
    """

    source = Path(
        path
    )


    target = Path(
        str(source)
        + backup_suffix
    )


    if source.exists():

        source.rename(
            target
        )


    return target
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
    Create complete exporter snapshot.
    """

    with self._lock:

        return {

            "version":
                self.VERSION,


            "exporter":

            {
                "id":
                    self._id,

                "name":
                    self._name,

                "format":
                    self.FORMAT,

            },


            "configuration":
                self.config(),


            "resource":
                copy.deepcopy(
                    self._resource
                ),


            "attributes":
                copy.deepcopy(
                    self._attributes
                ),


            "metrics":
                copy.deepcopy(
                    self._metrics
                ),


            "statistics":

            {
                "exports":
                    self._export_count,

                "errors":
                    self._error_count,

            },


            "last_export":
                copy.deepcopy(
                    self._last_export
                ),


            "created_at":
                self._created_at,

        }



# --------------------------------------------------
# Restore Snapshot
# --------------------------------------------------

def restore(
    self,
    state: dict[str, Any],
) -> "JSONExporter":
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


        stats = (
            state.get(
                "statistics",
                {}
            )
        )


        self._export_count = (
            stats.get(
                "exports",
                0,
            )
        )


        self._error_count = (
            stats.get(
                "errors",
                0,
            )
        )


        self._last_export = (
            copy.deepcopy(
                state.get(
                    "last_export"
                )
            )
        )


    return self



# --------------------------------------------------
# Clone
# --------------------------------------------------

def clone(
    self,
) -> "JSONExporter":
    """
    Create independent exporter clone.
    """

    new = JSONExporter(

        service_name=
            self._service_name,

        service_version=
            self._service_version,

    )


    new.restore(
        self.snapshot()
    )


    return new



# --------------------------------------------------
# Copy
# --------------------------------------------------

def copy(
    self,
) -> dict[str, Any]:
    """
    Return detached snapshot copy.
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
) -> Path:
    """
    Save snapshot JSON.
    """

    return self.write_json(

        path,

        self.snapshot()

    )



# --------------------------------------------------
# Load Snapshot
# --------------------------------------------------

def load_snapshot(
    self,
    path: str | Path,
) -> "JSONExporter":
    """
    Load snapshot JSON.
    """

    state = self.read_json(
        path
    )


    return self.restore(
        state
    )



# --------------------------------------------------
# Clear Snapshot
# --------------------------------------------------

def clear_snapshot(
    self,
) -> None:
    """
    Clear runtime state.
    """

    with self._lock:

        self._metrics.clear()

        self._attributes.clear()

        self._last_export = None



# --------------------------------------------------
# Snapshot Info
# --------------------------------------------------

def snapshot_info(
    self,
) -> dict[str, Any]:
    """
    Snapshot summary.
    """

    state = self.snapshot()


    return {

        "version":
            state["version"],


        "metrics":
            len(
                state["metrics"]
            ),


        "attributes":
            len(
                state["attributes"]
            ),


        "exports":
            state["statistics"]
            ["exports"],

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


            "attributes":
                len(
                    self._attributes
                ),


            "exports":
                self._export_count,


            "errors":
                self._error_count,


            "last_export":

                self._last_export
                is not None,

        }



# --------------------------------------------------
# Health Check
# --------------------------------------------------

def health(
    self,
) -> dict[str, Any]:
    """
    Runtime health.
    """

    with self._lock:

        healthy = (

            self._enabled

            and

            self._error_count == 0

        )


        return {

            "status":

                "healthy"

                if healthy

                else "degraded",


            "enabled":
                self._enabled,


            "metrics":
                len(
                    self._metrics
                ),


            "errors":
                self._error_count,

        }



# --------------------------------------------------
# Diagnostics
# --------------------------------------------------

def diagnostics(
    self,
) -> dict[str, Any]:
    """
    Full diagnostic report.
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


        "metric_summary":
            self.metric_summary(),

    }



# --------------------------------------------------
# Dump
# --------------------------------------------------

def dump(
    self,
) -> str:
    """
    Human readable state dump.
    """

    data = (
        self.diagnostics()
    )


    return (

        "\n"
        "=== JSONExporter ===\n"

        f"Service: "
        f"{data['info']['service_name']}\n"

        f"Format: "
        f"{data['info']['format']}\n"

        f"Enabled: "
        f"{data['info']['enabled']}\n"

        f"Metrics: "
        f"{data['stats']['metrics']}\n"

        f"Exports: "
        f"{data['stats']['exports']}\n"

        f"Errors: "
        f"{data['stats']['errors']}\n"

    )



# --------------------------------------------------
# Metric Summary
# --------------------------------------------------

def metric_summary(
    self,
) -> dict[str, int]:
    """
    Count metrics by type.
    """

    summary = {}


    with self._lock:

        for metric in self._metrics:

            metric_type = (

                metric.get(
                    "type",
                    "unknown",
                )

            )


            summary[metric_type] = (

                summary.get(
                    metric_type,
                    0,
                )

                + 1

            )


    return summary



# --------------------------------------------------
# Export Summary
# --------------------------------------------------

def export_summary(
    self,
) -> dict[str, Any]:
    """
    Export status summary.
    """

    return {

        "format":
            self.FORMAT,


        "version":
            self.VERSION,


        "metrics":
            len(
                self._metrics
            ),


        "exports":
            self._export_count,


        "last_export":
            self._last_export is not None,

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
# Locked State
# --------------------------------------------------

def locked(
    self,
) -> bool:
    """
    Check lock state.
    """

    acquired = (

        self._lock.acquire(
            False
        )

    )


    if acquired:

        self._lock.release()

        return False


    return True



# --------------------------------------------------
# Synchronization Context
# --------------------------------------------------

@contextmanager
def synchronized(
    self,
):
    """
    Thread-safe context.
    """

    self.acquire()

    try:

        yield self

    finally:

        self.release()



# --------------------------------------------------
# Safe Export
# --------------------------------------------------

def safe_export(
    self,
) -> dict[str, Any]:
    """
    Thread-safe export.
    """

    with self.synchronized():

        return copy.deepcopy(
            self.export()
        )



# --------------------------------------------------
# Safe Snapshot
# --------------------------------------------------

def safe_snapshot(
    self,
) -> dict[str, Any]:
    """
    Thread-safe snapshot.
    """

    with self.synchronized():

        return copy.deepcopy(
            self.snapshot()
        )



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

        "locked":
            self.locked(),


        "lock_type":
            type(
                self._lock
            ).__name__,

    }



# --------------------------------------------------
# Thread Information
# --------------------------------------------------

def thread_info(
    self,
) -> dict[str, Any]:
    """
    Runtime thread information.
    """

    import threading


    current = (
        threading.current_thread()
    )


    return {

        "thread.name":
            current.name,


        "thread.id":
            current.ident,


        "daemon":
            current.daemon,


        "lock":
            self.lock_status(),

    }



# --------------------------------------------------
# Reset Lock
# --------------------------------------------------

def reset_lock(
    self,
) -> None:
    """
    Recreate lock.

    Used only during recovery.
    """

    with self._lock:

        self._lock = (
            threading.RLock()
        )                                                    