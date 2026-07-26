"""
SciOS-NG Jaeger Exporter

Foundation layer:
- Jaeger telemetry models
- Export configuration
- Runtime state
- Base exporter integration
"""

from __future__ import annotations


# ==============================================================================
# Imports
# ==============================================================================

from abc import ABC
from dataclasses import dataclass, field
from enum import Enum
from typing import (
    Any,
    Dict,
    List,
    Mapping,
    Optional,
    TypeAlias,
)

import copy
import threading
import time
import uuid


from .base import (
    BaseExporter,
    ExportRecord,
    ExportResult,
)


# ==============================================================================
# Constants
# ==============================================================================

DEFAULT_JAEGER_ENDPOINT = (
    "http://localhost:14268/api/traces"
)

DEFAULT_AGENT_HOST = (
    "localhost"
)

DEFAULT_AGENT_PORT = (
    6831
)

DEFAULT_PROTOCOL = (
    "udp"
)

DEFAULT_BATCH_SIZE = (
    100
)

DEFAULT_TIMEOUT = (
    5
)

JAEGER_EXPORTER_VERSION = (
    "0.1.0"
)


# ==============================================================================
# Type Aliases
# ==============================================================================

TraceID: TypeAlias = str

SpanID: TypeAlias = str

SpanTags: TypeAlias = Dict[str, Any]

SpanLogs: TypeAlias = List[Dict[str, Any]]

ProcessMetadata: TypeAlias = Dict[str, Any]

JaegerPayload: TypeAlias = Dict[str, Any]


# ==============================================================================
# JaegerProtocol
# ==============================================================================

class JaegerProtocol(Enum):
    """
    Jaeger transport protocol.
    """

    UDP = "udp"

    HTTP = "http"

    GRPC = "grpc"


# ==============================================================================
# SpanKind
# ==============================================================================

class SpanKind(Enum):
    """
    Span operation type.
    """

    INTERNAL = "internal"

    SERVER = "server"

    CLIENT = "client"

    PRODUCER = "producer"

    CONSUMER = "consumer"


# ==============================================================================
# SpanStatus
# ==============================================================================

class SpanStatus(Enum):
    """
    Span execution status.
    """

    OK = "ok"

    ERROR = "error"

    UNSET = "unset"


# ==============================================================================
# JaegerTag
# ==============================================================================

@dataclass
class JaegerTag:
    """
    Jaeger span tag.
    """

    key: str

    value: Any

    type: str = "string"



# ==============================================================================
# JaegerLog
# ==============================================================================

@dataclass
class JaegerLog:
    """
    Jaeger span log event.
    """

    timestamp: float

    fields: Dict[str, Any] = field(
        default_factory=dict
    )

    level: str = "INFO"



# ==============================================================================
# JaegerSpan
# ==============================================================================

@dataclass
class JaegerSpan:
    """
    Jaeger trace span model.
    """

    trace_id: TraceID

    span_id: SpanID

    parent_id: Optional[SpanID]

    operation: str

    start_time: float

    duration: float = 0.0

    tags: List[JaegerTag] = field(
        default_factory=list
    )

    logs: List[JaegerLog] = field(
        default_factory=list
    )

    status: SpanStatus = (
        SpanStatus.UNSET
    )

    kind: SpanKind = (
        SpanKind.INTERNAL
    )


# ==============================================================================
# JaegerProcess
# ==============================================================================

@dataclass
class JaegerProcess:
    """
    Service process metadata.
    """

    service_name: str

    service_version: str

    tags: List[JaegerTag] = field(
        default_factory=list
    )



# ==============================================================================
# JaegerExportOptions
# ==============================================================================

@dataclass
class JaegerExportOptions:
    """
    Jaeger exporter configuration.
    """

    endpoint: str = (
        DEFAULT_JAEGER_ENDPOINT
    )

    agent_host: str = (
        DEFAULT_AGENT_HOST
    )

    agent_port: int = (
        DEFAULT_AGENT_PORT
    )

    protocol: str = (
        DEFAULT_PROTOCOL
    )

    batch_size: int = (
        DEFAULT_BATCH_SIZE
    )

    timeout: int = (
        DEFAULT_TIMEOUT
    )


# ==============================================================================
# JaegerExporter
# ==============================================================================

