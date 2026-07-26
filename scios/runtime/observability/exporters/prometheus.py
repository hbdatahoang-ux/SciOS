"""
SciOS-NG Runtime Observability

Prometheus Exporter

File:
    scios/runtime/observability/exporters/prometheus.py
"""

from __future__ import annotations

# ==============================================================================
# Imports
# ==============================================================================

import threading
import time

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, MutableMapping, Optional

from .base import (
    BaseExporter,
    ExportCapability,
    ExportFormat,
    ExportMode,
)

# ==============================================================================
# Constants
# ==============================================================================

DEFAULT_NAMESPACE = "scios"

DEFAULT_SUBSYSTEM = "runtime"

DEFAULT_ENDPOINT = "/metrics"

DEFAULT_PUSHGATEWAY = None

DEFAULT_JOB_NAME = "scios"

DEFAULT_INSTANCE = "localhost"

DEFAULT_PREFIX = ""

DEFAULT_SEPARATOR = "_"

PROMETHEUS_EXPORTER_VERSION = "0.1.0"

# ==============================================================================
# Prometheus Export Options
# ==============================================================================


@dataclass(slots=True)
class PrometheusExportOptions:
    """
    Configuration for Prometheus exporter.
    """

    namespace: str = DEFAULT_NAMESPACE

    subsystem: str = DEFAULT_SUBSYSTEM

    endpoint: str = DEFAULT_ENDPOINT

    pushgateway: Optional[str] = DEFAULT_PUSHGATEWAY

    job: str = DEFAULT_JOB_NAME

    instance: str = DEFAULT_INSTANCE

    prefix: str = DEFAULT_PREFIX

    separator: str = DEFAULT_SEPARATOR

    labels: Dict[str, str] = field(default_factory=dict)


# ==============================================================================
# Metric Family
# ==============================================================================


@dataclass(slots=True)
class MetricFamily:
    """
    A Prometheus metric family.
    """

    name: str

    metric_type: str

    help: str = ""

    unit: str = ""

    labels: Dict[str, str] = field(default_factory=dict)


# ==============================================================================
# Metric Sample
# ==============================================================================


@dataclass(slots=True)
class MetricSample:
    """
    One metric sample.
    """

    family: str

    value: float

    labels: Dict[str, str] = field(default_factory=dict)

    timestamp: Optional[float] = None

    exemplar: Optional[Dict[str, Any]] = None


# ==============================================================================
# Prometheus Exporter
# ==============================================================================


class PrometheusExporter(BaseExporter):
    """
    Prometheus metrics exporter.
    """

    def __init__(
        self,
        name: str = "PrometheusExporter",
        *,
        mode: ExportMode = ExportMode.SYNC,
        options: Optional[PrometheusExportOptions] = None,
    ) -> None:

        super().__init__(
            name=name,
            exporter_format=ExportFormat.PROMETHEUS,
            destination=DEFAULT_ENDPOINT,
            mode=mode,
        )

        if options is None:
            options = PrometheusExportOptions()

        # ------------------------------------------------------------------
        # Identity
        # ------------------------------------------------------------------

        self._name = name

        self._exporter_type = "PrometheusExporter"

        self._version = PROMETHEUS_EXPORTER_VERSION

        # ------------------------------------------------------------------
        # Configuration
        # ------------------------------------------------------------------

        self._namespace = options.namespace

        self._subsystem = options.subsystem

        self._endpoint = options.endpoint

        self._pushgateway = options.pushgateway

        self._job = options.job

        self._instance = options.instance

        self._prefix = options.prefix

        self._separator = options.separator

        self._labels = dict(options.labels)

        # ------------------------------------------------------------------
        # Runtime State
        # ------------------------------------------------------------------

        self._families: Dict[str, MetricFamily] = {}

        self._samples: List[MetricSample] = []

        self._metrics_exported = 0

        self._samples_exported = 0

        self._scrape_count = 0

        self._last_export = None

        self._lock = threading.RLock()

        self._metadata.update(
            {
                "namespace": self._namespace,
                "subsystem": self._subsystem,
                "endpoint": self._endpoint,
            }
        )

        self._capabilities |= (
            ExportCapability.SERIALIZATION
            | ExportCapability.BATCHING
            | ExportCapability.STREAMING
        )
