"""
SciOS-NG Runtime Observability
Zipkin Exporter

Part 1. Foundation
"""

from __future__ import annotations


# ==============================================================================
# Imports
# ==============================================================================

from abc import ABC

import copy
import time
import uuid
import threading

from enum import Enum

from dataclasses import (
    dataclass,
    field,
)

from typing import (
    Any,
    Dict,
    List,
    Mapping,
    Optional,
    Union,
)


# Optional BaseExporter integration

from .base import (
    BaseExporter,
    ExportResult,
)


# ==============================================================================
# Constants
# ==============================================================================


DEFAULT_ZIPKIN_ENDPOINT = (
    "http://localhost:9411/api/v2/spans"
)


DEFAULT_PROTOCOL = (
    "http_json"
)


DEFAULT_TIMEOUT = 5.0


DEFAULT_BATCH_SIZE = 100


ZIPKIN_EXPORTER_VERSION = (
    "0.1.0"
)



# ==============================================================================
# Type Aliases
# ==============================================================================


TraceID = str

SpanID = str

ParentID = Optional[str]


SpanTags = Dict[
    str,
    Any,
]


SpanAnnotations = List[
    Dict[str, Any]
]


EndpointMetadata = Dict[
    str,
    Any,
]


ZipkinPayload = Union[
    Dict[str, Any],
    List[Dict[str, Any]],
]



# ==============================================================================
# Zipkin Protocol
# ==============================================================================


class ZipkinProtocol(Enum):
    """
    Zipkin transport protocol.
    """

    HTTP_JSON = (
        "http_json"
    )

    HTTP_PROTO = (
        "http_proto"
    )

    GRPC = (
        "grpc"
    )



# ==============================================================================
# Span Kind
# ==============================================================================


class SpanKind(Enum):

    INTERNAL = (
        "internal"
    )

    SERVER = (
        "server"
    )

    CLIENT = (
        "client"
    )

    PRODUCER = (
        "producer"
    )

    CONSUMER = (
        "consumer"
    )



# ==============================================================================
# Span Status
# ==============================================================================


class SpanStatus(Enum):

    OK = (
        "ok"
    )

    ERROR = (
        "error"
    )

    UNSET = (
        "unset"
    )



# ==============================================================================
# Zipkin Data Models
# ==============================================================================


@dataclass
class ZipkinTag:
    """
    Zipkin span tag.
    """

    key: str

    value: Any

    type: str = "string"



# ------------------------------------------------------------------------------


@dataclass
class ZipkinAnnotation:
    """
    Zipkin annotation.

    Equivalent:
        timestamped event
    """

    timestamp: float

    value: str

    endpoint: Optional[
        "ZipkinEndpoint"
    ] = None



# ------------------------------------------------------------------------------


@dataclass
class ZipkinEndpoint:
    """
    Service endpoint metadata.
    """

    service_name: str

    ipv4: Optional[str] = None

    ipv6: Optional[str] = None

    port: Optional[int] = None



# ------------------------------------------------------------------------------


@dataclass
class ZipkinSpan:
    """
    Zipkin span model.
    """

    trace_id: TraceID

    id: SpanID

    parent_id: ParentID

    name: str

    timestamp: float

    duration: float = 0.0

    kind: SpanKind = (
        SpanKind.INTERNAL
    )

    tags: List[
        ZipkinTag
    ] = field(
        default_factory=list
    )

    annotations: List[
        ZipkinAnnotation
    ] = field(
        default_factory=list
    )

    local_endpoint: Optional[
        ZipkinEndpoint
    ] = None



# ------------------------------------------------------------------------------


@dataclass
class ZipkinExportOptions:
    """
    Zipkin exporter configuration.
    """

    endpoint: str = (
        DEFAULT_ZIPKIN_ENDPOINT
    )

    protocol: str = (
        DEFAULT_PROTOCOL
    )

    batch_size: int = (
        DEFAULT_BATCH_SIZE
    )

    timeout: float = (
        DEFAULT_TIMEOUT
    )

    compression: bool = False



# ==============================================================================
# ZipkinExporter
# ==============================================================================