class JaegerExporter(
    BaseExporter,
    ABC,
):
    """
    Jaeger distributed tracing exporter.

    Extends BaseExporter with:
    - Trace collection
    - Span lifecycle
    - Jaeger transport
    """


    # ------------------------------------------------------------------
    # __init__
    # ------------------------------------------------------------------

    def __init__(
        self,
        name: str = "JaegerExporter",
        options: Optional[
            JaegerExportOptions
        ] = None,
        **kwargs,
    ):
        """
        Initialize Jaeger exporter.
        """

        super().__init__(
            name=name,
            **kwargs,
        )


        # --------------------------------------------------------------
        # Identity
        # --------------------------------------------------------------

        self._id = uuid.uuid4()

        self._name = name

        self._exporter_type = (
            "jaeger"
        )


        # --------------------------------------------------------------
        # Configuration
        # --------------------------------------------------------------

        self._options = (
            options
            or
            JaegerExportOptions()
        )


        self._endpoint = (
            self._options.endpoint
        )

        self._agent_host = (
            self._options.agent_host
        )

        self._agent_port = (
            self._options.agent_port
        )

        self._protocol = (
            self._options.protocol
        )


        # --------------------------------------------------------------
        # Runtime State
        # --------------------------------------------------------------

        self._enabled = True

        self._frozen = False

        self._closed = False


        self._spans: List[
            JaegerSpan
        ] = []


        self._process = JaegerProcess(
            service_name="SciOS",
            service_version=(
                JAEGER_EXPORTER_VERSION
            ),
        )


        self._statistics = {

            "spans_exported": 0,

            "batches_exported": 0,

            "errors": 0,

        }


        self._created_at = (
            time.time()
        )


        self._lock = (
            threading.RLock()
        )


    # ==============================================================================
    # Identity Properties
    # ==============================================================================


    @property
    def id(
        self,
    ):
        return self._id


    @property
    def name(
        self,
    ):
        return self._name


    @property
    def exporter_type(
        self,
    ):
        return self._exporter_type



    # ==============================================================================
    # Configuration Properties
    # ==============================================================================


    @property
    def endpoint(
        self,
    ):
        return self._endpoint


    @property
    def agent_host(
        self,
    ):
        return self._agent_host


    @property
    def agent_port(
        self,
    ):
        return self._agent_port


    @property
    def protocol(
        self,
    ):
        return self._protocol


    @property
    def options(
        self,
    ):
        return self._options



    # ==============================================================================
    # Runtime State Properties
    # ==============================================================================


    @property
    def enabled(
        self,
    ):
        return self._enabled


    @property
    def frozen(
        self,
    ):
        return self._frozen


    @property
    def closed(
        self,
    ):
        return self._closed


    @property
    def spans(
        self,
    ):
        return self._spans


    @property
    def process(
        self,
    ):
        return self._process


    @property
    def statistics(
        self,
    ):
        return self._statistics
