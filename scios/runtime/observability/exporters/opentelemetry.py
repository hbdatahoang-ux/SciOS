"""
SciOS-NG Runtime Observability

OpenTelemetry Exporter

File:
    scios/runtime/observability/exporters/opentelemetry.py
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

DEFAULT_SERVICE_NAME = "scios-runtime"

DEFAULT_SERVICE_VERSION = "0.1.0"

DEFAULT_ENDPOINT = "http://localhost:4317"

DEFAULT_PROTOCOL = "grpc"

DEFAULT_TIMEOUT = 30.0

DEFAULT_HEADERS: Dict[str, str] = {}

DEFAULT_BATCH_SIZE = 512

OTEL_EXPORTER_VERSION = "0.1.0"

# ==============================================================================
# OpenTelemetry Export Options
# ==============================================================================


@dataclass(slots=True)
class OpenTelemetryExportOptions:
    """
    OpenTelemetry exporter configuration.
    """

    endpoint: str = DEFAULT_ENDPOINT

    protocol: str = DEFAULT_PROTOCOL

    timeout: float = DEFAULT_TIMEOUT

    batch_size: int = DEFAULT_BATCH_SIZE

    headers: Dict[str, str] = field(default_factory=dict)


# ==============================================================================
# Resource Attributes
# ==============================================================================


@dataclass(slots=True)
class ResourceAttributes:
    """
    OpenTelemetry Resource.
    """

    service_name: str = DEFAULT_SERVICE_NAME

    service_version: str = DEFAULT_SERVICE_VERSION

    attributes: Dict[str, Any] = field(default_factory=dict)


# ==============================================================================
# Instrumentation Scope
# ==============================================================================


@dataclass(slots=True)
class InstrumentationScope:
    """
    Instrumentation scope.
    """

    name: str = "SciOS"

    version: str = "0.1.0"

    schema_url: str = ""


# ==============================================================================
# OTel Span
# ==============================================================================


@dataclass(slots=True)
class OTelSpan:
    """
    Trace span.
    """

    trace_id: str

    span_id: str

    parent_id: Optional[str] = None

    name: str = ""

    start_time: float = field(default_factory=time.time)

    end_time: Optional[float] = None

    attributes: Dict[str, Any] = field(default_factory=dict)

    events: List[Dict[str, Any]] = field(default_factory=list)

    status: str = "OK"


# ==============================================================================
# OTel Metric
# ==============================================================================


@dataclass(slots=True)
class OTelMetric:
    """
    Metric record.
    """

    name: str

    value: float

    unit: str = ""

    metric_type: str = "gauge"

    attributes: Dict[str, Any] = field(default_factory=dict)

    timestamp: float = field(default_factory=time.time)


# ==============================================================================
# OTel Log
# ==============================================================================


@dataclass(slots=True)
class OTelLog:
    """
    Log record.
    """

    timestamp: float = field(default_factory=time.time)

    severity: str = "INFO"

    message: str = ""

    attributes: Dict[str, Any] = field(default_factory=dict)

    trace_id: Optional[str] = None

    span_id: Optional[str] = None


# ==============================================================================
# OpenTelemetry Exporter
# ==============================================================================


class OpenTelemetryExporter(BaseExporter):
    """
    OpenTelemetry exporter.
    """

    def __init__(
        self,
        name: str = "OpenTelemetryExporter",
        *,
        mode: ExportMode = ExportMode.BATCH,
        options: Optional[OpenTelemetryExportOptions] = None,
    ) -> None:

        super().__init__(
            name=name,
            exporter_format=ExportFormat.OPENTELEMETRY,
            destination=DEFAULT_ENDPOINT,
            mode=mode,
        )

        if options is None:
            options = OpenTelemetryExportOptions()

        # ------------------------------------------------------------------
        # Identity
        # ------------------------------------------------------------------

        self._name = name

        self._exporter_type = "OpenTelemetryExporter"

        self._version = OTEL_EXPORTER_VERSION

        # ------------------------------------------------------------------
        # Configuration
        # ------------------------------------------------------------------

        self._endpoint = options.endpoint

        self._protocol = options.protocol

        self._timeout = options.timeout

        self._batch_size = options.batch_size

        self._headers = dict(options.headers)

        self._resource = ResourceAttributes()

        self._scope = InstrumentationScope()

        # ------------------------------------------------------------------
        # Runtime State
        # ------------------------------------------------------------------

        self._spans: List[OTelSpan] = []

        self._metrics: List[OTelMetric] = []

        self._logs: List[OTelLog] = []

        self._spans_exported = 0

        self._metrics_exported = 0

        self._logs_exported = 0

        self._batches_exported = 0

        self._last_export = None

        self._lock = threading.RLock()

        self._metadata.update(
            {
                "endpoint": self._endpoint,
                "protocol": self._protocol,
                "service": self._resource.service_name,
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
    ) -> Dict[str, Any]:
        """
        Serialize an ExportRecord into an OpenTelemetry payload.
        """

        return self.encode(record.payload)

    # ------------------------------------------------------------------

    def deserialize(
        self,
        payload: Mapping[str, Any],
    ) -> ExportRecord:
        """
        Deserialize an OTLP payload.
        """

        return ExportRecord(
            payload=self.decode(payload),
            source="opentelemetry",
        )

    # ------------------------------------------------------------------

    def encode(
        self,
        payload: Any,
    ) -> Dict[str, Any]:
        """
        Encode telemetry into a serializable dictionary.
        """

        if isinstance(payload, OTelSpan):
            return self.format_span(payload)

        if isinstance(payload, OTelMetric):
            return self.format_metric(payload)

        if isinstance(payload, OTelLog):
            return self.format_log(payload)

        if isinstance(payload, Mapping):
            return dict(payload)

        raise TypeError(
            f"Unsupported payload type: {type(payload).__name__}"
        )

    # ------------------------------------------------------------------

    def decode(
        self,
        payload: Mapping[str, Any],
    ) -> Dict[str, Any]:
        """
        Decode an OTLP payload.

        Current implementation simply normalizes the mapping.
        """

        return dict(payload)

    # ------------------------------------------------------------------

    def format_span(
        self,
        span: OTelSpan,
    ) -> Dict[str, Any]:
        """
        Format a span.
        """

        return {
            "type": "span",
            "trace_id": span.trace_id,
            "span_id": span.span_id,
            "parent_id": span.parent_id,
            "name": span.name,
            "start_time": span.start_time,
            "end_time": span.end_time,
            "status": span.status,
            "attributes": dict(span.attributes),
            "events": list(span.events),
        }

    # ------------------------------------------------------------------

    def format_metric(
        self,
        metric: OTelMetric,
    ) -> Dict[str, Any]:
        """
        Format a metric.
        """

        return {
            "type": "metric",
            "name": metric.name,
            "value": metric.value,
            "unit": metric.unit,
            "metric_type": metric.metric_type,
            "timestamp": metric.timestamp,
            "attributes": dict(metric.attributes),
        }

    # ------------------------------------------------------------------

    def format_log(
        self,
        log: OTelLog,
    ) -> Dict[str, Any]:
        """
        Format a log record.
        """

        return {
            "type": "log",
            "timestamp": log.timestamp,
            "severity": log.severity,
            "message": log.message,
            "trace_id": log.trace_id,
            "span_id": log.span_id,
            "attributes": dict(log.attributes),
        }

    # ------------------------------------------------------------------

    def validate_record(
        self,
        payload: Any,
    ) -> bool:
        """
        Validate telemetry payload.
        """

        return isinstance(
            payload,
            (
                OTelSpan,
                OTelMetric,
                OTelLog,
                Mapping,
            ),
        )
# ==============================================================================
# Part 3. Telemetry API
# ==============================================================================

    def register_resource(
        self,
        resource: ResourceAttributes,
    ) -> ResourceAttributes:
        """
        Register OpenTelemetry resource.
        """

        with self._lock:
            self._resource = resource

        return resource

    # ------------------------------------------------------------------

    def register_scope(
        self,
        scope: InstrumentationScope,
    ) -> InstrumentationScope:
        """
        Register instrumentation scope.
        """

        with self._lock:
            self._scope = scope

        return scope

    # ------------------------------------------------------------------

    def record_span(
        self,
        span: OTelSpan,
    ) -> OTelSpan:
        """
        Record a trace span.
        """

        if span.end_time is None:
            span.end_time = time.time()

        with self._lock:
            self._spans.append(span)

        return span

    # ------------------------------------------------------------------

    def record_metric(
        self,
        metric: OTelMetric,
    ) -> OTelMetric:
        """
        Record a metric.
        """

        with self._lock:
            self._metrics.append(metric)

        return metric

    # ------------------------------------------------------------------

    def record_log(
        self,
        log: OTelLog,
    ) -> OTelLog:
        """
        Record a log entry.
        """

        with self._lock:
            self._logs.append(log)

        return log

    # ------------------------------------------------------------------

    def collect(
        self,
    ) -> Dict[str, List[Any]]:
        """
        Collect all pending telemetry.
        """

        with self._lock:

            data = {
                "spans": list(self._spans),
                "metrics": list(self._metrics),
                "logs": list(self._logs),
            }

        return data

    # ------------------------------------------------------------------

    def gather(
        self,
    ) -> Dict[str, Any]:
        """
        Gather telemetry batch with resource metadata.
        """

        with self._lock:

            payload = {
                "resource": {
                    "service_name":
                        self._resource.service_name,

                    "service_version":
                        self._resource.service_version,

                    "attributes":
                        dict(
                            self._resource.attributes
                        ),
                },

                "scope": {
                    "name":
                        self._scope.name,

                    "version":
                        self._scope.version,

                    "schema_url":
                        self._scope.schema_url,
                },

                "spans": [
                    self.format_span(span)
                    for span in self._spans
                ],

                "metrics": [
                    self.format_metric(metric)
                    for metric in self._metrics
                ],

                "logs": [
                    self.format_log(log)
                    for log in self._logs
                ],
            }

        return payload

    # ------------------------------------------------------------------

    def flush(
        self,
    ) -> ExportResult:
        """
        Flush collected telemetry.
        """

        payload = self.gather()

        result = self.export_otlp(
            payload
        )

        with self._lock:

            if result.success:

                self._spans.clear()

                self._metrics.clear()

                self._logs.clear()

        return result
# ==============================================================================
# Part 4. Export API
# ==============================================================================

    def export(
        self,
        payload: Any,
    ) -> ExportResult:
        """
        Export generic telemetry payload.
        """

        start = time.time()

        try:

            encoded = self.encode(
                payload
            )

            result = self.export_otlp(
                encoded
            )

            duration = time.time() - start

            result.duration = duration

            return result

        except Exception as exc:

            return ExportResult(
                success=False,
                status="FAILED",
                message=str(exc),
                exported=0,
                duration=time.time() - start,
            )

    # ------------------------------------------------------------------

    def export_batch(
        self,
        batch: Mapping[str, List[Any]],
    ) -> ExportResult:
        """
        Export telemetry batch.
        """

        start = time.time()

        exported = 0

        try:

            for span in batch.get(
                "spans",
                [],
            ):
                self.export_span(span)
                exported += 1


            for metric in batch.get(
                "metrics",
                [],
            ):
                self.export_metric(metric)
                exported += 1


            for log in batch.get(
                "logs",
                [],
            ):
                self.export_log(log)
                exported += 1


            self._batches_exported += 1


            return ExportResult(
                success=True,
                status="SUCCESS",
                message="Batch exported",
                exported=exported,
                duration=time.time() - start,
            )

        except Exception as exc:

            return ExportResult(
                success=False,
                status="FAILED",
                message=str(exc),
                exported=exported,
                duration=time.time() - start,
            )

    # ------------------------------------------------------------------

    def export_span(
        self,
        span: OTelSpan,
    ) -> ExportResult:
        """
        Export a single span.
        """

        payload = {
            "spans": [
                self.format_span(span)
            ]
        }

        result = self.export_otlp(
            payload
        )

        if result.success:
            self._spans_exported += 1

        return result

    # ------------------------------------------------------------------

    def export_metric(
        self,
        metric: OTelMetric,
    ) -> ExportResult:
        """
        Export a single metric.
        """

        payload = {
            "metrics": [
                self.format_metric(metric)
            ]
        }

        result = self.export_otlp(
            payload
        )

        if result.success:
            self._metrics_exported += 1

        return result

    # ------------------------------------------------------------------

    def export_log(
        self,
        log: OTelLog,
    ) -> ExportResult:
        """
        Export a single log.
        """

        payload = {
            "logs": [
                self.format_log(log)
            ]
        }

        result = self.export_otlp(
            payload
        )

        if result.success:
            self._logs_exported += 1

        return result

    # ------------------------------------------------------------------

    def export_trace(
        self,
        spans: List[OTelSpan],
    ) -> ExportResult:
        """
        Export complete trace.
        """

        payload = {
            "spans": [
                self.format_span(span)
                for span in spans
            ]
        }

        return self.export_otlp(
            payload
        )

    # ------------------------------------------------------------------

    def export_resource(
        self,
        resource: ResourceAttributes,
    ) -> ExportResult:
        """
        Export resource information.
        """

        payload = {
            "resource": {
                "service_name":
                    resource.service_name,

                "service_version":
                    resource.service_version,

                "attributes":
                    dict(
                        resource.attributes
                    ),
            }
        }

        return self.export_otlp(
            payload
        )

    # ------------------------------------------------------------------

    def export_otlp(
        self,
        payload: Mapping[str, Any],
    ) -> ExportResult:
        """
        Low-level OTLP exporter.

        Transport abstraction:
        gRPC / HTTP / Collector.
        """

        start = time.time()

        try:

            #
            # Placeholder transport layer.
            # Real implementation:
            #
            # OTLP/gRPC
            # OTLP/HTTP
            #

            bytes_sent = len(
                str(payload).encode(
                    "utf-8"
                )
            )

            self._last_export = time.time()


            return ExportResult(
                success=True,
                status="SUCCESS",
                message="OTLP export completed",
                exported=1,
                bytes_sent=bytes_sent,
                duration=time.time() - start,
            )


        except Exception as exc:

            return ExportResult(
                success=False,
                status="FAILED",
                message=str(exc),
                exported=0,
                duration=time.time() - start,
            )
# ==============================================================================
# Part 5. Configuration
# ==============================================================================

    def set_endpoint(
        self,
        endpoint: str,
    ) -> "OpenTelemetryExporter":
        """
        Set OTLP endpoint.
        """

        self._endpoint = str(endpoint)

        self._destination = self._endpoint

        self._metadata.update(
            {
                "endpoint": self._endpoint
            }
        )

        return self


    # ------------------------------------------------------------------

    def set_protocol(
        self,
        protocol: str,
    ) -> "OpenTelemetryExporter":
        """
        Set OTLP transport protocol.

        Supported:
            - grpc
            - http
        """

        protocol = protocol.lower().strip()

        if protocol not in {
            "grpc",
            "http",
            "http/protobuf",
            "http/json",
        }:
            raise ValueError(
                f"Unsupported OTLP protocol: {protocol}"
            )

        self._protocol = protocol

        self._metadata.update(
            {
                "protocol": protocol
            }
        )

        return self


    # ------------------------------------------------------------------

    def set_headers(
        self,
        headers: Mapping[str, str],
    ) -> "OpenTelemetryExporter":
        """
        Set OTLP request headers.
        """

        self._headers = dict(headers)

        return self


    # ------------------------------------------------------------------

    def set_resource(
        self,
        resource: ResourceAttributes,
    ) -> "OpenTelemetryExporter":
        """
        Set OpenTelemetry resource.
        """

        if not isinstance(
            resource,
            ResourceAttributes,
        ):
            raise TypeError(
                "resource must be ResourceAttributes"
            )

        self._resource = resource

        self._metadata.update(
            {
                "service":
                    resource.service_name,

                "service_version":
                    resource.service_version,
            }
        )

        return self


    # ------------------------------------------------------------------

    def set_scope(
        self,
        scope: InstrumentationScope,
    ) -> "OpenTelemetryExporter":
        """
        Set instrumentation scope.
        """

        if not isinstance(
            scope,
            InstrumentationScope,
        ):
            raise TypeError(
                "scope must be InstrumentationScope"
            )

        self._scope = scope

        return self


    # ------------------------------------------------------------------

    def options(
        self,
    ) -> Dict[str, Any]:
        """
        Return current OpenTelemetry configuration.
        """

        return {
            "endpoint": self._endpoint,

            "protocol": self._protocol,

            "timeout": self._timeout,

            "batch_size": self._batch_size,

            "headers": dict(
                self._headers
            ),

            "resource": {
                "service_name":
                    self._resource.service_name,

                "service_version":
                    self._resource.service_version,

                "attributes":
                    dict(
                        self._resource.attributes
                    ),
            },

            "scope": {
                "name":
                    self._scope.name,

                "version":
                    self._scope.version,

                "schema_url":
                    self._scope.schema_url,
            },
        }


    # ------------------------------------------------------------------

    def reset(
        self,
    ) -> "OpenTelemetryExporter":
        """
        Reset OpenTelemetry configuration.
        """

        self._endpoint = DEFAULT_ENDPOINT

        self._destination = DEFAULT_ENDPOINT

        self._protocol = DEFAULT_PROTOCOL

        self._timeout = DEFAULT_TIMEOUT

        self._batch_size = DEFAULT_BATCH_SIZE

        self._headers.clear()

        self._resource = ResourceAttributes()

        self._scope = InstrumentationScope()


        self._metadata.update(
            {
                "endpoint":
                    self._endpoint,

                "protocol":
                    self._protocol,

                "service":
                    self._resource.service_name,
            }
        )

        return self
# ==============================================================================
# Part 6. Runtime Operations
# ==============================================================================

    def snapshot(
        self,
    ) -> Dict[str, Any]:
        """
        Create OpenTelemetry runtime snapshot.
        """

        state = super().snapshot()

        state["opentelemetry"] = {

            "endpoint":
                self._endpoint,

            "protocol":
                self._protocol,

            "headers":
                dict(
                    self._headers
                ),

            "resource":
                {
                    "service_name":
                        self._resource.service_name,

                    "service_version":
                        self._resource.service_version,

                    "attributes":
                        dict(
                            self._resource.attributes
                        ),
                },

            "scope":
                {
                    "name":
                        self._scope.name,

                    "version":
                        self._scope.version,

                    "schema_url":
                        self._scope.schema_url,
                },


            "spans":
                copy.deepcopy(
                    self._spans
                ),

            "metrics":
                copy.deepcopy(
                    self._metrics
                ),

            "logs":
                copy.deepcopy(
                    self._logs
                ),


            "statistics":
                {
                    "spans_exported":
                        self._spans_exported,

                    "metrics_exported":
                        self._metrics_exported,

                    "logs_exported":
                        self._logs_exported,

                    "batches_exported":
                        self._batches_exported,

                    "last_export":
                        self._last_export,
                },
        }

        return state


    # ------------------------------------------------------------------

    def restore(
        self,
        snapshot: Dict[str, Any],
    ) -> "OpenTelemetryExporter":
        """
        Restore exporter runtime state.
        """

        super().restore(
            snapshot
        )

        state = snapshot.get(
            "opentelemetry",
            {},
        )


        self._endpoint = state.get(
            "endpoint",
            DEFAULT_ENDPOINT,
        )


        self._protocol = state.get(
            "protocol",
            DEFAULT_PROTOCOL,
        )


        self._headers = dict(
            state.get(
                "headers",
                {},
            )
        )


        resource = state.get(
            "resource",
            {},
        )

        self._resource = ResourceAttributes(
            service_name=
                resource.get(
                    "service_name",
                    DEFAULT_SERVICE_NAME,
                ),

            service_version=
                resource.get(
                    "service_version",
                    DEFAULT_SERVICE_VERSION,
                ),

            attributes=
                resource.get(
                    "attributes",
                    {},
                ),
        )


        scope = state.get(
            "scope",
            {},
        )

        self._scope = InstrumentationScope(
            name=
                scope.get(
                    "name",
                    "SciOS",
                ),

            version=
                scope.get(
                    "version",
                    "0.1.0",
                ),

            schema_url=
                scope.get(
                    "schema_url",
                    "",
                ),
        )


        self._spans = copy.deepcopy(
            state.get(
                "spans",
                [],
            )
        )


        self._metrics = copy.deepcopy(
            state.get(
                "metrics",
                [],
            )
        )


        self._logs = copy.deepcopy(
            state.get(
                "logs",
                [],
            )
        )


        statistics = state.get(
            "statistics",
            {},
        )


        self._spans_exported = statistics.get(
            "spans_exported",
            0,
        )

        self._metrics_exported = statistics.get(
            "metrics_exported",
            0,
        )

        self._logs_exported = statistics.get(
            "logs_exported",
            0,
        )

        self._batches_exported = statistics.get(
            "batches_exported",
            0,
        )

        self._last_export = statistics.get(
            "last_export",
        )


        return self


    # ------------------------------------------------------------------

    def clone(
        self,
    ) -> "OpenTelemetryExporter":
        """
        Create deep clone.
        """

        return copy.deepcopy(
            self
        )


    # ------------------------------------------------------------------

    def copy(
        self,
    ) -> "OpenTelemetryExporter":
        """
        Create shallow copy.
        """

        return copy.copy(
            self
        )


    # ------------------------------------------------------------------

    def cleanup(
        self,
    ) -> "OpenTelemetryExporter":
        """
        Cleanup transient telemetry buffers.
        """

        super().cleanup()


        with self._lock:

            self._spans.clear()

            self._metrics.clear()

            self._logs.clear()


        self._last_export = None


        return self


    # ------------------------------------------------------------------

    def compact(
        self,
    ) -> "OpenTelemetryExporter":
        """
        Reduce runtime memory footprint.
        """

        super().compact()


        with self._lock:

            #
            # Keep configuration and statistics.
            # Remove buffered telemetry.
            #

            self._spans = []

            self._metrics = []

            self._logs = []


        return self
# ==============================================================================
# Part 7. Statistics
# ==============================================================================


    @property
    def spans_exported(
        self,
    ) -> int:
        """
        Number of exported spans.
        """

        return self._spans_exported


    # ------------------------------------------------------------------

    @property
    def metrics_exported(
        self,
    ) -> int:
        """
        Number of exported metrics.
        """

        return self._metrics_exported


    # ------------------------------------------------------------------

    @property
    def logs_exported(
        self,
    ) -> int:
        """
        Number of exported logs.
        """

        return self._logs_exported


    # ------------------------------------------------------------------

    @property
    def batches_exported(
        self,
    ) -> int:
        """
        Number of exported batches.
        """

        return self._batches_exported


    # ------------------------------------------------------------------

    def report(
        self,
    ) -> Dict[str, Any]:
        """
        Generate detailed exporter report.
        """

        uptime = (
            time.time()
            -
            self._created_at
        )

        return {

            "exporter":
                self._name,


            "type":
                self._exporter_type,


            "version":
                self._version,


            "status":
                self.status,


            "endpoint":
                self._endpoint,


            "protocol":
                self._protocol,


            "resource":
                {
                    "service_name":
                        self._resource.service_name,

                    "service_version":
                        self._resource.service_version,
                },


            "telemetry":
                {
                    "spans_exported":
                        self._spans_exported,

                    "metrics_exported":
                        self._metrics_exported,

                    "logs_exported":
                        self._logs_exported,

                    "batches_exported":
                        self._batches_exported,
                },


            "buffer":
                {
                    "spans_pending":
                        len(self._spans),

                    "metrics_pending":
                        len(self._metrics),

                    "logs_pending":
                        len(self._logs),
                },


            "runtime":
                {
                    "uptime":
                        uptime,

                    "last_export":
                        self._last_export,
                },
        }


    # ------------------------------------------------------------------

    def summary(
        self,
    ) -> Dict[str, Any]:
        """
        Generate compact exporter summary.
        """

        return {

            "name":
                self._name,


            "type":
                self._exporter_type,


            "status":
                self.status,


            "spans":
                self._spans_exported,


            "metrics":
                self._metrics_exported,


            "logs":
                self._logs_exported,


            "batches":
                self._batches_exported,


            "pending":
                (
                    len(self._spans)
                    +
                    len(self._metrics)
                    +
                    len(self._logs)
                ),
        }
# ==============================================================================
# Part 8. Validation
# ==============================================================================


    def validate(
        self,
        record: Any,
    ) -> bool:
        """
        Validate generic telemetry record.
        """

        if isinstance(
            record,
            OTelSpan,
        ):
            return self.validate_span(
                record
            )

        if isinstance(
            record,
            OTelMetric,
        ):
            return self.validate_metric(
                record
            )

        if isinstance(
            record,
            OTelLog,
        ):
            return self.validate_log(
                record
            )

        return False


    # ------------------------------------------------------------------

    def validate_span(
        self,
        span: OTelSpan,
    ) -> bool:
        """
        Validate OpenTelemetry span.
        """

        if not span.trace_id:
            return False

        if not span.span_id:
            return False

        if not span.name:
            return False

        if span.start_time <= 0:
            return False

        if (
            span.end_time is not None
            and
            span.end_time < span.start_time
        ):
            return False


        return True


    # ------------------------------------------------------------------

    def validate_metric(
        self,
        metric: OTelMetric,
    ) -> bool:
        """
        Validate OpenTelemetry metric.
        """

        if not metric.name:
            return False


        if not isinstance(
            metric.value,
            (
                int,
                float,
            ),
        ):
            return False


        if metric.timestamp <= 0:
            return False


        return True


    # ------------------------------------------------------------------

    def validate_log(
        self,
        log: OTelLog,
    ) -> bool:
        """
        Validate OpenTelemetry log.
        """

        if not log.message:
            return False


        if log.timestamp <= 0:
            return False


        if not log.severity:
            return False


        return True


    # ------------------------------------------------------------------

    def validate_endpoint(
        self,
        endpoint: Optional[str] = None,
    ) -> bool:
        """
        Validate OTLP endpoint.
        """

        endpoint = (
            endpoint
            or
            self._endpoint
        )


        if not endpoint:
            return False


        valid_prefix = (
            "http://",
            "https://",
        )


        return endpoint.startswith(
            valid_prefix
        )


    # ------------------------------------------------------------------

    def check_integrity(
        self,
    ) -> Dict[str, Any]:
        """
        Check exporter internal integrity.
        """

        return {

            "valid_endpoint":
                self.validate_endpoint(),


            "resource_valid":
                bool(
                    self._resource.service_name
                ),


            "scope_valid":
                bool(
                    self._scope.name
                ),


            "buffer_state":
                {
                    "spans":
                        all(
                            self.validate_span(
                                span
                            )
                            for span
                            in self._spans
                        ),

                    "metrics":
                        all(
                            self.validate_metric(
                                metric
                            )
                            for metric
                            in self._metrics
                        ),

                    "logs":
                        all(
                            self.validate_log(
                                log
                            )
                            for log
                            in self._logs
                        ),
                },


            "healthy":
                (
                    self.validate_endpoint()
                    and
                    bool(
                        self._resource.service_name
                    )
                ),
        }
# ==============================================================================
# Part 9. Events & Hooks
# ==============================================================================


    def before_collect(
        self,
    ) -> None:
        """
        Hook executed before collecting telemetry.
        """

        self.emit_event(
            "before_collect",
            exporter=self,
        )


    # ------------------------------------------------------------------

    def after_collect(
        self,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Hook executed after telemetry collection.
        """

        self.emit_event(
            "after_collect",
            exporter=self,
            payload=payload,
        )

        return payload


    # ------------------------------------------------------------------

    def before_export(
        self,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Hook executed before export.
        """

        self.emit_event(
            "before_export",
            exporter=self,
            payload=payload,
        )

        return payload


    # ------------------------------------------------------------------

    def after_export(
        self,
        result: ExportResult,
    ) -> ExportResult:
        """
        Hook executed after export.
        """

        self.emit_event(
            "after_export",
            exporter=self,
            result=result,
        )

        return result


    # ------------------------------------------------------------------

    def before_flush(
        self,
    ) -> None:
        """
        Hook executed before flushing telemetry.
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
        Hook executed after flushing telemetry.
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
        **payload: Any,
    ) -> None:
        """
        Emit exporter lifecycle event.
        """

        super().emit_event(
            event,
            **payload,
        )