class ZipkinExporter(
    BaseExporter,
    ABC,
):
    """
    SciOS-NG Zipkin Exporter.

    Responsible for:
        - trace collection
        - span formatting
        - Zipkin transport
        - runtime lifecycle
    """



    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------

    def __init__(
        self,
        name: str = "ZipkinExporter",
        options: Optional[
            ZipkinExportOptions
        ] = None,
    ):

        self._lock = (
            threading.RLock()
        )


        self._id = (
            uuid.uuid4()
        )


        self._name = name


        self._exporter_type = (
            "zipkin"
        )


        # --------------------------------------------------------------
        # Configuration
        # --------------------------------------------------------------

        self._options = (
            options
            or
            ZipkinExportOptions()
        )


        self._endpoint = (
            self._options.endpoint
        )


        self._protocol = (
            self._options.protocol
        )


        self._service = (
            None
        )


        # --------------------------------------------------------------
        # Runtime State
        # --------------------------------------------------------------

        self._enabled = True

        self._frozen = False

        self._closed = False


        self._spans: List[
            ZipkinSpan
        ] = []


        self._endpoint_metadata = (
            ZipkinEndpoint(
                service_name="SciOS"
            )
        )


        # --------------------------------------------------------------
        # Statistics
        # --------------------------------------------------------------

        self._statistics = {

            "spans_exported": 0,

            "batches_exported": 0,

            "bytes_sent": 0,

            "errors": 0,

            "created_at":
                time.time(),

        }



    # ==========================================================================
    # Identity
    # ==========================================================================


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



    # ==========================================================================
    # Configuration
    # ==========================================================================


    @property
    def endpoint(
        self,
    ):
        return self._endpoint



    @property
    def protocol(
        self,
    ):
        return self._protocol



    @property
    def options(
        self,
    ):
        return copy.deepcopy(
            self._options
        )



    @property
    def service(
        self,
    ):
        return self._service



    # ==========================================================================
    # Runtime State
    # ==========================================================================


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
    def endpoint_metadata(
        self,
    ):
        return self._endpoint_metadata



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
        data: Any,
    ) -> ZipkinPayload:
        """
        Serialize Zipkin objects into
        Zipkin compatible payload.
        """

        if isinstance(
            data,
            ZipkinSpan,
        ):

            return [
                self.format_span(
                    data
                )
            ]


        if isinstance(
            data,
            list,
        ):

            return [
                self.format_span(
                    span
                )

                for span in data

                if isinstance(
                    span,
                    ZipkinSpan,
                )
            ]


        if isinstance(
            data,
            ZipkinEndpoint,
        ):

            return (
                self.format_endpoint(
                    data
                )
            )


        if isinstance(
            data,
            dict,
        ):
            return data


        raise TypeError(
            f"Unsupported serialization type: "
            f"{type(data).__name__}"
        )



    # ------------------------------------------------------------------

    def deserialize(
        self,
        payload: ZipkinPayload,
    ) -> Any:
        """
        Deserialize Zipkin payload
        back into SciOS objects.
        """

        if isinstance(
            payload,
            list,
        ):

            return [
                self._deserialize_span(
                    item
                )

                for item in payload
            ]


        if isinstance(
            payload,
            dict,
        ):

            return (
                self._deserialize_span(
                    payload
                )
            )


        raise TypeError(
            "Invalid Zipkin payload"
        )



    # ------------------------------------------------------------------

    def encode(
        self,
        payload: ZipkinPayload,
    ) -> bytes:
        """
        Encode payload for transport.
        """

        import json


        data = json.dumps(
            payload,
            default=str,
            separators=(
                ",",
                ":",
            ),
        )


        return data.encode(
            "utf-8"
        )



    # ------------------------------------------------------------------

    def decode(
        self,
        data: bytes,
    ) -> ZipkinPayload:
        """
        Decode transport payload.
        """

        import json


        if isinstance(
            data,
            bytes,
        ):

            data = data.decode(
                "utf-8"
            )


        return json.loads(
            data
        )



    # ------------------------------------------------------------------

    def format_span(
        self,
        span: ZipkinSpan,
    ) -> Dict[str, Any]:
        """
        Convert ZipkinSpan into
        Zipkin v2 JSON span format.
        """


        payload = {

            "traceId":
                span.trace_id,


            "id":
                span.id,


            "name":
                span.name,


            "timestamp":
                int(
                    span.timestamp
                    *
                    1000000
                ),


            "duration":
                int(
                    span.duration
                    *
                    1000000
                ),


            "kind":
                span.kind.value.upper(),


            "tags":
                self.format_tags(
                    span.tags
                ),


        }


        if span.parent_id:

            payload[
                "parentId"
            ] = span.parent_id



        if span.annotations:

            payload[
                "annotations"
            ] = [

                {

                    "timestamp":
                        int(
                            item.timestamp
                            *
                            1000000
                        ),

                    "value":
                        item.value,

                }

                for item
                in span.annotations

            ]



        if span.local_endpoint:

            payload[
                "localEndpoint"
            ] = (
                self.format_endpoint(
                    span.local_endpoint
                )
            )


        return payload



    # ------------------------------------------------------------------

    def format_tags(
        self,
        tags: List[
            ZipkinTag
        ],
    ) -> Dict[str, Any]:
        """
        Convert ZipkinTag list
        into Zipkin tags map.
        """

        return {

            tag.key:
                tag.value

            for tag
            in tags

        }



    # ------------------------------------------------------------------

    def format_endpoint(
        self,
        endpoint: ZipkinEndpoint,
    ) -> Dict[str, Any]:
        """
        Convert endpoint metadata
        into Zipkin format.
        """

        result = {

            "serviceName":
                endpoint.service_name,

        }


        if endpoint.ipv4:

            result[
                "ipv4"
            ] = endpoint.ipv4



        if endpoint.ipv6:

            result[
                "ipv6"
            ] = endpoint.ipv6



        if endpoint.port:

            result[
                "port"
            ] = endpoint.port



        return result



    # ------------------------------------------------------------------

    def _deserialize_span(
        self,
        payload: Dict[str, Any],
    ) -> ZipkinSpan:
        """
        Internal Zipkin span decoder.
        """


        tags = [

            ZipkinTag(
                key=key,
                value=value,
            )

            for key, value
            in payload.get(
                "tags",
                {}
            ).items()

        ]


        endpoint = None


        if (
            "localEndpoint"
            in payload
        ):

            ep = payload[
                "localEndpoint"
            ]


            endpoint = ZipkinEndpoint(

                service_name=
                    ep.get(
                        "serviceName",
                        "unknown"
                    ),

                ipv4=
                    ep.get(
                        "ipv4"
                    ),

                ipv6=
                    ep.get(
                        "ipv6"
                    ),

                port=
                    ep.get(
                        "port"
                    ),
            )


        return ZipkinSpan(

            trace_id=
                payload.get(
                    "traceId"
                ),

            id=
                payload.get(
                    "id"
                ),

            parent_id=
                payload.get(
                    "parentId"
                ),

            name=
                payload.get(
                    "name"
                ),

            timestamp=
                payload.get(
                    "timestamp",
                    0
                )
                /
                1000000,

            duration=
                payload.get(
                    "duration",
                    0
                )
                /
                1000000,


            tags=tags,

            local_endpoint=endpoint,

        )