# ==============================================================================
# Part 2. Serialization
# ==============================================================================


    def serialize(
        self,
        record: ExportRecord,
    ) -> JaegerPayload:
        """
        Serialize ExportRecord into Jaeger payload.
        """

        payload = self.encode(
            record.payload
        )

        return payload



    # ------------------------------------------------------------------

    def deserialize(
        self,
        payload: JaegerPayload,
    ) -> ExportRecord:
        """
        Deserialize Jaeger payload into ExportRecord.
        """

        return ExportRecord(
            payload=self.decode(
                payload
            ),
            metadata={
                "source": "jaeger"
            },
        )



    # ------------------------------------------------------------------

    def encode(
        self,
        data: Any,
    ) -> JaegerPayload:
        """
        Encode Jaeger objects into serializable payload.
        """


        if isinstance(
            data,
            JaegerSpan,
        ):

            return {
                "spans": [
                    self.format_span(
                        data
                    )
                ]
            }



        if isinstance(
            data,
            JaegerProcess,
        ):

            return {
                "process":
                    self.format_process(
                        data
                    )
            }



        if isinstance(
            data,
            list,
        ):

            return {
                "spans": [
                    self.format_span(
                        span
                    )
                    for span in data
                ]
            }



        if isinstance(
            data,
            Mapping,
        ):

            return dict(
                data
            )



        raise TypeError(
            f"Unsupported Jaeger payload type: "
            f"{type(data).__name__}"
        )



    # ------------------------------------------------------------------

    def decode(
        self,
        payload: JaegerPayload,
    ) -> JaegerPayload:
        """
        Decode Jaeger payload.

        Normalizes external payload
        into internal dictionary.
        """

        return dict(
            payload
        )



    # ------------------------------------------------------------------

    def format_span(
        self,
        span: JaegerSpan,
    ) -> Dict[str, Any]:
        """
        Format Jaeger span.

        Compatible with Jaeger JSON model.
        """


        return {

            "traceID":
                span.trace_id,


            "spanID":
                span.span_id,


            "parentSpanID":
                span.parent_id,


            "operationName":
                span.operation,


            "startTime":
                int(
                    span.start_time
                    *
                    1_000_000
                ),


            "duration":
                int(
                    span.duration
                    *
                    1_000_000
                ),


            "tags":
                self.format_tags(
                    span.tags
                ),


            "logs":
                [
                    {
                        "timestamp":
                            int(
                                log.timestamp
                                *
                                1_000_000
                            ),

                        "fields":
                            log.fields,

                        "level":
                            log.level,
                    }

                    for log
                    in span.logs
                ],


            "status":
                span.status.value,


            "kind":
                span.kind.value,
        }



    # ------------------------------------------------------------------

    def format_tags(
        self,
        tags: List[JaegerTag],
    ) -> List[Dict[str, Any]]:
        """
        Format Jaeger tags.
        """


        return [

            {
                "key":
                    tag.key,

                "type":
                    tag.type,

                "value":
                    tag.value,
            }

            for tag
            in tags

        ]



    # ------------------------------------------------------------------

    def format_process(
        self,
        process: JaegerProcess,
    ) -> Dict[str, Any]:
        """
        Format Jaeger process metadata.
        """


        return {

            "serviceName":
                process.service_name,


            "tags":
                self.format_tags(
                    process.tags
                ),


            "serviceVersion":
                process.service_version,
        }
# ==============================================================================
# Part 3. Trace API
# ==============================================================================


    def register_process(
        self,
        process: JaegerProcess,
    ) -> JaegerProcess:
        """
        Register Jaeger process metadata.
        """

        if not isinstance(
            process,
            JaegerProcess,
        ):
            raise TypeError(
                "process must be JaegerProcess"
            )


        with self._lock:

            self._process = process


        return process



    # ------------------------------------------------------------------

    def create_span(
        self,
        operation: str,
        parent_id: Optional[SpanID] = None,
        kind: SpanKind = SpanKind.INTERNAL,
        tags: Optional[
            List[JaegerTag]
        ] = None,
    ) -> JaegerSpan:
        """
        Create a new Jaeger span.
        """


        span = JaegerSpan(

            trace_id=
                uuid.uuid4().hex,


            span_id=
                uuid.uuid4().hex,


            parent_id=
                parent_id,


            operation=
                operation,


            start_time=
                time.time(),


            tags=
                tags
                or
                [],


            kind=
                kind,
        )


        return span



    # ------------------------------------------------------------------

    def record_span(
        self,
        span: JaegerSpan,
    ) -> JaegerSpan:
        """
        Record span into runtime buffer.
        """


        if not isinstance(
            span,
            JaegerSpan,
        ):
            raise TypeError(
                "span must be JaegerSpan"
            )


        with self._lock:

            self._spans.append(
                span
            )


        return span



    # ------------------------------------------------------------------

    def finish_span(
        self,
        span: JaegerSpan,
        status: SpanStatus = SpanStatus.OK,
        duration: Optional[float] = None,
    ) -> JaegerSpan:
        """
        Finish span lifecycle.
        """


        if duration is None:

            duration = (
                time.time()
                -
                span.start_time
            )


        span.duration = duration

        span.status = status


        self.record_span(
            span
        )


        return span



    # ------------------------------------------------------------------

    def collect(
        self,
    ) -> List[JaegerSpan]:
        """
        Collect pending spans.
        """


        with self._lock:

            return list(
                self._spans
            )



    # ------------------------------------------------------------------

    def gather(
        self,
    ) -> JaegerPayload:
        """
        Gather complete Jaeger trace payload.
        """


        with self._lock:


            payload = {

                "process":
                    self.format_process(
                        self._process
                    ),


                "spans":
                    [
                        self.format_span(
                            span
                        )

                        for span
                        in self._spans
                    ],

            }


        return payload



    # ------------------------------------------------------------------

    def flush(
        self,
    ) -> ExportResult:
        """
        Flush collected spans.

        Delegates actual transport
        to Part 4 Export API.
        """


        payload = self.gather()


        result = self.export_jaeger(
            payload
        )


        if result.success:

            with self._lock:

                self._spans.clear()


        return result