# ==============================================================================
# Part 10. Python Protocols
# ==============================================================================


    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"name={self._name!r}, "
            f"endpoint={self._endpoint!r}, "
            f"protocol={self._protocol!r}, "
            f"spans={len(self._spans)}, "
            f"metrics={len(self._metrics)}, "
            f"logs={len(self._logs)}, "
            f"status={self.status!r}"
            f")"
        )


    # ------------------------------------------------------------------

    def __str__(
        self,
    ) -> str:
        """
        Human readable representation.
        """

        return (
            f"{self._name} "
            f"[OpenTelemetry] "
            f"{self._protocol}://"
            f"{self._endpoint}"
        )


    # ------------------------------------------------------------------

    def __len__(
        self,
    ) -> int:
        """
        Return pending telemetry count.
        """

        return (
            len(self._spans)
            +
            len(self._metrics)
            +
            len(self._logs)
        )


    # ------------------------------------------------------------------

    def __call__(
        self,
        data: Any,
    ) -> ExportResult:
        """
        Shortcut export API.

        Supports:
            exporter(span)
            exporter(metric)
            exporter(log)
        """

        if isinstance(
            data,
            OTelSpan,
        ):
            return self.export_span(
                data
            )


        if isinstance(
            data,
            OTelMetric,
        ):
            return self.export_metric(
                data
            )


        if isinstance(
            data,
            OTelLog,
        ):
            return self.export_log(
                data
            )


        return self.export(
            data
        )


    # ------------------------------------------------------------------

    def __copy__(
        self,
    ) -> "OpenTelemetryExporter":
        """
        Shallow copy.
        """

        return self.copy()


    # ------------------------------------------------------------------

    def __deepcopy__(
        self,
        memo: Optional[Dict[int, Any]] = None,
    ) -> "OpenTelemetryExporter":
        """
        Deep copy.

        Used by clone().
        """

        return self.clone()                                                                            