# ==============================================================================
# Part 3. Trace API
# ==============================================================================


    def register_endpoint(
        self,
        endpoint: ZipkinEndpoint,
    ) -> ZipkinEndpoint:
        """
        Register local service endpoint.

        Used by:
            span.local_endpoint
        """

        if not isinstance(
            endpoint,
            ZipkinEndpoint,
        ):
            raise TypeError(
                "endpoint must be ZipkinEndpoint"
            )


        with self._lock:

            self._endpoint_metadata = endpoint


        return endpoint



    # ------------------------------------------------------------------

    def create_span(
        self,
        name: str,
        trace_id: Optional[
            TraceID
        ] = None,
        parent_id: Optional[
            ParentID
        ] = None,
        kind: SpanKind = SpanKind.INTERNAL,
        tags: Optional[
            SpanTags
        ] = None,
    ) -> ZipkinSpan:
        """
        Create new Zipkin span.

        Lifecycle:

            create_span()
                  |
                  ▼
            record_span()
                  |
                  ▼
            finish_span()
        """


        if not trace_id:

            trace_id = (
                uuid.uuid4()
                .hex
            )


        span_id = (
            uuid.uuid4()
            .hex[:16]
        )


        span = ZipkinSpan(

            trace_id=trace_id,

            id=span_id,

            parent_id=parent_id,

            name=name,

            timestamp=time.time(),

            kind=kind,

            local_endpoint=
                copy.deepcopy(
                    self._endpoint_metadata
                ),

        )


        if tags:

            span.tags = [

                ZipkinTag(
                    key=key,
                    value=value,
                )

                for key, value
                in tags.items()

            ]


        return span



    # ------------------------------------------------------------------

    def record_span(
        self,
        span: ZipkinSpan,
    ) -> ZipkinSpan:
        """
        Add completed or running span
        into exporter buffer.
        """

        if not isinstance(
            span,
            ZipkinSpan,
        ):
            raise TypeError(
                "span must be ZipkinSpan"
            )


        with self._lock:

            if self._closed:

                raise RuntimeError(
                    "Exporter is closed"
                )


            self._spans.append(
                span
            )


        return span



    # ------------------------------------------------------------------

    def finish_span(
        self,
        span: ZipkinSpan,
        status: SpanStatus = SpanStatus.OK,
        annotations: Optional[
            List[str]
        ] = None,
    ) -> ZipkinSpan:
        """
        Finish span lifecycle.
        """


        end_time = time.time()


        span.duration = (
            end_time
            -
            span.timestamp
        )


        if annotations:

            span.annotations.extend(

                [

                    ZipkinAnnotation(

                        timestamp=end_time,

                        value=item,

                        endpoint=
                            self._endpoint_metadata,

                    )

                    for item
                    in annotations

                ]

            )


        if status == SpanStatus.ERROR:

            span.tags.append(

                ZipkinTag(
                    key="error",
                    value=True,
                    type="boolean",
                )

            )


        self.record_span(
            span
        )


        return span



    # ------------------------------------------------------------------

    def collect(
        self,
    ) -> List[ZipkinSpan]:
        """
        Collect pending spans.

        Does not remove buffer.
        """

        with self._lock:

            spans = copy.deepcopy(
                self._spans
            )


        return spans



    # ------------------------------------------------------------------

    def gather(
        self,
    ) -> List[ZipkinSpan]:
        """
        Gather spans for export.

        Alias of collect()
        with statistics update.
        """


        spans = self.collect()


        self._statistics[
            "traces_collected"
        ] = (
            self._statistics.get(
                "traces_collected",
                0,
            )
            +
            len(spans)
        )


        return spans



    # ------------------------------------------------------------------

    def flush(
        self,
    ) -> List[ZipkinSpan]:
        """
        Flush internal span buffer.

        Returns:
            removed spans
        """

        with self._lock:

            spans = (
                self._spans
            )


            self._spans = []


        return spans