# ==============================================================================
# Part 2. Serialization
# ==============================================================================

    def serialize(
        self,
        record: ExportRecord,
    ) -> str:
        """
        Serialize an ExportRecord into Prometheus text exposition format.
        """

        return self.encode(record.payload)

    # ------------------------------------------------------------------

    def deserialize(
        self,
        payload: str,
    ) -> ExportRecord:
        """
        Deserialize Prometheus text into an ExportRecord.

        This implementation preserves the raw payload.
        """

        return ExportRecord(
            payload=payload,
            source="prometheus",
        )

    # ------------------------------------------------------------------

    def encode(
        self,
        payload: Any,
    ) -> str:
        """
        Encode a metric object into Prometheus exposition text.
        """

        if isinstance(payload, MetricSample):
            return self.format_metric(payload)

        if isinstance(payload, MetricFamily):
            return payload.name

        if isinstance(payload, dict):
            name = payload.get("name", "metric")
            value = payload.get("value", 0)
            labels = payload.get("labels", {})

            sample = MetricSample(
                family=name,
                value=float(value),
                labels=dict(labels),
            )

            return self.format_metric(sample)

        raise TypeError(
            f"Unsupported payload type: {type(payload).__name__}"
        )

    # ------------------------------------------------------------------

    def decode(
        self,
        payload: str,
    ) -> str:
        """
        Decode Prometheus text.

        Parsing is intentionally left minimal.
        """

        return payload

    # ------------------------------------------------------------------

    def format_metric(
        self,
        sample: MetricSample,
    ) -> str:
        """
        Format one metric sample.

        Example:
            cpu_usage{host="node1"} 0.81
        """

        labels = self.format_labels(
            sample.labels,
        )

        if labels:
            return (
                f"{sample.family}"
                f"{{{labels}}} "
                f"{sample.value}"
            )

        return (
            f"{sample.family} "
            f"{sample.value}"
        )

    # ------------------------------------------------------------------

    def format_labels(
        self,
        labels: Mapping[str, str],
    ) -> str:
        """
        Format Prometheus labels.
        """

        return ",".join(
            f'{k}="{v}"'
            for k, v in sorted(labels.items())
        )

    # ------------------------------------------------------------------

    def validate_metric(
        self,
        sample: MetricSample,
    ) -> bool:
        """
        Validate a metric sample.
        """

        if not sample.family:
            return False

        if not isinstance(
            sample.value,
            (int, float),
        ):
            return False

        return True
# ==============================================================================
# Part 3. Metrics API
# ==============================================================================

    def register_metric(
        self,
        family: MetricFamily,
    ) -> MetricFamily:
        """
        Register a metric family.
        """

        with self._lock:
            self._families[family.name] = family

        return family

    # ------------------------------------------------------------------

    def unregister_metric(
        self,
        name: str,
    ) -> bool:
        """
        Remove a metric family.
        """

        with self._lock:
            return self._families.pop(name, None) is not None

    # ------------------------------------------------------------------

    def update_metric(
        self,
        sample: MetricSample,
    ) -> MetricSample:
        """
        Add or update a metric sample.
        """

        if sample.timestamp is None:
            sample.timestamp = time.time()

        with self._lock:
            self._samples.append(sample)

        return sample

    # ------------------------------------------------------------------

    def collect(
        self,
    ) -> List[MetricSample]:
        """
        Collect all pending metric samples.
        """

        with self._lock:
            return list(self._samples)

    # ------------------------------------------------------------------

    def gather(
        self,
    ) -> str:
        """
        Gather all metrics into Prometheus exposition format.
        """

        lines: List[str] = []

        with self._lock:

            for family in self._families.values():

                if family.help:
                    lines.append(
                        f"# HELP {family.name} {family.help}"
                    )

                lines.append(
                    f"# TYPE {family.name} {family.metric_type}"
                )

                if family.unit:
                    lines.append(
                        f"# UNIT {family.name} {family.unit}"
                    )

            for sample in self._samples:
                lines.append(
                    self.format_metric(sample)
                )

            self._scrape_count += 1

        return "\n".join(lines)

    # ------------------------------------------------------------------

    def clear_metrics(
        self,
        *,
        samples: bool = True,
        families: bool = False,
    ) -> None:
        """
        Clear cached metrics.

        By default only samples are removed while
        metric families remain registered.
        """

        with self._lock:

            if samples:
                self._samples.clear()

            if families:
                self._families.clear()

    # ------------------------------------------------------------------

    def flush(
        self,
    ) -> ExportResult:
        """
        Flush all collected metrics.

        Metrics are gathered into one exposition payload and
        exported through the standard exporter pipeline.
        """

        payload = self.gather()

        result = self.export_text(payload)

        self.clear_metrics(samples=True)

        return result