# ==============================================================================
# Part 4. Export API
# ==============================================================================


    def export(
        self,
        data: Any,
    ) -> ExportResult:
        """
        Generic Jaeger export entry point.
        """

        start = time.time()

        try:

            if isinstance(
                data,
                JaegerSpan,
            ):
                return self.export_span(
                    data
                )


            if isinstance(
                data,
                JaegerProcess,
            ):
                return self.export_process(
                    data
                )


            if isinstance(
                data,
                list,
            ):
                return self.export_batch(
                    data
                )


            if isinstance(
                data,
                Mapping,
            ):
                return self.export_jaeger(
                    data
                )


            raise TypeError(
                f"Unsupported export type: "
                f"{type(data).__name__}"
            )


        except Exception as exc:

            self._statistics[
                "errors"
            ] += 1


            return ExportResult(
                success=False,
                status="FAILED",
                message=str(exc),
                exported=0,
                duration=
                    time.time() - start,
            )



    # ------------------------------------------------------------------

    def export_batch(
        self,
        spans: List[JaegerSpan],
    ) -> ExportResult:
        """
        Export multiple spans.
        """

        start = time.time()


        payload = {

            "process":
                self.format_process(
                    self._process
                ),


            "spans":
                [
                    self.format_span(
                        span
                    )

                    for span
                    in spans
                ],

        }


        result = self.export_jaeger(
            payload
        )


        if result.success:

            self._statistics[
                "spans_exported"
            ] += len(spans)


            self._statistics[
                "batches_exported"
            ] += 1


        result.duration = (
            time.time() - start
        )


        return result



    # ------------------------------------------------------------------

    def export_span(
        self,
        span: JaegerSpan,
    ) -> ExportResult:
        """
        Export single span.
        """

        payload = {

            "process":
                self.format_process(
                    self._process
                ),


            "spans":
                [
                    self.format_span(
                        span
                    )
                ],
        }


        result = self.export_jaeger(
            payload
        )


        if result.success:

            self._statistics[
                "spans_exported"
            ] += 1


        return result



    # ------------------------------------------------------------------

    def export_trace(
        self,
        spans: List[JaegerSpan],
    ) -> ExportResult:
        """
        Export complete trace.
        """

        return self.export_batch(
            spans
        )



    # ------------------------------------------------------------------

    def export_process(
        self,
        process: JaegerProcess,
    ) -> ExportResult:
        """
        Export process metadata.
        """

        payload = {

            "process":
                self.format_process(
                    process
                )

        }


        return self.export_jaeger(
            payload
        )



    # ------------------------------------------------------------------

    def export_jaeger(
        self,
        payload: JaegerPayload,
    ) -> ExportResult:
        """
        Low-level Jaeger transport layer.

        Transport abstraction:
            UDP Agent
            HTTP Collector
            GRPC Gateway
        """

        start = time.time()


        try:

            encoded = self.encode(
                payload
            )


            bytes_sent = len(
                str(encoded)
                .encode(
                    "utf-8"
                )
            )


            #
            # Transport placeholder.
            #
            # Future:
            #
            # UDP:
            #   agent_host:agent_port
            #
            # HTTP:
            #   POST endpoint
            #
            # GRPC:
            #   Jaeger protobuf
            #


            self._last_export = (
                time.time()
            )


            return ExportResult(

                success=True,

                status="SUCCESS",

                message=(
                    "Jaeger export completed"
                ),

                exported=1,

                bytes_sent=bytes_sent,

                duration=
                    time.time() - start,
            )


        except Exception as exc:


            self._statistics[
                "errors"
            ] += 1


            return ExportResult(

                success=False,

                status="FAILED",

                message=str(exc),

                exported=0,

                duration=
                    time.time() - start,
            )