# ==============================================================================
# Part 4. Export API
# ==============================================================================


    def export(
        self,
        data: Any,
    ) -> ExportResult:
        """
        Generic export entry point.

        Supports:

            ZipkinSpan
            List[ZipkinSpan]
            ZipkinEndpoint
            Payload
        """


        if self._closed:

            return ExportResult(
                success=False,
                message="Exporter closed",
            )


        if not self._enabled:

            return ExportResult(
                success=False,
                message="Exporter disabled",
            )


        if isinstance(
            data,
            ZipkinSpan,
        ):

            return self.export_span(
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
            ZipkinEndpoint,
        ):

            return self.export_endpoint(
                data
            )


        return ExportResult(
            success=False,
            message=(
                "Unsupported export type"
            ),
        )



    # ------------------------------------------------------------------

    def export_batch(
        self,
        spans: List[
            ZipkinSpan
        ],
    ) -> ExportResult:
        """
        Export multiple spans.
        """


        if not spans:

            return ExportResult(
                success=True,
                exported=0,
            )


        payload = [

            self.format_span(
                span
            )

            for span in spans

            if isinstance(
                span,
                ZipkinSpan,
            )

        ]


        return self.export_zipkin(
            payload
        )



    # ------------------------------------------------------------------

    def export_span(
        self,
        span: ZipkinSpan,
    ) -> ExportResult:
        """
        Export single span.
        """


        payload = (
            self.format_span(
                span
            )
        )


        return self.export_zipkin(
            [
                payload
            ]
        )



    # ------------------------------------------------------------------

    def export_trace(
        self,
        trace_id: TraceID,
    ) -> ExportResult:
        """
        Export all spans belonging
        to a trace.
        """


        spans = [

            span

            for span
            in self._spans

            if span.trace_id == trace_id

        ]


        return self.export_batch(
            spans
        )



    # ------------------------------------------------------------------

    def export_endpoint(
        self,
        endpoint: ZipkinEndpoint,
    ) -> ExportResult:
        """
        Export endpoint metadata.

        Used for service registration.
        """


        payload = (
            self.format_endpoint(
                endpoint
            )
        )


        return self.export_zipkin(
            [
                {
                    "endpoint":
                        payload
                }
            ]
        )



    # ------------------------------------------------------------------

    def export_zipkin(
        self,
        payload: ZipkinPayload,
    ) -> ExportResult:
        """
        Low-level Zipkin transport layer.

        Future integrations:

            HTTP JSON
            HTTP PROTO
            gRPC
        """


        try:

            encoded = (
                self.encode(
                    payload
                )
            )


            #
            # Transport placeholder
            #
            # requests.post(
            #     self._endpoint,
            #     data=encoded
            # )
            #


            size = len(
                encoded
            )


            self._statistics[
                "spans_exported"
            ] += len(
                payload
            )


            self._statistics[
                "batches_exported"
            ] += 1


            self._statistics[
                "bytes_sent"
            ] += size



            return ExportResult(

                success=True,

                exported=len(
                    payload
                ),

                bytes_sent=size,

                endpoint=self._endpoint,

            )



        except Exception as exc:


            self._statistics[
                "errors"
            ] += 1


            return ExportResult(

                success=False,

                message=str(
                    exc
                ),

            )