# ==============================================================================
# Part 4. Export API
# ==============================================================================

    def export(
        self,
        record: ExportRecord,
    ) -> ExportResult:
        """
        Export one record.

        Delegates to BaseExporter.
        """

        return super().export(record)

    # ------------------------------------------------------------------

    def export_batch(
        self,
        records: Sequence[ExportRecord],
    ) -> List[ExportResult]:
        """
        Export multiple records.
        """

        return [
            self.export(record)
            for record in records
        ]

    # ------------------------------------------------------------------

    def export_metric(
        self,
        name: str,
        value: float,
        *,
        metric_type: str = "gauge",
        labels: Optional[Mapping[str, str]] = None,
        help: str = "",
        unit: str = "",
    ) -> ExportResult:
        """
        Export a generic Prometheus metric.
        """

        if name not in self._families:

            self.register_metric(
                MetricFamily(
                    name=name,
                    metric_type=metric_type,
                    help=help,
                    unit=unit,
                )
            )

        sample = MetricSample(
            family=name,
            value=float(value),
            labels=dict(labels or {}),
            timestamp=time.time(),
        )

        self.update_metric(sample)

        return self.export_text(
            self.format_metric(sample)
        )

    # ------------------------------------------------------------------

    def export_counter(
        self,
        name: str,
        value: float,
        *,
        labels: Optional[Mapping[str, str]] = None,
        help: str = "",
    ) -> ExportResult:
        """
        Export a counter metric.
        """

        return self.export_metric(
            name=name,
            value=value,
            metric_type="counter",
            labels=labels,
            help=help,
        )

    # ------------------------------------------------------------------

    def export_gauge(
        self,
        name: str,
        value: float,
        *,
        labels: Optional[Mapping[str, str]] = None,
        help: str = "",
    ) -> ExportResult:
        """
        Export a gauge metric.
        """

        return self.export_metric(
            name=name,
            value=value,
            metric_type="gauge",
            labels=labels,
            help=help,
        )

    # ------------------------------------------------------------------

    def export_histogram(
        self,
        name: str,
        value: float,
        *,
        labels: Optional[Mapping[str, str]] = None,
        help: str = "",
    ) -> ExportResult:
        """
        Export a histogram observation.

        Histogram bucket aggregation can be added later.
        """

        return self.export_metric(
            name=name,
            value=value,
            metric_type="histogram",
            labels=labels,
            help=help,
        )

    # ------------------------------------------------------------------

    def export_summary(
        self,
        name: str,
        value: float,
        *,
        labels: Optional[Mapping[str, str]] = None,
        help: str = "",
    ) -> ExportResult:
        """
        Export a summary observation.
        """

        return self.export_metric(
            name=name,
            value=value,
            metric_type="summary",
            labels=labels,
            help=help,
        )

    # ------------------------------------------------------------------

    def export_text(
        self,
        payload: str,
    ) -> ExportResult:
        """
        Export raw Prometheus exposition text.
        """

        record = ExportRecord(
            payload=payload,
            source="prometheus",
        )

        return super().export(record)