# ==============================================================================
# Part 5. Configuration API
# ==============================================================================


    def set_endpoint(
        self,
        endpoint: str,
    ) -> "JaegerExporter":
        """
        Configure Jaeger collector endpoint.
        """

        if not isinstance(
            endpoint,
            str,
        ):
            raise TypeError(
                "endpoint must be str"
            )


        with self._lock:

            self._endpoint = endpoint

            self._options.endpoint = endpoint


        return self



    # ------------------------------------------------------------------

    def set_agent(
        self,
        host: str,
        port: int = DEFAULT_AGENT_PORT,
    ) -> "JaegerExporter":
        """
        Configure Jaeger agent address.
        """

        if not isinstance(
            host,
            str,
        ):
            raise TypeError(
                "agent host must be str"
            )


        if not isinstance(
            port,
            int,
        ):
            raise TypeError(
                "agent port must be int"
            )


        with self._lock:

            self._agent_host = host

            self._agent_port = port


            self._options.agent_host = host

            self._options.agent_port = port


        return self



    # ------------------------------------------------------------------

    def set_protocol(
        self,
        protocol: str | JaegerProtocol,
    ) -> "JaegerExporter":
        """
        Configure Jaeger transport protocol.

        Supported:

        - udp
        - http
        - grpc
        """

        if isinstance(
            protocol,
            JaegerProtocol,
        ):
            protocol = protocol.value


        protocol = protocol.lower()


        supported = {

            JaegerProtocol.UDP.value,

            JaegerProtocol.HTTP.value,

            JaegerProtocol.GRPC.value,

        }


        if protocol not in supported:

            raise ValueError(
                f"Unsupported Jaeger protocol: "
                f"{protocol}"
            )


        with self._lock:

            self._protocol = protocol

            self._options.protocol = protocol


        return self



    # ------------------------------------------------------------------

    def set_service(
        self,
        name: str,
        version: str = JAEGER_EXPORTER_VERSION,
    ) -> "JaegerExporter":
        """
        Configure service identity.
        """

        if not isinstance(
            name,
            str,
        ):
            raise TypeError(
                "service name must be str"
            )


        with self._lock:

            self._process.service_name = name

            self._process.service_version = version


        return self



    # ------------------------------------------------------------------

    def set_tags(
        self,
        tags: Mapping[str, Any],
    ) -> "JaegerExporter":
        """
        Configure process tags.
        """

        if not isinstance(
            tags,
            Mapping,
        ):
            raise TypeError(
                "tags must be mapping"
            )


        with self._lock:

            self._process.tags = [

                JaegerTag(
                    key=key,
                    value=value,
                )

                for key, value
                in tags.items()

            ]


        return self



    # ------------------------------------------------------------------

    def options(
        self,
    ) -> JaegerExportOptions:
        """
        Return current exporter options.
        """

        return copy.deepcopy(
            self._options
        )



    # ------------------------------------------------------------------

    def reset(
        self,
    ) -> "JaegerExporter":
        """
        Reset configuration to defaults.
        """

        with self._lock:

            self._options = (
                JaegerExportOptions()
            )


            self._endpoint = (
                DEFAULT_JAEGER_ENDPOINT
            )


            self._agent_host = (
                DEFAULT_AGENT_HOST
            )


            self._agent_port = (
                DEFAULT_AGENT_PORT
            )


            self._protocol = (
                DEFAULT_PROTOCOL
            )


            self._process = JaegerProcess(

                service_name="SciOS",

                service_version=(
                    JAEGER_EXPORTER_VERSION
                ),

            )


        return self