# ==============================================================================
# Part 5. Configuration API
# ==============================================================================


    def set_endpoint(
        self,
        endpoint: str,
    ) -> str:
        """
        Update Zipkin collector endpoint.
        """

        if not isinstance(
            endpoint,
            str,
        ):
            raise TypeError(
                "endpoint must be string"
            )


        if not endpoint:

            raise ValueError(
                "endpoint cannot be empty"
            )


        with self._lock:

            self._endpoint = endpoint

            self._options.endpoint = endpoint


        return self._endpoint



    # ------------------------------------------------------------------

    def set_protocol(
        self,
        protocol: Union[
            str,
            ZipkinProtocol,
        ],
    ) -> str:
        """
        Configure Zipkin transport protocol.

        Supported:

            http_json
            http_proto
            grpc
        """


        if isinstance(
            protocol,
            ZipkinProtocol,
        ):

            protocol = (
                protocol.value
            )


        valid_protocols = [

            item.value

            for item
            in ZipkinProtocol

        ]


        if protocol not in valid_protocols:

            raise ValueError(
                f"Unsupported Zipkin protocol: {protocol}"
            )


        with self._lock:

            self._protocol = protocol

            self._options.protocol = protocol


        return self._protocol



    # ------------------------------------------------------------------

    def set_service(
        self,
        service: str,
    ) -> str:
        """
        Set service identity.

        Example:

            SciOS Kernel
            Runtime Engine
        """


        if not service:

            raise ValueError(
                "service name required"
            )


        with self._lock:

            self._service = service

            self._endpoint_metadata.service_name = service


        return self._service



    # ------------------------------------------------------------------

    def set_tags(
        self,
        tags: Mapping[
            str,
            Any
        ],
    ) -> List[ZipkinTag]:
        """
        Set default exporter tags.

        Applied to new spans.
        """


        if not isinstance(
            tags,
            Mapping,
        ):
            raise TypeError(
                "tags must be mapping"
            )


        with self._lock:

            self._default_tags = [

                ZipkinTag(
                    key=key,
                    value=value,
                )

                for key, value
                in tags.items()

            ]


        return self._default_tags



    # ------------------------------------------------------------------

    def options(
        self,
    ) -> ZipkinExportOptions:
        """
        Return exporter options snapshot.
        """

        return copy.deepcopy(
            self._options
        )



    # ------------------------------------------------------------------

    def reset(
        self,
    ) -> None:
        """
        Reset configuration to defaults.
        """


        with self._lock:

            self._options = (
                ZipkinExportOptions()
            )


            self._endpoint = (
                self._options.endpoint
            )


            self._protocol = (
                self._options.protocol
            )


            self._service = None


            self._default_tags = []


            self._endpoint_metadata = (
                ZipkinEndpoint(
                    service_name="SciOS"
                )
            )