# ==============================================================================
# Part 5. Configuration
# ==============================================================================

    def set_namespace(
        self,
        namespace: str,
    ) -> "PrometheusExporter":
        """
        Set the Prometheus namespace.
        """

        self._namespace = str(namespace).strip()

        return self

    # ------------------------------------------------------------------

    def set_subsystem(
        self,
        subsystem: str,
    ) -> "PrometheusExporter":
        """
        Set the Prometheus subsystem.
        """

        self._subsystem = str(subsystem).strip()

        return self

    # ------------------------------------------------------------------

    def set_labels(
        self,
        labels: Mapping[str, str],
    ) -> "PrometheusExporter":
        """
        Set default labels.
        """

        self._labels = dict(labels)

        return self

    # ------------------------------------------------------------------

    def set_endpoint(
        self,
        endpoint: str,
    ) -> "PrometheusExporter":
        """
        Set metrics endpoint.
        """

        self._endpoint = str(endpoint)

        self._destination = self._endpoint

        return self

    # ------------------------------------------------------------------

    def set_pushgateway(
        self,
        pushgateway: Optional[str],
    ) -> "PrometheusExporter":
        """
        Configure Prometheus Pushgateway.
        """

        self._pushgateway = pushgateway

        return self

    # ------------------------------------------------------------------

    def options(self) -> Dict[str, Any]:
        """
        Return exporter configuration.
        """

        return {
            "namespace": self._namespace,
            "subsystem": self._subsystem,
            "endpoint": self._endpoint,
            "pushgateway": self._pushgateway,
            "job": self._job,
            "instance": self._instance,
            "labels": dict(self._labels),
            "prefix": self._prefix,
            "separator": self._separator,
        }

    # ------------------------------------------------------------------

    def reset(self) -> "PrometheusExporter":
        """
        Restore default configuration.
        """

        self._namespace = DEFAULT_NAMESPACE

        self._subsystem = DEFAULT_SUBSYSTEM

        self._endpoint = DEFAULT_ENDPOINT

        self._destination = DEFAULT_ENDPOINT

        self._pushgateway = DEFAULT_PUSHGATEWAY

        self._job = DEFAULT_JOB_NAME

        self._instance = DEFAULT_INSTANCE

        self._prefix = DEFAULT_PREFIX

        self._separator = DEFAULT_SEPARATOR

        self._labels.clear()

        return self
# ==============================================================================
# Part 6. Runtime Operations
# ==============================================================================

    def snapshot(self) -> Dict[str, Any]:
        """
        Create a runtime snapshot.
        """

        state = super().snapshot()

        state["prometheus"] = {
            "namespace": self._namespace,
            "subsystem": self._subsystem,
            "endpoint": self._endpoint,
            "pushgateway": self._pushgateway,
            "job": self._job,
            "instance": self._instance,
            "labels": dict(self._labels),
            "families": copy.deepcopy(self._families),
            "samples": copy.deepcopy(self._samples),
            "metrics_exported": self._metrics_exported,
            "samples_exported": self._samples_exported,
            "scrape_count": self._scrape_count,
            "last_export": self._last_export,
        }

        return state

    # ------------------------------------------------------------------

    def restore(
        self,
        snapshot: Dict[str, Any],
    ) -> "PrometheusExporter":
        """
        Restore exporter state.
        """

        super().restore(snapshot)

        state = snapshot.get("prometheus", {})

        self._namespace = state.get(
            "namespace",
            DEFAULT_NAMESPACE,
        )

        self._subsystem = state.get(
            "subsystem",
            DEFAULT_SUBSYSTEM,
        )

        self._endpoint = state.get(
            "endpoint",
            DEFAULT_ENDPOINT,
        )

        self._pushgateway = state.get(
            "pushgateway",
            DEFAULT_PUSHGATEWAY,
        )

        self._job = state.get(
            "job",
            DEFAULT_JOB_NAME,
        )

        self._instance = state.get(
            "instance",
            DEFAULT_INSTANCE,
        )

        self._labels = dict(
            state.get("labels", {})
        )

        self._families = copy.deepcopy(
            state.get("families", {})
        )

        self._samples = copy.deepcopy(
            state.get("samples", [])
        )

        self._metrics_exported = state.get(
            "metrics_exported",
            0,
        )

        self._samples_exported = state.get(
            "samples_exported",
            0,
        )

        self._scrape_count = state.get(
            "scrape_count",
            0,
        )

        self._last_export = state.get(
            "last_export",
        )

        return self

    # ------------------------------------------------------------------

    def clone(self) -> "PrometheusExporter":
        """
        Create a deep clone.
        """

        return copy.deepcopy(self)

    # ------------------------------------------------------------------

    def copy(self) -> "PrometheusExporter":
        """
        Create a shallow copy.
        """

        return copy.copy(self)

    # ------------------------------------------------------------------

    def cleanup(self) -> "PrometheusExporter":
        """
        Cleanup transient runtime state.
        """

        super().cleanup()

        self._samples.clear()

        self._last_export = None

        return self

    # ------------------------------------------------------------------

    def compact(self) -> "PrometheusExporter":
        """
        Compact runtime memory usage.
        """

        super().compact()

        #
        # Keep metric families, discard collected samples.
        #

        self._samples.clear()

        return self