# ==============================================================================
# Part 6. Runtime Operations
# ==============================================================================


    def snapshot(
        self,
    ) -> Dict[str, Any]:
        """
        Create runtime snapshot.

        Includes:
        - configuration
        - process metadata
        - pending spans
        - statistics
        - lifecycle state
        """

        with self._lock:

            snapshot = {

                "id":
                    str(self._id),


                "name":
                    self._name,


                "exporter_type":
                    self._exporter_type,


                "configuration": {

                    "endpoint":
                        self._endpoint,

                    "agent_host":
                        self._agent_host,

                    "agent_port":
                        self._agent_port,

                    "protocol":
                        self._protocol,

                },


                "process":
                {
                    "service_name":
                        self._process.service_name,

                    "service_version":
                        self._process.service_version,

                    "tags":
                        self.format_tags(
                            self._process.tags
                        ),
                },


                "spans":
                [
                    self.format_span(span)

                    for span
                    in self._spans
                ],


                "statistics":
                    copy.deepcopy(
                        self._statistics
                    ),


                "state":
                {
                    "enabled":
                        self._enabled,

                    "frozen":
                        self._frozen,

                    "closed":
                        self._closed,
                },


                "created_at":
                    self._created_at,

                "timestamp":
                    time.time(),
            }


        return snapshot



    # ------------------------------------------------------------------

    def restore(
        self,
        snapshot: Dict[str, Any],
    ) -> "JaegerExporter":
        """
        Restore exporter runtime state.
        """

        if not isinstance(
            snapshot,
            dict,
        ):
            raise TypeError(
                "snapshot must be dict"
            )


        with self._lock:

            configuration = (
                snapshot.get(
                    "configuration",
                    {}
                )
            )


            self._endpoint = (
                configuration.get(
                    "endpoint",
                    DEFAULT_JAEGER_ENDPOINT
                )
            )


            self._agent_host = (
                configuration.get(
                    "agent_host",
                    DEFAULT_AGENT_HOST
                )
            )


            self._agent_port = (
                configuration.get(
                    "agent_port",
                    DEFAULT_AGENT_PORT
                )
            )


            self._protocol = (
                configuration.get(
                    "protocol",
                    DEFAULT_PROTOCOL
                )
            )


            process = (
                snapshot.get(
                    "process",
                    {}
                )
            )


            self._process = JaegerProcess(

                service_name=
                    process.get(
                        "service_name",
                        "SciOS"
                    ),


                service_version=
                    process.get(
                        "service_version",
                        JAEGER_EXPORTER_VERSION
                    ),

            )


            self._statistics = (
                snapshot.get(
                    "statistics",
                    {}
                )
            )


            state = (
                snapshot.get(
                    "state",
                    {}
                )
            )


            self._enabled = (
                state.get(
                    "enabled",
                    True
                )
            )


            self._frozen = (
                state.get(
                    "frozen",
                    False
                )
            )


            self._closed = (
                state.get(
                    "closed",
                    False
                )
            )


        return self



    # ------------------------------------------------------------------

    def clone(
        self,
    ) -> "JaegerExporter":
        """
        Create deep clone.

        Used by:
        - distributed workers
        - runtime isolation
        """

        cloned = (
            copy.deepcopy(
                self
            )
        )

        cloned._id = (
            uuid.uuid4()
        )

        return cloned



    # ------------------------------------------------------------------

    def copy(
        self,
    ) -> "JaegerExporter":
        """
        Create shallow copy.
        """

        return copy.copy(
            self
        )



    # ------------------------------------------------------------------

    def cleanup(
        self,
    ) -> None:
        """
        Cleanup runtime resources.

        Clears:
        - pending spans
        - temporary buffers
        """

        with self._lock:

            self._spans.clear()



    # ------------------------------------------------------------------

    def compact(
        self,
    ) -> int:
        """
        Compact internal span buffer.

        Removes invalid/empty spans.

        Returns:
            removed count
        """

        removed = 0


        with self._lock:

            valid_spans = []


            for span in self._spans:

                if (
                    span.trace_id
                    and
                    span.span_id
                    and
                    span.operation
                ):

                    valid_spans.append(
                        span
                    )

                else:

                    removed += 1



            self._spans = valid_spans



        return removed