# ==============================================================================
# Part 6. Runtime Operations
# ==============================================================================


    def snapshot(
        self,
    ) -> Dict[str, Any]:
        """
        Create runtime checkpoint.

        Contains:
            - configuration
            - lifecycle state
            - spans
            - statistics
        """


        with self._lock:

            return {

                "id":
                    str(self._id),

                "name":
                    self._name,

                "exporter_type":
                    self._exporter_type,


                "options":
                    copy.deepcopy(
                        self._options
                    ),


                "endpoint":
                    self._endpoint,


                "protocol":
                    self._protocol,


                "service":
                    self._service,


                "enabled":
                    self._enabled,


                "frozen":
                    self._frozen,


                "closed":
                    self._closed,


                "spans":
                    copy.deepcopy(
                        self._spans
                    ),


                "endpoint_metadata":
                    copy.deepcopy(
                        self._endpoint_metadata
                    ),


                "statistics":
                    copy.deepcopy(
                        self._statistics
                    ),

            }



    # ------------------------------------------------------------------

    def restore(
        self,
        state: Dict[str, Any],
    ) -> None:
        """
        Restore exporter from snapshot.
        """


        if not isinstance(
            state,
            dict,
        ):
            raise TypeError(
                "state must be dict"
            )


        with self._lock:

            self._options = (
                copy.deepcopy(
                    state["options"]
                )
            )


            self._endpoint = (
                state["endpoint"]
            )


            self._protocol = (
                state["protocol"]
            )


            self._service = (
                state["service"]
            )


            self._enabled = (
                state["enabled"]
            )


            self._frozen = (
                state["frozen"]
            )


            self._closed = (
                state["closed"]
            )


            self._spans = (
                copy.deepcopy(
                    state["spans"]
                )
            )


            self._endpoint_metadata = (
                copy.deepcopy(
                    state[
                        "endpoint_metadata"
                    ]
                )
            )


            self._statistics = (
                copy.deepcopy(
                    state["statistics"]
                )
            )



    # ------------------------------------------------------------------

    def clone(
        self,
    ) -> "ZipkinExporter":
        """
        Create isolated exporter clone.
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
    ) -> "ZipkinExporter":
        """
        Create shallow runtime copy.
        """


        new = ZipkinExporter(
            name=self._name,
            options=
                copy.copy(
                    self._options
                ),
        )


        new._endpoint = (
            self._endpoint
        )


        new._protocol = (
            self._protocol
        )


        new._service = (
            self._service
        )


        new._enabled = (
            self._enabled
        )


        return new



    # ------------------------------------------------------------------

    def cleanup(
        self,
    ) -> None:
        """
        Release runtime resources.

        Clears:
            - spans
            - temporary buffers
            - metadata cache
        """


        with self._lock:

            self._spans.clear()


            self._endpoint_metadata = (
                None
            )


            self._default_tags = []



    # ------------------------------------------------------------------

    def compact(
        self,
    ) -> int:
        """
        Optimize span buffer.

        Removes:
            - invalid spans
            - empty spans

        Returns:
            removed count
        """


        with self._lock:

            before = len(
                self._spans
            )


            self._spans = [

                span

                for span
                in self._spans

                if (

                    span.trace_id

                    and

                    span.id

                    and

                    span.name

                )

            ]


            removed = (
                before
                -
                len(
                    self._spans
                )
            )


        return removed
# ==============================================================================
# Part 7. Statistics API
# ==============================================================================


    @property
    def spans_exported(
        self,
    ) -> int:
        """
        Number of exported spans.
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
        Number of exported batches.
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
        Number of traces collected.
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


        count = self._statistics.get(
            "export_operations",
            0,
        )


        if count == 0:

            return 0.0


        total = self._statistics.get(
            "total_latency",
            0.0,
        )


        return (
            total
            /
            count
        )



    # ------------------------------------------------------------------

    def report(
        self,
    ) -> Dict[str, Any]:
        """
        Full runtime statistics report.
        """


        return {

            "exporter":

                self._name,


            "type":

                self._exporter_type,


            "version":

                ZIPKIN_EXPORTER_VERSION,


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


            "buffer_size":

                len(
                    self._spans
                ),


            "enabled":

                self._enabled,


            "closed":

                self._closed,


            "endpoint":

                self._endpoint,


            "protocol":

                self._protocol,

        }



    # ------------------------------------------------------------------

    def summary(
        self,
    ) -> Dict[str, Any]:
        """
        Compact statistics summary.

        Used by:
            dashboards
            health checks
        """


        return {

            "spans":

                self.spans_exported,


            "batches":

                self.batches_exported,


            "bytes":

                self.bytes_sent,


            "traces":

                self.traces_collected,


            "latency":

                self.average_latency,


        }