# ==============================================================================
# Part 7. Statistics
# ==============================================================================

    @property
    def metrics_exported(self) -> int:
        """
        Total exported metrics.
        """

        return self._metrics_exported

    # ------------------------------------------------------------------

    @property
    def metric_families(self) -> int:
        """
        Number of registered metric families.
        """

        return len(self._families)

    # ------------------------------------------------------------------

    @property
    def samples_exported(self) -> int:
        """
        Total exported metric samples.
        """

        return self._samples_exported

    # ------------------------------------------------------------------

    @property
    def scrape_count(self) -> int:
        """
        Number of scrape/gather operations.
        """

        return self._scrape_count

    # ------------------------------------------------------------------

    def report(self) -> Dict[str, Any]:
        """
        Return a detailed Prometheus exporter report.
        """

        report = super().report()

        report["prometheus"] = {
            "namespace": self._namespace,
            "subsystem": self._subsystem,
            "endpoint": self._endpoint,
            "pushgateway": self._pushgateway,
            "job": self._job,
            "instance": self._instance,
            "metric_families": self.metric_families,
            "metrics_exported": self.metrics_exported,
            "samples_exported": self.samples_exported,
            "scrape_count": self.scrape_count,
            "registered_metrics": sorted(
                self._families.keys()
            ),
        }

        return report

    # ------------------------------------------------------------------

    def summary(self) -> Dict[str, Any]:
        """
        Return a concise Prometheus exporter summary.
        """

        summary = super().summary()

        summary.update(
            {
                "metric_families": self.metric_families,
                "metrics_exported": self.metrics_exported,
                "samples_exported": self.samples_exported,
                "scrape_count": self.scrape_count,
            }
        )

        return summary
# ==============================================================================
# Part 8. Validation
# ==============================================================================

    def validate(
        self,
        raise_error: bool = False,
    ) -> bool:
        """
        Validate the Prometheus exporter.
        """

        try:

            super().validate(raise_error=True)

            self.validate_endpoint(
                self._endpoint,
                raise_error=True,
            )

            self.validate_labels(
                self._labels,
                raise_error=True,
            )

            self.check_integrity(
                raise_error=True,
            )

            return True

        except Exception:

            if raise_error:
                raise

            return False

    # ------------------------------------------------------------------

    def validate_metric(
        self,
        sample: MetricSample,
        raise_error: bool = False,
    ) -> bool:
        """
        Validate a metric sample.
        """

        try:

            if not isinstance(sample, MetricSample):
                raise TypeError(
                    "sample must be MetricSample"
                )

            if not sample.family:
                raise ValueError(
                    "metric family cannot be empty"
                )

            if not isinstance(
                sample.value,
                (int, float),
            ):
                raise TypeError(
                    "metric value must be numeric"
                )

            self.validate_labels(
                sample.labels,
                raise_error=True,
            )

            return True

        except Exception:

            if raise_error:
                raise

            return False

    # ------------------------------------------------------------------

    def validate_labels(
        self,
        labels: Mapping[str, str],
        raise_error: bool = False,
    ) -> bool:
        """
        Validate Prometheus labels.
        """

        try:

            if not isinstance(labels, Mapping):
                raise TypeError(
                    "labels must be a mapping"
                )

            for key, value in labels.items():

                if not isinstance(key, str):
                    raise TypeError(
                        "label name must be str"
                    )

                if not isinstance(value, str):
                    raise TypeError(
                        "label value must be str"
                    )

            return True

        except Exception:

            if raise_error:
                raise

            return False

    # ------------------------------------------------------------------

    def validate_endpoint(
        self,
        endpoint: str,
        raise_error: bool = False,
    ) -> bool:
        """
        Validate the metrics endpoint.
        """

        try:

            if not isinstance(endpoint, str):
                raise TypeError(
                    "endpoint must be str"
                )

            if not endpoint.startswith("/"):
                raise ValueError(
                    "endpoint must start with '/'"
                )

            return True

        except Exception:

            if raise_error:
                raise

            return False

    # ------------------------------------------------------------------

    def check_integrity(
        self,
        raise_error: bool = False,
    ) -> bool:
        """
        Check internal exporter integrity.
        """

        try:

            super().check_integrity(
                raise_error=True,
            )

            if not isinstance(
                self._families,
                dict,
            ):
                raise TypeError(
                    "families must be dict"
                )

            if not isinstance(
                self._samples,
                list,
            ):
                raise TypeError(
                    "samples must be list"
                )

            if self._metrics_exported < 0:
                raise ValueError(
                    "invalid metrics_exported"
                )

            if self._samples_exported < 0:
                raise ValueError(
                    "invalid samples_exported"
                )

            if self._scrape_count < 0:
                raise ValueError(
                    "invalid scrape_count"
                )

            return True

        except Exception:

            if raise_error:
                raise

            return False