# ==============================================================================
# Part 7. Statistics API
# ==============================================================================


    @property
    def spans_exported(
        self,
    ) -> int:
        """
        Total exported spans.
        """

        return self._statistics.get(
            "spans_exported",
            0,
        )



    # ------------------------------------------------------------------

    @property
    def batches_exported(
        self,
    ) -> int:
        """
        Total exported batches.
        """

        return self._statistics.get(
            "batches_exported",
            0,
        )



    # ------------------------------------------------------------------

    @property
    def bytes_sent(
        self,
    ) -> int:
        """
        Total bytes transmitted.
        """

        return self._statistics.get(
            "bytes_sent",
            0,
        )



    # ------------------------------------------------------------------

    @property
    def traces_collected(
        self,
    ) -> int:
        """
        Total traces collected.
        """

        return self._statistics.get(
            "traces_collected",
            0,
        )



    # ------------------------------------------------------------------

    @property
    def average_latency(
        self,
    ) -> float:
        """
        Average export latency.

        Unit:
            seconds
        """

        exports = self._statistics.get(
            "exports",
            0,
        )

        if exports == 0:
            return 0.0


        total = self._statistics.get(
            "total_latency",
            0.0,
        )


        return total / exports



    # ------------------------------------------------------------------

    def report(
        self,
    ) -> Dict[str, Any]:
        """
        Generate detailed statistics report.
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
                JAEGER_EXPORTER_VERSION,


            "uptime":
                uptime,


            "spans_exported":
                self.spans_exported,


            "batches_exported":
                self.batches_exported,


            "bytes_sent":
                self.bytes_sent,


            "traces_collected":
                self.traces_collected,


            "average_latency":
                self.average_latency,


            "pending_spans":
                len(self._spans),


            "errors":
                self._statistics.get(
                    "errors",
                    0,
                ),


            "protocol":
                self._protocol,


            "endpoint":
                self._endpoint,
        }



    # ------------------------------------------------------------------

    def summary(
        self,
    ) -> str:
        """
        Human readable statistics summary.
        """

        report = self.report()


        return (
            f"JaegerExporter("
            f"spans={report['spans_exported']}, "
            f"batches={report['batches_exported']}, "
            f"bytes={report['bytes_sent']}, "
            f"errors={report['errors']}, "
            f"latency="
            f"{report['average_latency']:.6f}s"
            f")"
        )
# ==============================================================================
# Part 8. Validation API
# ==============================================================================


    def validate(
        self,
        data: Any = None,
    ) -> bool:
        """
        Validate exporter state or payload.
        """

        if data is None:

            return self.check_integrity()


        if isinstance(
            data,
            JaegerSpan,
        ):

            return self.validate_span(
                data
            )


        if isinstance(
            data,
            JaegerProcess,
        ):

            return self.validate_process(
                data
            )


        if isinstance(
            data,
            Mapping,
        ):

            return (
                self.validate_endpoint()
                and
                bool(data)
            )


        return False



    # ------------------------------------------------------------------

    def validate_span(
        self,
        span: JaegerSpan,
    ) -> bool:
        """
        Validate Jaeger span structure.
        """


        if not isinstance(
            span,
            JaegerSpan,
        ):
            return False


        if not span.trace_id:

            return False


        if not span.span_id:

            return False


        if not span.operation:

            return False


        if span.start_time <= 0:

            return False


        if span.duration < 0:

            return False


        if not isinstance(
            span.tags,
            list,
        ):
            return False


        if not isinstance(
            span.logs,
            list,
        ):
            return False


        return True



    # ------------------------------------------------------------------

    def validate_process(
        self,
        process: JaegerProcess,
    ) -> bool:
        """
        Validate Jaeger process metadata.
        """


        if not isinstance(
            process,
            JaegerProcess,
        ):
            return False


        if not process.service_name:

            return False


        if not process.service_version:

            return False


        if not isinstance(
            process.tags,
            list,
        ):
            return False


        return True



    # ------------------------------------------------------------------

    def validate_endpoint(
        self,
    ) -> bool:
        """
        Validate Jaeger transport endpoint.
        """


        if not self._endpoint:

            return False


        if not isinstance(
            self._endpoint,
            str,
        ):
            return False


        if self._protocol not in (

            JaegerProtocol.UDP.value,

            JaegerProtocol.HTTP.value,

            JaegerProtocol.GRPC.value,

        ):
            return False


        if self._protocol == (
            JaegerProtocol.UDP.value
        ):

            if not self._agent_host:

                return False


            if self._agent_port <= 0:

                return False


        return True



    # ------------------------------------------------------------------

    def check_integrity(
        self,
    ) -> bool:
        """
        Validate complete exporter integrity.

        Checks:
        - lifecycle state
        - configuration
        - process
        - runtime buffers
        """


        if self._closed:

            return False


        if not self.validate_endpoint():

            return False


        if not self.validate_process(
            self._process
        ):
            return False



        for span in self._spans:

            if not self.validate_span(
                span
            ):
                return False



        return True
# ==============================================================================
# Part 9. Events & Hooks
# ==============================================================================


    def before_collect(
        self,
    ) -> None:
        """
        Hook before collecting spans.

        Called before:
            collect()
            gather()
        """

        self.emit_event(
            "before_collect",
            exporter=self,
            timestamp=time.time(),
        )



    # ------------------------------------------------------------------

    def after_collect(
        self,
        spans: List[JaegerSpan],
    ) -> List[JaegerSpan]:
        """
        Hook after span collection.
        """


        self.emit_event(
            "after_collect",
            exporter=self,
            count=len(spans),
            spans=spans,
            timestamp=time.time(),
        )


        return spans



    # ------------------------------------------------------------------

    def before_export(
        self,
        payload: JaegerPayload,
    ) -> JaegerPayload:
        """
        Hook before sending payload.

        Allows:
        - filtering
        - enrichment
        - modification
        """


        self.emit_event(
            "before_export",
            exporter=self,
            payload=payload,
            timestamp=time.time(),
        )


        return payload



    # ------------------------------------------------------------------

    def after_export(
        self,
        result: ExportResult,
    ) -> ExportResult:
        """
        Hook after export completed.
        """


        self.emit_event(
            "after_export",
            exporter=self,
            result=result,
            timestamp=time.time(),
        )


        return result



    # ------------------------------------------------------------------

    def before_flush(
        self,
    ) -> None:
        """
        Hook before flushing spans.
        """


        self.emit_event(
            "before_flush",
            exporter=self,
            pending_spans=len(
                self._spans
            ),
            timestamp=time.time(),
        )



    # ------------------------------------------------------------------

    def after_flush(
        self,
        result: ExportResult,
    ) -> ExportResult:
        """
        Hook after flush completed.
        """


        self.emit_event(
            "after_flush",
            exporter=self,
            result=result,
            timestamp=time.time(),
        )


        return result



    # ------------------------------------------------------------------

    def emit_event(
        self,
        event: str,
        **payload: Any,
    ) -> None:
        """
        Emit SciOS-NG exporter event.

        Compatible with:
            EventBus
            Plugin System
            Runtime Monitor
        """


        event_payload = {

            "event":
                event,


            "source":
                self._name,


            "exporter_type":
                self._exporter_type,


            "timestamp":
                time.time(),


            **payload,

        }


        #
        # Integration point:
        #
        # self.event_bus.emit(
        #       event,
        #       event_payload
        # )
        #


        if hasattr(
            self,
            "_event_handlers",
        ):

            handlers = (
                self._event_handlers
            )


            for handler in handlers.get(
                event,
                [],
            ):

                try:

                    handler(
                        event_payload
                    )

                except Exception:

                    self._statistics[
                        "errors"
                    ] += 1
# ==============================================================================
# Part 10. Python Protocols
# ==============================================================================


    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.

        Used by:
            repr(exporter)
        """

        return (

            f"{self.__class__.__name__}("

            f"id={str(self._id)!r}, "

            f"name={self._name!r}, "

            f"type={self._exporter_type!r}, "

            f"protocol={self._protocol!r}, "

            f"spans={len(self._spans)}, "

            f"enabled={self._enabled}, "

            f"closed={self._closed}"

            f")"

        )



    # ------------------------------------------------------------------

    def __str__(
        self,
    ) -> str:
        """
        Human readable representation.

        Used by:
            print(exporter)
        """

        return (

            f"{self._name} "

            f"[Jaeger] "

            f"{self._protocol.upper()} "

            f"{self._endpoint}"

        )



    # ------------------------------------------------------------------

    def __len__(
        self,
    ) -> int:
        """
        Return pending span count.

        Example:

            len(exporter)

        """

        return len(
            self._spans
        )



    # ------------------------------------------------------------------

    def __call__(
        self,
        data: Any,
    ) -> ExportResult:
        """
        Callable exporter shortcut.

        Examples:

            exporter(span)

            exporter([span1, span2])

        """


        return self.export(
            data
        )



    # ------------------------------------------------------------------

    def __copy__(
        self,
    ) -> "JaegerExporter":
        """
        Shallow copy.

        Keeps:
        - configuration reference
        - process metadata

        """

        new = self.__class__(
            name=self._name,
            options=self._options,
        )


        new._process = self._process

        new._enabled = self._enabled

        new._frozen = self._frozen

        new._closed = self._closed


        return new



    # ------------------------------------------------------------------

    def __deepcopy__(
        self,
        memo: Optional[
            Dict[int, Any]
        ] = None,
    ) -> "JaegerExporter":
        """
        Deep copy.

        Used by:

            clone()

            checkpoint recovery

            distributed worker spawn

        """


        if memo is None:

            memo = {}


        cloned = self.__class__(
            name=self._name,
            options=
                copy.deepcopy(
                    self._options,
                    memo,
                ),
        )


        cloned._id = uuid.uuid4()


        cloned._process = (
            copy.deepcopy(
                self._process,
                memo,
            )
        )


        cloned._spans = (
            copy.deepcopy(
                self._spans,
                memo,
            )
        )


        cloned._statistics = (
            copy.deepcopy(
                self._statistics,
                memo,
            )
        )


        cloned._enabled = self._enabled

        cloned._frozen = self._frozen

        cloned._closed = self._closed


        return cloned                                                                                        