# ==============================================================================
# Part 8. Validation API
# ==============================================================================


    def validate(
        self,
        data: Any,
    ) -> bool:
        """
        Generic validation entry point.

        Supports:

            ZipkinSpan
            ZipkinEndpoint
            TraceID
            Payload
        """


        if isinstance(
            data,
            ZipkinSpan,
        ):

            return self.validate_span(
                data
            )


        if isinstance(
            data,
            ZipkinEndpoint,
        ):

            return self.validate_endpoint(
                data
            )


        if isinstance(
            data,
            str,
        ):

            return self.validate_trace(
                data
            )


        return False



    # ------------------------------------------------------------------

    def validate_span(
        self,
        span: ZipkinSpan,
    ) -> bool:
        """
        Validate Zipkin span.

        Required:

            trace_id
            id
            name
            timestamp
        """


        if not isinstance(
            span,
            ZipkinSpan,
        ):
            return False



        if not span.trace_id:

            return False



        if not span.id:

            return False



        if not span.name:

            return False



        if span.timestamp <= 0:

            return False



        if span.duration < 0:

            return False



        if not isinstance(
            span.kind,
            SpanKind,
        ):

            return False



        if span.local_endpoint:

            if not self.validate_endpoint(
                span.local_endpoint
            ):
                return False



        return True



    # ------------------------------------------------------------------

    def validate_endpoint(
        self,
        endpoint: ZipkinEndpoint,
    ) -> bool:
        """
        Validate service endpoint.
        """


        if not isinstance(
            endpoint,
            ZipkinEndpoint,
        ):
            return False



        if not endpoint.service_name:

            return False



        if endpoint.port:

            if not (
                0
                <
                endpoint.port
                <
                65536
            ):

                return False



        if (
            endpoint.ipv4 is None
            and
            endpoint.ipv6 is None
        ):

            #
            # Allowed:
            # local-only service
            #
            pass



        return True



    # ------------------------------------------------------------------

    def validate_trace(
        self,
        trace_id: TraceID,
    ) -> bool:
        """
        Validate trace identifier.

        Zipkin v2:

            16 or 32 hex chars
        """


        if not isinstance(
            trace_id,
            str,
        ):
            return False



        if len(trace_id) not in (
            16,
            32,
        ):

            return False



        try:

            int(
                trace_id,
                16,
            )

        except ValueError:

            return False



        return True



    # ------------------------------------------------------------------

    def check_integrity(
        self,
    ) -> Dict[str, Any]:
        """
        Check exporter internal consistency.
        """


        problems = []



        if not self._endpoint:

            problems.append(
                "missing endpoint"
            )



        if not self._protocol:

            problems.append(
                "missing protocol"
            )



        if self._closed:

            problems.append(
                "exporter closed"
            )



        invalid_spans = [

            span

            for span
            in self._spans

            if not self.validate_span(
                span
            )

        ]



        if invalid_spans:

            problems.append(
                f"{len(invalid_spans)} invalid spans"
            )



        return {

            "healthy":
                len(problems) == 0,


            "problems":
                problems,


            "span_count":
                len(
                    self._spans
                ),


            "endpoint_valid":
                self.validate_endpoint(
                    self._endpoint_metadata
                ),

        }