# ==============================================================================
# Part 9. Events & Hooks
# ==============================================================================

    def before_collect(self) -> None:
        """
        Hook executed before collecting metrics.
        """

        self.emit_event(
            "before_collect",
            exporter=self,
        )

    # ------------------------------------------------------------------

    def after_collect(
        self,
        samples: Sequence[MetricSample],
    ) -> Sequence[MetricSample]:
        """
        Hook executed after metrics have been collected.
        """

        self.emit_event(
            "after_collect",
            exporter=self,
            samples=samples,
        )

        return samples

    # ------------------------------------------------------------------

    def before_export(
        self,
        record: ExportRecord,
    ) -> ExportRecord:
        """
        Hook executed before exporting.
        """

        record = super().before_export(record)

        self.emit_event(
            "before_prometheus_export",
            exporter=self,
            record=record,
        )

        return record

    # ------------------------------------------------------------------

    def after_export(
        self,
        record: ExportRecord,
        result: ExportResult,
    ) -> ExportResult:
        """
        Hook executed after exporting.
        """

        result = super().after_export(
            record,
            result,
        )

        self.emit_event(
            "after_prometheus_export",
            exporter=self,
            record=record,
            result=result,
        )

        return result

    # ------------------------------------------------------------------

    def before_flush(self) -> None:
        """
        Hook executed before flushing metrics.
        """

        self.emit_event(
            "before_flush",
            exporter=self,
        )

    # ------------------------------------------------------------------

    def after_flush(
        self,
        result: ExportResult,
    ) -> ExportResult:
        """
        Hook executed after flushing metrics.
        """

        self.emit_event(
            "after_flush",
            exporter=self,
            result=result,
        )

        return result

    # ------------------------------------------------------------------

    def emit_event(
        self,
        event: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Emit a Prometheus exporter event.

        Delegates to BaseExporter.
        """

        super().emit_event(
            event,
            *args,
            **kwargs,
        )
# ==============================================================================
# Part 10. Python Protocols
# ==============================================================================

    def __repr__(self) -> str:
        """
        Developer-friendly representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"name={self._name!r}, "
            f"namespace={self._namespace!r}, "
            f"subsystem={self._subsystem!r}, "
            f"endpoint={self._endpoint!r}, "
            f"families={len(self._families)}, "
            f"samples={len(self._samples)}, "
            f"status={self._status.value!r})"
        )

    # ------------------------------------------------------------------

    def __str__(self) -> str:
        """
        Human-readable representation.
        """

        return (
            f"{self._name} "
            f"[PROMETHEUS] -> "
            f"{self._endpoint}"
        )

    # ------------------------------------------------------------------

    def __len__(self) -> int:
        """
        Return the number of registered metric families.
        """

        return len(self._families)

    # ------------------------------------------------------------------

    def __call__(
        self,
        name: str,
        value: float,
        **kwargs: Any,
    ) -> ExportResult:
        """
        Shortcut for export_metric().
        """

        return self.export_metric(
            name=name,
            value=value,
            **kwargs,
        )

    # ------------------------------------------------------------------

    def __copy__(self) -> "PrometheusExporter":
        """
        Create a shallow copy.
        """

        return self.copy()

    # ------------------------------------------------------------------

    def __deepcopy__(
        self,
        memo: Dict[int, Any],
    ) -> "PrometheusExporter":
        """
        Create a deep copy.
        """

        return self.clone()                                                                            