# ==============================================================================
# Part 9. Events & Hooks
# ==============================================================================


    def emit_event(
        self,
        event: str,
        payload: Optional[
            Dict[str, Any]
        ] = None,
    ) -> Dict[str, Any]:
        """
        Emit exporter lifecycle event.

        Event format:

        {
            "source":
                "ZipkinExporter",

            "event":
                "...",

            "timestamp":
                ...
        }
        """


        event_data = {

            "source":
                self._name,


            "type":
                self._exporter_type,


            "event":
                event,


            "timestamp":
                time.time(),


            "payload":
                payload or {},

        }


        #
        # Internal event buffer
        #

        if not hasattr(
            self,
            "_events",
        ):

            self._events = []



        self._events.append(
            event_data
        )


        return event_data



    # ------------------------------------------------------------------

    def before_collect(
        self,
    ) -> Dict[str, Any]:
        """
        Hook executed before span collection.
        """


        return self.emit_event(
            "before_collect",
            {
                "buffer_size":
                    len(
                        self._spans
                    )
            }
        )



    # ------------------------------------------------------------------

    def after_collect(
        self,
        spans: List[
            ZipkinSpan
        ],
    ) -> Dict[str, Any]:
        """
        Hook executed after collection.
        """


        return self.emit_event(
            "after_collect",
            {
                "collected":
                    len(spans)
            }
        )



    # ------------------------------------------------------------------

    def before_export(
        self,
        payload: Optional[
            ZipkinPayload
        ] = None,
    ) -> Dict[str, Any]:
        """
        Hook before sending data.
        """


        return self.emit_event(
            "before_export",
            {
                "items":
                    len(payload)
                    if payload
                    else 0
            }
        )



    # ------------------------------------------------------------------

    def after_export(
        self,
        result: Optional[
            Any
        ] = None,
    ) -> Dict[str, Any]:
        """
        Hook after export completed.
        """


        return self.emit_event(
            "after_export",
            {
                "success":
                    getattr(
                        result,
                        "success",
                        None,
                    )
            }
        )



    # ------------------------------------------------------------------

    def before_flush(
        self,
    ) -> Dict[str, Any]:
        """
        Hook before buffer cleanup.
        """


        return self.emit_event(
            "before_flush",
            {
                "pending":
                    len(
                        self._spans
                    )
            }
        )



    # ------------------------------------------------------------------

    def after_flush(
        self,
        count: int = 0,
    ) -> Dict[str, Any]:
        """
        Hook after flush completed.
        """


        return self.emit_event(
            "after_flush",
            {
                "removed":
                    count
            }
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

            f"id={self._id}, "

            f"name='{self._name}', "

            f"type='{self._exporter_type}', "

            f"protocol='{self._protocol}', "

            f"endpoint='{self._endpoint}', "

            f"spans={len(self._spans)}"

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

            f"ZipkinExporter "

            f"[{self._service or 'unknown'}] "

            f"- "

            f"{self._protocol} "

            f"@ "

            f"{self._endpoint}"

        )



    # ------------------------------------------------------------------

    def __len__(
        self,
    ) -> int:
        """
        Number of buffered spans.
        """


        return len(
            self._spans
        )



    # ------------------------------------------------------------------

    def __call__(
        self,
        data: Any = None,
        **kwargs,
    ):
        """
        Callable exporter.

        Example:

            exporter(span)

        equals:

            exporter.export(span)
        """


        if data is None:

            return self.summary()


        return self.export(
            data
        )



    # ------------------------------------------------------------------

    def __copy__(
        self,
    ):
        """
        Shallow copy protocol.
        """


        return self.copy()



    # ------------------------------------------------------------------

    def __deepcopy__(
        self,
        memo,
    ):
        """
        Deep copy protocol.
        """


        cloned = (
            self.clone()
        )


        memo[
            id(self)
        ] = cloned


        return cloned                                                                                