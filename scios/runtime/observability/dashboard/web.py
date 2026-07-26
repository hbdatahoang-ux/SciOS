"""
SciOS-NG Dashboard Web Runtime

File:
    scios/runtime/observability/dashboard/web.py

Part 1.1
---------
Foundation
    - Imports
    - Constants
    - Type aliases
    - Optional dependencies
    - Foundation utilities

This module provides the web runtime used by the
SciOS-NG observability dashboard.

Later parts add:

    Part 1.2 Constructor
    Part 2   Configuration
    Part 3   Runtime State
    Part 4   API Router
    Part 5   WebSocket
    Part 6   Middleware
    Part 7   Authentication
    Part 8   Static Assets
    Part 9   Events & Hooks
    Part 10  Lifecycle
    Part 11  Python Protocols
    Part 12  Diagnostics
"""

from __future__ import annotations

import copy
import json
import logging
import os
import socket
import threading
import time
import uuid

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from typing import (
    Any,
    Callable,
    Deque,
    Dict,
    Iterable,
    Iterator,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
    Set,
    Tuple,
    TypeAlias,
    Union,
)

# ==========================================================
# Optional FastAPI Support
# ==========================================================

FASTAPI_AVAILABLE = False

try:

    from fastapi import (
        APIRouter,
        FastAPI,
        HTTPException,
        Request,
        Response,
        WebSocket,
        WebSocketDisconnect,
    )

    FASTAPI_AVAILABLE = True

except ImportError:

    APIRouter = Any
    FastAPI = Any
    HTTPException = Exception
    Request = Any
    Response = Any
    WebSocket = Any
    WebSocketDisconnect = Exception


# ==========================================================
# Optional Starlette
# ==========================================================

STARLETTE_AVAILABLE = False

try:

    from starlette.middleware.base import (
        BaseHTTPMiddleware,
    )

    STARLETTE_AVAILABLE = True

except ImportError:

    BaseHTTPMiddleware = object


# ==========================================================
# Logger
# ==========================================================

LOGGER = logging.getLogger(__name__)


# ==========================================================
# Runtime Constants
# ==========================================================

DEFAULT_HOST = "127.0.0.1"

DEFAULT_PORT = 8000

DEFAULT_API_PREFIX = "/api"

DEFAULT_WS_PATH = "/ws"

DEFAULT_MAX_EVENTS = 1000

DEFAULT_MAX_CONNECTIONS = 1024

DEFAULT_MAX_REQUEST_HISTORY = 500

DEFAULT_SERVER_NAME = "SciOS Dashboard"

DEFAULT_VERSION = "0.1.0"

DEFAULT_DESCRIPTION = (
    "SciOS-NG Dashboard Web Runtime"
)

DEFAULT_SERVER_TYPE = (
    "dashboard-web"
)


# ==========================================================
# Runtime States
# ==========================================================

STATE_CREATED = "created"

STATE_READY = "ready"

STATE_RUNNING = "running"

STATE_STOPPED = "stopped"

STATE_DISABLED = "disabled"

STATE_FROZEN = "frozen"

STATE_CLOSED = "closed"

STATE_ERROR = "error"


VALID_STATES = {

    STATE_CREATED,

    STATE_READY,

    STATE_RUNNING,

    STATE_STOPPED,

    STATE_DISABLED,

    STATE_FROZEN,

    STATE_CLOSED,

    STATE_ERROR,

}


# ==========================================================
# HTTP Methods
# ==========================================================

HTTP_GET = "GET"

HTTP_POST = "POST"

HTTP_PUT = "PUT"

HTTP_DELETE = "DELETE"

HTTP_PATCH = "PATCH"


# ==========================================================
# Type Aliases
# ==========================================================

JSONDict: TypeAlias = Dict[str, Any]

Headers: TypeAlias = Dict[str, str]

Metadata: TypeAlias = Dict[str, Any]

Event: TypeAlias = Dict[str, Any]

Statistics: TypeAlias = Dict[str, Any]

Configuration: TypeAlias = Dict[str, Any]

RouteTable: TypeAlias = List[Dict[str, Any]]

Hook: TypeAlias = Callable[..., Any]

Middleware: TypeAlias = Callable[..., Any]


# ==========================================================
# Runtime Event
# ==========================================================

@dataclass(slots=True)
class RuntimeEvent:
    """
    Dashboard runtime event.
    """

    name: str

    timestamp: float = field(
        default_factory=time.time
    )

    payload: JSONDict = field(
        default_factory=dict
    )

    level: str = "INFO"

    source: str = "DashboardWebServer"

    def to_dict(
        self,
    ) -> JSONDict:

        return {

            "name": self.name,

            "timestamp": self.timestamp,

            "payload": dict(self.payload),

            "level": self.level,

            "source": self.source,

        }


# ==========================================================
# Runtime Statistics
# ==========================================================

@dataclass(slots=True)
class RuntimeStatistics:
    """
    Runtime statistics container.
    """

    requests: int = 0

    successful_requests: int = 0

    failed_requests: int = 0

    websocket_connections: int = 0

    websocket_messages: int = 0

    total_response_time: float = 0.0

    bytes_sent: int = 0

    bytes_received: int = 0

    events: int = 0

    started_at: Optional[float] = None

    def reset(
        self,
    ) -> None:

        self.requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.websocket_connections = 0
        self.websocket_messages = 0
        self.total_response_time = 0.0
        self.bytes_sent = 0
        self.bytes_received = 0
        self.events = 0
        self.started_at = None

    @property
    def average_latency(
        self,
    ) -> float:

        if self.successful_requests == 0:

            return 0.0

        return (
            self.total_response_time
            / self.successful_requests
        )

    def to_dict(
        self,
    ) -> JSONDict:

        return {

            "requests": self.requests,

            "successful_requests":
                self.successful_requests,

            "failed_requests":
                self.failed_requests,

            "websocket_connections":
                self.websocket_connections,

            "websocket_messages":
                self.websocket_messages,

            "average_latency":
                self.average_latency,

            "bytes_sent":
                self.bytes_sent,

            "bytes_received":
                self.bytes_received,

            "events":
                self.events,

            "started_at":
                self.started_at,

        }


# ==========================================================
# Foundation Utilities
# ==========================================================

def utc_timestamp() -> float:
    """
    Current UTC timestamp.
    """

    return time.time()


def utc_datetime() -> datetime:
    """
    Current UTC datetime.
    """

    return datetime.utcnow()


def generate_uuid() -> str:
    """
    Generate runtime UUID.
    """

    return str(
        uuid.uuid4()
    )


def hostname() -> str:
    """
    Local machine hostname.
    """

    try:

        return socket.gethostname()

    except Exception:

        return "localhost"


def deep_copy(
    value: Any,
) -> Any:
    """
    Safe deepcopy helper.
    """

    return copy.deepcopy(value)


def current_revision(
    revision: int,
) -> int:
    """
    Increment revision.
    """

    return revision + 1


def ensure_dict(
    value: Optional[Mapping[str, Any]],
) -> JSONDict:
    """
    Ensure dictionary instance.
    """

    if value is None:

        return {}

    return dict(value)


def clamp(
    value: int,
    minimum: int,
    maximum: int,
) -> int:
    """
    Clamp integer value.
    """

    return max(
        minimum,
        min(maximum, value),
    )


def iso_now() -> str:
    """
    ISO-8601 UTC timestamp.
    """

    return datetime.utcnow().isoformat() + "Z"


# ==========================================================
# Public Exports
# ==========================================================

__all__ = [

    "DashboardWebServer",

    "RuntimeEvent",

    "RuntimeStatistics",

    "FASTAPI_AVAILABLE",

    "STATE_CREATED",
    "STATE_READY",
    "STATE_RUNNING",
    "STATE_STOPPED",
    "STATE_DISABLED",
    "STATE_FROZEN",
    "STATE_CLOSED",
    "STATE_ERROR",

    "DEFAULT_HOST",
    "DEFAULT_PORT",
    "DEFAULT_API_PREFIX",
    "DEFAULT_WS_PATH",

    "generate_uuid",
    "utc_timestamp",
    "utc_datetime",
    "hostname",
]
# ==========================================================
# DashboardWebServer
# ==========================================================


class DashboardWebServer:
    """
    SciOS-NG Dashboard Web Runtime Server.

    DashboardWebServer exposes DashboardViewer through
    HTTP/WebSocket interfaces and acts as the entry point
    for the Observability Dashboard.

    Architecture

        DashboardViewer
               │
               ▼
        DashboardWebServer
               │
        ┌──────┼──────────┐
        ▼      ▼          ▼
      REST    WS       Static UI

    Later Parts

        Part 2  Configuration
        Part 3  Runtime State
        Part 4  API Router
        Part 5  WebSocket
        Part 6  Middleware
        Part 7  Authentication
        Part 8  Static Assets
        Part 9  Events
        Part 10 Lifecycle
        Part 11 Protocols
        Part 12 Diagnostics
    """

    # ======================================================
    # Constructor
    # ======================================================

    def __init__(
        self,
        viewer: Any | None = None,
        *,
        name: str = DEFAULT_SERVER_NAME,
        version: str = DEFAULT_VERSION,
        description: str = DEFAULT_DESCRIPTION,
        server_type: str = DEFAULT_SERVER_TYPE,
    ) -> None:
        """
        Initialize DashboardWebServer.
        """

        now = utc_timestamp()

        # ==================================================
        # Identity
        # ==================================================

        self.id: str = generate_uuid()

        self.name: str = name

        self.version: str = version

        self.description: str = description

        self.server_type: str = server_type

        # ==================================================
        # Viewer Binding
        # ==================================================

        self.viewer = viewer

        # ==================================================
        # Runtime Metadata
        # ==================================================

        self.created_at: float = now

        self.updated_at: float = now

        self.revision: int = 0

        self.hostname: str = hostname()

        self.process_id: int = os.getpid()

        # ==================================================
        # Configuration
        # ==================================================

        self.host: str = DEFAULT_HOST

        self.port: int = DEFAULT_PORT

        self.api_prefix: str = DEFAULT_API_PREFIX

        self.websocket_path: str = DEFAULT_WS_PATH

        self.workers: int = 1

        self.debug: bool = False

        self.reload: bool = False

        self.ssl_enabled: bool = False

        self.ssl_cert: str | None = None

        self.ssl_key: str | None = None

        self.websocket_enabled: bool = True

        self.max_connections: int = DEFAULT_MAX_CONNECTIONS

        self.max_events: int = DEFAULT_MAX_EVENTS

        self.max_request_history: int = (
            DEFAULT_MAX_REQUEST_HISTORY
        )

        self.cors: JSONDict = {

            "enabled": True,

            "origins": ["*"],

            "methods": ["*"],

            "headers": ["*"],

        }

        self.authentication: JSONDict = {

            "enabled": False,

            "provider": None,

            "configuration": {},

        }

        self.extra_configuration: JSONDict = {}

        # ==================================================
        # Runtime State
        # ==================================================

        self.state: str = STATE_CREATED

        self.running: bool = False

        self.enabled: bool = True

        self.frozen: bool = False

        self.closed: bool = False

        self.started_at: float | None = None

        self.stopped_at: float | None = None

        self.last_request_at: float | None = None

        self.last_error_at: float | None = None

        self.last_error: str | None = None

        # ==================================================
        # Statistics
        # ==================================================

        self.statistics = RuntimeStatistics()

        # ==================================================
        # Event Storage
        # ==================================================

        self.events: Deque[RuntimeEvent] = deque(
            maxlen=self.max_events
        )

        # ==================================================
        # API Runtime
        # ==================================================

        self.app: FastAPI | None = None

        self.router: APIRouter | None = None

        self.routes_registered: bool = False

        self.request_history: Deque[JSONDict] = deque(
            maxlen=self.max_request_history
        )

        # ==================================================
        # WebSocket Runtime
        # ==================================================

        self.websocket_clients: Set[Any] = set()

        self.websocket_lock = threading.RLock()

        # ==================================================
        # Middleware
        # ==================================================

        self.middlewares: List[Middleware] = []

        # ==================================================
        # Hooks
        # ==================================================

        self.before_request_hooks: List[Hook] = []

        self.after_request_hooks: List[Hook] = []

        self.before_render_hooks: List[Hook] = []

        self.after_render_hooks: List[Hook] = []

        self.before_shutdown_hooks: List[Hook] = []

        self.after_shutdown_hooks: List[Hook] = []

        # ==================================================
        # Static Resources
        # ==================================================

        self.static_directory: Path | None = None

        self.template_directory: Path | None = None

        self.asset_directory: Path | None = None

        # ==================================================
        # Diagnostics
        # ==================================================

        self.logger = LOGGER

        self.logger.debug(
            "DashboardWebServer initialized (%s)",
            self.id,
        )
# ==========================================================
# Part 1.3
# Identity & Metadata
# ==========================================================

    # ------------------------------------------------------
    # Identity Properties
    # ------------------------------------------------------

    @property
    def identity(self) -> JSONDict:
        """
        Return immutable server identity.
        """

        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "server_type": self.server_type,
        }

    @property
    def metadata(self) -> JSONDict:
        """
        Runtime metadata.
        """

        return {
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "revision": self.revision,
            "hostname": self.hostname,
            "process_id": self.process_id,
        }

    @property
    def runtime(self) -> JSONDict:
        """
        Runtime information.
        """

        return {
            "state": self.state,
            "running": self.running,
            "enabled": self.enabled,
            "frozen": self.frozen,
            "closed": self.closed,
            "started_at": self.started_at,
            "stopped_at": self.stopped_at,
        }

    @property
    def uptime(self) -> float:
        """
        Runtime uptime (seconds).
        """

        if self.started_at is None:
            return 0.0

        if self.running:
            return max(
                0.0,
                utc_timestamp() - self.started_at,
            )

        if self.stopped_at is None:
            return 0.0

        return max(
            0.0,
            self.stopped_at - self.started_at,
        )

    @property
    def active(self) -> bool:
        """
        Active state.
        """

        return (
            self.enabled
            and self.running
            and not self.closed
            and not self.frozen
        )

    # ------------------------------------------------------
    # Metadata Operations
    # ------------------------------------------------------

    def touch(self) -> "DashboardWebServer":
        """
        Update metadata.
        """

        self.updated_at = utc_timestamp()

        self.revision += 1

        return self

    def rename(
        self,
        name: str,
    ) -> "DashboardWebServer":
        """
        Rename server.
        """

        self.name = str(name)

        return self.touch()

    def set_version(
        self,
        version: str,
    ) -> "DashboardWebServer":
        """
        Update version.
        """

        self.version = str(version)

        return self.touch()

    def set_description(
        self,
        description: str,
    ) -> "DashboardWebServer":
        """
        Update description.
        """

        self.description = str(description)

        return self.touch()

    def set_server_type(
        self,
        server_type: str,
    ) -> "DashboardWebServer":
        """
        Update server type.
        """

        self.server_type = str(server_type)

        return self.touch()

    # ------------------------------------------------------
    # Viewer Binding
    # ------------------------------------------------------

    def bind_viewer(
        self,
        viewer: Any,
    ) -> "DashboardWebServer":
        """
        Bind DashboardViewer.
        """

        self.viewer = viewer

        return self.touch()

    def unbind_viewer(
        self,
    ) -> "DashboardWebServer":
        """
        Remove bound viewer.
        """

        self.viewer = None

        return self.touch()

    def has_viewer(self) -> bool:
        """
        Whether a viewer is bound.
        """

        return self.viewer is not None

    # ------------------------------------------------------
    # Identity Export
    # ------------------------------------------------------

    def identity_dict(self) -> JSONDict:
        """
        Export identity.
        """

        return dict(self.identity)

    def metadata_dict(self) -> JSONDict:
        """
        Export metadata.
        """

        return dict(self.metadata)

    def runtime_dict(self) -> JSONDict:
        """
        Export runtime information.
        """

        runtime = dict(self.runtime)

        runtime["uptime"] = self.uptime

        runtime["active"] = self.active

        return runtime

    # ------------------------------------------------------
    # Information
    # ------------------------------------------------------

    def info(self) -> JSONDict:
        """
        Complete server information.
        """

        return {
            "identity": self.identity_dict(),
            "metadata": self.metadata_dict(),
            "runtime": self.runtime_dict(),
            "viewer_bound": self.has_viewer(),
        }

    # ------------------------------------------------------
    # Revision
    # ------------------------------------------------------

    def increment_revision(self) -> int:
        """
        Increase revision number.
        """

        self.revision += 1

        self.updated_at = utc_timestamp()

        return self.revision

    def reset_revision(self) -> "DashboardWebServer":
        """
        Reset revision counter.
        """

        self.revision = 0

        self.updated_at = utc_timestamp()

        return self

    # ------------------------------------------------------
    # Metadata Merge
    # ------------------------------------------------------

    def update_metadata(
        self,
        **kwargs: Any,
    ) -> "DashboardWebServer":
        """
        Update supported metadata fields.
        """

        if "name" in kwargs:
            self.name = str(kwargs["name"])

        if "version" in kwargs:
            self.version = str(kwargs["version"])

        if "description" in kwargs:
            self.description = str(kwargs["description"])

        if "server_type" in kwargs:
            self.server_type = str(kwargs["server_type"])

        self.touch()

        return self

    # ------------------------------------------------------
    # Timestamp Helpers
    # ------------------------------------------------------

    def created_datetime(self) -> datetime:
        """
        Creation time as datetime.
        """

        return datetime.fromtimestamp(
            self.created_at
        )

    def updated_datetime(self) -> datetime:
        """
        Last update time as datetime.
        """

        return datetime.fromtimestamp(
            self.updated_at
        )

    # ------------------------------------------------------
    # Summary
    # ------------------------------------------------------

    def summary(self) -> JSONDict:
        """
        Lightweight summary.
        """

        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "state": self.state,
            "active": self.active,
            "uptime": self.uptime,
            "revision": self.revision,
            "viewer": self.has_viewer(),
        }
    # ==========================================================
    # Part 1.4
    # Base Runtime Helpers
    # ==========================================================

    # ----------------------------------------------------------
    # Internal Helpers
    # ----------------------------------------------------------

    def _now(self) -> float:
        """
        Return current UTC timestamp.
        """

        return utc_timestamp()

    def _generate_event(
        self,
        name: str,
        **payload: Any,
    ) -> RuntimeEvent:
        """
        Create runtime event.
        """

        event = RuntimeEvent(
            name=name,
            payload=payload,
        )

        return event

    def _record_event(
        self,
        name: str,
        **payload: Any,
    ) -> RuntimeEvent:
        """
        Store runtime event.
        """

        event = self._generate_event(
            name,
            **payload,
        )

        self.events.append(event)

        self.statistics.events += 1

        return event

    def _set_state(
        self,
        state: str,
    ) -> None:
        """
        Internal state transition.
        """

        if state not in VALID_STATES:
            raise ValueError(
                f"Invalid runtime state: {state}"
            )

        self.state = state

        self.touch()

    def _safe_call(
        self,
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Execute callback safely.
        """

        try:

            return func(
                *args,
                **kwargs,
            )

        except Exception as exc:

            self.last_error = str(exc)

            self.last_error_at = self._now()

            self.logger.exception(exc)

            return None

    # ----------------------------------------------------------
    # Request Helpers
    # ----------------------------------------------------------

    def begin_request(
        self,
        path: str = "",
        method: str = HTTP_GET,
    ) -> float:
        """
        Begin request.
        """

        start = self._now()

        self.statistics.requests += 1

        self.last_request_at = start

        self.request_history.append(
            {
                "path": path,
                "method": method,
                "started": start,
            }
        )

        return start

    def end_request(
        self,
        started_at: float,
        *,
        success: bool = True,
    ) -> float:
        """
        Finish request.
        """

        elapsed = self._now() - started_at

        self.statistics.total_response_time += elapsed

        if success:

            self.statistics.successful_requests += 1

        else:

            self.statistics.failed_requests += 1

        return elapsed

    # ----------------------------------------------------------
    # Runtime Checks
    # ----------------------------------------------------------

    def is_running(self) -> bool:
        """
        Runtime is running.
        """

        return self.running

    def is_enabled(self) -> bool:
        """
        Runtime enabled.
        """

        return self.enabled

    def is_closed(self) -> bool:
        """
        Runtime closed.
        """

        return self.closed

    def is_frozen(self) -> bool:
        """
        Runtime frozen.
        """

        return self.frozen

    def is_ready(self) -> bool:
        """
        Runtime ready.
        """

        return (
            self.enabled
            and not self.closed
            and not self.frozen
        )

    # ----------------------------------------------------------
    # Statistics Helpers
    # ----------------------------------------------------------

    def reset_statistics(self) -> "DashboardWebServer":
        """
        Reset runtime statistics.
        """

        self.statistics.reset()

        return self.touch()

    def statistics_dict(self) -> JSONDict:
        """
        Export runtime statistics.
        """

        return self.statistics.to_dict()

    # ----------------------------------------------------------
    # Event Helpers
    # ----------------------------------------------------------

    def clear_events(self) -> "DashboardWebServer":
        """
        Remove all runtime events.
        """

        self.events.clear()

        return self.touch()

    def event_count(self) -> int:
        """
        Number of stored events.
        """

        return len(self.events)

    def latest_event(
        self,
    ) -> RuntimeEvent | None:
        """
        Latest runtime event.
        """

        if not self.events:

            return None

        return self.events[-1]

    # ----------------------------------------------------------
    # Viewer Helpers
    # ----------------------------------------------------------

    def viewer_name(self) -> str | None:
        """
        Bound viewer class name.
        """

        if self.viewer is None:

            return None

        return self.viewer.__class__.__name__

    def viewer_info(self) -> JSONDict:
        """
        Viewer information.
        """

        if self.viewer is None:

            return {
                "available": False,
            }

        if hasattr(self.viewer, "info"):

            try:

                return self.viewer.info()

            except Exception:

                pass

        return {
            "available": True,
            "type": self.viewer.__class__.__name__,
        }

    # ----------------------------------------------------------
    # Runtime Snapshot
    # ----------------------------------------------------------

    def snapshot(self) -> JSONDict:
        """
        Export runtime snapshot.
        """

        return {
            "identity": self.identity_dict(),
            "metadata": self.metadata_dict(),
            "runtime": self.runtime_dict(),
            "statistics": self.statistics_dict(),
            "viewer": self.viewer_info(),
            "events": self.event_count(),
        }

    # ----------------------------------------------------------
    # Runtime Restore
    # ----------------------------------------------------------

    def restore(
        self,
        snapshot: Mapping[str, Any],
    ) -> "DashboardWebServer":
        """
        Restore basic runtime metadata.
        """

        metadata = snapshot.get(
            "metadata",
            {},
        )

        self.revision = metadata.get(
            "revision",
            self.revision,
        )

        self.updated_at = metadata.get(
            "updated_at",
            self.updated_at,
        )

        runtime = snapshot.get(
            "runtime",
            {},
        )

        self.state = runtime.get(
            "state",
            self.state,
        )

        self.enabled = runtime.get(
            "enabled",
            self.enabled,
        )

        self.running = runtime.get(
            "running",
            self.running,
        )

        self.frozen = runtime.get(
            "frozen",
            self.frozen,
        )

        self.closed = runtime.get(
            "closed",
            self.closed,
        )

        return self.touch()

    # ----------------------------------------------------------
    # Diagnostics
    # ----------------------------------------------------------

    def diagnostics(self) -> JSONDict:
        """
        Runtime diagnostics.
        """

        return {
            "identity": self.identity,
            "metadata": self.metadata,
            "runtime": self.runtime_dict(),
            "statistics": self.statistics_dict(),
            "viewer": self.viewer_info(),
            "events": self.event_count(),
            "hostname": self.hostname,
            "pid": self.process_id,
            "fastapi_available": FASTAPI_AVAILABLE,
        }
    # ==========================================================
    # Part 2.1
    # Configuration Properties & Defaults
    # ==========================================================

    # ----------------------------------------------------------
    # Default Configuration
    # ----------------------------------------------------------

    def load_default_configuration(self) -> "DashboardWebServer":
        """
        Initialize all runtime configuration with
        production-safe defaults.

        This method may be called from __init__() or reset().
        """

        # --------------------------------------------------
        # Network
        # --------------------------------------------------

        self.host = DEFAULT_HOST

        self.port = DEFAULT_PORT

        self.api_prefix = DEFAULT_API_PREFIX

        self.websocket_path = DEFAULT_WS_PATH

        self.base_url = (
            f"http://{self.host}:{self.port}"
        )

        # --------------------------------------------------
        # Runtime
        # --------------------------------------------------

        self.workers = 1

        self.worker_class = "thread"

        self.max_threads = 8

        self.timeout = 30

        self.keep_alive = 5

        self.backlog = 2048

        # --------------------------------------------------
        # Development
        # --------------------------------------------------

        self.debug = False

        self.reload = False

        self.verbose = False

        self.auto_reload_templates = False

        # --------------------------------------------------
        # Dashboard
        # --------------------------------------------------

        self.dashboard_title = self.name

        self.dashboard_theme = "light"

        self.dashboard_refresh = 1.0

        self.dashboard_cache = True

        self.dashboard_compression = True

        # --------------------------------------------------
        # REST API
        # --------------------------------------------------

        self.api_enabled = True

        self.api_version = "v1"

        self.openapi_enabled = True

        self.docs_enabled = True

        self.redoc_enabled = False

        # --------------------------------------------------
        # WebSocket
        # --------------------------------------------------

        self.websocket_enabled = True

        self.websocket_ping = 20

        self.websocket_timeout = 60

        self.websocket_max_clients = (
            DEFAULT_MAX_CONNECTIONS
        )

        self.websocket_compression = True

        # --------------------------------------------------
        # Static Resources
        # --------------------------------------------------

        self.static_enabled = True

        self.static_url = "/static"

        self.static_directory = None

        self.template_directory = None

        self.asset_directory = None

        # --------------------------------------------------
        # CORS
        # --------------------------------------------------

        self.cors_enabled = True

        self.cors_allow_origins = ["*"]

        self.cors_allow_methods = ["*"]

        self.cors_allow_headers = ["*"]

        self.cors_allow_credentials = False

        # --------------------------------------------------
        # SSL
        # --------------------------------------------------

        self.ssl_enabled = False

        self.ssl_cert = None

        self.ssl_key = None

        self.ssl_password = None

        # --------------------------------------------------
        # Authentication
        # --------------------------------------------------

        self.authentication_enabled = False

        self.authentication_provider = None

        self.authentication_config = {}

        # --------------------------------------------------
        # Rate Limit
        # --------------------------------------------------

        self.rate_limit_enabled = False

        self.rate_limit = 100

        self.rate_window = 60

        # --------------------------------------------------
        # Compression
        # --------------------------------------------------

        self.compression_enabled = True

        self.compression_level = 6

        self.minimum_compression_size = 1024

        # --------------------------------------------------
        # Logging
        # --------------------------------------------------

        self.logging_enabled = True

        self.access_log = True

        self.error_log = True

        self.log_requests = True

        self.log_responses = False

        # --------------------------------------------------
        # Metrics
        # --------------------------------------------------

        self.metrics_enabled = True

        self.metrics_route = "/metrics"

        self.prometheus_enabled = False

        # --------------------------------------------------
        # Health Check
        # --------------------------------------------------

        self.health_enabled = True

        self.health_route = "/health"

        self.health_interval = 30

        # --------------------------------------------------
        # Limits
        # --------------------------------------------------

        self.max_request_size = (
            100 * 1024 * 1024
        )

        self.max_response_size = (
            100 * 1024 * 1024
        )

        self.max_routes = 512

        self.max_events = DEFAULT_MAX_EVENTS

        self.max_history = (
            DEFAULT_MAX_REQUEST_HISTORY
        )

        # --------------------------------------------------
        # Misc
        # --------------------------------------------------

        self.configuration = {}

        self.labels = {}

        self.tags = set()

        self.attributes = {}

        self.environment = "production"

        self.touch()

        return self

    # ----------------------------------------------------------
    # Configuration Properties
    # ----------------------------------------------------------

    @property
    def configuration_state(self) -> JSONDict:
        """
        Runtime configuration summary.
        """

        return {

            "host": self.host,

            "port": self.port,

            "workers": self.workers,

            "debug": self.debug,

            "reload": self.reload,

            "api_enabled": self.api_enabled,

            "websocket_enabled":
                self.websocket_enabled,

            "ssl_enabled":
                self.ssl_enabled,

            "authentication_enabled":
                self.authentication_enabled,

            "metrics_enabled":
                self.metrics_enabled,

            "health_enabled":
                self.health_enabled,

            "environment":
                self.environment,

        }

    @property
    def address(self) -> str:
        """
        Runtime host:port.
        """

        return f"{self.host}:{self.port}"

    @property
    def endpoint(self) -> str:
        """
        Root endpoint.
        """

        protocol = (
            "https"
            if self.ssl_enabled
            else "http"
        )

        return (
            f"{protocol}://"
            f"{self.host}:"
            f"{self.port}"
        )

    @property
    def websocket_endpoint(self) -> str:
        """
        WebSocket endpoint.
        """

        protocol = (
            "wss"
            if self.ssl_enabled
            else "ws"
        )

        return (
            f"{protocol}://"
            f"{self.host}:"
            f"{self.port}"
            f"{self.websocket_path}"
        )

    @property
    def development_mode(self) -> bool:
        """
        Development mode.
        """

        return (
            self.debug
            or self.reload
            or self.environment.lower()
            == "development"
        )

    @property
    def production_mode(self) -> bool:
        """
        Production mode.
        """

        return not self.development_mode

    @property
    def security_enabled(self) -> bool:
        """
        Whether security features are active.
        """

        return (
            self.ssl_enabled
            or self.authentication_enabled
        )
    # ==========================================================
    # Part 2.2
    # Configuration API
    #
    # configure()
    # update_config()
    # merge_config()
    # ==========================================================

    # ----------------------------------------------------------
    # Configure
    # ----------------------------------------------------------

    def configure(
        self,
        **kwargs: Any,
    ) -> "DashboardWebServer":
        """
        Configure runtime.

        Example
        -------
        server.configure(
            host="0.0.0.0",
            port=8080,
            debug=True,
        )
        """

        return self.update_config(kwargs)

    # ----------------------------------------------------------
    # Update Configuration
    # ----------------------------------------------------------

    def update_config(
        self,
        configuration: Mapping[str, Any],
    ) -> "DashboardWebServer":
        """
        Update runtime configuration.

        Unknown keys are stored inside
        self.configuration.

        Returns
        -------
        DashboardWebServer
        """

        if configuration is None:

            return self

        configuration = dict(configuration)

        #
        # Known configuration fields
        #

        known_fields = {

            "host",

            "port",

            "workers",

            "worker_class",

            "max_threads",

            "timeout",

            "keep_alive",

            "backlog",

            "debug",

            "reload",

            "verbose",

            "environment",

            "api_prefix",

            "api_enabled",

            "api_version",

            "openapi_enabled",

            "docs_enabled",

            "redoc_enabled",

            "dashboard_title",

            "dashboard_theme",

            "dashboard_refresh",

            "dashboard_cache",

            "dashboard_compression",

            "websocket_enabled",

            "websocket_path",

            "websocket_ping",

            "websocket_timeout",

            "websocket_max_clients",

            "websocket_compression",

            "cors_enabled",

            "cors_allow_origins",

            "cors_allow_methods",

            "cors_allow_headers",

            "cors_allow_credentials",

            "ssl_enabled",

            "ssl_cert",

            "ssl_key",

            "ssl_password",

            "authentication_enabled",

            "authentication_provider",

            "authentication_config",

            "rate_limit_enabled",

            "rate_limit",

            "rate_window",

            "compression_enabled",

            "compression_level",

            "minimum_compression_size",

            "logging_enabled",

            "access_log",

            "error_log",

            "log_requests",

            "log_responses",

            "metrics_enabled",

            "metrics_route",

            "prometheus_enabled",

            "health_enabled",

            "health_route",

            "health_interval",

            "max_request_size",

            "max_response_size",

            "max_routes",

            "max_events",

            "max_history",

            "labels",

            "tags",

            "attributes",

        }

        #
        # Apply configuration
        #

        for key, value in configuration.items():

            if key in known_fields:

                setattr(
                    self,
                    key,
                    value,
                )

            else:

                self.configuration[key] = value

        #
        # Derived values
        #

        self.base_url = (
            f"http://{self.host}:{self.port}"
        )

        #
        # Validation
        #

        if hasattr(
            self,
            "validate_config",
        ):

            self.validate_config()

        self.touch()

        return self

    # ----------------------------------------------------------
    # Merge Configuration
    # ----------------------------------------------------------

    def merge_config(
        self,
        configuration: Mapping[str, Any],
        *,
        overwrite: bool = True,
    ) -> "DashboardWebServer":
        """
        Merge configuration.

        Parameters
        ----------
        overwrite

            True

                Existing values are replaced.

            False

                Existing values are preserved.
        """

        if configuration is None:

            return self

        for key, value in configuration.items():

            #
            # Existing attribute
            #

            if hasattr(
                self,
                key,
            ):

                current = getattr(
                    self,
                    key,
                )

                #
                # Merge dict
                #

                if (

                    isinstance(current, dict)

                    and

                    isinstance(value, Mapping)

                ):

                    merged = dict(current)

                    merged.update(value)

                    setattr(
                        self,
                        key,
                        merged,
                    )

                    continue

                #
                # Merge set
                #

                if (

                    isinstance(current, set)

                    and

                    isinstance(value, (set, list, tuple))

                ):

                    current.update(value)

                    continue

                #
                # Merge list
                #

                if (

                    isinstance(current, list)

                    and

                    isinstance(value, list)

                ):

                    current.extend(value)

                    continue

                #
                # Replace scalar
                #

                if overwrite:

                    setattr(
                        self,
                        key,
                        value,
                    )

            #
            # Unknown configuration
            #

            else:

                self.configuration[key] = value

        if hasattr(
            self,
            "validate_config",
        ):

            self.validate_config()

        self.touch()

        return self

    # ----------------------------------------------------------
    # Configuration Queries
    # ----------------------------------------------------------

    def get_config(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Get configuration value.
        """

        if hasattr(
            self,
            key,
        ):

            return getattr(
                self,
                key,
            )

        return self.configuration.get(
            key,
            default,
        )

    def has_config(
        self,
        key: str,
    ) -> bool:
        """
        Configuration exists.
        """

        return (

            hasattr(
                self,
                key,
            )

            or

            key in self.configuration

        )

    def remove_config(
        self,
        key: str,
    ) -> bool:
        """
        Remove custom configuration.
        """

        if key in self.configuration:

            del self.configuration[key]

            self.touch()

            return True

        return False

    # ----------------------------------------------------------
    # Reset Configuration
    # ----------------------------------------------------------

    def reset_configuration(
        self,
    ) -> "DashboardWebServer":
        """
        Restore default configuration.
        """

        self.load_default_configuration()

        return self

    # ----------------------------------------------------------
    # Export Configuration
    # ----------------------------------------------------------

    def config(
        self,
    ) -> JSONDict:
        """
        Export complete configuration.
        """

        return {

            "host": self.host,

            "port": self.port,

            "workers": self.workers,

            "debug": self.debug,

            "reload": self.reload,

            "environment": self.environment,

            "api_prefix": self.api_prefix,

            "base_url": self.base_url,

            "endpoint": self.endpoint,

            "websocket_endpoint":
                self.websocket_endpoint,

            "configuration":
                deep_copy(self.configuration),

            "labels":
                deep_copy(self.labels),

            "tags":
                sorted(self.tags),

            "attributes":
                deep_copy(self.attributes),

        }
    # ==========================================================
    # Part 2.3
    # Configuration Validation
    #
    # validate_config()
    # validate_host()
    # validate_port()
    # validate_workers()
    # validate_ssl()
    # validate_cors()
    # validate_authentication()
    # validate_websocket()
    # validate_limits()
    # validate_environment()
    # check_configuration()
    # ==========================================================

    # ----------------------------------------------------------
    # Validate All
    # ----------------------------------------------------------

    def validate_config(self) -> bool:
        """
        Validate the complete runtime configuration.

        Raises
        ------
        ValueError
            When configuration is invalid.

        Returns
        -------
        bool
            True if configuration is valid.
        """

        self.validate_host()
        self.validate_port()
        self.validate_workers()
        self.validate_environment()
        self.validate_ssl()
        self.validate_cors()
        self.validate_authentication()
        self.validate_websocket()
        self.validate_limits()

        return True

    # ----------------------------------------------------------
    # Host
    # ----------------------------------------------------------

    def validate_host(self) -> bool:
        """
        Validate host.
        """

        if not isinstance(self.host, str):

            raise TypeError(
                "host must be a string."
            )

        self.host = self.host.strip()

        if not self.host:

            raise ValueError(
                "host cannot be empty."
            )

        return True

    # ----------------------------------------------------------
    # Port
    # ----------------------------------------------------------

    def validate_port(self) -> bool:
        """
        Validate TCP port.
        """

        if not isinstance(self.port, int):

            raise TypeError(
                "port must be an integer."
            )

        if not (1 <= self.port <= 65535):

            raise ValueError(
                "port must be between 1 and 65535."
            )

        return True

    # ----------------------------------------------------------
    # Workers
    # ----------------------------------------------------------

    def validate_workers(self) -> bool:
        """
        Validate worker configuration.
        """

        if not isinstance(self.workers, int):

            raise TypeError(
                "workers must be an integer."
            )

        if self.workers < 1:

            raise ValueError(
                "workers must be >= 1."
            )

        if self.max_threads < 1:

            raise ValueError(
                "max_threads must be >= 1."
            )

        return True

    # ----------------------------------------------------------
    # Environment
    # ----------------------------------------------------------

    def validate_environment(self) -> bool:
        """
        Validate runtime environment.
        """

        allowed = {

            "development",
            "testing",
            "staging",
            "production",

        }

        env = str(
            self.environment
        ).lower()

        if env not in allowed:

            raise ValueError(
                f"Unsupported environment: {env}"
            )

        self.environment = env

        return True

    # ----------------------------------------------------------
    # SSL
    # ----------------------------------------------------------

    def validate_ssl(self) -> bool:
        """
        Validate SSL configuration.
        """

        if not self.ssl_enabled:

            return True

        if not self.ssl_cert:

            raise ValueError(
                "ssl_cert is required."
            )

        if not self.ssl_key:

            raise ValueError(
                "ssl_key is required."
            )

        cert = Path(self.ssl_cert)

        key = Path(self.ssl_key)

        if not cert.exists():

            raise FileNotFoundError(
                cert
            )

        if not key.exists():

            raise FileNotFoundError(
                key
            )

        return True

    # ----------------------------------------------------------
    # CORS
    # ----------------------------------------------------------

    def validate_cors(self) -> bool:
        """
        Validate CORS configuration.
        """

        if not self.cors_enabled:

            return True

        if not isinstance(
            self.cors_allow_origins,
            list,
        ):

            raise TypeError(
                "cors_allow_origins must be a list."
            )

        if not isinstance(
            self.cors_allow_methods,
            list,
        ):

            raise TypeError(
                "cors_allow_methods must be a list."
            )

        if not isinstance(
            self.cors_allow_headers,
            list,
        ):

            raise TypeError(
                "cors_allow_headers must be a list."
            )

        return True

    # ----------------------------------------------------------
    # Authentication
    # ----------------------------------------------------------

    def validate_authentication(self) -> bool:
        """
        Validate authentication settings.
        """

        if not self.authentication_enabled:

            return True

        if self.authentication_provider is None:

            raise ValueError(
                "authentication_provider is required."
            )

        if not isinstance(
            self.authentication_config,
            dict,
        ):

            raise TypeError(
                "authentication_config must be a dictionary."
            )

        return True

    # ----------------------------------------------------------
    # WebSocket
    # ----------------------------------------------------------

    def validate_websocket(self) -> bool:
        """
        Validate WebSocket configuration.
        """

        if not self.websocket_enabled:

            return True

        if not self.websocket_path.startswith("/"):

            raise ValueError(
                "websocket_path must start with '/'."
            )

        if self.websocket_ping <= 0:

            raise ValueError(
                "websocket_ping must be > 0."
            )

        if self.websocket_timeout <= 0:

            raise ValueError(
                "websocket_timeout must be > 0."
            )

        if self.websocket_max_clients < 1:

            raise ValueError(
                "websocket_max_clients must be >= 1."
            )

        return True

    # ----------------------------------------------------------
    # Limits
    # ----------------------------------------------------------

    def validate_limits(self) -> bool:
        """
        Validate runtime limits.
        """

        numeric_limits = {

            "max_request_size":
                self.max_request_size,

            "max_response_size":
                self.max_response_size,

            "max_routes":
                self.max_routes,

            "max_events":
                self.max_events,

            "max_history":
                self.max_history,

            "rate_limit":
                self.rate_limit,

            "rate_window":
                self.rate_window,

        }

        for name, value in numeric_limits.items():

            if value < 0:

                raise ValueError(
                    f"{name} must be >= 0."
                )

        return True

    # ----------------------------------------------------------
    # Diagnostics
    # ----------------------------------------------------------

    def check_configuration(self) -> JSONDict:
        """
        Run configuration diagnostics.

        Returns
        -------
        dict
            Validation report.
        """

        report = {

            "valid": True,

            "errors": [],

            "warnings": [],

        }

        validators = (

            self.validate_host,
            self.validate_port,
            self.validate_workers,
            self.validate_environment,
            self.validate_ssl,
            self.validate_cors,
            self.validate_authentication,
            self.validate_websocket,
            self.validate_limits,

        )

        for validator in validators:

            try:

                validator()

            except Exception as exc:

                report["valid"] = False

                report["errors"].append({

                    "validator":
                        validator.__name__,

                    "message":
                        str(exc),

                })

        #
        # Optional warnings
        #

        if self.debug and self.environment == "production":

            report["warnings"].append(
                "Debug mode enabled in production."
            )

        if (

            self.cors_enabled

            and

            self.cors_allow_origins == ["*"]

        ):

            report["warnings"].append(
                "CORS allows all origins."
            )

        if (

            not self.ssl_enabled

            and

            self.environment == "production"

        ):

            report["warnings"].append(
                "SSL is disabled."
            )

        return report
    # ==========================================================
    # Part 2.4
    # Runtime Configuration Helpers
    #
    # Debug
    # Reload
    # API
    # WebSocket
    # SSL
    # Authentication
    # CORS
    # Compression
    # Metrics
    # Health
    # Logging
    # Environment
    # ==========================================================

    # ----------------------------------------------------------
    # Debug
    # ----------------------------------------------------------

    def enable_debug(self) -> "DashboardWebServer":
        """
        Enable debug mode.
        """

        self.debug = True
        self.touch()

        return self

    def disable_debug(self) -> "DashboardWebServer":
        """
        Disable debug mode.
        """

        self.debug = False
        self.touch()

        return self

    # ----------------------------------------------------------
    # Auto Reload
    # ----------------------------------------------------------

    def enable_reload(self) -> "DashboardWebServer":
        """
        Enable auto reload.
        """

        self.reload = True
        self.touch()

        return self

    def disable_reload(self) -> "DashboardWebServer":
        """
        Disable auto reload.
        """

        self.reload = False
        self.touch()

        return self

    # ----------------------------------------------------------
    # Verbose
    # ----------------------------------------------------------

    def enable_verbose(self) -> "DashboardWebServer":
        """
        Enable verbose logging.
        """

        self.verbose = True
        self.touch()

        return self

    def disable_verbose(self) -> "DashboardWebServer":
        """
        Disable verbose logging.
        """

        self.verbose = False
        self.touch()

        return self

    # ----------------------------------------------------------
    # API
    # ----------------------------------------------------------

    def enable_api(self) -> "DashboardWebServer":
        """
        Enable REST API.
        """

        self.api_enabled = True
        self.touch()

        return self

    def disable_api(self) -> "DashboardWebServer":
        """
        Disable REST API.
        """

        self.api_enabled = False
        self.touch()

        return self

    # ----------------------------------------------------------
    # WebSocket
    # ----------------------------------------------------------

    def enable_websocket(self) -> "DashboardWebServer":
        """
        Enable WebSocket endpoint.
        """

        self.websocket_enabled = True
        self.touch()

        return self

    def disable_websocket(self) -> "DashboardWebServer":
        """
        Disable WebSocket endpoint.
        """

        self.websocket_enabled = False
        self.touch()

        return self

    # ----------------------------------------------------------
    # SSL
    # ----------------------------------------------------------

    def enable_ssl(
        self,
        cert: str,
        key: str,
        password: str | None = None,
    ) -> "DashboardWebServer":
        """
        Enable SSL.
        """

        self.ssl_enabled = True
        self.ssl_cert = cert
        self.ssl_key = key
        self.ssl_password = password

        self.validate_ssl()

        self.touch()

        return self

    def disable_ssl(self) -> "DashboardWebServer":
        """
        Disable SSL.
        """

        self.ssl_enabled = False
        self.ssl_cert = None
        self.ssl_key = None
        self.ssl_password = None

        self.touch()

        return self

    # ----------------------------------------------------------
    # Authentication
    # ----------------------------------------------------------

    def enable_authentication(
        self,
        provider: str,
        **configuration: Any,
    ) -> "DashboardWebServer":
        """
        Enable authentication.
        """

        self.authentication_enabled = True
        self.authentication_provider = provider
        self.authentication_config = dict(configuration)

        self.validate_authentication()

        self.touch()

        return self

    def disable_authentication(
        self,
    ) -> "DashboardWebServer":
        """
        Disable authentication.
        """

        self.authentication_enabled = False
        self.authentication_provider = None
        self.authentication_config.clear()

        self.touch()

        return self

    # ----------------------------------------------------------
    # CORS
    # ----------------------------------------------------------

    def enable_cors(
        self,
        origins: list[str] | None = None,
    ) -> "DashboardWebServer":
        """
        Enable CORS.
        """

        self.cors_enabled = True

        if origins is not None:

            self.cors_allow_origins = list(origins)

        self.validate_cors()

        self.touch()

        return self

    def disable_cors(self) -> "DashboardWebServer":
        """
        Disable CORS.
        """

        self.cors_enabled = False

        self.touch()

        return self

    # ----------------------------------------------------------
    # Compression
    # ----------------------------------------------------------

    def enable_compression(
        self,
        level: int | None = None,
    ) -> "DashboardWebServer":
        """
        Enable response compression.
        """

        self.compression_enabled = True

        if level is not None:

            self.compression_level = level

        self.touch()

        return self

    def disable_compression(
        self,
    ) -> "DashboardWebServer":
        """
        Disable response compression.
        """

        self.compression_enabled = False

        self.touch()

        return self

    # ----------------------------------------------------------
    # Metrics
    # ----------------------------------------------------------

    def enable_metrics(
        self,
    ) -> "DashboardWebServer":
        """
        Enable metrics endpoint.
        """

        self.metrics_enabled = True

        self.touch()

        return self

    def disable_metrics(
        self,
    ) -> "DashboardWebServer":
        """
        Disable metrics endpoint.
        """

        self.metrics_enabled = False

        self.touch()

        return self

    # ----------------------------------------------------------
    # Health
    # ----------------------------------------------------------

    def enable_health_check(
        self,
    ) -> "DashboardWebServer":
        """
        Enable health endpoint.
        """

        self.health_enabled = True

        self.touch()

        return self

    def disable_health_check(
        self,
    ) -> "DashboardWebServer":
        """
        Disable health endpoint.
        """

        self.health_enabled = False

        self.touch()

        return self

    # ----------------------------------------------------------
    # Logging
    # ----------------------------------------------------------

    def enable_logging(
        self,
    ) -> "DashboardWebServer":
        """
        Enable runtime logging.
        """

        self.logging_enabled = True

        self.touch()

        return self

    def disable_logging(
        self,
    ) -> "DashboardWebServer":
        """
        Disable runtime logging.
        """

        self.logging_enabled = False

        self.touch()

        return self

    # ----------------------------------------------------------
    # Environment
    # ----------------------------------------------------------

    def set_environment(
        self,
        environment: str,
    ) -> "DashboardWebServer":
        """
        Set runtime environment.

        Supported values:
            development
            testing
            staging
            production
        """

        self.environment = str(environment).lower()

        self.validate_environment()

        self.touch()

        return self

    # ----------------------------------------------------------
    # Batch Helpers
    # ----------------------------------------------------------

    def enable_production_mode(
        self,
    ) -> "DashboardWebServer":
        """
        Configure recommended production settings.
        """

        self.set_environment("production")

        self.disable_debug()
        self.disable_reload()

        self.enable_api()
        self.enable_websocket()
        self.enable_metrics()
        self.enable_health_check()
        self.enable_compression()
        self.enable_logging()

        return self

    def enable_development_mode(
        self,
    ) -> "DashboardWebServer":
        """
        Configure recommended development settings.
        """

        self.set_environment("development")

        self.enable_debug()
        self.enable_reload()
        self.enable_verbose()

        self.enable_api()
        self.enable_websocket()
        self.enable_metrics()
        self.enable_health_check()

        return self

    # ----------------------------------------------------------
    # Configuration Refresh
    # ----------------------------------------------------------

    def refresh_configuration(
        self,
    ) -> "DashboardWebServer":
        """
        Recompute derived configuration values
        and validate the current configuration.
        """

        protocol = (
            "https"
            if self.ssl_enabled
            else "http"
        )

        self.base_url = (
            f"{protocol}://{self.host}:{self.port}"
        )

        self.validate_config()

        self.touch()

        return self
    # ==========================================================
    # Part 2.5
    # Export & Serialization
    #
    # config()
    # configuration_state()
    # to_config_dict()
    # to_json()
    # from_config_dict()
    # load_config()
    # save_config()
    # export_config()
    # ==========================================================

    # ----------------------------------------------------------
    # Configuration State
    # ----------------------------------------------------------

    @property
    def configuration_state(self) -> JSONDict:
        """
        Lightweight runtime configuration summary.

        Returns
        -------
        dict
        """

        return {

            "host": self.host,

            "port": self.port,

            "endpoint": self.endpoint,

            "environment": self.environment,

            "debug": self.debug,

            "reload": self.reload,

            "workers": self.workers,

            "running": self.running,

            "enabled": self.enabled,

            "closed": self.closed,

            "ssl": self.ssl_enabled,

            "websocket": self.websocket_enabled,

            "metrics": self.metrics_enabled,

            "authentication":
                self.authentication_enabled,

            "revision":
                self.revision,

        }

    # ----------------------------------------------------------
    # Configuration Export
    # ----------------------------------------------------------

    def config(self) -> JSONDict:
        """
        Alias of to_config_dict().
        """

        return self.to_config_dict()

    def to_config_dict(self) -> JSONDict:
        """
        Export complete configuration.

        Returns
        -------
        dict
        """

        return {

            # --------------------------------------
            # Identity
            # --------------------------------------

            "id":
                self.id,

            "name":
                self.name,

            "version":
                self.version,

            "description":
                self.description,

            "server_type":
                self.server_type,

            # --------------------------------------
            # Network
            # --------------------------------------

            "host":
                self.host,

            "port":
                self.port,

            "endpoint":
                self.endpoint,

            "api_prefix":
                self.api_prefix,

            "base_url":
                self.base_url,

            # --------------------------------------
            # Runtime
            # --------------------------------------

            "environment":
                self.environment,

            "workers":
                self.workers,

            "worker_class":
                self.worker_class,

            "max_threads":
                self.max_threads,

            "timeout":
                self.timeout,

            "keep_alive":
                self.keep_alive,

            "backlog":
                self.backlog,

            # --------------------------------------
            # Development
            # --------------------------------------

            "debug":
                self.debug,

            "reload":
                self.reload,

            "verbose":
                self.verbose,

            # --------------------------------------
            # Dashboard
            # --------------------------------------

            "dashboard_title":
                self.dashboard_title,

            "dashboard_theme":
                self.dashboard_theme,

            "dashboard_refresh":
                self.dashboard_refresh,

            "dashboard_cache":
                self.dashboard_cache,

            "dashboard_compression":
                self.dashboard_compression,

            # --------------------------------------
            # REST
            # --------------------------------------

            "api_enabled":
                self.api_enabled,

            "api_version":
                self.api_version,

            "openapi_enabled":
                self.openapi_enabled,

            "docs_enabled":
                self.docs_enabled,

            "redoc_enabled":
                self.redoc_enabled,

            # --------------------------------------
            # WebSocket
            # --------------------------------------

            "websocket_enabled":
                self.websocket_enabled,

            "websocket_path":
                self.websocket_path,

            "websocket_ping":
                self.websocket_ping,

            "websocket_timeout":
                self.websocket_timeout,

            "websocket_max_clients":
                self.websocket_max_clients,

            # --------------------------------------
            # SSL
            # --------------------------------------

            "ssl_enabled":
                self.ssl_enabled,

            "ssl_cert":
                self.ssl_cert,

            "ssl_key":
                self.ssl_key,

            # --------------------------------------
            # Authentication
            # --------------------------------------

            "authentication_enabled":
                self.authentication_enabled,

            "authentication_provider":
                self.authentication_provider,

            "authentication_config":
                deep_copy(
                    self.authentication_config
                ),

            # --------------------------------------
            # CORS
            # --------------------------------------

            "cors_enabled":
                self.cors_enabled,

            "cors_allow_origins":
                list(self.cors_allow_origins),

            "cors_allow_methods":
                list(self.cors_allow_methods),

            "cors_allow_headers":
                list(self.cors_allow_headers),

            "cors_allow_credentials":
                self.cors_allow_credentials,

            # --------------------------------------
            # Compression
            # --------------------------------------

            "compression_enabled":
                self.compression_enabled,

            "compression_level":
                self.compression_level,

            # --------------------------------------
            # Metrics
            # --------------------------------------

            "metrics_enabled":
                self.metrics_enabled,

            "metrics_route":
                self.metrics_route,

            "prometheus_enabled":
                self.prometheus_enabled,

            # --------------------------------------
            # Health
            # --------------------------------------

            "health_enabled":
                self.health_enabled,

            "health_route":
                self.health_route,

            # --------------------------------------
            # Logging
            # --------------------------------------

            "logging_enabled":
                self.logging_enabled,

            "access_log":
                self.access_log,

            "error_log":
                self.error_log,

            "log_requests":
                self.log_requests,

            "log_responses":
                self.log_responses,

            # --------------------------------------
            # Limits
            # --------------------------------------

            "max_request_size":
                self.max_request_size,

            "max_response_size":
                self.max_response_size,

            "max_routes":
                self.max_routes,

            "max_events":
                self.max_events,

            "max_history":
                self.max_history,

            # --------------------------------------
            # Metadata
            # --------------------------------------

            "labels":
                deep_copy(self.labels),

            "attributes":
                deep_copy(self.attributes),

            "tags":
                sorted(self.tags),

            "configuration":
                deep_copy(self.configuration),

            # --------------------------------------
            # Runtime Metadata
            # --------------------------------------

            "created_at":
                self.created_at,

            "updated_at":
                self.updated_at,

            "revision":
                self.revision,

        }

    # ----------------------------------------------------------
    # JSON Serialization
    # ----------------------------------------------------------

    def to_json(
        self,
        *,
        indent: int = 4,
        sort_keys: bool = False,
    ) -> str:
        """
        Serialize configuration to JSON.
        """

        return json.dumps(

            self.to_config_dict(),

            indent=indent,

            sort_keys=sort_keys,

            default=str,

        )

    # ----------------------------------------------------------
    # Import Configuration
    # ----------------------------------------------------------

    def from_config_dict(
        self,
        configuration: Mapping[str, Any],
    ) -> "DashboardWebServer":
        """
        Restore configuration from dictionary.
        """

        self.update_config(
            dict(configuration)
        )

        return self

    def load_config(
        self,
        configuration: Mapping[str, Any],
    ) -> "DashboardWebServer":
        """
        Alias of from_config_dict().
        """

        return self.from_config_dict(
            configuration
        )

    # ----------------------------------------------------------
    # Save Configuration
    # ----------------------------------------------------------

    def save_config(
        self,
        path: str | Path,
        *,
        indent: int = 4,
    ) -> Path:
        """
        Save configuration to JSON file.
        """

        path = Path(path)

        path.parent.mkdir(

            parents=True,

            exist_ok=True,

        )

        path.write_text(

            self.to_json(
                indent=indent,
            ),

            encoding="utf-8",

        )

        return path

    # ----------------------------------------------------------
    # Export Configuration
    # ----------------------------------------------------------

    def export_config(
        self,
        path: str | Path | None = None,
    ) -> JSONDict | Path:
        """
        Export configuration.

        Parameters
        ----------
        path

            None
                Return dictionary.

            Path
                Save to JSON.

        Returns
        -------
        dict | Path
        """

        if path is None:

            return self.to_config_dict()

        return self.save_config(path)
    # ==========================================================
    # Part 3.1
    # Runtime State Properties
    #
    # state
    # previous_state
    # running
    # enabled
    # frozen
    # closed
    # started_at
    # stopped_at
    # last_activity
    # last_error
    # uptime
    # ==========================================================

    # ----------------------------------------------------------
    # Runtime State
    # ----------------------------------------------------------

    @property
    def state(self) -> str:
        """
        Current runtime state.
        """

        return self._state

    @state.setter
    def state(
        self,
        value: str,
    ) -> None:
        """
        Update runtime state.

        Automatically records the previous state and
        updates runtime timestamps.
        """

        value = str(value).lower()

        if hasattr(self, "_state"):

            if self._state == value:

                return

            self._previous_state = self._state

        else:

            self._previous_state = None

        self._state = value

        self.last_activity = self._now()

        if hasattr(self, "touch"):

            self.touch()

    @property
    def previous_state(self) -> str | None:
        """
        Previous runtime state.
        """

        return self._previous_state

    # ----------------------------------------------------------
    # Runtime Flags
    # ----------------------------------------------------------

    @property
    def running(self) -> bool:
        """
        Whether runtime is currently running.
        """

        return self._running

    @running.setter
    def running(
        self,
        value: bool,
    ) -> None:

        value = bool(value)

        #
        # Starting
        #

        if value and not getattr(self, "_running", False):

            self.started_at = self._now()

            self.last_activity = self.started_at

            self.stopped_at = None

        #
        # Stopping
        #

        elif (

            not value

            and

            getattr(self, "_running", False)

        ):

            self.stopped_at = self._now()

            self.last_activity = self.stopped_at

        self._running = value

    @property
    def enabled(self) -> bool:
        """
        Runtime enabled.
        """

        return self._enabled

    @enabled.setter
    def enabled(
        self,
        value: bool,
    ) -> None:

        self._enabled = bool(value)

        self.last_activity = self._now()

    @property
    def frozen(self) -> bool:
        """
        Runtime frozen.
        """

        return self._frozen

    @frozen.setter
    def frozen(
        self,
        value: bool,
    ) -> None:

        self._frozen = bool(value)

        self.last_activity = self._now()

    @property
    def closed(self) -> bool:
        """
        Runtime closed.
        """

        return self._closed

    @closed.setter
    def closed(
        self,
        value: bool,
    ) -> None:

        self._closed = bool(value)

        self.last_activity = self._now()

    # ----------------------------------------------------------
    # Runtime Timestamps
    # ----------------------------------------------------------

    @property
    def started_at(self) -> float | None:
        """
        Runtime start timestamp.
        """

        return self._started_at

    @started_at.setter
    def started_at(
        self,
        value: float | None,
    ) -> None:

        self._started_at = value

    @property
    def stopped_at(self) -> float | None:
        """
        Runtime stop timestamp.
        """

        return self._stopped_at

    @stopped_at.setter
    def stopped_at(
        self,
        value: float | None,
    ) -> None:

        self._stopped_at = value

    @property
    def last_activity(self) -> float | None:
        """
        Last runtime activity timestamp.
        """

        return self._last_activity

    @last_activity.setter
    def last_activity(
        self,
        value: float | None,
    ) -> None:

        self._last_activity = value

    # ----------------------------------------------------------
    # Runtime Errors
    # ----------------------------------------------------------

    @property
    def last_error(self) -> str | None:
        """
        Last runtime error.
        """

        return self._last_error

    @last_error.setter
    def last_error(
        self,
        value: str | Exception | None,
    ) -> None:

        if value is None:

            self._last_error = None

        else:

            self._last_error = str(value)

        self.last_activity = self._now()

    @property
    def has_error(self) -> bool:
        """
        Whether runtime has an error.
        """

        return self.last_error is not None

    # ----------------------------------------------------------
    # Runtime Uptime
    # ----------------------------------------------------------

    @property
    def uptime(self) -> float:
        """
        Runtime uptime in seconds.
        """

        if self.started_at is None:

            return 0.0

        #
        # Runtime currently running
        #

        if self.running:

            return max(

                0.0,

                self._now() - self.started_at,

            )

        #
        # Runtime stopped
        #

        if self.stopped_at is None:

            return 0.0

        return max(

            0.0,

            self.stopped_at - self.started_at,

        )

    # ----------------------------------------------------------
    # Runtime Status
    # ----------------------------------------------------------

    @property
    def active(self) -> bool:
        """
        Runtime is active.
        """

        return (

            self.enabled

            and

            self.running

            and

            not self.frozen

            and

            not self.closed

        )

    @property
    def inactive(self) -> bool:
        """
        Runtime inactive.
        """

        return not self.active

    @property
    def idle(self) -> bool:
        """
        Runtime idle.
        """

        return (

            self.running

            and

            not self.frozen

            and

            self.last_activity is not None

            and

            (self._now() - self.last_activity)

            > 60

        )

    @property
    def runtime_state(self) -> JSONDict:
        """
        Export runtime state.
        """

        return {

            "state":
                self.state,

            "previous_state":
                self.previous_state,

            "running":
                self.running,

            "enabled":
                self.enabled,

            "frozen":
                self.frozen,

            "closed":
                self.closed,

            "active":
                self.active,

            "uptime":
                self.uptime,

            "started_at":
                self.started_at,

            "stopped_at":
                self.stopped_at,

            "last_activity":
                self.last_activity,

            "last_error":
                self.last_error,

        }
    # ==========================================================
    # Part 3.2
    # Runtime Statistics
    #
    # Request Counters
    # WebSocket Counters
    # Latency
    # Error Counters
    # Throughput
    # Statistics Helpers
    # ==========================================================

    # ----------------------------------------------------------
    # Request Counters
    # ----------------------------------------------------------

    @property
    def request_count(self) -> int:
        """
        Total received requests.
        """
        return self._request_count

    @request_count.setter
    def request_count(
        self,
        value: int,
    ) -> None:
        self._request_count = max(
            0,
            int(value),
        )

    @property
    def success_count(self) -> int:
        """
        Successfully completed requests.
        """
        return self._success_count

    @success_count.setter
    def success_count(
        self,
        value: int,
    ) -> None:
        self._success_count = max(
            0,
            int(value),
        )

    @property
    def error_count(self) -> int:
        """
        Failed requests.
        """
        return self._error_count

    @error_count.setter
    def error_count(
        self,
        value: int,
    ) -> None:
        self._error_count = max(
            0,
            int(value),
        )

    @property
    def pending_requests(self) -> int:
        """
        Requests currently in progress.
        """
        return self._pending_requests

    @pending_requests.setter
    def pending_requests(
        self,
        value: int,
    ) -> None:
        self._pending_requests = max(
            0,
            int(value),
        )

    # ----------------------------------------------------------
    # WebSocket Counters
    # ----------------------------------------------------------

    @property
    def websocket_connections(self) -> int:
        """
        Active websocket clients.
        """
        return self._websocket_connections

    @websocket_connections.setter
    def websocket_connections(
        self,
        value: int,
    ) -> None:
        self._websocket_connections = max(
            0,
            int(value),
        )

    @property
    def websocket_messages(self) -> int:
        """
        Total websocket messages.
        """
        return self._websocket_messages

    @websocket_messages.setter
    def websocket_messages(
        self,
        value: int,
    ) -> None:
        self._websocket_messages = max(
            0,
            int(value),
        )

    @property
    def websocket_bytes_sent(self) -> int:
        """
        Total websocket bytes sent.
        """
        return self._websocket_bytes_sent

    @websocket_bytes_sent.setter
    def websocket_bytes_sent(
        self,
        value: int,
    ) -> None:
        self._websocket_bytes_sent = max(
            0,
            int(value),
        )

    @property
    def websocket_bytes_received(self) -> int:
        """
        Total websocket bytes received.
        """
        return self._websocket_bytes_received

    @websocket_bytes_received.setter
    def websocket_bytes_received(
        self,
        value: int,
    ) -> None:
        self._websocket_bytes_received = max(
            0,
            int(value),
        )

    # ----------------------------------------------------------
    # Latency
    # ----------------------------------------------------------

    @property
    def total_response_time(self) -> float:
        """
        Total accumulated response time.
        """
        return self._total_response_time

    @total_response_time.setter
    def total_response_time(
        self,
        value: float,
    ) -> None:
        self._total_response_time = max(
            0.0,
            float(value),
        )

    @property
    def minimum_latency(self) -> float:
        return self._minimum_latency

    @minimum_latency.setter
    def minimum_latency(
        self,
        value: float,
    ) -> None:
        self._minimum_latency = max(
            0.0,
            float(value),
        )

    @property
    def maximum_latency(self) -> float:
        return self._maximum_latency

    @maximum_latency.setter
    def maximum_latency(
        self,
        value: float,
    ) -> None:
        self._maximum_latency = max(
            0.0,
            float(value),
        )

    @property
    def average_response_time(self) -> float:
        """
        Average request latency.
        """
        if self.success_count == 0:
            return 0.0

        return (
            self.total_response_time
            / self.success_count
        )

    # ----------------------------------------------------------
    # Error Statistics
    # ----------------------------------------------------------

    @property
    def last_exception(self) -> str | None:
        """
        Last exception.
        """
        return self._last_exception

    @last_exception.setter
    def last_exception(
        self,
        value: str | None,
    ) -> None:
        self._last_exception = (
            None
            if value is None
            else str(value)
        )

    @property
    def error_rate(self) -> float:
        """
        Error percentage.
        """
        if self.request_count == 0:
            return 0.0

        return (
            self.error_count
            / self.request_count
        )

    @property
    def success_rate(self) -> float:
        """
        Success percentage.
        """
        if self.request_count == 0:
            return 0.0

        return (
            self.success_count
            / self.request_count
        )

    # ----------------------------------------------------------
    # Throughput
    # ----------------------------------------------------------

    @property
    def requests_per_second(self) -> float:
        """
        Average request throughput.
        """
        uptime = self.uptime

        if uptime <= 0:
            return 0.0

        return (
            self.request_count
            / uptime
        )

    @property
    def websocket_messages_per_second(
        self,
    ) -> float:
        """
        WebSocket throughput.
        """
        uptime = self.uptime

        if uptime <= 0:
            return 0.0

        return (
            self.websocket_messages
            / uptime
        )

    # ----------------------------------------------------------
    # Statistics Helpers
    # ----------------------------------------------------------

    @property
    def statistics(self) -> JSONDict:
        """
        Complete runtime statistics.
        """

        return {

            "requests": {

                "total":
                    self.request_count,

                "pending":
                    self.pending_requests,

                "success":
                    self.success_count,

                "errors":
                    self.error_count,

            },

            "latency": {

                "average":
                    self.average_response_time,

                "minimum":
                    self.minimum_latency,

                "maximum":
                    self.maximum_latency,

                "total":
                    self.total_response_time,

            },

            "websocket": {

                "connections":
                    self.websocket_connections,

                "messages":
                    self.websocket_messages,

                "bytes_sent":
                    self.websocket_bytes_sent,

                "bytes_received":
                    self.websocket_bytes_received,

            },

            "throughput": {

                "requests_per_second":
                    self.requests_per_second,

                "messages_per_second":
                    self.websocket_messages_per_second,

            },

            "rates": {

                "success":
                    self.success_rate,

                "error":
                    self.error_rate,

            },

            "last_exception":
                self.last_exception,

        }

    def reset_statistics(
        self,
    ) -> "DashboardWebServer":
        """
        Reset all runtime statistics.
        """

        self.request_count = 0
        self.pending_requests = 0
        self.success_count = 0
        self.error_count = 0

        self.websocket_connections = 0
        self.websocket_messages = 0
        self.websocket_bytes_sent = 0
        self.websocket_bytes_received = 0

        self.total_response_time = 0.0
        self.minimum_latency = 0.0
        self.maximum_latency = 0.0

        self.last_exception = None

        self.touch()

        return self

    def statistics_summary(self) -> JSONDict:
        """
        Lightweight statistics summary.
        """

        return {

            "requests":
                self.request_count,

            "success":
                self.success_count,

            "errors":
                self.error_count,

            "avg_latency":
                self.average_response_time,

            "rps":
                self.requests_per_second,

            "ws_clients":
                self.websocket_connections,

            "ws_messages":
                self.websocket_messages,

            "uptime":
                self.uptime,

        }
    # ==========================================================
    # Part 3.3
    # State Transition API
    #
    # set_state()
    # transition_to()
    # is_running()
    # is_ready()
    # is_closed()
    # is_frozen()
    # ==========================================================

    # ----------------------------------------------------------
    # Runtime States
    # ----------------------------------------------------------

    STATE_CREATED = "created"
    STATE_INITIALIZING = "initializing"
    STATE_READY = "ready"
    STATE_RUNNING = "running"
    STATE_PAUSED = "paused"
    STATE_FROZEN = "frozen"
    STATE_STOPPING = "stopping"
    STATE_STOPPED = "stopped"
    STATE_DISABLED = "disabled"
    STATE_CLOSED = "closed"
    STATE_ERROR = "error"

    VALID_STATES = frozenset({

        STATE_CREATED,

        STATE_INITIALIZING,

        STATE_READY,

        STATE_RUNNING,

        STATE_PAUSED,

        STATE_FROZEN,

        STATE_STOPPING,

        STATE_STOPPED,

        STATE_DISABLED,

        STATE_CLOSED,

        STATE_ERROR,

    })

    # ----------------------------------------------------------
    # State Transition Table
    # ----------------------------------------------------------

    _STATE_TRANSITIONS = {

        STATE_CREATED: {

            STATE_INITIALIZING,
            STATE_READY,
            STATE_DISABLED,
            STATE_CLOSED,

        },

        STATE_INITIALIZING: {

            STATE_READY,
            STATE_ERROR,
            STATE_CLOSED,

        },

        STATE_READY: {

            STATE_RUNNING,
            STATE_DISABLED,
            STATE_CLOSED,
            STATE_ERROR,

        },

        STATE_RUNNING: {

            STATE_PAUSED,
            STATE_STOPPING,
            STATE_FROZEN,
            STATE_ERROR,

        },

        STATE_PAUSED: {

            STATE_RUNNING,
            STATE_STOPPING,
            STATE_FROZEN,
            STATE_ERROR,

        },

        STATE_FROZEN: {

            STATE_RUNNING,
            STATE_READY,
            STATE_STOPPING,
            STATE_ERROR,

        },

        STATE_STOPPING: {

            STATE_STOPPED,
            STATE_ERROR,

        },

        STATE_STOPPED: {

            STATE_READY,
            STATE_RUNNING,
            STATE_CLOSED,

        },

        STATE_DISABLED: {

            STATE_READY,
            STATE_CLOSED,

        },

        STATE_ERROR: {

            STATE_READY,
            STATE_STOPPED,
            STATE_CLOSED,

        },

        STATE_CLOSED: set(),

    }

    # ----------------------------------------------------------
    # Set State
    # ----------------------------------------------------------

    def set_state(
        self,
        state: str,
        *,
        force: bool = False,
    ) -> "DashboardWebServer":
        """
        Set runtime state.

        Parameters
        ----------
        state:
            Target runtime state.

        force:
            Ignore transition validation.
        """

        state = str(state).lower()

        if state not in self.VALID_STATES:

            raise ValueError(
                f"Invalid runtime state: {state}"
            )

        if not force:

            self.transition_to(state)

        else:

            self.previous_state = self.state
            self.state = state

            self._apply_state_flags(state)

            self.last_activity = self._now()

            self.touch()

        return self

    # ----------------------------------------------------------
    # Transition
    # ----------------------------------------------------------

    def transition_to(
        self,
        target: str,
    ) -> "DashboardWebServer":
        """
        Transition runtime to another state.

        Raises
        ------
        RuntimeError
            If transition is illegal.
        """

        target = str(target).lower()

        if target == self.state:

            return self

        allowed = self._STATE_TRANSITIONS.get(

            self.state,

            set(),

        )

        if target not in allowed:

            raise RuntimeError(

                f"Illegal transition "

                f"{self.state!r} -> {target!r}"

            )

        self.previous_state = self.state

        self.state = target

        self._apply_state_flags(target)

        self.last_activity = self._now()

        self.touch()

        return self

    # ----------------------------------------------------------
    # Apply Runtime Flags
    # ----------------------------------------------------------

    def _apply_state_flags(
        self,
        state: str,
    ) -> None:
        """
        Synchronize runtime flags with state.
        """

        self.running = (
            state == self.STATE_RUNNING
        )

        self.frozen = (
            state == self.STATE_FROZEN
        )

        self.closed = (
            state == self.STATE_CLOSED
        )

        self.enabled = (

            state

            not in {

                self.STATE_DISABLED,
                self.STATE_CLOSED,

            }

        )

        if state == self.STATE_STOPPED:

            self.running = False

        elif state == self.STATE_STOPPING:

            self.running = False

        elif state == self.STATE_PAUSED:

            self.running = False

    # ----------------------------------------------------------
    # State Queries
    # ----------------------------------------------------------

    def is_running(self) -> bool:
        """
        Runtime is running.
        """

        return (

            self.state == self.STATE_RUNNING

            and

            self.running

        )

    def is_ready(self) -> bool:
        """
        Runtime is ready.
        """

        return (

            self.state == self.STATE_READY

        )

    def is_closed(self) -> bool:
        """
        Runtime is closed.
        """

        return (

            self.state == self.STATE_CLOSED

            or

            self.closed

        )

    def is_frozen(self) -> bool:
        """
        Runtime is frozen.
        """

        return (

            self.state == self.STATE_FROZEN

            or

            self.frozen

        )

    def is_enabled(self) -> bool:
        """
        Runtime enabled.
        """

        return self.enabled

    def is_disabled(self) -> bool:
        """
        Runtime disabled.
        """

        return not self.enabled

    def is_created(self) -> bool:
        """
        Runtime newly created.
        """

        return self.state == self.STATE_CREATED

    def is_initialized(self) -> bool:
        """
        Runtime initialized.
        """

        return self.state == self.STATE_INITIALIZING

    def is_stopped(self) -> bool:
        """
        Runtime stopped.
        """

        return self.state == self.STATE_STOPPED

    def is_error(self) -> bool:
        """
        Runtime is in error state.
        """

        return self.state == self.STATE_ERROR

    # ----------------------------------------------------------
    # Transition Information
    # ----------------------------------------------------------

    @property
    def available_transitions(
        self,
    ) -> tuple[str, ...]:
        """
        Available transitions from current state.
        """

        return tuple(

            sorted(

                self._STATE_TRANSITIONS.get(

                    self.state,

                    set(),

                )

            )

        )

    @property
    def state_transition_table(
        self,
    ) -> dict[str, tuple[str, ...]]:
        """
        Export transition table.
        """

        return {

            state: tuple(sorted(targets))

            for state, targets

            in self._STATE_TRANSITIONS.items()

        }

    def can_transition_to(
        self,
        target: str,
    ) -> bool:
        """
        Check whether transition is allowed.
        """

        target = str(target).lower()

        return (

            target

            in

            self._STATE_TRANSITIONS.get(

                self.state,

                set(),

            )

        )
    # ==========================================================
    # Part 3.4
    # Request Runtime
    #
    # request_started()
    # request_completed()
    # request_failed()
    # average_response_time
    # request_history
    # ==========================================================

    # ----------------------------------------------------------
    # Request Started
    # ----------------------------------------------------------

    def request_started(
        self,
        *,
        method: str = "GET",
        path: str = "/",
        client: str | None = None,
    ) -> dict[str, Any]:
        """
        Register an incoming request.

        Returns
        -------
        dict
            Runtime request context.
        """

        now = self._now()

        self.request_count += 1

        self.pending_requests += 1

        self.last_activity = now

        self._active_requests += 1

        self._last_request = {

            "id": self.request_count,

            "method": method,

            "path": path,

            "client": client,

            "started_at": now,

        }

        self._request_history.append({

            "id": self.request_count,

            "method": method,

            "path": path,

            "client": client,

            "status": "running",

            "started_at": now,

            "completed_at": None,

            "duration": None,

            "error": None,

        })

        if len(self._request_history) > self.max_history:

            self._request_history.pop(0)

        self.touch()

        return self._last_request

    # ----------------------------------------------------------
    # Request Completed
    # ----------------------------------------------------------

    def request_completed(
        self,
        duration: float,
        *,
        status_code: int = 200,
        bytes_sent: int = 0,
    ) -> None:
        """
        Register a successful request.
        """

        duration = max(
            0.0,
            float(duration),
        )

        now = self._now()

        self.success_count += 1

        self.pending_requests = max(

            0,

            self.pending_requests - 1,

        )

        self._active_requests = max(

            0,

            self._active_requests - 1,

        )

        self.total_response_time += duration

        #
        # latency
        #

        if (

            self.minimum_latency == 0

            or

            duration < self.minimum_latency

        ):

            self.minimum_latency = duration

        if duration > self.maximum_latency:

            self.maximum_latency = duration

        #
        # traffic
        #

        self._bytes_sent += max(

            0,

            int(bytes_sent),

        )

        #
        # history
        #

        if self._request_history:

            item = self._request_history[-1]

            if item["status"] == "running":

                item["status"] = "completed"

                item["completed_at"] = now

                item["duration"] = duration

                item["status_code"] = status_code

        self.last_activity = now

        self.touch()

    # ----------------------------------------------------------
    # Request Failed
    # ----------------------------------------------------------

    def request_failed(
        self,
        error: Exception | str,
        *,
        status_code: int = 500,
    ) -> None:
        """
        Register a failed request.
        """

        now = self._now()

        message = str(error)

        self.error_count += 1

        self.pending_requests = max(

            0,

            self.pending_requests - 1,

        )

        self._active_requests = max(

            0,

            self._active_requests - 1,

        )

        self.last_error = message

        self.last_exception = message

        self._error_history.append({

            "time": now,

            "message": message,

            "status_code": status_code,

        })

        if len(self._error_history) > self.max_history:

            self._error_history.pop(0)

        if self._request_history:

            item = self._request_history[-1]

            if item["status"] == "running":

                item["status"] = "failed"

                item["completed_at"] = now

                item["duration"] = (

                    now - item["started_at"]

                )

                item["status_code"] = status_code

                item["error"] = message

        self.last_activity = now

        self.touch()

    # ----------------------------------------------------------
    # Request Properties
    # ----------------------------------------------------------

    @property
    def average_response_time(self) -> float:
        """
        Mean response latency.
        """

        if self.success_count == 0:

            return 0.0

        return (

            self.total_response_time

            /

            self.success_count

        )

    @property
    def active_requests(self) -> int:
        """
        Number of executing requests.
        """

        return self._active_requests

    @property
    def bytes_sent(self) -> int:
        """
        Total transmitted bytes.
        """

        return self._bytes_sent

    @property
    def last_request(self) -> dict[str, Any] | None:
        """
        Last request information.
        """

        return self._last_request

    # ----------------------------------------------------------
    # Request History
    # ----------------------------------------------------------

    @property
    def request_history(
        self,
    ) -> list[dict[str, Any]]:
        """
        Complete request history.
        """

        return list(

            self._request_history

        )

    @property
    def error_history(
        self,
    ) -> list[dict[str, Any]]:
        """
        Runtime error history.
        """

        return list(

            self._error_history

        )

    def clear_request_history(
        self,
    ) -> "DashboardWebServer":
        """
        Clear request history.
        """

        self._request_history.clear()

        self._error_history.clear()

        self.touch()

        return self

    # ----------------------------------------------------------
    # Request Summary
    # ----------------------------------------------------------

    def request_statistics(
        self,
    ) -> JSONDict:
        """
        Request runtime statistics.
        """

        return {

            "total":
                self.request_count,

            "active":
                self.active_requests,

            "pending":
                self.pending_requests,

            "success":
                self.success_count,

            "failed":
                self.error_count,

            "success_rate":
                self.success_rate,

            "error_rate":
                self.error_rate,

            "average_latency":
                self.average_response_time,

            "minimum_latency":
                self.minimum_latency,

            "maximum_latency":
                self.maximum_latency,

            "bytes_sent":
                self.bytes_sent,

            "history_size":
                len(self._request_history),

        }
    # ==========================================================
    # Part 3.5
    # WebSocket Runtime
    #
    # websocket_connected()
    # websocket_disconnected()
    # websocket_message()
    # broadcast statistics
    # ==========================================================

    # ----------------------------------------------------------
    # WebSocket Connected
    # ----------------------------------------------------------

    def websocket_connected(
        self,
        client_id: str | None = None,
        *,
        metadata: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Register a new websocket connection.

        Returns
        -------
        dict
            Connection information.
        """

        now = self._now()

        if client_id is None:

            client_id = str(uuid.uuid4())

        info = {

            "id": client_id,

            "connected_at": now,

            "last_activity": now,

            "messages": 0,

            "bytes_sent": 0,

            "bytes_received": 0,

            "metadata": dict(metadata or {}),

        }

        self._websocket_clients[client_id] = info

        self.websocket_connections = len(
            self._websocket_clients
        )

        self._websocket_connect_count += 1

        self.last_activity = now

        self.touch()

        return info

    # ----------------------------------------------------------
    # WebSocket Disconnected
    # ----------------------------------------------------------

    def websocket_disconnected(
        self,
        client_id: str,
    ) -> bool:
        """
        Remove websocket connection.
        """

        if client_id not in self._websocket_clients:

            return False

        del self._websocket_clients[client_id]

        self.websocket_connections = len(
            self._websocket_clients
        )

        self._websocket_disconnect_count += 1

        self.last_activity = self._now()

        self.touch()

        return True

    # ----------------------------------------------------------
    # WebSocket Message
    # ----------------------------------------------------------

    def websocket_message(
        self,
        client_id: str,
        *,
        size: int = 0,
        outgoing: bool = False,
    ) -> None:
        """
        Register websocket traffic.
        """

        self.websocket_messages += 1

        size = max(0, int(size))

        client = self._websocket_clients.get(
            client_id
        )

        if client is not None:

            client["messages"] += 1

            client["last_activity"] = self._now()

            if outgoing:

                client["bytes_sent"] += size

                self.websocket_bytes_sent += size

            else:

                client["bytes_received"] += size

                self.websocket_bytes_received += size

        self.last_activity = self._now()

        self.touch()

    # ----------------------------------------------------------
    # Broadcast
    # ----------------------------------------------------------

    def websocket_broadcast(
        self,
        payload: Any,
        *,
        size: int | None = None,
    ) -> int:
        """
        Register a broadcast operation.

        This method records statistics only.
        Actual network transmission is handled
        by the WebSocket backend.
        """

        if size is None:

            try:

                size = len(str(payload).encode("utf-8"))

            except Exception:

                size = 0

        receivers = len(
            self._websocket_clients
        )

        self._broadcast_count += 1

        self._broadcast_messages += receivers

        self.websocket_messages += receivers

        bytes_sent = receivers * size

        self.websocket_bytes_sent += bytes_sent

        for client in self._websocket_clients.values():

            client["messages"] += 1

            client["bytes_sent"] += size

            client["last_activity"] = self._now()

        self.last_activity = self._now()

        self.touch()

        return receivers

    # ----------------------------------------------------------
    # WebSocket Properties
    # ----------------------------------------------------------

    @property
    def websocket_clients(
        self,
    ) -> dict[str, dict[str, Any]]:
        """
        Active websocket clients.
        """

        return dict(
            self._websocket_clients
        )

    @property
    def websocket_client_count(
        self,
    ) -> int:
        """
        Number of active clients.
        """

        return len(
            self._websocket_clients
        )

    @property
    def websocket_statistics(
        self,
    ) -> JSONDict:
        """
        WebSocket runtime statistics.
        """

        return {

            "connections": {

                "active":
                    self.websocket_client_count,

                "connected":
                    self._websocket_connect_count,

                "disconnected":
                    self._websocket_disconnect_count,

            },

            "traffic": {

                "messages":
                    self.websocket_messages,

                "bytes_sent":
                    self.websocket_bytes_sent,

                "bytes_received":
                    self.websocket_bytes_received,

            },

            "broadcast": {

                "operations":
                    self._broadcast_count,

                "delivered_messages":
                    self._broadcast_messages,

            },

        }

    # ----------------------------------------------------------
    # Helpers
    # ----------------------------------------------------------

    def clear_websocket_statistics(
        self,
    ) -> "DashboardWebServer":
        """
        Reset websocket statistics.
        """

        self._websocket_clients.clear()

        self.websocket_connections = 0

        self.websocket_messages = 0

        self.websocket_bytes_sent = 0

        self.websocket_bytes_received = 0

        self._websocket_connect_count = 0

        self._websocket_disconnect_count = 0

        self._broadcast_count = 0

        self._broadcast_messages = 0

        self.touch()

        return self

    def websocket_summary(
        self,
    ) -> JSONDict:
        """
        Lightweight websocket summary.
        """

        return {

            "clients":
                self.websocket_client_count,

            "messages":
                self.websocket_messages,

            "bytes_sent":
                self.websocket_bytes_sent,

            "bytes_received":
                self.websocket_bytes_received,

            "broadcasts":
                self._broadcast_count,

        }
    # ==========================================================
    # Part 3.6
    # Health & Diagnostics
    #
    # health()
    # runtime_snapshot()
    # diagnostics()
    # runtime_status()
    # ==========================================================

    # ----------------------------------------------------------
    # Health
    # ----------------------------------------------------------

    def health(self) -> JSONDict:
        """
        Return runtime health information.

        Overall health is determined from runtime state,
        lifecycle flags and recent errors.

        Returns
        -------
        JSONDict
        """

        healthy = (

            self.enabled

            and

            not self.closed

            and

            not self.is_error()

        )

        degraded = (

            healthy

            and

            self.error_count > 0

        )

        status = (

            "healthy"

            if healthy and not degraded

            else

            "degraded"

            if degraded

            else

            "unhealthy"

        )

        return {

            "status":
                status,

            "healthy":
                healthy,

            "running":
                self.running,

            "enabled":
                self.enabled,

            "frozen":
                self.frozen,

            "closed":
                self.closed,

            "state":
                self.state,

            "uptime":
                self.uptime,

            "last_activity":
                self.last_activity,

            "last_error":
                self.last_error,

            "request_count":
                self.request_count,

            "error_count":
                self.error_count,

            "active_requests":
                self.active_requests,

            "websocket_clients":
                self.websocket_client_count,

            "timestamp":
                self._now(),

        }

    # ----------------------------------------------------------
    # Runtime Snapshot
    # ----------------------------------------------------------

    def runtime_snapshot(self) -> JSONDict:
        """
        Export lightweight runtime snapshot.

        Suitable for persistence or debugging.
        """

        return {

            # ----------------------------------
            # Identity
            # ----------------------------------

            "id":
                self.id,

            "name":
                self.name,

            "version":
                self.version,

            # ----------------------------------
            # Runtime
            # ----------------------------------

            "state":
                self.state,

            "previous_state":
                self.previous_state,

            "running":
                self.running,

            "enabled":
                self.enabled,

            "frozen":
                self.frozen,

            "closed":
                self.closed,

            # ----------------------------------
            # Time
            # ----------------------------------

            "started_at":
                self.started_at,

            "stopped_at":
                self.stopped_at,

            "last_activity":
                self.last_activity,

            "uptime":
                self.uptime,

            # ----------------------------------
            # Statistics
            # ----------------------------------

            "requests":
                self.request_count,

            "success":
                self.success_count,

            "errors":
                self.error_count,

            "pending":
                self.pending_requests,

            "average_latency":
                self.average_response_time,

            # ----------------------------------
            # WebSocket
            # ----------------------------------

            "websocket_clients":
                self.websocket_client_count,

            "websocket_messages":
                self.websocket_messages,

            # ----------------------------------
            # Metadata
            # ----------------------------------

            "revision":
                self.revision,

            "updated_at":
                self.updated_at,

        }

    # ----------------------------------------------------------
    # Diagnostics
    # ----------------------------------------------------------

    def diagnostics(self) -> JSONDict:
        """
        Complete runtime diagnostics.

        Returns a full diagnostic report suitable for
        dashboards, monitoring and debugging.
        """

        return {

            "identity":

                self.identity,

            "configuration":

                self.configuration_state,

            "runtime":

                self.runtime_state,

            "health":

                self.health(),

            "statistics":

                self.statistics,

            "requests":

                self.request_statistics(),

            "websocket":

                self.websocket_statistics,

            "transitions":

                {

                    "current":
                        self.state,

                    "previous":
                        self.previous_state,

                    "available":
                        list(
                            self.available_transitions
                        ),

                },

            "metadata":

                {

                    "created_at":
                        self.created_at,

                    "updated_at":
                        self.updated_at,

                    "revision":
                        self.revision,

                },

        }

    # ----------------------------------------------------------
    # Runtime Status
    # ----------------------------------------------------------

    def runtime_status(self) -> JSONDict:
        """
        Lightweight runtime status.

        Intended for health endpoints
        and monitoring systems.
        """

        return {

            "server":

                self.name,

            "version":

                self.version,

            "state":

                self.state,

            "running":

                self.running,

            "healthy":

                self.health()["healthy"],

            "uptime":

                self.uptime,

            "requests":

                self.request_count,

            "errors":

                self.error_count,

            "clients":

                self.websocket_client_count,

            "latency":

                self.average_response_time,

        }

    # ----------------------------------------------------------
    # Convenience Properties
    # ----------------------------------------------------------

    @property
    def is_healthy(self) -> bool:
        """
        Runtime health flag.
        """

        return self.health()["healthy"]

    @property
    def is_degraded(self) -> bool:
        """
        Runtime degradation flag.
        """

        return (

            self.is_healthy

            and

            self.error_count > 0

        )

    @property
    def diagnostic_summary(self) -> JSONDict:
        """
        Minimal diagnostic summary.
        """

        return {

            "state":
                self.state,

            "health":
                self.health()["status"],

            "uptime":
                self.uptime,

            "requests":
                self.request_count,

            "errors":
                self.error_count,

            "websocket":
                self.websocket_client_count,

        }
    # ==========================================================
    # Part 4.1
    # FastAPI Initialization
    #
    # create_app()
    # create_router()
    # mount_router()
    # app
    # router
    # ==========================================================

    # ----------------------------------------------------------
    # FastAPI Application
    # ----------------------------------------------------------

    @property
    def app(self) -> FastAPI | None:
        """
        Return FastAPI application instance.
        """

        return self._app

    @property
    def router(self) -> APIRouter | None:
        """
        Return APIRouter instance.
        """

        return self._router

    @property
    def has_app(self) -> bool:
        """
        Whether FastAPI application exists.
        """

        return self._app is not None

    @property
    def has_router(self) -> bool:
        """
        Whether APIRouter exists.
        """

        return self._router is not None

    # ----------------------------------------------------------
    # FastAPI Factory
    # ----------------------------------------------------------

    def create_app(
        self,
        *,
        title: str | None = None,
        version: str | None = None,
        description: str | None = None,
        docs_url: str | None = "/docs",
        redoc_url: str | None = "/redoc",
        openapi_url: str | None = "/openapi.json",
        **kwargs: Any,
    ) -> FastAPI:
        """
        Create FastAPI application.
        """

        if FastAPI is None:

            raise RuntimeError(

                "FastAPI is not installed."

            )

        if self._app is not None:

            return self._app

        self._app = FastAPI(

            title=title or self.name,

            version=version or self.version,

            description=description or self.description,

            docs_url=docs_url,

            redoc_url=redoc_url,

            openapi_url=openapi_url,

            **kwargs,

        )

        self.touch()

        return self._app

    # ----------------------------------------------------------
    # Router Factory
    # ----------------------------------------------------------

    def create_router(
        self,
        *,
        prefix: str | None = None,
        tags: list[str] | None = None,
    ) -> APIRouter:
        """
        Create APIRouter.
        """

        if APIRouter is None:

            raise RuntimeError(

                "FastAPI is not installed."

            )

        if self._router is not None:

            return self._router

        self._router = APIRouter(

            prefix=prefix or self.api_prefix,

            tags=tags or ["Dashboard"],

        )

        self.touch()

        return self._router

    # ----------------------------------------------------------
    # Router Mount
    # ----------------------------------------------------------

    def mount_router(
        self,
        *,
        app: FastAPI | None = None,
        router: APIRouter | None = None,
    ) -> "DashboardWebServer":
        """
        Mount router into FastAPI application.
        """

        if app is None:

            app = self._app

        if router is None:

            router = self._router

        if app is None:

            app = self.create_app()

        if router is None:

            router = self.create_router()

        app.include_router(router)

        self._routes_mounted = True

        self.touch()

        return self

    # ----------------------------------------------------------
    # Bootstrap
    # ----------------------------------------------------------

    def initialize_fastapi(
        self,
    ) -> FastAPI:
        """
        Create application, router and mount them.
        """

        self.create_app()

        self.create_router()

        self.mount_router()

        return self._app

    # ----------------------------------------------------------
    # Utilities
    # ----------------------------------------------------------

    @property
    def routes_mounted(self) -> bool:
        """
        Whether router has been mounted.
        """

        return self._routes_mounted

    def ensure_app(self) -> FastAPI:
        """
        Ensure application exists.
        """

        if self._app is None:

            self.create_app()

        return self._app

    def ensure_router(self) -> APIRouter:
        """
        Ensure router exists.
        """

        if self._router is None:

            self.create_router()

        return self._router

    # ----------------------------------------------------------
    # FastAPI Information
    # ----------------------------------------------------------

    def fastapi_info(
        self,
    ) -> JSONDict:
        """
        Return FastAPI runtime information.
        """

        return {

            "enabled":
                FastAPI is not None,

            "has_app":
                self.has_app,

            "has_router":
                self.has_router,

            "mounted":
                self.routes_mounted,

            "api_prefix":
                self.api_prefix,

            "docs":

                (

                    None

                    if self._app is None

                    else self._app.docs_url

                ),

            "openapi":

                (

                    None

                    if self._app is None

                    else self._app.openapi_url

                ),

        }
    # ==========================================================
    # Part 4.2
    # Route Registration
    #
    # register_routes()
    # register_route()
    # unregister_route()
    # list_routes()
    # ==========================================================

    # ----------------------------------------------------------
    # Internal Route Registry
    # ----------------------------------------------------------

    @property
    def registered_routes(self) -> dict[str, dict[str, Any]]:
        """
        Registered API routes.
        """

        return self._registered_routes

    @property
    def route_count(self) -> int:
        """
        Number of registered routes.
        """

        return len(self._registered_routes)

    # ----------------------------------------------------------
    # Register Route
    # ----------------------------------------------------------

    def register_route(
        self,
        path: str,
        endpoint: Callable[..., Any],
        *,
        methods: Sequence[str] = ("GET",),
        name: str | None = None,
        tags: Sequence[str] | None = None,
        summary: str | None = None,
        description: str | None = None,
        include_in_schema: bool = True,
        response_model: Any = None,
    ) -> "DashboardWebServer":
        """
        Register a single REST endpoint.
        """

        router = self.ensure_router()

        methods = tuple(

            str(m).upper()

            for m in methods

        )

        route_name = name or endpoint.__name__

        router.add_api_route(

            path=path,

            endpoint=endpoint,

            methods=list(methods),

            name=route_name,

            tags=list(tags or ["Dashboard"]),

            summary=summary,

            description=description,

            include_in_schema=include_in_schema,

            response_model=response_model,

        )

        self._registered_routes[path] = {

            "path":
                path,

            "name":
                route_name,

            "endpoint":
                endpoint,

            "methods":
                methods,

            "tags":
                list(tags or ["Dashboard"]),

            "summary":
                summary,

            "description":
                description,

            "registered_at":
                self._now(),

        }

        self.touch()

        return self

    # ----------------------------------------------------------
    # Register Built-in Routes
    # ----------------------------------------------------------

    def register_routes(
        self,
    ) -> "DashboardWebServer":
        """
        Register all built-in REST endpoints.

        Safe to call multiple times.
        """

        if getattr(

            self,

            "_builtin_routes_registered",

            False,

        ):

            return self

        # --------------------------------------
        # Root
        # --------------------------------------

        self.register_route(

            "/",

            self._root_endpoint,

            methods=("GET",),

            name="root",

            summary="Dashboard root",

        )

        # --------------------------------------
        # Runtime
        # --------------------------------------

        self.register_route(

            "/status",

            self._status_endpoint,

            methods=("GET",),

            name="status",

        )

        self.register_route(

            "/health",

            self._health_endpoint,

            methods=("GET",),

            name="health",

        )

        self.register_route(

            "/diagnostics",

            self._diagnostics_endpoint,

            methods=("GET",),

            name="diagnostics",

        )

        self.register_route(

            "/snapshot",

            self._snapshot_endpoint,

            methods=("GET",),

            name="snapshot",

        )

        self.register_route(

            "/config",

            self._config_endpoint,

            methods=("GET",),

            name="config",

        )

        self._builtin_routes_registered = True

        self.touch()

        return self

    # ----------------------------------------------------------
    # Unregister Route
    # ----------------------------------------------------------

    def unregister_route(
        self,
        path: str,
    ) -> bool:
        """
        Remove a registered route.

        Notes
        -----
        FastAPI does not officially support
        runtime removal of routes.

        This method removes the route from both
        the router and the internal registry.
        """

        router = self.ensure_router()

        removed = False

        router.routes[:] = [

            route

            for route in router.routes

            if getattr(route, "path", None) != path

        ]

        if path in self._registered_routes:

            del self._registered_routes[path]

            removed = True

        if removed:

            self.touch()

        return removed

    # ----------------------------------------------------------
    # Route Listing
    # ----------------------------------------------------------

    def list_routes(
        self,
    ) -> list[JSONDict]:
        """
        Return all registered routes.
        """

        routes: list[JSONDict] = []

        for info in self._registered_routes.values():

            routes.append({

                "path":
                    info["path"],

                "name":
                    info["name"],

                "methods":
                    list(info["methods"]),

                "tags":
                    list(info["tags"]),

                "summary":
                    info["summary"],

            })

        routes.sort(

            key=lambda item: item["path"]

        )

        return routes

    # ----------------------------------------------------------
    # Lookup Helpers
    # ----------------------------------------------------------

    def has_route(
        self,
        path: str,
    ) -> bool:
        """
        Whether a route is registered.
        """

        return path in self._registered_routes

    def get_route(
        self,
        path: str,
    ) -> JSONDict | None:
        """
        Return route metadata.
        """

        return self._registered_routes.get(path)

    def clear_routes(
        self,
    ) -> "DashboardWebServer":
        """
        Remove all registered routes.
        """

        router = self.ensure_router()

        router.routes.clear()

        self._registered_routes.clear()

        self._builtin_routes_registered = False

        self.touch()

        return self

    # ----------------------------------------------------------
    # Route Statistics
    # ----------------------------------------------------------

    def route_statistics(
        self,
    ) -> JSONDict:
        """
        Route registration statistics.
        """

        return {

            "registered":
                self.route_count,

            "builtin_registered":
                self._builtin_routes_registered,

            "mounted":
                self.routes_mounted,

            "paths":

                sorted(

                    self._registered_routes.keys()

                ),

        }
    # ==========================================================
    # Part 4.3
    # REST Endpoints
    #
    # /
    # /status
    # /health
    # /diagnostics
    # /snapshot
    # /config
    # ==========================================================

    # ----------------------------------------------------------
    # GET /
    # ----------------------------------------------------------

    async def _root_endpoint(
        self,
    ) -> JSONDict:
        """
        Root endpoint.

        GET /
        """

        self.request_started(
            method="GET",
            path="/",
        )

        try:

            payload = {

                "service": self.name,

                "version": self.version,

                "description": self.description,

                "server_type": self.server_type,

                "state": self.state,

                "healthy": self.is_healthy,

                "viewer": (

                    self.viewer is not None

                ),

                "api": {

                    "status": "/status",

                    "health": "/health",

                    "diagnostics": "/diagnostics",

                    "snapshot": "/snapshot",

                    "config": "/config",

                    "metrics": "/metrics",

                },

            }

            self.request_completed(0.0)

            return payload

        except Exception as exc:

            self.request_failed(exc)

            raise

    # ----------------------------------------------------------
    # GET /status
    # ----------------------------------------------------------

    async def _status_endpoint(
        self,
    ) -> JSONDict:
        """
        Runtime status.

        GET /status
        """

        self.request_started(

            method="GET",

            path="/status",

        )

        try:

            result = self.runtime_status()

            self.request_completed(0.0)

            return result

        except Exception as exc:

            self.request_failed(exc)

            raise

    # ----------------------------------------------------------
    # GET /health
    # ----------------------------------------------------------

    async def _health_endpoint(
        self,
    ) -> JSONDict:
        """
        Runtime health.

        GET /health
        """

        self.request_started(

            method="GET",

            path="/health",

        )

        try:

            result = self.health()

            self.request_completed(0.0)

            return result

        except Exception as exc:

            self.request_failed(exc)

            raise

    # ----------------------------------------------------------
    # GET /diagnostics
    # ----------------------------------------------------------

    async def _diagnostics_endpoint(
        self,
    ) -> JSONDict:
        """
        Runtime diagnostics.

        GET /diagnostics
        """

        self.request_started(

            method="GET",

            path="/diagnostics",

        )

        try:

            result = self.diagnostics()

            self.request_completed(0.0)

            return result

        except Exception as exc:

            self.request_failed(exc)

            raise

    # ----------------------------------------------------------
    # GET /snapshot
    # ----------------------------------------------------------

    async def _snapshot_endpoint(
        self,
    ) -> JSONDict:
        """
        Runtime snapshot.

        GET /snapshot
        """

        self.request_started(

            method="GET",

            path="/snapshot",

        )

        try:

            result = self.runtime_snapshot()

            self.request_completed(0.0)

            return result

        except Exception as exc:

            self.request_failed(exc)

            raise

    # ----------------------------------------------------------
    # GET /config
    # ----------------------------------------------------------

    async def _config_endpoint(
        self,
    ) -> JSONDict:
        """
        Runtime configuration.

        GET /config
        """

        self.request_started(

            method="GET",

            path="/config",

        )

        try:

            result = self.configuration_state

            self.request_completed(0.0)

            return result

        except Exception as exc:

            self.request_failed(exc)

            raise

    # ----------------------------------------------------------
    # Endpoint Registration Helper
    # ----------------------------------------------------------

    def register_default_endpoints(
        self,
    ) -> "DashboardWebServer":
        """
        Register the default REST API.
        """

        self.register_routes()

        return self
    # ==========================================================
    # Part 4.4
    # Metrics Endpoints
    #
    # GET /metrics
    # GET /statistics
    # GET /runtime
    # ==========================================================

    # ----------------------------------------------------------
    # GET /metrics
    # ----------------------------------------------------------

    async def _metrics_endpoint(
        self,
    ) -> JSONDict:
        """
        Runtime metrics.

        GET /metrics
        """

        self.request_started(
            method="GET",
            path="/metrics",
        )

        try:

            metrics = {

                # ----------------------------------
                # Requests
                # ----------------------------------

                "requests": {

                    "total":
                        self.request_count,

                    "success":
                        self.success_count,

                    "failed":
                        self.error_count,

                    "active":
                        self.active_requests,

                    "pending":
                        self.pending_requests,

                },

                # ----------------------------------
                # Latency
                # ----------------------------------

                "latency": {

                    "average":
                        self.average_response_time,

                    "minimum":
                        self.minimum_latency,

                    "maximum":
                        self.maximum_latency,

                },

                # ----------------------------------
                # WebSocket
                # ----------------------------------

                "websocket":

                    self.websocket_statistics,

                # ----------------------------------
                # Throughput
                # ----------------------------------

                "throughput": {

                    "requests_per_second":
                        self.requests_per_second,

                    "bytes_sent":
                        self.bytes_sent,

                    "websocket_bytes_sent":
                        self.websocket_bytes_sent,

                    "websocket_bytes_received":
                        self.websocket_bytes_received,

                },

                # ----------------------------------
                # Runtime
                # ----------------------------------

                "runtime": {

                    "uptime":
                        self.uptime,

                    "revision":
                        self.revision,

                    "state":
                        self.state,

                },

            }

            self.request_completed(0.0)

            return metrics

        except Exception as exc:

            self.request_failed(exc)

            raise

    # ----------------------------------------------------------
    # GET /statistics
    # ----------------------------------------------------------

    async def _statistics_endpoint(
        self,
    ) -> JSONDict:
        """
        Runtime statistics.

        GET /statistics
        """

        self.request_started(

            method="GET",

            path="/statistics",

        )

        try:

            payload = {

                "runtime":

                    self.statistics,

                "requests":

                    self.request_statistics(),

                "websocket":

                    self.websocket_statistics,

                "health":

                    self.health(),

            }

            self.request_completed(0.0)

            return payload

        except Exception as exc:

            self.request_failed(exc)

            raise

    # ----------------------------------------------------------
    # GET /runtime
    # ----------------------------------------------------------

    async def _runtime_endpoint(
        self,
    ) -> JSONDict:
        """
        Runtime overview.

        GET /runtime
        """

        self.request_started(

            method="GET",

            path="/runtime",

        )

        try:

            payload = {

                "identity":

                    self.identity,

                "runtime":

                    self.runtime_state,

                "configuration":

                    self.configuration_state,

                "snapshot":

                    self.runtime_snapshot(),

                "health":

                    self.health(),

            }

            self.request_completed(0.0)

            return payload

        except Exception as exc:

            self.request_failed(exc)

            raise

    # ----------------------------------------------------------
    # Metrics Registration
    # ----------------------------------------------------------

    def register_metric_routes(
        self,
    ) -> "DashboardWebServer":
        """
        Register metrics-related endpoints.
        """

        self.register_route(

            "/metrics",

            self._metrics_endpoint,

            methods=("GET",),

            name="metrics",

            summary="Runtime metrics",

            tags=["Metrics"],

        )

        self.register_route(

            "/statistics",

            self._statistics_endpoint,

            methods=("GET",),

            name="statistics",

            summary="Runtime statistics",

            tags=["Metrics"],

        )

        self.register_route(

            "/runtime",

            self._runtime_endpoint,

            methods=("GET",),

            name="runtime",

            summary="Runtime overview",

            tags=["Runtime"],

        )

        return self
    # ==========================================================
    # Part 4.5
    # Viewer Endpoints
    #
    # GET  /viewer
    # GET  /viewer/render
    # GET  /viewer/state
    # GET  /viewer/export
    # ==========================================================

    # ----------------------------------------------------------
    # GET /viewer
    # ----------------------------------------------------------

    async def _viewer_endpoint(
        self,
    ) -> JSONDict:
        """
        Dashboard viewer information.

        GET /viewer
        """

        self.request_started(
            method="GET",
            path="/viewer",
        )

        try:

            if self.viewer is None:

                raise HTTPException(
                    status_code=404,
                    detail="DashboardViewer is not attached.",
                )

            payload = {

                "available": True,

                "viewer": {

                    "id":
                        getattr(
                            self.viewer,
                            "id",
                            None,
                        ),

                    "name":
                        getattr(
                            self.viewer,
                            "name",
                            None,
                        ),

                    "version":
                        getattr(
                            self.viewer,
                            "version",
                            None,
                        ),

                    "type":
                        self.viewer.__class__.__name__,

                },

                "server": {

                    "state":
                        self.state,

                    "running":
                        self.running,

                },

            }

            self.request_completed(0.0)

            return payload

        except Exception as exc:

            self.request_failed(exc)

            raise

    # ----------------------------------------------------------
    # GET /viewer/render
    # ----------------------------------------------------------

    async def _viewer_render_endpoint(
        self,
    ) -> Any:
        """
        Render dashboard.

        GET /viewer/render
        """

        self.request_started(
            method="GET",
            path="/viewer/render",
        )

        try:

            if self.viewer is None:

                raise HTTPException(
                    status_code=404,
                    detail="DashboardViewer is not attached.",
                )

            #
            # Preferred render API
            #

            if hasattr(
                self.viewer,
                "render",
            ):

                result = self.viewer.render()

            elif hasattr(
                self.viewer,
                "render_dict",
            ):

                result = self.viewer.render_dict()

            elif hasattr(
                self.viewer,
                "to_dict",
            ):

                result = self.viewer.to_dict()

            else:

                result = {

                    "viewer":

                        str(self.viewer)

                }

            self.request_completed(0.0)

            return result

        except Exception as exc:

            self.request_failed(exc)

            raise

    # ----------------------------------------------------------
    # GET /viewer/state
    # ----------------------------------------------------------

    async def _viewer_state_endpoint(
        self,
    ) -> JSONDict:
        """
        Viewer runtime state.

        GET /viewer/state
        """

        self.request_started(
            method="GET",
            path="/viewer/state",
        )

        try:

            if self.viewer is None:

                raise HTTPException(
                    status_code=404,
                    detail="DashboardViewer is not attached.",
                )

            payload = {

                "enabled":

                    getattr(
                        self.viewer,
                        "enabled",
                        None,
                    ),

                "running":

                    getattr(
                        self.viewer,
                        "running",
                        None,
                    ),

                "closed":

                    getattr(
                        self.viewer,
                        "closed",
                        None,
                    ),

                "frozen":

                    getattr(
                        self.viewer,
                        "frozen",
                        None,
                    ),

                "state":

                    getattr(
                        self.viewer,
                        "state",
                        None,
                    ),

                "updated_at":

                    getattr(
                        self.viewer,
                        "updated_at",
                        None,
                    ),

            }

            self.request_completed(0.0)

            return payload

        except Exception as exc:

            self.request_failed(exc)

            raise

    # ----------------------------------------------------------
    # GET /viewer/export
    # ----------------------------------------------------------

    async def _viewer_export_endpoint(
        self,
    ) -> JSONDict:
        """
        Export viewer.

        GET /viewer/export
        """

        self.request_started(
            method="GET",
            path="/viewer/export",
        )

        try:

            if self.viewer is None:

                raise HTTPException(
                    status_code=404,
                    detail="DashboardViewer is not attached.",
                )

            #
            # Preferred export API
            #

            if hasattr(
                self.viewer,
                "export",
            ):

                exported = self.viewer.export()

            elif hasattr(
                self.viewer,
                "to_dict",
            ):

                exported = self.viewer.to_dict()

            else:

                exported = {

                    "viewer":

                        str(self.viewer)

                }

            payload = {

                "viewer":

                    exported,

                "exported_at":

                    self._now(),

                "server_revision":

                    self.revision,

            }

            self.request_completed(0.0)

            return payload

        except Exception as exc:

            self.request_failed(exc)

            raise

    # ----------------------------------------------------------
    # Viewer Route Registration
    # ----------------------------------------------------------

    def register_viewer_routes(
        self,
    ) -> "DashboardWebServer":
        """
        Register DashboardViewer REST endpoints.
        """

        self.register_route(

            "/viewer",

            self._viewer_endpoint,

            methods=("GET",),

            name="viewer",

            summary="Dashboard Viewer",

            tags=["Viewer"],

        )

        self.register_route(

            "/viewer/render",

            self._viewer_render_endpoint,

            methods=("GET",),

            name="viewer-render",

            summary="Render Dashboard",

            tags=["Viewer"],

        )

        self.register_route(

            "/viewer/state",

            self._viewer_state_endpoint,

            methods=("GET",),

            name="viewer-state",

            summary="Viewer Runtime State",

            tags=["Viewer"],

        )

        self.register_route(

            "/viewer/export",

            self._viewer_export_endpoint,

            methods=("GET",),

            name="viewer-export",

            summary="Export Dashboard",

            tags=["Viewer"],

        )

        return self
    # ==========================================================
    # Part 5.1.1A
    # WebSocket Endpoint & Accept
    #
    # websocket_endpoint()
    # accept connection
    # client registration
    # ==========================================================

    async def websocket_endpoint(
        self,
        websocket: Any,
    ) -> None:
        """
        Main WebSocket endpoint.

        Lifecycle
        ---------
            Accept
                ↓
            Register Client
                ↓
            Startup Hook
                ↓
            Message Loop
                ↓
            Disconnect
                ↓
            Cleanup

        Notes
        -----
        The message loop is implemented in Part 5.1.3.
        """

        #
        # Accept websocket connection
        #

        await websocket.accept()

        #
        # Register client
        #

        client = await self._accept_connection(
            websocket,
        )

        try:

            #
            # Startup hook
            #

            await self._websocket_startup(
                client,
            )

            #
            # Message loop
            #
            # Implemented in Part 5.1.3
            #

            await self._websocket_message_loop(
                client,
            )

        except Exception as exc:

            self.request_failed(exc)

            self.last_error = str(exc)

            raise

        finally:

            #
            # Cleanup
            #
            # Implemented in Part 5.1.1C
            #

            await self._disconnect_client(
                client,
            )

    # ----------------------------------------------------------
    # Accept Connection
    # ----------------------------------------------------------

    async def _accept_connection(
        self,
        websocket: Any,
    ) -> JSONDict:
        """
        Accept and register one websocket client.
        """

        #
        # Client identifier
        #

        client_id = str(
            uuid.uuid4()
        )

        #
        # Best effort client address
        #

        address = None

        try:

            client = websocket.client

            if client is not None:

                address = {

                    "host": getattr(
                        client,
                        "host",
                        None,
                    ),

                    "port": getattr(
                        client,
                        "port",
                        None,
                    ),

                }

        except Exception:

            address = None

        #
        # Client record
        #

        now = self._now()

        info = {

            "id":
                client_id,

            "websocket":
                websocket,

            "connected_at":
                now,

            "last_activity":
                now,

            "messages":
                0,

            "bytes_sent":
                0,

            "bytes_received":
                0,

            "subscriptions":
                set(),

            "address":
                address,

            "metadata":
                {},

        }

        #
        # Register runtime
        #

        self._websocket_clients[
            client_id
        ] = info

        self.websocket_connected(
            client_id,
        )

        self.touch()

        return info

    # ----------------------------------------------------------
    # Registration Helpers
    # ----------------------------------------------------------

    def register_websocket_client(
        self,
        client: JSONDict,
    ) -> JSONDict:
        """
        Register an externally created client.
        """

        client_id = client["id"]

        self._websocket_clients[
            client_id
        ] = client

        self.websocket_connections = len(
            self._websocket_clients
        )

        self.touch()

        return client

    def unregister_websocket_client(
        self,
        client_id: str,
    ) -> bool:
        """
        Remove websocket client.
        """

        if client_id not in self._websocket_clients:

            return False

        del self._websocket_clients[
            client_id
        ]

        self.websocket_connections = len(
            self._websocket_clients
        )

        self.touch()

        return True

    # ----------------------------------------------------------
    # Client Lookup
    # ----------------------------------------------------------

    def get_websocket_client(
        self,
        client_id: str,
    ) -> JSONDict | None:
        """
        Return client information.
        """

        return self._websocket_clients.get(
            client_id
        )

    @property
    def websocket_client_ids(
        self,
    ) -> list[str]:
        """
        Active websocket client ids.
        """

        return sorted(
            self._websocket_clients.keys()
        )

    @property
    def websocket_client_count(
        self,
    ) -> int:
        """
        Number of connected clients.
        """

        return len(
            self._websocket_clients
        )

    @property
    def websocket_clients(
        self,
    ) -> list[JSONDict]:
        """
        Connected clients.
        """

        return list(
            self._websocket_clients.values()
        )

    # ----------------------------------------------------------
    # Endpoint Information
    # ----------------------------------------------------------

    def websocket_endpoint_info(
        self,
    ) -> JSONDict:
        """
        WebSocket endpoint metadata.
        """

        return {

            "enabled":
                self.websocket_enabled,

            "path":
                self.websocket_path,

            "clients":
                self.websocket_client_count,

            "connections":
                self._websocket_connect_count,

            "messages":
                self.websocket_messages,

            "running":
                self.running,

        }
    # ==========================================================
    # Part 5.1.1B.1
    # WebSocket Startup
    #
    # _websocket_startup()
    # startup hooks
    # runtime checks
    # ==========================================================

    async def _websocket_startup(
        self,
        client: JSONDict,
    ) -> None:
        """
        Initialize a newly connected WebSocket client.

        Startup Pipeline
        ----------------
            1. Runtime validation
            2. Client validation
            3. Server capacity check
            4. Startup hooks
            5. Runtime initialization
            6. Session initialization

        Raises
        ------
        RuntimeError
            If server cannot accept new clients.
        """

        # --------------------------------------------------
        # Runtime Checks
        # --------------------------------------------------

        self._check_websocket_runtime()

        # --------------------------------------------------
        # Validate Client
        # --------------------------------------------------

        self._validate_websocket_client(
            client,
        )

        # --------------------------------------------------
        # Capacity
        # --------------------------------------------------

        self._check_websocket_capacity()

        # --------------------------------------------------
        # Startup Hooks
        # --------------------------------------------------

        await self._run_websocket_hooks(
            "before_startup",
            client,
        )

        # --------------------------------------------------
        # Initialize Runtime
        # --------------------------------------------------

        now = self._now()

        client["started_at"] = now

        client["last_activity"] = now

        client["state"] = "connected"

        client["authenticated"] = False

        client["session"] = None

        client["heartbeat"] = now

        client["closed"] = False

        # --------------------------------------------------
        # Statistics
        # --------------------------------------------------

        self.last_activity = now

        self.touch()

        # --------------------------------------------------
        # Startup Hooks
        # --------------------------------------------------

        await self._run_websocket_hooks(
            "after_startup",
            client,
        )

    # ==========================================================
    # Runtime Validation
    # ==========================================================

    def _check_websocket_runtime(
        self,
    ) -> None:
        """
        Validate runtime before accepting
        websocket traffic.
        """

        if not self.websocket_enabled:

            raise RuntimeError(
                "WebSocket support is disabled."
            )

        if self.closed:

            raise RuntimeError(
                "Server has been closed."
            )

        if self.frozen:

            raise RuntimeError(
                "Server is frozen."
            )

        if not self.enabled:

            raise RuntimeError(
                "Server is disabled."
            )

        if not self.running:

            raise RuntimeError(
                "Server is not running."
            )

    # ==========================================================
    # Client Validation
    # ==========================================================

    def _validate_websocket_client(
        self,
        client: JSONDict,
    ) -> None:
        """
        Validate client object.
        """

        if not isinstance(
            client,
            dict,
        ):
            raise TypeError(
                "Client must be a dictionary."
            )

        if "id" not in client:

            raise RuntimeError(
                "Client identifier missing."
            )

        if "websocket" not in client:

            raise RuntimeError(
                "WebSocket instance missing."
            )

    # ==========================================================
    # Capacity Check
    # ==========================================================

    def _check_websocket_capacity(
        self,
    ) -> None:
        """
        Verify server capacity.
        """

        limit = getattr(
            self,
            "max_websocket_clients",
            1000,
        )

        if self.websocket_client_count >= limit:

            raise RuntimeError(
                "Maximum websocket clients reached."
            )

    # ==========================================================
    # Hook Dispatcher
    # ==========================================================

    async def _run_websocket_hooks(
        self,
        hook: str,
        client: JSONDict,
    ) -> None:
        """
        Execute websocket startup hooks.

        Missing hooks are ignored.
        """

        callback = getattr(
            self,
            hook,
            None,
        )

        if callback is None:

            return

        if callable(callback):

            result = callback(client)

            #
            # Support async callbacks
            #

            if hasattr(
                result,
                "__await__",
            ):

                await result

    # ==========================================================
    # Startup Summary
    # ==========================================================

    def websocket_startup_state(
        self,
        client: JSONDict,
    ) -> JSONDict:
        """
        Return startup information.
        """

        return {

            "client":

                client["id"],

            "state":

                client.get(
                    "state",
                ),

            "started_at":

                client.get(
                    "started_at",
                ),

            "authenticated":

                client.get(
                    "authenticated",
                ),

            "running":

                self.running,

            "server_state":

                self.state,

        }
    # ==========================================================
    # Part 5.1.1B.2
    # Initial Handshake
    #
    # - protocol handshake
    # - capability negotiation
    # - session initialization
    # ==========================================================

    async def _websocket_handshake(
        self,
        client: JSONDict,
    ) -> JSONDict:
        """
        Perform the initial protocol handshake.

        Pipeline
        --------
            validate protocol
                    ↓
            negotiate capabilities
                    ↓
            initialize session
                    ↓
            execute hooks
                    ↓
            return handshake result
        """

        await self._run_websocket_hooks(
            "before_handshake",
            client,
        )

        protocol = self._negotiate_protocol(
            client,
        )

        capabilities = self._negotiate_capabilities(
            client,
        )

        session = self._initialize_websocket_session(
            client,
            protocol=protocol,
            capabilities=capabilities,
        )

        client["protocol"] = protocol

        client["capabilities"] = capabilities

        client["session"] = session

        client["state"] = "handshake-complete"

        client["handshake_completed_at"] = self._now()

        self.touch()

        await self._run_websocket_hooks(
            "after_handshake",
            client,
        )

        return {

            "protocol": protocol,

            "capabilities": capabilities,

            "session": session,

        }

    # ==========================================================
    # Protocol Negotiation
    # ==========================================================

    def _negotiate_protocol(
        self,
        client: JSONDict,
    ) -> str:
        """
        Select websocket protocol.

        Future versions may inspect:

            websocket.headers
            websocket.scope
            Sec-WebSocket-Protocol
        """

        websocket = client["websocket"]

        protocol = None

        #
        # Starlette/FastAPI stores negotiated
        # subprotocol here after accept().
        #

        protocol = getattr(
            websocket,
            "subprotocol",
            None,
        )

        if protocol:

            return protocol

        #
        # Default SciOS protocol
        #

        return "scios.dashboard.v1"

    # ==========================================================
    # Capability Negotiation
    # ==========================================================

    def _negotiate_capabilities(
        self,
        client: JSONDict,
    ) -> JSONDict:
        """
        Build negotiated capability set.

        Future:
            compression
            binary transport
            protobuf
            tracing
            streaming
            authentication
        """

        viewer_available = (

            self.viewer is not None

        )

        capabilities = {

            "json": True,

            "heartbeat": True,

            "events": True,

            "broadcast": True,

            "statistics": True,

            "diagnostics": True,

            "viewer": viewer_available,

            "streaming": True,

            "binary": False,

            "compression": False,

        }

        return capabilities

    # ==========================================================
    # Session Initialization
    # ==========================================================

    def _initialize_websocket_session(
        self,
        client: JSONDict,
        *,
        protocol: str,
        capabilities: JSONDict,
    ) -> JSONDict:
        """
        Initialize runtime session.

        One session exists per websocket client.
        """

        session = {

            "id":

                str(
                    uuid.uuid4()
                ),

            "client_id":

                client["id"],

            "protocol":

                protocol,

            "created_at":

                self._now(),

            "last_activity":

                self._now(),

            "authenticated":

                False,

            "subscriptions":

                set(),

            "metadata":

                {},

            "context":

                {},

            "capabilities":

                capabilities,

        }

        #
        # Runtime registry
        #

        if not hasattr(
            self,
            "_websocket_sessions",
        ):

            self._websocket_sessions = {}

        self._websocket_sessions[
            session["id"]
        ] = session

        return session

    # ==========================================================
    # Session Helpers
    # ==========================================================

    def websocket_session(
        self,
        client_id: str,
    ) -> JSONDict | None:
        """
        Return websocket session.
        """

        client = self.get_websocket_client(
            client_id,
        )

        if client is None:

            return None

        return client.get(
            "session",
        )

    @property
    def websocket_session_count(
        self,
    ) -> int:
        """
        Number of active sessions.
        """

        return len(

            getattr(
                self,
                "_websocket_sessions",
                {},
            )

        )

    def websocket_capabilities(
        self,
    ) -> JSONDict:
        """
        Server capability description.
        """

        return {

            "protocol":

                "scios.dashboard.v1",

            "viewer":

                self.viewer is not None,

            "streaming":

                True,

            "broadcast":

                True,

            "heartbeat":

                True,

            "diagnostics":

                True,

            "statistics":

                True,

        }
    # ==========================================================
    # Part 5.1.1B.3
    # Welcome Message
    #
    # • welcome payload
    # • server info
    # • viewer info
    # • runtime state
    # • send JSON
    # ==========================================================

    async def _send_welcome(
        self,
        client: JSONDict,
    ) -> JSONDict:
        """
        Send the initial welcome message.

        Pipeline
        --------
            build payload
                  ↓
            before_send hook
                  ↓
            websocket.send_json()
                  ↓
            update statistics
                  ↓
            after_send hook
        """

        websocket = client["websocket"]

        payload = self._build_welcome_payload(
            client,
        )

        await self._run_websocket_hooks(
            "before_welcome",
            client,
        )

        await websocket.send_json(
            payload
        )

        #
        # Statistics
        #

        encoded = json.dumps(
            payload,
            default=str,
        ).encode("utf-8")

        size = len(encoded)

        client["messages"] += 1

        client["bytes_sent"] += size

        client["last_activity"] = self._now()

        self.websocket_messages += 1

        self.websocket_bytes_sent += size

        self.last_activity = self._now()

        self.touch()

        await self._run_websocket_hooks(
            "after_welcome",
            client,
        )

        return payload

    # ==========================================================
    # Welcome Payload
    # ==========================================================

    def _build_welcome_payload(
        self,
        client: JSONDict,
    ) -> JSONDict:
        """
        Build welcome payload.

        Returned to every newly connected client.
        """

        session = client.get(
            "session",
            {},
        )

        payload = {

            # --------------------------------------
            # Envelope
            # --------------------------------------

            "type":

                "welcome",

            "timestamp":

                self._now(),

            # --------------------------------------
            # Protocol
            # --------------------------------------

            "protocol":

                client.get(
                    "protocol",
                    self.websocket_protocol,
                ),

            # --------------------------------------
            # Session
            # --------------------------------------

            "session": {

                "id":

                    session.get("id"),

                "client_id":

                    client["id"],

                "created_at":

                    session.get(
                        "created_at",
                    ),

            },

            # --------------------------------------
            # Server
            # --------------------------------------

            "server":

                self._server_information(),

            # --------------------------------------
            # Viewer
            # --------------------------------------

            "viewer":

                self._viewer_information(),

            # --------------------------------------
            # Runtime
            # --------------------------------------

            "runtime":

                self._runtime_information(),

            # --------------------------------------
            # Capabilities
            # --------------------------------------

            "capabilities":

                client.get(
                    "capabilities",
                    {},
                ),

        }

        return payload

    # ==========================================================
    # Server Information
    # ==========================================================

    def _server_information(
        self,
    ) -> JSONDict:
        """
        Server identity.
        """

        return {

            "id":
                self.id,

            "name":
                self.name,

            "version":
                self.version,

            "description":
                self.description,

            "server_type":
                self.server_type,

            "revision":
                self.revision,

            "created_at":
                self.created_at,

        }

    # ==========================================================
    # Viewer Information
    # ==========================================================

    def _viewer_information(
        self,
    ) -> JSONDict:
        """
        Viewer description.
        """

        if self.viewer is None:

            return {

                "available": False,

            }

        return {

            "available": True,

            "class":

                self.viewer.__class__.__name__,

            "id":

                getattr(
                    self.viewer,
                    "id",
                    None,
                ),

            "name":

                getattr(
                    self.viewer,
                    "name",
                    None,
                ),

            "version":

                getattr(
                    self.viewer,
                    "version",
                    None,
                ),

            "state":

                getattr(
                    self.viewer,
                    "state",
                    None,
                ),

        }

    # ==========================================================
    # Runtime Information
    # ==========================================================

    def _runtime_information(
        self,
    ) -> JSONDict:
        """
        Lightweight runtime state.
        """

        return {

            "state":
                self.state,

            "running":
                self.running,

            "enabled":
                self.enabled,

            "frozen":
                self.frozen,

            "closed":
                self.closed,

            "uptime":
                self.uptime,

            "request_count":
                self.request_count,

            "websocket_clients":
                self.websocket_client_count,

            "health":

                self.health(),

        }

    # ==========================================================
    # Convenience API
    # ==========================================================

    async def send_welcome(
        self,
        client_id: str,
    ) -> JSONDict:
        """
        Send welcome packet to one client.
        """

        client = self.get_websocket_client(
            client_id,
        )

        if client is None:

            raise RuntimeError(
                f"Unknown websocket client: {client_id}"
            )

        return await self._send_welcome(
            client,
        )
    # ==========================================================
    # Part 5.1.1C.1
    # Disconnect Handling
    #
    # • _disconnect_client()
    # • graceful disconnect
    # • websocket close
    # • close code / reason
    # ==========================================================

    async def _disconnect_client(
        self,
        client: JSONDict,
        *,
        code: int = 1000,
        reason: str = "Normal Closure",
    ) -> None:
        """
        Gracefully disconnect a websocket client.

        Pipeline
        --------
            before_disconnect hook
                    ↓
            send closing frame
                    ↓
            websocket.close()
                    ↓
            update client state
                    ↓
            after_disconnect hook

        Notes
        -----
        Cleanup of runtime/session resources is implemented
        in Part 5.1.1C.2.
        """

        if not client:

            return

        websocket = client.get("websocket")

        #
        # Already closed
        #

        if client.get("closed", False):

            return

        await self._run_websocket_hooks(
            "before_disconnect",
            client,
        )

        #
        # Close websocket
        #

        if websocket is not None:

            try:

                await websocket.close(

                    code=code,

                    reason=reason,

                )

            #
            # Ignore transport errors during shutdown
            #

            except Exception:

                pass

        #
        # Runtime state
        #

        now = self._now()

        client["closed"] = True

        client["state"] = "disconnected"

        client["disconnect_code"] = code

        client["disconnect_reason"] = reason

        client["disconnected_at"] = now

        client["last_activity"] = now

        #
        # Runtime statistics
        #

        self.last_activity = now

        self.touch()

        await self._run_websocket_hooks(
            "after_disconnect",
            client,
        )

        #
        # Continue with cleanup
        #
        # Implemented in Part 5.1.1C.2
        #

        await self._cleanup_client(
            client,
        )

    # ==========================================================
    # Public Disconnect API
    # ==========================================================

    async def disconnect(
        self,
        client_id: str,
        *,
        code: int = 1000,
        reason: str = "Normal Closure",
    ) -> bool:
        """
        Disconnect one client.
        """

        client = self.get_websocket_client(
            client_id,
        )

        if client is None:

            return False

        await self._disconnect_client(

            client,

            code=code,

            reason=reason,

        )

        return True

    async def disconnect_all(
        self,
        *,
        code: int = 1001,
        reason: str = "Server Shutdown",
    ) -> int:
        """
        Disconnect all websocket clients.
        """

        clients = list(
            self._websocket_clients.values()
        )

        count = 0

        for client in clients:

            try:

                await self._disconnect_client(

                    client,

                    code=code,

                    reason=reason,

                )

                count += 1

            except Exception:

                #
                # Continue disconnecting remaining clients.
                #

                continue

        return count

    # ==========================================================
    # Close Helpers
    # ==========================================================

    @staticmethod
    def websocket_close_reason(
        code: int,
    ) -> str:
        """
        RFC 6455 close-code descriptions.
        """

        reasons = {

            1000: "Normal Closure",

            1001: "Going Away",

            1002: "Protocol Error",

            1003: "Unsupported Data",

            1005: "No Status",

            1006: "Abnormal Closure",

            1007: "Invalid Payload",

            1008: "Policy Violation",

            1009: "Message Too Large",

            1010: "Mandatory Extension",

            1011: "Internal Error",

            1012: "Service Restart",

            1013: "Try Again Later",

            1015: "TLS Handshake Failure",

        }

        return reasons.get(

            code,

            "Unknown",

        )

    def disconnect_statistics(
        self,
    ) -> JSONDict:
        """
        Disconnect statistics.
        """

        return {

            "active_clients":

                self.websocket_client_count,

            "disconnects":

                self._websocket_disconnect_count,

            "messages":

                self.websocket_messages,

            "bytes_sent":

                self.websocket_bytes_sent,

            "bytes_received":

                self.websocket_bytes_received,

        }
    # ==========================================================
    # Part 5.1.1C.2
    # Cleanup
    #
    # • cleanup session
    # • unsubscribe topics
    # • remove resources
    # • lifecycle hooks
    # ==========================================================

    async def _cleanup_client(
        self,
        client: JSONDict,
    ) -> None:
        """
        Cleanup websocket client resources.

        Cleanup Pipeline
        ----------------
            before_cleanup
                    ↓
            cleanup session
                    ↓
            unsubscribe topics
                    ↓
            release runtime resources
                    ↓
            unregister client
                    ↓
            after_cleanup
        """

        if not client:

            return

        await self._run_websocket_hooks(
            "before_cleanup",
            client,
        )

        #
        # Cleanup session
        #

        self._cleanup_session(
            client,
        )

        #
        # Remove subscriptions
        #

        self._cleanup_subscriptions(
            client,
        )

        #
        # Release runtime resources
        #

        self._cleanup_resources(
            client,
        )

        #
        # Remove from runtime registry
        #

        self.unregister_websocket_client(
            client["id"],
        )

        #
        # Update runtime statistics
        #

        self.websocket_disconnected(
            client["id"],
        )

        self.last_activity = self._now()

        self.touch()

        await self._run_websocket_hooks(
            "after_cleanup",
            client,
        )

    # ==========================================================
    # Session Cleanup
    # ==========================================================

    def _cleanup_session(
        self,
        client: JSONDict,
    ) -> None:
        """
        Destroy websocket session.
        """

        session = client.get(
            "session",
        )

        if session is None:

            return

        session_id = session.get(
            "id",
        )

        if hasattr(
            self,
            "_websocket_sessions",
        ):

            self._websocket_sessions.pop(
                session_id,
                None,
            )

        client["session"] = None

    # ==========================================================
    # Subscription Cleanup
    # ==========================================================

    def _cleanup_subscriptions(
        self,
        client: JSONDict,
    ) -> None:
        """
        Remove all topic subscriptions.
        """

        subscriptions = client.get(
            "subscriptions",
            set(),
        )

        #
        # Global topic registry
        #

        topics = getattr(
            self,
            "_websocket_topics",
            {},
        )

        for topic in list(subscriptions):

            clients = topics.get(
                topic,
            )

            if clients is None:

                continue

            clients.discard(
                client["id"],
            )

            if not clients:

                topics.pop(
                    topic,
                    None,
                )

        subscriptions.clear()

    # ==========================================================
    # Runtime Resource Cleanup
    # ==========================================================

    def _cleanup_resources(
        self,
        client: JSONDict,
    ) -> None:
        """
        Release runtime resources.
        """

        #
        # Remove websocket reference
        #

        client.pop(
            "websocket",
            None,
        )

        #
        # Remove metadata
        #

        client.pop(
            "metadata",
            None,
        )

        #
        # Remove context
        #

        client.pop(
            "context",
            None,
        )

        #
        # Remove negotiated capabilities
        #

        client.pop(
            "capabilities",
            None,
        )

        #
        # Remove protocol
        #

        client.pop(
            "protocol",
            None,
        )

    # ==========================================================
    # Cleanup Helpers
    # ==========================================================

    def cleanup_summary(
        self,
        client: JSONDict,
    ) -> JSONDict:
        """
        Return cleanup information.
        """

        return {

            "client_id":

                client.get(
                    "id",
                ),

            "state":

                client.get(
                    "state",
                ),

            "closed":

                client.get(
                    "closed",
                ),

            "disconnected_at":

                client.get(
                    "disconnected_at",
                ),

            "remaining_clients":

                self.websocket_client_count,

            "remaining_sessions":

                self.websocket_session_count,

        }

    def cleanup_all_sessions(
        self,
    ) -> int:
        """
        Remove all websocket sessions.
        """

        sessions = getattr(
            self,
            "_websocket_sessions",
            {},
        )

        count = len(
            sessions,
        )

        sessions.clear()

        return count

    def cleanup_all_topics(
        self,
    ) -> int:
        """
        Remove all topic subscriptions.
        """

        topics = getattr(
            self,
            "_websocket_topics",
            {},
        )

        count = len(
            topics,
        )

        topics.clear()

        return count

    def cleanup_runtime(
        self,
    ) -> JSONDict:
        """
        Cleanup all websocket runtime objects.

        Intended for shutdown/restart.
        """

        sessions = self.cleanup_all_sessions()

        topics = self.cleanup_all_topics()

        clients = len(
            self._websocket_clients,
        )

        self._websocket_clients.clear()

        self.websocket_connections = 0

        self.touch()

        return {

            "clients_removed":
                clients,

            "sessions_removed":
                sessions,

            "topics_removed":
                topics,

            "timestamp":
                self._now(),

        }
    # ==========================================================
    # Part 5.1.1C.3
    # Metrics & Finalization
    #
    # • unregister client
    # • update metrics
    # • runtime statistics
    # • final diagnostics
    # ==========================================================

    async def _finalize_client(
        self,
        client: JSONDict,
    ) -> JSONDict:
        """
        Finalize websocket client after cleanup.

        Pipeline
        --------
            before_finalize
                    ↓
            unregister client
                    ↓
            update metrics
                    ↓
            runtime statistics
                    ↓
            diagnostics
                    ↓
            after_finalize

        Returns
        -------
        dict
            Final runtime summary.
        """

        if not client:

            return {}

        await self._run_websocket_hooks(
            "before_finalize",
            client,
        )

        #
        # Collect final statistics before removal.
        #

        final_summary = self._collect_client_statistics(
            client,
        )

        #
        # Remove client registry entry.
        #

        self.unregister_websocket_client(
            client["id"],
        )

        #
        # Runtime metrics.
        #

        self.websocket_disconnected(
            client["id"],
        )

        self._websocket_disconnect_count += 1

        self.last_activity = self._now()

        self.touch()

        #
        # Runtime diagnostics.
        #

        diagnostics = self._build_disconnect_diagnostics(
            client,
        )

        await self._run_websocket_hooks(
            "after_finalize",
            client,
        )

        return {

            "summary":
                final_summary,

            "diagnostics":
                diagnostics,

        }

    # ==========================================================
    # Client Statistics
    # ==========================================================

    def _collect_client_statistics(
        self,
        client: JSONDict,
    ) -> JSONDict:
        """
        Collect final statistics for one client.
        """

        connected = client.get(
            "connected_at",
        )

        disconnected = client.get(
            "disconnected_at",
        )

        duration = 0.0

        if connected is not None and disconnected is not None:

            duration = max(
                0.0,
                disconnected - connected,
            )

        return {

            "client_id":
                client.get("id"),

            "session_id":
                (
                    client.get("session") or {}
                ).get("id"),

            "connected_at":
                connected,

            "disconnected_at":
                disconnected,

            "connection_duration":
                duration,

            "messages":
                client.get("messages", 0),

            "bytes_sent":
                client.get("bytes_sent", 0),

            "bytes_received":
                client.get("bytes_received", 0),

            "disconnect_code":
                client.get("disconnect_code"),

            "disconnect_reason":
                client.get("disconnect_reason"),

        }

    # ==========================================================
    # Runtime Statistics
    # ==========================================================

    def websocket_runtime_statistics(
        self,
    ) -> JSONDict:
        """
        Runtime websocket statistics.
        """

        total = max(
            1,
            self._websocket_connect_count,
        )

        disconnect_ratio = (
            self._websocket_disconnect_count
            / total
        )

        return {

            "active_clients":
                self.websocket_client_count,

            "sessions":
                self.websocket_session_count,

            "connections":
                self._websocket_connect_count,

            "disconnects":
                self._websocket_disconnect_count,

            "messages":
                self.websocket_messages,

            "bytes_sent":
                self.websocket_bytes_sent,

            "bytes_received":
                self.websocket_bytes_received,

            "disconnect_ratio":
                disconnect_ratio,

            "uptime":
                self.uptime,

        }

    # ==========================================================
    # Disconnect Diagnostics
    # ==========================================================

    def _build_disconnect_diagnostics(
        self,
        client: JSONDict,
    ) -> JSONDict:
        """
        Build diagnostics snapshot after disconnect.
        """

        return {

            "timestamp":
                self._now(),

            "runtime_state":
                self.state,

            "healthy":
                self.health()["healthy"],

            "client":

                self._collect_client_statistics(
                    client,
                ),

            "runtime":

                self.websocket_runtime_statistics(),

        }

    # ==========================================================
    # Public API
    # ==========================================================

    def websocket_summary(
        self,
    ) -> JSONDict:
        """
        Public websocket runtime summary.
        """

        return {

            "connections":

                self._websocket_connect_count,

            "disconnects":

                self._websocket_disconnect_count,

            "active_clients":

                self.websocket_client_count,

            "sessions":

                self.websocket_session_count,

            "messages":

                self.websocket_messages,

            "bytes_sent":

                self.websocket_bytes_sent,

            "bytes_received":

                self.websocket_bytes_received,

            "uptime":

                self.uptime,

            "healthy":

                self.health()["healthy"],

        }

    def reset_websocket_statistics(
        self,
    ) -> "DashboardWebServer":
        """
        Reset websocket runtime metrics.
        """

        self._websocket_connect_count = 0

        self._websocket_disconnect_count = 0

        self.websocket_messages = 0

        self.websocket_connections = 0

        self.websocket_bytes_sent = 0

        self.websocket_bytes_received = 0

        self.touch()

        return self
    # ==========================================================
    # Part 5.1.2
    # Connection Lifecycle
    #
    # • on_connect()
    # • on_disconnect()
    # • lifecycle hooks
    # • metrics integration
    # ==========================================================

    async def on_connect(
        self,
        client: JSONDict,
    ) -> JSONDict:
        """
        Invoked immediately after a websocket client
        has been accepted and registered.

        Pipeline
        --------
            before_connect hook
                    ↓
            initialize lifecycle state
                    ↓
            update metrics
                    ↓
            emit event
                    ↓
            after_connect hook
        """

        await self._run_websocket_hooks(
            "before_connect",
            client,
        )

        now = self._now()

        client["state"] = "connected"

        client["connected"] = True

        client["connected_at"] = now

        client["last_activity"] = now

        #
        # Runtime statistics
        #

        self._websocket_connect_count += 1

        self.websocket_connections = (
            self.websocket_client_count
        )

        self.last_activity = now

        self.touch()

        #
        # Event
        #

        self.emit_event(

            "websocket.connected",

            client_id=client["id"],

            timestamp=now,

        )

        await self._run_websocket_hooks(

            "after_connect",

            client,

        )

        return {

            "client_id":

                client["id"],

            "connected_at":

                now,

            "connections":

                self.websocket_connections,

        }

    # ==========================================================
    # Disconnect Lifecycle
    # ==========================================================

    async def on_disconnect(
        self,
        client: JSONDict,
    ) -> JSONDict:
        """
        Invoked after websocket cleanup.

        Pipeline
        --------
            before_disconnect hook
                    ↓
            update metrics
                    ↓
            emit event
                    ↓
            after_disconnect hook
        """

        await self._run_websocket_hooks(
            "before_disconnect_event",
            client,
        )

        now = self._now()

        client["connected"] = False

        client["last_activity"] = now

        client["state"] = "offline"

        self.websocket_connections = (
            self.websocket_client_count
        )

        self.last_activity = now

        self.touch()

        self.emit_event(

            "websocket.disconnected",

            client_id=client["id"],

            timestamp=now,

            reason=client.get(
                "disconnect_reason",
            ),

            code=client.get(
                "disconnect_code",
            ),

        )

        await self._run_websocket_hooks(

            "after_disconnect_event",

            client,

        )

        return {

            "client_id":

                client["id"],

            "disconnected_at":

                now,

            "remaining_clients":

                self.websocket_client_count,

        }

    # ==========================================================
    # Lifecycle Hooks
    # ==========================================================

    async def before_connect(
        self,
        client: JSONDict,
    ) -> None:
        """
        Default hook.

        Override in subclasses.
        """
        return None

    async def after_connect(
        self,
        client: JSONDict,
    ) -> None:
        """
        Default hook.
        """
        return None

    async def before_disconnect_event(
        self,
        client: JSONDict,
    ) -> None:
        """
        Default hook.
        """
        return None

    async def after_disconnect_event(
        self,
        client: JSONDict,
    ) -> None:
        """
        Default hook.
        """
        return None

    # ==========================================================
    # Lifecycle Metrics
    # ==========================================================

    @property
    def total_connections(
        self,
    ) -> int:
        """
        Total websocket connections accepted.
        """

        return self._websocket_connect_count

    @property
    def total_disconnects(
        self,
    ) -> int:
        """
        Total websocket disconnects.
        """

        return self._websocket_disconnect_count

    @property
    def active_connections(
        self,
    ) -> int:
        """
        Current active websocket clients.
        """

        return self.websocket_client_count

    @property
    def connection_success_rate(
        self,
    ) -> float:
        """
        Percentage of completed connections.
        """

        if self.total_connections == 0:

            return 100.0

        return (

            (
                self.total_connections
                -
                self.total_disconnects
            )
            /
            self.total_connections

        ) * 100.0

    # ==========================================================
    # Lifecycle State
    # ==========================================================

    def lifecycle_summary(
        self,
    ) -> JSONDict:
        """
        Connection lifecycle summary.
        """

        return {

            "connections":

                self.total_connections,

            "disconnects":

                self.total_disconnects,

            "active":

                self.active_connections,

            "success_rate":

                round(
                    self.connection_success_rate,
                    2,
                ),

            "last_activity":

                self.last_activity,

        }

    # ==========================================================
    # Internal Integration Helpers
    # ==========================================================

    async def _connection_started(
        self,
        client: JSONDict,
    ) -> None:
        """
        Internal helper.

        Called immediately after
        _accept_connection().
        """

        await self.on_connect(
            client,
        )

    async def _connection_finished(
        self,
        client: JSONDict,
    ) -> None:
        """
        Internal helper.

        Called after final cleanup.
        """

        await self.on_disconnect(
            client,
        )
    # ==========================================================
    # Part 5.1.3A
    # Receive Loop
    #
    # • _websocket_message_loop()
    # • receive loop
    # • graceful exit
    # ==========================================================

    async def _websocket_message_loop(
        self,
        client: JSONDict,
    ) -> None:
        """
        Main websocket receive loop.

        Runtime Pipeline
        ----------------
            Receive
                ↓
            Parse
                ↓
            Dispatch
                ↓
            Send Response
                ↓
            Heartbeat
                ↓
            Continue

        Exit Conditions
        ---------------
            • client disconnect
            • websocket closed
            • runtime closed
            • runtime disabled
            • fatal error
        """

        websocket = client["websocket"]

        while self._message_loop_active(client):

            try:

                message = await self._receive_message(
                    websocket,
                )

                #
                # Peer disconnected
                #

                if message is None:

                    break

                client["last_activity"] = self._now()

                #
                # Runtime statistics
                #

                client["messages"] += 1

                self.websocket_messages += 1

                #
                # Dispatch
                #
                # Implemented in Part 5.1.3B
                #

                await self._process_message(

                    client,

                    message,

                )

            except asyncio.CancelledError:

                #
                # Graceful shutdown
                #

                break

            except Exception as exc:

                #
                # Runtime error
                #

                self.request_failed(exc)

                self.last_error = str(exc)

                #
                # Implemented in Part 5.1.3E
                #

                await self._handle_websocket_error(

                    client,

                    exc,

                )

                break

    # ==========================================================
    # Receive Helpers
    # ==========================================================

    async def _receive_message(
        self,
        websocket: Any,
    ) -> JSONDict | str | bytes | None:
        """
        Receive one websocket message.

        Supports:

            • JSON
            • Text
            • Binary
        """

        try:

            #
            # Starlette/FastAPI API
            #

            message = await websocket.receive()

        except Exception:

            return None

        message_type = message.get(
            "type",
        )

        #
        # Disconnect
        #

        if message_type == "websocket.disconnect":

            return None

        #
        # Text
        #

        if "text" in message:

            return message["text"]

        #
        # Binary
        #

        if "bytes" in message:

            return message["bytes"]

        #
        # JSON payload
        #

        if "json" in message:

            return message["json"]

        return message

    # ==========================================================
    # Loop State
    # ==========================================================

    def _message_loop_active(
        self,
        client: JSONDict,
    ) -> bool:
        """
        Determine whether receive loop
        should continue.
        """

        if self.closed:

            return False

        if self.frozen:

            return False

        if not self.enabled:

            return False

        if not self.running:

            return False

        if client.get("closed"):

            return False

        if client.get("state") == "disconnected":

            return False

        return True

    # ==========================================================
    # Graceful Exit
    # ==========================================================

    async def _graceful_loop_exit(
        self,
        client: JSONDict,
    ) -> None:
        """
        Exit receive loop gracefully.
        """

        client["state"] = "closing"

        client["last_activity"] = self._now()

        self.touch()

    async def stop_message_loop(
        self,
        client_id: str,
    ) -> bool:
        """
        Request graceful loop shutdown.
        """

        client = self.get_websocket_client(
            client_id,
        )

        if client is None:

            return False

        client["closed"] = True

        await self._graceful_loop_exit(
            client,
        )

        return True

    # ==========================================================
    # Runtime Helpers
    # ==========================================================

    @property
    def active_message_loops(
        self,
    ) -> int:
        """
        Number of currently active
        websocket receive loops.
        """

        count = 0

        for client in self._websocket_clients.values():

            if self._message_loop_active(
                client,
            ):

                count += 1

        return count

    def message_loop_statistics(
        self,
    ) -> JSONDict:
        """
        Receive-loop runtime statistics.
        """

        return {

            "active_loops":
                self.active_message_loops,

            "messages":
                self.websocket_messages,

            "clients":
                self.websocket_client_count,

            "running":
                self.running,

            "enabled":
                self.enabled,

            "closed":
                self.closed,

        }
    # ==========================================================
    # Part 5.1.3B.1
    # Message Parsing
    #
    # • _process_message()
    # • parse JSON
    # • parse text
    # • parse binary
    # • normalize message
    # ==========================================================

    async def _process_message(
        self,
        client: JSONDict,
        message: Any,
    ) -> None:
        """
        Normalize and process one incoming websocket message.

        Pipeline
        --------
            Raw Message
                 │
                 ▼
            Parse
                 │
                 ▼
            Normalize
                 │
                 ▼
            Validation (Part 5.1.3B.2)
                 │
                 ▼
            Dispatch (Part 5.1.3B.3)
                 │
                 ▼
            Response (Part 5.1.3B.4)
        """

        await self._run_websocket_hooks(
            "before_message",
            client,
        )

        normalized = await self._normalize_message(
            client,
            message,
        )

        client["last_message"] = normalized

        client["last_activity"] = self._now()

        self.last_activity = self._now()

        #
        # Continue pipeline
        # (implemented in next parts)
        #

        await self.validate_message(
            client,
            normalized,
        )

        response = await self.dispatch_command(
            client,
            normalized,
        )

        await self.send_response(
            client,
            response,
        )

        await self._run_websocket_hooks(
            "after_message",
            client,
        )

    # ==========================================================
    # Normalization
    # ==========================================================

    async def _normalize_message(
        self,
        client: JSONDict,
        message: Any,
    ) -> JSONDict:
        """
        Convert every websocket payload into
        one normalized structure.
        """

        if isinstance(message, dict):

            return self._parse_json_message(
                client,
                message,
            )

        if isinstance(message, str):

            return self._parse_text_message(
                client,
                message,
            )

        if isinstance(message, (bytes, bytearray)):

            return self._parse_binary_message(
                client,
                bytes(message),
            )

        return {

            "type": "unknown",

            "command": None,

            "payload": message,

            "encoding": type(message).__name__,

            "timestamp": self._now(),

        }

    # ==========================================================
    # JSON Parsing
    # ==========================================================

    def _parse_json_message(
        self,
        client: JSONDict,
        payload: JSONDict,
    ) -> JSONDict:
        """
        Parse JSON websocket message.
        """

        command = (

            payload.get("command")
            or payload.get("action")
            or payload.get("type")
            or "unknown"

        )

        return {

            "type": "json",

            "command": str(command),

            "payload": payload,

            "encoding": "json",

            "client_id": client["id"],

            "timestamp": self._now(),

        }

    # ==========================================================
    # Text Parsing
    # ==========================================================

    def _parse_text_message(
        self,
        client: JSONDict,
        text: str,
    ) -> JSONDict:
        """
        Parse plain text command.

        Examples
        --------
        ping

        viewer.render

        stats
        """

        text = text.strip()

        command = text

        arguments: list[str] = []

        if " " in text:

            command, *arguments = text.split()

        return {

            "type": "text",

            "command": command,

            "arguments": arguments,

            "payload": text,

            "encoding": "utf-8",

            "client_id": client["id"],

            "timestamp": self._now(),

        }

    # ==========================================================
    # Binary Parsing
    # ==========================================================

    def _parse_binary_message(
        self,
        client: JSONDict,
        data: bytes,
    ) -> JSONDict:
        """
        Parse binary payload.

        Binary decoding is intentionally
        deferred to higher-level protocols.
        """

        return {

            "type": "binary",

            "command": "binary",

            "payload": data,

            "size": len(data),

            "encoding": "bytes",

            "client_id": client["id"],

            "timestamp": self._now(),

        }

    # ==========================================================
    # Helpers
    # ==========================================================

    def message_type(
        self,
        message: JSONDict,
    ) -> str:
        """
        Return normalized message type.
        """

        return message.get(
            "type",
            "unknown",
        )

    def message_command(
        self,
        message: JSONDict,
    ) -> str:
        """
        Return normalized command.
        """

        return message.get(
            "command",
            "",
        )

    def message_payload(
        self,
        message: JSONDict,
    ) -> Any:
        """
        Return normalized payload.
        """

        return message.get(
            "payload",
        )

    def normalize_message(
        self,
        message: Any,
    ) -> JSONDict:
        """
        Public normalization helper.
        """

        if isinstance(message, dict):

            return {

                "type": "json",

                "command":

                    message.get(
                        "command",
                        "unknown",
                    ),

                "payload":

                    message,

            }

        if isinstance(message, str):

            return {

                "type": "text",

                "command":

                    message.strip(),

                "payload":

                    message,

            }

        if isinstance(message, (bytes, bytearray)):

            return {

                "type": "binary",

                "command":

                    "binary",

                "payload":

                    bytes(message),

            }

        return {

            "type": "unknown",

            "command": None,

            "payload": message,

        }
    # ==========================================================
    # Part 5.1.3B.2
    # Validation
    #
    # • validate_message()
    # • schema validation
    # • payload validation
    # • protocol validation
    # ==========================================================

    async def validate_message(
        self,
        client: JSONDict,
        message: JSONDict,
    ) -> JSONDict:
        """
        Validate a normalized websocket message.

        Validation Pipeline
        -------------------
            Message
                │
                ▼
            Schema Validation
                │
                ▼
            Payload Validation
                │
                ▼
            Protocol Validation
                │
                ▼
            Validation Hooks
                │
                ▼
            Validated Message

        Raises
        ------
        ValueError
            Invalid message.
        """

        await self._run_websocket_hooks(
            "before_validate_message",
            client,
        )

        self._validate_message_schema(
            message,
        )

        self._validate_message_payload(
            message,
        )

        self._validate_message_protocol(
            client,
            message,
        )

        message["validated"] = True

        message["validated_at"] = self._now()

        client["last_validated_message"] = message

        self.last_activity = self._now()

        self.touch()

        await self._run_websocket_hooks(
            "after_validate_message",
            client,
        )

        return message

    # ==========================================================
    # Schema Validation
    # ==========================================================

    def _validate_message_schema(
        self,
        message: JSONDict,
    ) -> bool:
        """
        Validate normalized message schema.
        """

        if not isinstance(message, dict):

            raise ValueError(
                "Message must be a dictionary."
            )

        required = (

            "type",
            "command",
            "payload",

        )

        for field in required:

            if field not in message:

                raise ValueError(
                    f"Missing required field: {field}"
                )

        if message["type"] not in {

            "json",
            "text",
            "binary",
            "unknown",

        }:

            raise ValueError(
                f"Unsupported message type: "
                f"{message['type']}"
            )

        return True

    # ==========================================================
    # Payload Validation
    # ==========================================================

    def _validate_message_payload(
        self,
        message: JSONDict,
    ) -> bool:
        """
        Validate payload.
        """

        payload = message.get(
            "payload",
        )

        #
        # Binary payload
        #

        if isinstance(payload, bytes):

            if len(payload) > self.max_message_size:

                raise ValueError(
                    "Binary payload exceeds "
                    "maximum allowed size."
                )

            return True

        #
        # Text payload
        #

        if isinstance(payload, str):

            encoded = payload.encode(
                "utf-8",
            )

            if len(encoded) > self.max_message_size:

                raise ValueError(
                    "Text payload exceeds "
                    "maximum allowed size."
                )

            return True

        #
        # JSON payload
        #

        if isinstance(payload, dict):

            return True

        #
        # Unknown payload
        #

        if payload is None:

            raise ValueError(
                "Payload cannot be None."
            )

        return True

    # ==========================================================
    # Protocol Validation
    # ==========================================================

    def _validate_message_protocol(
        self,
        client: JSONDict,
        message: JSONDict,
    ) -> bool:
        """
        Validate websocket protocol.
        """

        protocol = client.get(
            "protocol",
            self.websocket_protocol,
        )

        supported = {

            self.websocket_protocol,

            "scios.dashboard.v1",

        }

        if protocol not in supported:

            raise ValueError(
                f"Unsupported websocket protocol: "
                f"{protocol}"
            )

        command = message.get(
            "command",
        )

        if command is None:

            raise ValueError(
                "Command cannot be None."
            )

        return True

    # ==========================================================
    # Validation Helpers
    # ==========================================================

    def message_is_valid(
        self,
        message: JSONDict,
    ) -> bool:
        """
        Check validation state.
        """

        return bool(
            message.get(
                "validated",
                False,
            )
        )

    def validation_summary(
        self,
        message: JSONDict,
    ) -> JSONDict:
        """
        Return validation metadata.
        """

        return {

            "validated":

                message.get(
                    "validated",
                    False,
                ),

            "validated_at":

                message.get(
                    "validated_at",
                ),

            "type":

                message.get(
                    "type",
                ),

            "command":

                message.get(
                    "command",
                ),

        }

    # ==========================================================
    # Validation Configuration
    # ==========================================================

    @property
    def validation_enabled(
        self,
    ) -> bool:
        """
        Validation flag.
        """

        return getattr(
            self,
            "_validation_enabled",
            True,
        )

    def enable_validation(
        self,
    ) -> None:
        """
        Enable runtime validation.
        """

        self._validation_enabled = True

    def disable_validation(
        self,
    ) -> None:
        """
        Disable runtime validation.
        """

        self._validation_enabled = False

    def validation_configuration(
        self,
    ) -> JSONDict:
        """
        Validation configuration.
        """

        return {

            "enabled":
                self.validation_enabled,

            "max_message_size":
                self.max_message_size,

            "protocol":
                self.websocket_protocol,

        }
    # ==========================================================
    # Part 5.1.3B.3
    # Command Dispatch
    #
    # • dispatch_command()
    # • command registry
    # • builtin commands
    # • unknown command
    # ==========================================================

    async def dispatch_command(
        self,
        client: JSONDict,
        message: JSONDict,
    ) -> JSONDict:
        """
        Dispatch one validated websocket command.

        Pipeline
        --------
            Validated Message
                    │
                    ▼
            Lookup Registry
                    │
            ┌───────┴────────┐
            │                │
        Builtin         Custom Handler
            │                │
            └───────┬────────┘
                    ▼
              Unknown Handler
                    ▼
                 Response
        """

        command = str(

            message.get(
                "command",
                "",
            )

        ).strip().lower()

        await self._run_websocket_hooks(
            "before_dispatch",
            client,
        )

        self.command_dispatch_count += 1

        self.last_command = command

        registry = self.command_registry

        #
        # Registered handler
        #

        handler = registry.get(
            command,
        )

        if handler is not None:

            result = await self._invoke_command_handler(

                handler,

                client,

                message,

            )

            await self._run_websocket_hooks(

                "after_dispatch",

                client,

            )

            return result

        #
        # Builtin commands
        #

        result = await self._dispatch_builtin_command(

            client,

            message,

        )

        await self._run_websocket_hooks(

            "after_dispatch",

            client,

        )

        return result

    # ==========================================================
    # Builtin Dispatcher
    # ==========================================================

    async def _dispatch_builtin_command(
        self,
        client: JSONDict,
        message: JSONDict,
    ) -> JSONDict:
        """
        Dispatch built-in commands.
        """

        command = message.get(
            "command",
            "",
        ).lower()

        builtin = {

            "ping":
                self._command_ping,

            "health":
                self._command_health,

            "status":
                self._command_status,

            "runtime":
                self._command_runtime,

            "statistics":
                self._command_statistics,

            "metrics":
                self._command_metrics,

            "viewer":
                self._command_viewer,

            "viewer.state":
                self._command_viewer_state,

            "viewer.render":
                self._command_viewer_render,

            "viewer.export":
                self._command_viewer_export,

            "config":
                self._command_config,

            "diagnostics":
                self._command_diagnostics,

            "help":
                self._command_help,

        }

        handler = builtin.get(
            command,
        )

        if handler is None:

            return await self._command_unknown(

                client,

                message,

            )

        return await handler(

            client,

            message,

        )

    # ==========================================================
    # Command Registry
    # ==========================================================

    def register_command(
        self,
        name: str,
        handler: Any,
    ) -> "DashboardWebServer":
        """
        Register custom websocket command.
        """

        self.command_registry[
            name.lower()
        ] = handler

        return self

    def unregister_command(
        self,
        name: str,
    ) -> bool:
        """
        Remove command.
        """

        return (

            self.command_registry.pop(

                name.lower(),

                None,

            )

            is not None

        )

    def has_command(
        self,
        name: str,
    ) -> bool:
        """
        Check command existence.
        """

        return (

            name.lower()

            in

            self.command_registry

        )

    def list_commands(
        self,
    ) -> list[str]:
        """
        Return all available commands.
        """

        commands = set(

            self.command_registry.keys()

        )

        commands.update({

            "ping",

            "health",

            "status",

            "runtime",

            "statistics",

            "metrics",

            "viewer",

            "viewer.state",

            "viewer.render",

            "viewer.export",

            "config",

            "diagnostics",

            "help",

        })

        return sorted(commands)

    # ==========================================================
    # Handler Invocation
    # ==========================================================

    async def _invoke_command_handler(
        self,
        handler: Any,
        client: JSONDict,
        message: JSONDict,
    ) -> JSONDict:
        """
        Invoke registered handler.
        """

        if asyncio.iscoroutinefunction(
            handler,
        ):

            return await handler(

                client,

                message,

            )

        return handler(

            client,

            message,

        )

    # ==========================================================
    # Unknown Command
    # ==========================================================

    async def _command_unknown(
        self,
        client: JSONDict,
        message: JSONDict,
    ) -> JSONDict:
        """
        Default unknown-command handler.
        """

        self.command_unknown_count += 1

        return {

            "success": False,

            "type": "error",

            "command":

                message.get(
                    "command",
                ),

            "error":

                "Unknown command.",

            "available":

                self.list_commands(),

            "timestamp":

                self._now(),

        }

    # ==========================================================
    # Dispatcher Statistics
    # ==========================================================

    @property
    def registered_command_count(
        self,
    ) -> int:
        """
        Number of registered commands.
        """

        return len(
            self.command_registry,
        )

    def command_statistics(
        self,
    ) -> JSONDict:
        """
        Command dispatcher statistics.
        """

        return {

            "registered":

                self.registered_command_count,

            "dispatches":

                self.command_dispatch_count,

            "unknown":

                self.command_unknown_count,

            "last_command":

                self.last_command,

        }
    # ==========================================================
    # Part 5.1.3B.4A
    # Response Builder
    #
    # • success_response()
    # • error_response()
    # • event_response()
    # • response envelope
    # ==========================================================

    def success_response(
        self,
        command: str,
        *,
        data: Any = None,
        message: str | None = None,
        request_id: str | None = None,
        metadata: JSONDict | None = None,
    ) -> JSONDict:
        """
        Build a successful websocket response.
        """

        return self._response_envelope(

            response_type="success",

            command=command,

            success=True,

            data=data,

            error=None,

            message=message,

            event=None,

            request_id=request_id,

            metadata=metadata,

        )

    # ----------------------------------------------------------

    def error_response(
        self,
        command: str,
        *,
        error: str,
        code: str = "runtime_error",
        details: Any = None,
        request_id: str | None = None,
        metadata: JSONDict | None = None,
    ) -> JSONDict:
        """
        Build an error response.
        """

        return self._response_envelope(

            response_type="error",

            command=command,

            success=False,

            data=None,

            error={

                "code": code,

                "message": error,

                "details": details,

            },

            message=None,

            event=None,

            request_id=request_id,

            metadata=metadata,

        )

    # ----------------------------------------------------------

    def event_response(
        self,
        event: str,
        *,
        data: Any = None,
        level: str = "info",
        request_id: str | None = None,
        metadata: JSONDict | None = None,
    ) -> JSONDict:
        """
        Build an event response.
        """

        return self._response_envelope(

            response_type="event",

            command="event",

            success=True,

            data=data,

            error=None,

            message=None,

            event={

                "name": event,

                "level": level,

            },

            request_id=request_id,

            metadata=metadata,

        )

    # ==========================================================
    # Response Envelope
    # ==========================================================

    def _response_envelope(
        self,
        *,
        response_type: str,
        command: str,
        success: bool,
        data: Any,
        error: Any,
        message: str | None,
        event: Any,
        request_id: str | None,
        metadata: JSONDict | None,
    ) -> JSONDict:
        """
        Create the standard SciOS websocket response.

        Every outbound websocket packet uses
        exactly this envelope.
        """

        envelope = {

            # --------------------------------------
            # Protocol
            # --------------------------------------

            "version":

                self.version,

            "protocol":

                self.websocket_protocol,

            "type":

                response_type,

            # --------------------------------------
            # Status
            # --------------------------------------

            "success":

                success,

            "command":

                command,

            # --------------------------------------
            # Payload
            # --------------------------------------

            "data":

                data,

            "error":

                error,

            "message":

                message,

            "event":

                event,

            # --------------------------------------
            # Runtime
            # --------------------------------------

            "timestamp":

                self._now(),

            "request_id":

                request_id,

            "server_id":

                self.id,

            "revision":

                self.revision,

            # --------------------------------------
            # Metadata
            # --------------------------------------

            "metadata":

                metadata or {},

        }

        return envelope

    # ==========================================================
    # Convenience Builders
    # ==========================================================

    def ok(
        self,
        command: str,
        data: Any = None,
    ) -> JSONDict:
        """
        Shortcut for success_response().
        """

        return self.success_response(

            command,

            data=data,

        )

    def fail(
        self,
        command: str,
        error: str,
    ) -> JSONDict:
        """
        Shortcut for error_response().
        """

        return self.error_response(

            command,

            error=error,

        )

    def notify(
        self,
        event: str,
        data: Any = None,
    ) -> JSONDict:
        """
        Shortcut for event_response().
        """

        return self.event_response(

            event,

            data=data,

        )

    # ==========================================================
    # Envelope Helpers
    # ==========================================================

    def response_type(
        self,
        response: JSONDict,
    ) -> str:
        """
        Return response type.
        """

        return response.get(

            "type",

            "unknown",

        )

    def response_success(
        self,
        response: JSONDict,
    ) -> bool:
        """
        Return success flag.
        """

        return bool(

            response.get(

                "success",

                False,

            )

        )

    def response_command(
        self,
        response: JSONDict,
    ) -> str:
        """
        Return command name.
        """

        return response.get(

            "command",

            "",

        )

    def response_data(
        self,
        response: JSONDict,
    ) -> Any:
        """
        Return payload.
        """

        return response.get(

            "data",

        )

    def response_error(
        self,
        response: JSONDict,
    ) -> Any:
        """
        Return error object.
        """

        return response.get(

            "error",

        )

    # ==========================================================
    # Response Metadata
    # ==========================================================

    def response_summary(
        self,
        response: JSONDict,
    ) -> JSONDict:
        """
        Small response summary.
        """

        return {

            "type":

                response.get("type"),

            "command":

                response.get("command"),

            "success":

                response.get("success"),

            "timestamp":

                response.get("timestamp"),

            "request_id":

                response.get("request_id"),

        }
    # ==========================================================
    # Part 5.1.3B.4B
    # Serialization
    #
    # • serialize_response()
    # • JSON serialization
    # • binary/text serialization
    # • response metadata
    # ==========================================================

    def serialize_response(
        self,
        response: JSONDict,
        *,
        encoding: str = "json",
        pretty: bool = False,
    ) -> str | bytes:
        """
        Serialize a websocket response.

        Supported
        ---------
            • json
            • text
            • bytes

        Returns
        -------
        str | bytes
        """

        response = self._prepare_response_metadata(
            response,
        )

        encoding = encoding.lower()

        if encoding == "json":

            return self._serialize_json(
                response,
                pretty=pretty,
            )

        if encoding == "text":

            return self._serialize_text(
                response,
            )

        if encoding in {

            "bytes",
            "binary",

        }:

            return self._serialize_binary(
                response,
            )

        raise ValueError(
            f"Unsupported serialization: "
            f"{encoding}"
        )

    # ==========================================================
    # JSON Serialization
    # ==========================================================

    def _serialize_json(
        self,
        response: JSONDict,
        *,
        pretty: bool = False,
    ) -> str:
        """
        Serialize to JSON.
        """

        kwargs = {

            "default": str,

            "ensure_ascii": False,

        }

        if pretty:

            kwargs["indent"] = 2

            kwargs["sort_keys"] = True

        return json.dumps(

            response,

            **kwargs,

        )

    # ==========================================================
    # Text Serialization
    # ==========================================================

    def _serialize_text(
        self,
        response: JSONDict,
    ) -> str:
        """
        Human-readable serialization.
        """

        status = (

            "OK"

            if response.get("success")

            else

            "ERROR"

        )

        command = response.get(
            "command",
            "-",
        )

        message = response.get(
            "message",
        )

        if message is None:

            if response.get("error"):

                message = response["error"].get(
                    "message",
                    "",
                )

            else:

                message = ""

        return (

            f"[{status}] "

            f"{command}: "

            f"{message}"

        )

    # ==========================================================
    # Binary Serialization
    # ==========================================================

    def _serialize_binary(
        self,
        response: JSONDict,
    ) -> bytes:
        """
        Serialize to UTF-8 bytes.

        Binary protocol support can replace
        this implementation later.
        """

        return self._serialize_json(
            response,
        ).encode(
            "utf-8",
        )

    # ==========================================================
    # Metadata
    # ==========================================================

    def _prepare_response_metadata(
        self,
        response: JSONDict,
    ) -> JSONDict:
        """
        Ensure serialization metadata exists.
        """

        metadata = response.setdefault(
            "metadata",
            {},
        )

        metadata.setdefault(

            "serialized_at",

            self._now(),

        )

        metadata.setdefault(

            "runtime_revision",

            self.revision,

        )

        metadata.setdefault(

            "server",

            self.name,

        )

        metadata.setdefault(

            "server_version",

            self.version,

        )

        metadata.setdefault(

            "protocol",

            self.websocket_protocol,

        )

        return response

    # ==========================================================
    # Serialization Helpers
    # ==========================================================

    def response_encoding(
        self,
        encoding: str = "json",
    ) -> str:
        """
        Normalize response encoding.
        """

        encoding = encoding.lower()

        supported = {

            "json",

            "text",

            "bytes",

            "binary",

        }

        if encoding not in supported:

            raise ValueError(
                f"Unsupported encoding: "
                f"{encoding}"
            )

        if encoding == "binary":

            return "bytes"

        return encoding

    def response_size(
        self,
        response: JSONDict,
    ) -> int:
        """
        Serialized size in bytes.
        """

        payload = self.serialize_response(
            response,
            encoding="bytes",
        )

        return len(payload)

    def response_metadata(
        self,
        response: JSONDict,
    ) -> JSONDict:
        """
        Return metadata block.
        """

        return response.get(
            "metadata",
            {},
        )

    def serialization_summary(
        self,
        response: JSONDict,
    ) -> JSONDict:
        """
        Serialization diagnostics.
        """

        return {

            "encoding":

                "json",

            "size":

                self.response_size(
                    response,
                ),

            "success":

                response.get(
                    "success",
                    False,
                ),

            "type":

                response.get(
                    "type",
                ),

            "command":

                response.get(
                    "command",
                ),

            "timestamp":

                response.get(
                    "timestamp",
                ),

        }

    # ==========================================================
    # Runtime Statistics
    # ==========================================================

    @property
    def serialization_count(
        self,
    ) -> int:
        """
        Total serialized responses.
        """

        return getattr(
            self,
            "_serialization_count",
            0,
        )

    @property
    def serialization_bytes(
        self,
    ) -> int:
        """
        Total serialized bytes.
        """

        return getattr(
            self,
            "_serialization_bytes",
            0,
        )

    def _record_serialization(
        self,
        response: JSONDict,
    ) -> None:
        """
        Update serialization metrics.
        """

        if not hasattr(
            self,
            "_serialization_count",
        ):

            self._serialization_count = 0

        if not hasattr(
            self,
            "_serialization_bytes",
        ):

            self._serialization_bytes = 0

        self._serialization_count += 1

        self._serialization_bytes += (

            self.response_size(
                response,
            )

        )

        self.touch()
    # ==========================================================
    # Part 5.1.3B.4C
    # Send Response
    #
    # • send_response()
    # • websocket.send_json()
    # • send_text()
    # • metrics update
    # • lifecycle hooks
    # ==========================================================

    async def send_response(
        self,
        client: JSONDict,
        response: JSONDict,
        *,
        encoding: str = "json",
    ) -> bool:
        """
        Send one response to a websocket client.

        Pipeline
        --------
            Response
                │
                ▼
            before_send hook
                │
                ▼
            Serialize
                │
                ▼
            Send
                │
                ▼
            Metrics
                │
                ▼
            after_send hook
        """

        websocket = client.get("websocket")

        if websocket is None:
            return False

        if client.get("closed", False):
            return False

        response = self._prepare_response_metadata(
            response,
        )

        await self._run_websocket_hooks(
            "before_send",
            client,
        )

        try:

            success = await self._send_serialized_response(
                websocket,
                response,
                encoding=encoding,
            )

            if success:

                self._update_send_metrics(
                    client,
                    response,
                )

                client["last_response"] = response

                client["last_activity"] = self._now()

                self.last_activity = self._now()

                self.touch()

                await self._run_websocket_hooks(
                    "after_send",
                    client,
                )

            return success

        except Exception as exc:

            self.request_failed(exc)

            self.last_error = str(exc)

            await self._run_websocket_hooks(
                "send_error",
                client,
            )

            raise

    # ==========================================================
    # Internal Sender
    # ==========================================================

    async def _send_serialized_response(
        self,
        websocket: Any,
        response: JSONDict,
        *,
        encoding: str = "json",
    ) -> bool:
        """
        Serialize and send response.
        """

        encoding = self.response_encoding(
            encoding,
        )

        #
        # Native JSON
        #

        if encoding == "json":

            await websocket.send_json(
                response,
            )

            return True

        #
        # Plain text
        #

        if encoding == "text":

            payload = self.serialize_response(
                response,
                encoding="text",
            )

            await websocket.send_text(
                payload,
            )

            return True

        #
        # Binary
        #

        payload = self.serialize_response(
            response,
            encoding="bytes",
        )

        await websocket.send_bytes(
            payload,
        )

        return True

    # ==========================================================
    # Convenience Senders
    # ==========================================================

    async def send_json(
        self,
        client: JSONDict,
        payload: JSONDict,
    ) -> bool:
        """
        Send JSON payload.
        """

        websocket = client.get(
            "websocket",
        )

        if websocket is None:

            return False

        await websocket.send_json(
            payload,
        )

        self._update_send_metrics(
            client,
            payload,
        )

        return True

    async def send_text(
        self,
        client: JSONDict,
        text: str,
    ) -> bool:
        """
        Send plain text.
        """

        websocket = client.get(
            "websocket",
        )

        if websocket is None:

            return False

        await websocket.send_text(
            text,
        )

        self.websocket_text_sent += 1

        self.touch()

        return True

    async def send_bytes(
        self,
        client: JSONDict,
        payload: bytes,
    ) -> bool:
        """
        Send binary payload.
        """

        websocket = client.get(
            "websocket",
        )

        if websocket is None:

            return False

        await websocket.send_bytes(
            payload,
        )

        self.websocket_binary_sent += 1

        self.touch()

        return True

    # ==========================================================
    # Metrics
    # ==========================================================

    def _update_send_metrics(
        self,
        client: JSONDict,
        response: JSONDict,
    ) -> None:
        """
        Update outbound websocket metrics.
        """

        size = self.response_size(
            response,
        )

        #
        # Global statistics
        #

        self.websocket_responses += 1

        self.websocket_bytes_sent += size

        #
        # Client statistics
        #

        client["responses"] = (

            client.get(
                "responses",
                0,
            ) + 1

        )

        client["bytes_sent"] = (

            client.get(
                "bytes_sent",
                0,
            ) + size

        )

        client["last_response_size"] = size

        client["last_response_at"] = self._now()

        self.touch()

    # ==========================================================
    # Send Statistics
    # ==========================================================

    @property
    def total_responses_sent(
        self,
    ) -> int:
        """
        Total websocket responses.
        """

        return self.websocket_responses

    @property
    def total_bytes_sent(
        self,
    ) -> int:
        """
        Total transmitted bytes.
        """

        return self.websocket_bytes_sent

    def send_statistics(
        self,
    ) -> JSONDict:
        """
        Outbound websocket statistics.
        """

        return {

            "responses":

                self.websocket_responses,

            "bytes":

                self.websocket_bytes_sent,

            "text":

                self.websocket_text_sent,

            "binary":

                self.websocket_binary_sent,

            "serialization":

                self.serialization_count,

        }

    # ==========================================================
    # Default Hooks
    # ==========================================================

    async def before_send(
        self,
        client: JSONDict,
    ) -> None:
        """
        Hook executed before sending.
        """
        return None

    async def after_send(
        self,
        client: JSONDict,
    ) -> None:
        """
        Hook executed after sending.
        """
        return None

    async def send_error(
        self,
        client: JSONDict,
    ) -> None:
        """
        Hook executed when send fails.
        """
        return None
    # ==========================================================
    # Part 5.1.3C
    # Send Loop
    #
    # • send_json()
    # • send_text()
    # • queue handling
    # • flush
    #
    # Async outbound websocket pipeline
    #
    # Queue
    #   │
    #   ▼
    # Send Loop
    #   │
    #   ├── JSON
    #   ├── TEXT
    #   └── BINARY
    #   │
    #   ▼
    # Flush
    # ==========================================================


    async def _websocket_send_loop(
        self,
        client: JSONDict,
    ) -> None:
        """
        Background websocket send loop.

        Responsibilities
        ----------------
        - consume outgoing queue
        - serialize messages
        - send messages
        - update metrics
        - graceful shutdown
        """

        queue = client.get(
            "send_queue",
        )

        if queue is None:

            return


        client["send_loop_running"] = True


        while self._send_loop_active(
            client,
        ):

            try:

                message = await queue.get()

                if message is None:

                    break


                await self._send_queued_message(

                    client,

                    message,

                )


                queue.task_done()


            except asyncio.CancelledError:

                break


            except Exception as exc:

                self.request_failed(
                    exc,
                )

                await self._handle_send_error(

                    client,

                    exc,

                )

                break



        client["send_loop_running"] = False


    # ==========================================================
    # Send JSON
    # ==========================================================


    async def send_json(
        self,
        client: JSONDict,
        payload: JSONDict,
        *,
        immediate: bool = False,
    ) -> bool:
        """
        Send JSON message.

        immediate=False:
            push into queue

        immediate=True:
            send directly
        """

        message = {

            "type":
                "json",

            "payload":
                payload,

            "created_at":
                self._now(),

        }


        if immediate:

            return await self._send_json_direct(

                client,

                payload,

            )


        return await self.enqueue_message(

            client,

            message,

        )


    async def _send_json_direct(
        self,
        client: JSONDict,
        payload: JSONDict,
    ) -> bool:
        """
        Direct JSON websocket send.
        """

        websocket = client.get(
            "websocket",
        )


        if websocket is None:

            return False


        await websocket.send_json(
            payload,
        )


        self._record_send_success(

            client,

            payload,

        )


        return True



    # ==========================================================
    # Send TEXT
    # ==========================================================


    async def send_text(
        self,
        client: JSONDict,
        text: str,
        *,
        immediate: bool = False,
    ) -> bool:
        """
        Send text message.
        """

        message = {

            "type":
                "text",

            "payload":
                text,

            "created_at":
                self._now(),

        }


        if immediate:

            return await self._send_text_direct(

                client,

                text,

            )


        return await self.enqueue_message(

            client,

            message,

        )



    async def _send_text_direct(
        self,
        client: JSONDict,
        text: str,
    ) -> bool:
        """
        Direct text websocket send.
        """

        websocket = client.get(
            "websocket",
        )


        if websocket is None:

            return False


        await websocket.send_text(
            text,
        )


        self.websocket_text_sent += 1


        self._record_send_success(

            client,

            text,

        )


        return True



    # ==========================================================
    # Queue Handling
    # ==========================================================


    async def enqueue_message(
        self,
        client: JSONDict,
        message: JSONDict,
    ) -> bool:
        """
        Add outbound message to queue.
        """

        queue = client.get(
            "send_queue",
        )


        if queue is None:

            return False



        if queue.full():

            self.send_queue_overflow += 1

            return False



        await queue.put(
            message,
        )


        self.send_queue_size_max = max(

            self.send_queue_size_max,

            queue.qsize(),

        )


        return True



    def queue_size(
        self,
        client: JSONDict,
    ) -> int:
        """
        Return queue size.
        """

        queue = client.get(
            "send_queue",
        )


        if queue is None:

            return 0


        return queue.qsize()



    def clear_send_queue(
        self,
        client: JSONDict,
    ) -> int:
        """
        Remove queued messages.
        """

        queue = client.get(
            "send_queue",
        )


        if queue is None:

            return 0


        count = 0


        while not queue.empty():

            try:

                queue.get_nowait()

                queue.task_done()

                count += 1


            except Exception:

                break



        return count



    # ==========================================================
    # Send Dispatcher
    # ==========================================================


    async def _send_queued_message(
        self,
        client: JSONDict,
        message: JSONDict,
    ) -> bool:
        """
        Dispatch queued message.
        """

        msg_type = message.get(
            "type",
        )


        payload = message.get(
            "payload",
        )



        if msg_type == "json":

            return await self._send_json_direct(

                client,

                payload,

            )


        if msg_type == "text":

            return await self._send_text_direct(

                client,

                payload,

            )


        return False



    # ==========================================================
    # Flush
    # ==========================================================


    async def flush(
        self,
        client: JSONDict,
    ) -> bool:
        """
        Wait until send queue empty.
        """

        queue = client.get(
            "send_queue",
        )


        if queue is None:

            return False



        await queue.join()


        return True



    async def flush_all(
        self,
    ) -> None:
        """
        Flush all websocket clients.
        """

        tasks = []


        for client in self._websocket_clients.values():

            tasks.append(

                self.flush(
                    client,
                )

            )


        if tasks:

            await asyncio.gather(
                *tasks,
            )



    # ==========================================================
    # Send Loop State
    # ==========================================================


    def _send_loop_active(
        self,
        client: JSONDict,
    ) -> bool:
        """
        Check send loop state.
        """

        if self.closed:

            return False


        if client.get(
            "closed",
            False,
        ):

            return False


        if not self.running:

            return False


        return True



    # ==========================================================
    # Metrics
    # ==========================================================


    def _record_send_success(
        self,
        client: JSONDict,
        payload: Any,
    ) -> None:
        """
        Update outbound metrics.
        """

        self.websocket_messages_sent += 1


        client["messages_sent"] = (

            client.get(
                "messages_sent",
                0,
            )

            + 1

        )


        if isinstance(
            payload,
            str,
        ):

            size = len(
                payload.encode(
                    "utf-8",
                )
            )

        else:

            size = len(
                json.dumps(
                    payload,
                    default=str,
                ).encode(
                    "utf-8",
                )
            )


        self.websocket_bytes_sent += size


        client["bytes_sent"] = (

            client.get(
                "bytes_sent",
                0,
            )

            + size

        )


        self.touch()



    async def _handle_send_error(
        self,
        client: JSONDict,
        error: Exception,
    ) -> None:
        """
        Send loop error handler.
        """

        client["last_send_error"] = str(
            error,
        )

        self.last_error = str(
            error,
        )

        self.error_count += 1
    # ==========================================================
    # Part 5.1.3D
    # Heartbeat Runtime
    #
    # • ping
    # • pong
    # • timeout
    # • keep-alive
    #
    # WebSocket heartbeat pipeline
    #
    # Heartbeat Loop
    #       │
    #       ▼
    #      Ping
    #       │
    #       ▼
    #      Pong
    #       │
    #       ▼
    #   Update Activity
    #       │
    #       ▼
    #   Timeout Check
    #       │
    #       ▼
    #   Disconnect Dead Client
    # ==========================================================


    async def _heartbeat_loop(
        self,
    ) -> None:
        """
        Global heartbeat manager.

        Periodically checks all websocket clients
        and keeps connections alive.
        """

        self._heartbeat_running = True


        while (

            self._heartbeat_running

            and

            not self.closed

        ):

            try:

                await asyncio.sleep(

                    self.heartbeat_interval

                )


                await self._heartbeat_tick()


            except asyncio.CancelledError:

                break


            except Exception as exc:

                self.request_failed(
                    exc,
                )



        self._heartbeat_running = False



    async def _heartbeat_tick(
        self,
    ) -> None:
        """
        Execute one heartbeat cycle.
        """

        now = self._now()


        for client in list(

            self._websocket_clients.values()

        ):

            if client.get(
                "closed",
                False,
            ):

                continue


            #
            # Timeout detection
            #

            if self._heartbeat_timeout_reached(

                client,

                now,

            ):

                await self._handle_heartbeat_timeout(

                    client,

                )

                continue



            #
            # Send ping
            #

            await self.ping(
                client,
            )



    # ==========================================================
    # Ping
    # ==========================================================


    async def ping(
        self,
        client: JSONDict,
    ) -> bool:
        """
        Send heartbeat ping.

        Uses websocket native ping
        when available.

        Otherwise sends protocol message.
        """

        websocket = client.get(
            "websocket",
        )


        if websocket is None:

            return False



        timestamp = self._now()


        try:

            #
            # Native websocket ping
            #

            if hasattr(

                websocket,

                "send_ping",

            ):

                await websocket.send_ping()



            else:

                await self.send_json(

                    client,

                    {

                        "type":
                            "event",

                        "event":
                            "ping",

                        "timestamp":
                            timestamp,

                    },

                )



            client["last_ping"] = timestamp

            client["ping_count"] = (

                client.get(

                    "ping_count",

                    0,

                )

                + 1

            )


            self.heartbeat_pings += 1


            return True



        except Exception as exc:

            await self._handle_heartbeat_error(

                client,

                exc,

            )

            return False



    # ==========================================================
    # Pong
    # ==========================================================


    async def pong(
        self,
        client: JSONDict,
    ) -> bool:
        """
        Register pong response.
        """

        now = self._now()


        client["last_pong"] = now


        client["pong_count"] = (

            client.get(

                "pong_count",

                0,

            )

            + 1

        )


        #
        # Calculate latency
        #

        last_ping = client.get(
            "last_ping",
        )


        if last_ping:

            latency = (

                now

                -

                last_ping

            )


            client["heartbeat_latency"] = latency


            self.heartbeat_latency_total += latency


        self.heartbeat_pongs += 1


        self.touch()


        return True



    # ==========================================================
    # Timeout
    # ==========================================================


    def _heartbeat_timeout_reached(
        self,
        client: JSONDict,
        now: float,
    ) -> bool:
        """
        Check heartbeat timeout.
        """

        last_activity = client.get(

            "last_activity",

            now,

        )


        elapsed = (

            now

            -

            last_activity

        )


        return (

            elapsed

            >

            self.heartbeat_timeout

        )



    async def _handle_heartbeat_timeout(
        self,
        client: JSONDict,
    ) -> None:
        """
        Handle dead websocket client.
        """

        client["heartbeat_timeout"] = True


        client["disconnect_reason"] = (

            "heartbeat_timeout"

        )


        self.heartbeat_timeouts += 1



        await self._disconnect_client(

            client,

            code=1001,

            reason="Heartbeat timeout",

        )



    # ==========================================================
    # Keep Alive
    # ==========================================================


    async def keep_alive(
        self,
        client: JSONDict,
    ) -> bool:
        """
        Keep websocket alive.

        Called by external runtime
        or heartbeat loop.
        """

        if client.get(
            "closed",
            False,
        ):

            return False


        await self.ping(
            client,
        )


        client["keep_alive_at"] = (

            self._now()

        )


        self.keep_alive_count += 1


        return True



    # ==========================================================
    # Heartbeat Configuration
    # ==========================================================


    def configure_heartbeat(
        self,
        *,
        interval: float | None = None,
        timeout: float | None = None,
    ) -> None:
        """
        Configure heartbeat runtime.
        """

        if interval is not None:

            self.heartbeat_interval = interval



        if timeout is not None:

            self.heartbeat_timeout = timeout



    def heartbeat_state(
        self,
    ) -> JSONDict:
        """
        Heartbeat diagnostics.
        """

        return {

            "running":

                self._heartbeat_running,


            "interval":

                self.heartbeat_interval,


            "timeout":

                self.heartbeat_timeout,


            "pings":

                self.heartbeat_pings,


            "pongs":

                self.heartbeat_pongs,


            "timeouts":

                self.heartbeat_timeouts,


            "latency":

                (

                    self.heartbeat_latency_total

                    /

                    max(

                        self.heartbeat_pongs,

                        1,

                    )

                ),

        }



    # ==========================================================
    # Heartbeat Error Handling
    # ==========================================================


    async def _handle_heartbeat_error(
        self,
        client: JSONDict,
        error: Exception,
    ) -> None:
        """
        Heartbeat failure handler.
        """

        client["heartbeat_error"] = str(
            error,
        )

        self.last_error = str(
            error,
        )

        self.error_count += 1



    # ==========================================================
    # Metrics
    # ==========================================================


    @property
    def heartbeat_statistics(
        self,
    ) -> JSONDict:
        """
        Heartbeat metrics.
        """

        return {

            "pings":

                self.heartbeat_pings,


            "pongs":

                self.heartbeat_pongs,


            "timeouts":

                self.heartbeat_timeouts,


            "average_latency":

                (

                    self.heartbeat_latency_total

                    /

                    max(

                        self.heartbeat_pongs,

                        1,

                    )

                ),


            "keep_alive":

                self.keep_alive_count,

        }
    # ==========================================================
    # Part 5.1.3E
    # Error Handling Runtime
    #
    # • protocol errors
    # • transport errors
    # • runtime exceptions
    # • disconnect policies
    # • metrics
    #
    # Error Pipeline
    #
    # Exception
    #     │
    #     ▼
    # Classify Error
    #     │
    #     ├── Protocol Error
    #     ├── Transport Error
    #     ├── Runtime Error
    #     │
    #     ▼
    # Build Error Response
    #     │
    #     ▼
    # Notify Client
    #     │
    #     ▼
    # Policy Decision
    #     │
    #     ▼
    # Disconnect / Recover
    # ==========================================================


    # ==========================================================
    # Main Error Handler
    # ==========================================================

    async def _handle_websocket_error(
        self,
        client: JSONDict,
        error: Exception,
    ) -> None:
        """
        Central websocket error handler.

        Classifies and processes
        every websocket exception.
        """

        error_type = self._classify_error(
            error,
        )


        self._record_error(
            client,
            error,
            error_type,
        )


        await self._run_websocket_hooks(
            "before_error",
            client,
        )


        #
        # Send error response
        #

        response = self.error_response(

            command="runtime",

            error=str(error),

            code=error_type,

        )


        try:

            await self.send_response(

                client,

                response,

            )


        except Exception:

            pass



        #
        # Apply disconnect policy
        #

        await self._apply_disconnect_policy(

            client,

            error_type,

        )


        await self._run_websocket_hooks(

            "after_error",

            client,

        )


    # ==========================================================
    # Error Classification
    # ==========================================================

    def _classify_error(
        self,
        error: Exception,
    ) -> str:
        """
        Classify websocket exception.
        """

        name = type(error).__name__


        protocol_errors = {

            "ValidationError",

            "ProtocolError",

            "ValueError",

        }


        transport_errors = {

            "WebSocketDisconnect",

            "ConnectionError",

            "BrokenPipeError",

            "TimeoutError",

        }


        if name in protocol_errors:

            return "protocol_error"


        if name in transport_errors:

            return "transport_error"


        return "runtime_error"



    # ==========================================================
    # Protocol Errors
    # ==========================================================

    async def handle_protocol_error(
        self,
        client: JSONDict,
        error: Exception,
    ) -> None:
        """
        Handle invalid websocket protocol.
        """

        self.protocol_error_count += 1


        response = self.error_response(

            command="protocol",

            error=str(error),

            code="invalid_protocol",

        )


        await self.send_response(

            client,

            response,

        )


        if self.disconnect_on_protocol_error:

            await self._disconnect_client(

                client,

                code=1002,

                reason="Protocol error",

            )



    # ==========================================================
    # Transport Errors
    # ==========================================================

    async def handle_transport_error(
        self,
        client: JSONDict,
        error: Exception,
    ) -> None:
        """
        Handle network transport failure.
        """

        self.transport_error_count += 1


        client["transport_error"] = str(
            error,
        )


        await self._disconnect_client(

            client,

            code=1006,

            reason="Transport failure",

        )



    # ==========================================================
    # Runtime Exceptions
    # ==========================================================

    async def handle_runtime_exception(
        self,
        client: JSONDict,
        error: Exception,
    ) -> None:
        """
        Handle internal runtime errors.
        """

        self.runtime_exception_count += 1


        response = self.error_response(

            command="runtime",

            error=str(error),

            code="internal_error",

        )


        await self.send_response(

            client,

            response,

        )


        if self.disconnect_on_runtime_error:

            await self._disconnect_client(

                client,

                code=1011,

                reason="Server error",

            )



    # ==========================================================
    # Disconnect Policies
    # ==========================================================

    async def _apply_disconnect_policy(
        self,
        client: JSONDict,
        error_type: str,
    ) -> None:
        """
        Decide whether client should disconnect.
        """

        policy = self.disconnect_policy


        if error_type == "protocol_error":

            if policy.get(
                "protocol",
                True,
            ):

                await self._disconnect_client(

                    client,

                    code=1002,

                    reason="Protocol violation",

                )


        elif error_type == "transport_error":

            await self._disconnect_client(

                client,

                code=1006,

                reason="Transport failure",

            )


        elif error_type == "runtime_error":

            if policy.get(
                "runtime",
                False,
            ):

                await self._disconnect_client(

                    client,

                    code=1011,

                    reason="Runtime failure",

                )



    # ==========================================================
    # Disconnect Helper
    # ==========================================================

    async def _disconnect_client(
        self,
        client: JSONDict,
        *,
        code: int = 1000,
        reason: str = "Closed",
    ) -> None:
        """
        Graceful websocket disconnect.
        """

        websocket = client.get(
            "websocket",
        )


        client["closed"] = True

        client["state"] = "disconnected"

        client["disconnect_code"] = code

        client["disconnect_reason"] = reason


        try:

            if websocket:

                await websocket.close(

                    code=code,

                    reason=reason,

                )

        except Exception:

            pass


        self.websocket_disconnects += 1



    # ==========================================================
    # Error Recording
    # ==========================================================

    def _record_error(
        self,
        client: JSONDict,
        error: Exception,
        error_type: str,
    ) -> None:
        """
        Store runtime error metrics.
        """

        item = {

            "type":
                error_type,

            "error":
                str(error),

            "time":
                self._now(),

            "client":
                client.get(
                    "id",
                ),

        }


        self.error_history.append(
            item,
        )


        if len(
            self.error_history
        ) > self.max_error_history:

            self.error_history.pop(
                0,
            )


        self.error_count += 1

        self.last_error = str(
            error,
        )



    # ==========================================================
    # Error Diagnostics
    # ==========================================================

    def error_statistics(
        self,
    ) -> JSONDict:
        """
        Return websocket error metrics.
        """

        return {

            "total":

                self.error_count,


            "protocol":

                self.protocol_error_count,


            "transport":

                self.transport_error_count,


            "runtime":

                self.runtime_exception_count,


            "disconnects":

                self.websocket_disconnects,


            "last_error":

                self.last_error,


            "history":

                self.error_history[-10:],

        }
# ==========================================================
# Part 5.2
# WebSocket Client Manager
#
# • register_client()
# • unregister_client()
# • get_client()
# • list_clients()
# • client statistics
#
# Client Manager
#
# WebSocket
#      │
#      ▼
# Client Registry
#      │
#      ├── register
#      ├── lookup
#      ├── remove
#      └── statistics
# ==========================================================


    # ==========================================================
    # Client Registry Foundation
    # ==========================================================

    def _ensure_client_registry(
        self,
    ) -> None:
        """
        Initialize client registry lazily.
        """

        if not hasattr(
            self,
            "_websocket_clients",
        ):

            self._websocket_clients = {}



    # ==========================================================
    # Register Client
    # ==========================================================

    async def register_client(
        self,
        websocket: Any,
        *,
        client_id: str | None = None,
        metadata: JSONDict | None = None,
    ) -> JSONDict:
        """
        Register websocket client.

        Creates client session state.
        """

        self._ensure_client_registry()


        if client_id is None:

            client_id = str(
                uuid.uuid4()
            )


        now = self._now()


        client = {

            # Identity

            "id":
                client_id,


            "websocket":
                websocket,


            "metadata":
                metadata or {},


            # State

            "state":
                "connected",


            "connected":
                True,


            "closed":
                False,


            # Runtime

            "created_at":
                now,


            "connected_at":
                now,


            "last_activity":
                now,


            "last_error":
                None,


            # Queue

            "send_queue":
                asyncio.Queue(
                    maxsize=self.send_queue_size
                ),


            "send_loop_running":
                False,


            # Statistics

            "messages_received":
                0,


            "messages_sent":
                0,


            "bytes_received":
                0,


            "bytes_sent":
                0,


            "responses":
                0,


            # Heartbeat

            "last_ping":
                None,


            "last_pong":
                None,


            "heartbeat_latency":
                0.0,


            "ping_count":
                0,


            "pong_count":
                0,


            # Subscription

            "subscriptions":
                set(),

        }


        self._websocket_clients[

            client_id

        ] = client



        #
        # Global metrics
        #

        self.websocket_connections += 1


        self.websocket_total_clients += 1


        self.touch()



        await self._run_websocket_hooks(

            "client_connected",

            client,

        )


        return client



    # ==========================================================
    # Unregister Client
    # ==========================================================

    async def unregister_client(
        self,
        client_id: str,
        *,
        reason: str = "unregistered",
    ) -> bool:
        """
        Remove websocket client.
        """

        self._ensure_client_registry()


        client = self._websocket_clients.get(
            client_id,
        )


        if client is None:

            return False



        client["state"] = (
            "removed"
        )


        client["closed"] = True


        client["disconnect_reason"] = reason


        #
        # Clear queue
        #

        self.clear_send_queue(
            client,
        )


        #
        # Remove registry
        #

        del self._websocket_clients[

            client_id

        ]



        self.websocket_connections = max(

            0,

            self.websocket_connections - 1,

        )


        self.touch()



        await self._run_websocket_hooks(

            "client_disconnected",

            client,

        )


        return True



    # ==========================================================
    # Get Client
    # ==========================================================

    def get_client(
        self,
        client_id: str,
    ) -> JSONDict | None:
        """
        Return client by id.
        """

        self._ensure_client_registry()


        return self._websocket_clients.get(
            client_id,
        )



    # ==========================================================
    # List Clients
    # ==========================================================

    def list_clients(
        self,
        *,
        include_closed: bool = False,
    ) -> list[JSONDict]:
        """
        Return all clients.
        """

        self._ensure_client_registry()


        clients = list(
            self._websocket_clients.values()
        )


        if include_closed:

            return clients


        return [

            client

            for client in clients

            if not client.get(
                "closed",
                False,
            )

        ]



    # ==========================================================
    # Client Count
    # ==========================================================

    @property
    def client_count(
        self,
    ) -> int:
        """
        Active websocket clients.
        """

        return len(

            self.list_clients()

        )



    # ==========================================================
    # Client State
    # ==========================================================

    def client_state(
        self,
        client_id: str,
    ) -> JSONDict | None:
        """
        Return lightweight client state.
        """

        client = self.get_client(
            client_id,
        )


        if client is None:

            return None



        return {

            "id":

                client["id"],


            "state":

                client["state"],


            "connected":

                client["connected"],


            "closed":

                client["closed"],


            "connected_at":

                client["connected_at"],


            "last_activity":

                client["last_activity"],

        }



    # ==========================================================
    # Client Statistics
    # ==========================================================

    def client_statistics(
        self,
        client_id: str | None = None,
    ) -> JSONDict:
        """
        Return client metrics.

        If client_id is None,
        returns global statistics.
        """

        if client_id:

            client = self.get_client(
                client_id,
            )


            if client is None:

                return {}


            return self._client_statistics(
                client,
            )


        return {

            "clients":

                self.client_count,


            "total_clients":

                self.websocket_total_clients,


            "connections":

                self.websocket_connections,


            "messages_sent":

                sum(

                    c.get(
                        "messages_sent",
                        0,
                    )

                    for c in self.list_clients(
                        include_closed=True
                    )

                ),


            "messages_received":

                sum(

                    c.get(
                        "messages_received",
                        0,
                    )

                    for c in self.list_clients(
                        include_closed=True
                    )

                ),


            "bytes_sent":

                sum(

                    c.get(
                        "bytes_sent",
                        0,
                    )

                    for c in self.list_clients(
                        include_closed=True
                    )

                ),


            "bytes_received":

                sum(

                    c.get(
                        "bytes_received",
                        0,
                    )

                    for c in self.list_clients(
                        include_closed=True
                    )

                ),

        }



    def _client_statistics(
        self,
        client: JSONDict,
    ) -> JSONDict:
        """
        Internal client statistics.
        """

        return {

            "id":

                client["id"],


            "state":

                client["state"],


            "messages":

                {

                    "sent":

                        client["messages_sent"],


                    "received":

                        client["messages_received"],

                },


            "bytes":

                {

                    "sent":

                        client["bytes_sent"],


                    "received":

                        client["bytes_received"],

                },


            "heartbeat":

                {

                    "ping":

                        client["ping_count"],


                    "pong":

                        client["pong_count"],


                    "latency":

                        client["heartbeat_latency"],

                },


            "queue":

                {

                    "size":

                        self.queue_size(
                            client,
                        ),

                },


        }



    # ==========================================================
    # Client Broadcast Helpers
    # ==========================================================

    async def broadcast_to_clients(
        self,
        payload: JSONDict,
    ) -> int:
        """
        Send payload to all clients.
        """

        sent = 0


        for client in self.list_clients():

            try:

                result = await self.send_json(

                    client,

                    payload,

                )


                if result:

                    sent += 1


            except Exception:

                continue



        return sent
# ==========================================================
# Part 5.3
# Broadcast API
#
# • broadcast()
# • broadcast_json()
# • broadcast_event()
# • broadcast_view()
#
# Broadcast Pipeline
#
# Producer
#    │
#    ▼
# Broadcast API
#    │
#    ├── JSON
#    ├── Event
#    └── View Update
#    │
#    ▼
# Client Manager
#    │
#    ▼
# Send Queue
#    │
#    ▼
# WebSocket Clients
# ==========================================================


    # ==========================================================
    # Broadcast Foundation
    # ==========================================================

    async def broadcast(
        self,
        payload: Any,
        *,
        clients: list[JSONDict] | None = None,
        exclude: set[str] | None = None,
        encoding: str = "json",
    ) -> int:
        """
        Broadcast payload to websocket clients.

        Parameters
        ----------
        payload:
            Data to broadcast.

        clients:
            Optional target clients.

        exclude:
            Client ids to skip.

        encoding:
            json | text | bytes
        """

        targets = (

            clients

            if clients is not None

            else

            self.list_clients()

        )


        exclude = exclude or set()


        sent = 0


        for client in targets:


            client_id = client.get(
                "id",
            )


            if client_id in exclude:

                continue



            try:

                result = await self._broadcast_send(

                    client,

                    payload,

                    encoding,

                )


                if result:

                    sent += 1



            except Exception as exc:

                await self._handle_websocket_error(

                    client,

                    exc,

                )



        self.broadcast_count += 1


        self.broadcast_messages += sent


        self.touch()


        return sent



    async def _broadcast_send(
        self,
        client: JSONDict,
        payload: Any,
        encoding: str,
    ) -> bool:
        """
        Internal broadcast sender.
        """

        if encoding == "json":

            return await self.send_json(

                client,

                payload,

            )


        if encoding == "text":

            return await self.send_text(

                client,

                str(payload),

            )


        message = {

            "type":

                "binary",

            "payload":

                payload,

        }


        return await self.enqueue_message(

            client,

            message,

        )



    # ==========================================================
    # Broadcast JSON
    # ==========================================================

    async def broadcast_json(
        self,
        data: JSONDict,
        *,
        event: str | None = None,
        exclude: set[str] | None = None,
    ) -> int:
        """
        Broadcast JSON payload.

        Standard dashboard format.
        """

        payload = {

            "type":

                "broadcast",


            "event":

                event,


            "data":

                data,


            "timestamp":

                self._now(),


            "server":

                self.id,

        }


        return await self.broadcast(

            payload,

            exclude=exclude,

            encoding="json",

        )



    # ==========================================================
    # Broadcast Event
    # ==========================================================

    async def broadcast_event(
        self,
        event: str,
        *,
        data: Any = None,
        level: str = "info",
        exclude: set[str] | None = None,
    ) -> int:
        """
        Broadcast runtime event.

        Used by:
            - lifecycle
            - metrics
            - viewer updates
        """

        payload = self.event_response(

            event,

            data=data,

            level=level,

        )


        return await self.broadcast(

            payload,

            exclude=exclude,

            encoding="json",

        )



    # ==========================================================
    # Broadcast View
    # ==========================================================

    async def broadcast_view(
        self,
        view: Any,
        *,
        action: str = "update",
        exclude: set[str] | None = None,
    ) -> int:
        """
        Broadcast dashboard view update.

        Examples
        --------
        {
            "action": "update",
            "view": {
                "id": "...",
                "state": {}
            }
        }
        """

        payload = {

            "type":

                "view",


            "action":

                action,


            "view":

                self._serialize_view(
                    view,
                ),


            "timestamp":

                self._now(),

        }


        return await self.broadcast(

            payload,

            exclude=exclude,

            encoding="json",

        )



    # ==========================================================
    # View Serialization
    # ==========================================================

    def _serialize_view(
        self,
        view: Any,
    ) -> JSONDict:
        """
        Normalize view object.
        """

        if view is None:

            return {}


        if isinstance(
            view,
            dict,
        ):

            return view


        if hasattr(
            view,
            "to_dict",
        ):

            return view.to_dict()



        if hasattr(
            view,
            "__dict__",
        ):

            return {

                k: v

                for k, v in view.__dict__.items()

                if not k.startswith(
                    "_"
                )

            }



        return {

            "value":

                str(view)

        }



    # ==========================================================
    # Broadcast Control
    # ==========================================================

    async def broadcast_except(
        self,
        client_id: str,
        payload: Any,
    ) -> int:
        """
        Broadcast excluding one client.
        """

        return await self.broadcast(

            payload,

            exclude={client_id},

        )



    async def broadcast_to(
        self,
        client_ids: list[str],
        payload: Any,
    ) -> int:
        """
        Broadcast to selected clients.
        """

        clients = []


        for cid in client_ids:

            client = self.get_client(
                cid,
            )


            if client:

                clients.append(
                    client
                )



        return await self.broadcast(

            payload,

            clients=clients,

        )



    # ==========================================================
    # Broadcast Metrics
    # ==========================================================

    def broadcast_statistics(
        self,
    ) -> JSONDict:
        """
        Return broadcast metrics.
        """

        return {

            "broadcasts":

                self.broadcast_count,


            "messages":

                self.broadcast_messages,


            "clients":

                self.client_count,


            "connections":

                self.websocket_connections,


            "last_broadcast":

                self.last_broadcast_at,

        }



    # ==========================================================
    # Broadcast Hooks
    # ==========================================================

    async def before_broadcast(
        self,
        payload: Any,
    ):
        """
        Hook before broadcast.
        """

        return None



    async def after_broadcast(
        self,
        payload: Any,
        count: int,
    ):
        """
        Hook after broadcast.
        """

        return None
# ==========================================================
# Part 5.4
# Subscription API
#
# • subscribe()
# • unsubscribe()
# • publish()
# • topics
# • channels
#
# Pub/Sub Architecture
#
# Publisher
#     │
#     ▼
#   Topic
#     │
#     ▼
# Channel Registry
#     │
#     ▼
# Subscribers
#     │
#     ▼
# WebSocket Send Queue
# ==========================================================


    # ==========================================================
    # Subscription Foundation
    # ==========================================================

    def _ensure_subscription_registry(
        self,
    ) -> None:
        """
        Initialize pub/sub registries.
        """

        if not hasattr(
            self,
            "_topics",
        ):

            self._topics = {}


        if not hasattr(
            self,
            "_channels",
        ):

            self._channels = {}



    # ==========================================================
    # Subscribe
    # ==========================================================

    async def subscribe(
        self,
        client: JSONDict,
        topic: str,
        *,
        channel: str | None = None,
    ) -> bool:
        """
        Subscribe websocket client
        to topic/channel.
        """

        self._ensure_subscription_registry()


        client_id = client.get(
            "id",
        )


        if client_id is None:

            return False



        #
        # Create topic
        #

        if topic not in self._topics:

            self._topics[topic] = set()



        self._topics[topic].add(
            client_id,
        )



        #
        # Client subscriptions
        #

        subscriptions = client.setdefault(

            "subscriptions",

            set(),

        )


        subscriptions.add(
            topic,
        )



        #
        # Channel mapping
        #

        if channel:

            self._register_channel(

                client_id,

                channel,

            )



        self.subscription_count += 1


        self.touch()



        await self._run_websocket_hooks(

            "subscribe",

            client,

        )


        return True



    # ==========================================================
    # Unsubscribe
    # ==========================================================

    async def unsubscribe(
        self,
        client: JSONDict,
        topic: str,
        *,
        channel: str | None = None,
    ) -> bool:
        """
        Remove client subscription.
        """

        self._ensure_subscription_registry()


        client_id = client.get(
            "id",
        )


        if client_id is None:

            return False



        subscribers = self._topics.get(
            topic,
        )


        if subscribers:

            subscribers.discard(
                client_id,
            )


            if not subscribers:

                del self._topics[topic]



        client.get(

            "subscriptions",

            set(),

        ).discard(

            topic

        )



        if channel:

            self._unregister_channel(

                client_id,

                channel,

            )



        self.unsubscribe_count += 1


        self.touch()



        await self._run_websocket_hooks(

            "unsubscribe",

            client,

        )


        return True



    # ==========================================================
    # Publish
    # ==========================================================

    async def publish(
        self,
        topic: str,
        payload: Any,
        *,
        channel: str | None = None,
        event: str | None = None,
    ) -> int:
        """
        Publish message to subscribers.
        """

        self._ensure_subscription_registry()


        subscribers = set(

            self._topics.get(

                topic,

                set(),

            )

        )


        if channel:

            channel_clients = self._channels.get(

                channel,

                set(),

            )


            subscribers.intersection_update(

                channel_clients

            )



        sent = 0



        for client_id in subscribers:

            client = self.get_client(
                client_id,
            )


            if client is None:

                continue



            message = {

                "type":

                    "topic",


                "topic":

                    topic,


                "event":

                    event,


                "data":

                    payload,


                "timestamp":

                    self._now(),

            }



            try:

                result = await self.send_json(

                    client,

                    message,

                )


                if result:

                    sent += 1



            except Exception as exc:

                await self._handle_websocket_error(

                    client,

                    exc,

                )



        self.publish_count += 1


        self.published_messages += sent


        self.last_publish_topic = topic


        self.touch()



        return sent



    # ==========================================================
    # Channel Registry
    # ==========================================================

    def _register_channel(
        self,
        client_id: str,
        channel: str,
    ) -> None:
        """
        Add client to channel.
        """

        self._ensure_subscription_registry()


        if channel not in self._channels:

            self._channels[channel] = set()



        self._channels[channel].add(
            client_id,
        )



    def _unregister_channel(
        self,
        client_id: str,
        channel: str,
    ) -> None:
        """
        Remove client from channel.
        """

        clients = self._channels.get(
            channel,
        )


        if clients:

            clients.discard(
                client_id,
            )


            if not clients:

                del self._channels[channel]



    # ==========================================================
    # Topic Management
    # ==========================================================

    def topics(
        self,
    ) -> list[str]:
        """
        List active topics.
        """

        self._ensure_subscription_registry()


        return list(
            self._topics.keys()
        )



    def channels(
        self,
    ) -> list[str]:
        """
        List active channels.
        """

        self._ensure_subscription_registry()


        return list(
            self._channels.keys()
        )



    def topic_subscribers(
        self,
        topic: str,
    ) -> list[str]:
        """
        Return topic subscribers.
        """

        return list(

            self._topics.get(

                topic,

                set(),

            )

        )



    def channel_members(
        self,
        channel: str,
    ) -> list[str]:
        """
        Return channel clients.
        """

        return list(

            self._channels.get(

                channel,

                set(),

            )

        )



    # ==========================================================
    # Client Cleanup
    # ==========================================================

    async def remove_client_subscriptions(
        self,
        client: JSONDict,
    ) -> None:
        """
        Remove all client subscriptions.
        """

        client_id = client.get(
            "id",
        )


        if client_id is None:

            return



        subscriptions = list(

            client.get(

                "subscriptions",

                set(),

            )

        )



        for topic in subscriptions:

            await self.unsubscribe(

                client,

                topic,

            )



    # ==========================================================
    # Subscription Diagnostics
    # ==========================================================

    def subscription_statistics(
        self,
    ) -> JSONDict:
        """
        Return pub/sub statistics.
        """

        return {

            "topics":

                len(

                    self._topics

                ),


            "channels":

                len(

                    self._channels

                ),


            "subscriptions":

                self.subscription_count,


            "unsubscriptions":

                self.unsubscribe_count,


            "publishes":

                self.publish_count,


            "messages":

                self.published_messages,


            "last_topic":

                self.last_publish_topic,

        }



    # ==========================================================
    # Subscription Hooks
    # ==========================================================

    async def on_subscribe(
        self,
        client: JSONDict,
        topic: str,
    ):
        """
        Subscribe hook.
        """

        return None



    async def on_unsubscribe(
        self,
        client: JSONDict,
        topic: str,
    ):
        """
        Unsubscribe hook.
        """

        return None
# ==========================================================
# Part 5.5
# WebSocket Runtime Helpers
#
# • websocket_state()
# • websocket_snapshot()
# • clear_clients()
# • diagnostics()
#
# Runtime Helper Layer
#
# WebSocket Runtime
#          │
#          ▼
#   State Snapshot
#          │
#   ┌──────┼────────┐
#   ▼      ▼        ▼
# State Snapshot Diagnostics Cleanup
# ==========================================================



    # ==========================================================
    # WebSocket State
    # ==========================================================

    def websocket_state(
        self,
    ) -> JSONDict:
        """
        Return current websocket runtime state.

        Lightweight runtime view.
        """

        self._ensure_client_registry()

        return {

            "enabled":

                self.websocket_enabled,


            "connections":

                self.websocket_connections,


            "clients":

                len(
                    self._websocket_clients
                ),


            "active_clients":

                self.client_count,


            "heartbeat":

                self.heartbeat_state(),


            "broadcast":

                self.broadcast_statistics(),


            "subscriptions":

                self.subscription_statistics(),


            "running":

                self.running,


            "state":

                self.state,


            "timestamp":

                self._now(),

        }



    # ==========================================================
    # WebSocket Snapshot
    # ==========================================================

    def websocket_snapshot(
        self,
    ) -> JSONDict:
        """
        Full websocket runtime snapshot.

        Includes clients,
        subscriptions,
        metrics.
        """

        self._ensure_client_registry()


        clients = []


        for client in self.list_clients(

            include_closed=True

        ):

            clients.append(

                {

                    "id":

                        client.get(
                            "id"
                        ),


                    "state":

                        client.get(
                            "state"
                        ),


                    "connected":

                        client.get(
                            "connected"
                        ),


                    "created_at":

                        client.get(
                            "created_at"
                        ),


                    "last_activity":

                        client.get(
                            "last_activity"
                        ),


                    "messages_sent":

                        client.get(
                            "messages_sent",
                            0,
                        ),


                    "messages_received":

                        client.get(
                            "messages_received",
                            0,
                        ),


                    "subscriptions":

                        list(

                            client.get(

                                "subscriptions",

                                set(),

                            )

                        ),

                }

            )



        return {

            "runtime":

                {

                    "state":

                        self.state,


                    "running":

                        self.running,


                    "enabled":

                        self.enabled,


                    "closed":

                        self.closed,

                },


            "clients":

                clients,


            "client_statistics":

                self.client_statistics(),


            "heartbeat":

                self.heartbeat_state(),


            "broadcast":

                self.broadcast_statistics(),


            "subscriptions":

                self.subscription_statistics(),


            "errors":

                self.error_statistics(),


            "timestamp":

                self._now(),

        }



    # ==========================================================
    # Clear Clients
    # ==========================================================

    async def clear_clients(
        self,
        *,
        close_connections: bool = True,
        reason: str = "server_cleanup",
    ) -> int:
        """
        Remove all websocket clients.

        Used by:
            - shutdown
            - restart
            - maintenance
        """

        self._ensure_client_registry()


        clients = list(

            self._websocket_clients.values()

        )


        removed = 0


        for client in clients:


            try:

                if close_connections:

                    await self._disconnect_client(

                        client,

                        code=1001,

                        reason=reason,

                    )



                result = await self.unregister_client(

                    client["id"],

                    reason=reason,

                )


                if result:

                    removed += 1



            except Exception as exc:

                await self._handle_websocket_error(

                    client,

                    exc,

                )



        return removed



    # ==========================================================
    # Clear Client By ID
    # ==========================================================

    async def clear_client(
        self,
        client_id: str,
        *,
        reason: str = "manual_cleanup",
    ) -> bool:
        """
        Remove single client.
        """

        client = self.get_client(
            client_id,
        )


        if client is None:

            return False



        await self._disconnect_client(

            client,

            code=1001,

            reason=reason,

        )


        return await self.unregister_client(

            client_id,

            reason=reason,

        )



    # ==========================================================
    # Diagnostics
    # ==========================================================

    def diagnostics(
        self,
    ) -> JSONDict:
        """
        Complete websocket diagnostics.
        """

        return {

            "identity":

                {

                    "server":

                        self.name,


                    "id":

                        self.id,

                },



            "runtime":

                {

                    "state":

                        self.state,


                    "running":

                        self.running,


                    "enabled":

                        self.enabled,


                    "closed":

                        self.closed,


                    "uptime":

                        self.uptime,

                },



            "websocket":

                {

                    "enabled":

                        self.websocket_enabled,


                    "connections":

                        self.websocket_connections,


                    "clients":

                        self.client_count,


                },



            "clients":

                self.client_statistics(),



            "heartbeat":

                self.heartbeat_state(),



            "broadcast":

                self.broadcast_statistics(),



            "subscriptions":

                self.subscription_statistics(),



            "errors":

                self.error_statistics(),



            "snapshot":

                self.websocket_snapshot(),



            "timestamp":

                self._now(),

        }



    # ==========================================================
    # Runtime Export
    # ==========================================================

    def export_websocket_state(
        self,
    ) -> JSONDict:
        """
        Serialization helper.
        """

        return {

            "type":

                "websocket_runtime",


            "version":

                self.version,


            "data":

                self.websocket_snapshot(),

        }



    # ==========================================================
    # Runtime Reset
    # ==========================================================

    async def reset_websocket_runtime(
        self,
    ) -> None:
        """
        Reset websocket runtime counters.
        """

        await self.clear_clients()


        self.broadcast_count = 0

        self.broadcast_messages = 0


        self.subscription_count = 0

        self.unsubscribe_count = 0


        self.publish_count = 0

        self.published_messages = 0


        self.heartbeat_pings = 0

        self.heartbeat_pongs = 0

        self.heartbeat_timeouts = 0


        self.error_count = 0

        self.error_history.clear()


        self.touch()
# ==========================================================
# Part 6
# Middleware Runtime
#
# • logging middleware
# • metrics middleware
# • CORS
# • compression
# • exception middleware
#
# Middleware Pipeline
#
# Request
#    │
#    ▼
# Middleware Chain
#    │
#    ├── Logging
#    │
#    ├── Metrics
#    │
#    ├── CORS
#    │
#    ├── Compression
#    │
#    └── Exception Handler
#    │
#    ▼
# FastAPI Router
# ==========================================================


# ==========================================================
# Middleware Registry Foundation
# ==========================================================


    def _ensure_middleware_registry(
        self,
    ) -> None:
        """
        Initialize middleware registry.
        """

        if not hasattr(
            self,
            "_middlewares",
        ):

            self._middlewares = []



    # ==========================================================
    # Register Middleware
    # ==========================================================

    def register_middleware(
        self,
        middleware,
        *,
        name: str | None = None,
        priority: int = 100,
        enabled: bool = True,
    ) -> dict:
        """
        Register middleware.

        Lower priority executes first.
        """

        self._ensure_middleware_registry()


        item = {

            "name":

                name or middleware.__name__,


            "middleware":

                middleware,


            "priority":

                priority,


            "enabled":

                enabled,

        }


        self._middlewares.append(
            item
        )


        self._middlewares.sort(

            key=lambda x: x["priority"]

        )


        self.middleware_count += 1


        return item



    # ==========================================================
    # Remove Middleware
    # ==========================================================

    def unregister_middleware(
        self,
        name: str,
    ) -> bool:
        """
        Remove middleware.
        """

        self._ensure_middleware_registry()


        for item in list(

            self._middlewares

        ):

            if item["name"] == name:

                self._middlewares.remove(
                    item
                )

                return True



        return False



    # ==========================================================
    # List Middleware
    # ==========================================================

    def list_middlewares(
        self,
    ) -> list:
        """
        Return middleware list.
        """

        self._ensure_middleware_registry()


        return [

            {

                "name":

                    item["name"],


                "priority":

                    item["priority"],


                "enabled":

                    item["enabled"],

            }

            for item in self._middlewares

        ]



    # ==========================================================
    # Apply Middleware Chain
    # ==========================================================

    def apply_middlewares(
        self,
        app,
    ):
        """
        Attach middleware to FastAPI app.
        """

        self._ensure_middleware_registry()


        for item in reversed(

            self._middlewares

        ):

            if not item["enabled"]:

                continue


            app.add_middleware(

                item["middleware"]

            )


        return app



# ==========================================================
# Logging Middleware
# ==========================================================


    def enable_logging_middleware(
        self,
    ):
        """
        Enable request logging.
        """

        if FastAPI is None:

            return None


        from starlette.middleware.base import (
            BaseHTTPMiddleware
        )


        server = self


        class LoggingMiddleware(
            BaseHTTPMiddleware
        ):


            async def dispatch(
                self,
                request,
                call_next,
            ):

                start = time.time()


                server.request_started()


                try:

                    response = await call_next(
                        request
                    )


                    duration = (

                        time.time()

                        -

                        start

                    )


                    server.request_completed(
                        duration
                    )


                    return response



                except Exception as exc:


                    server.request_failed(
                        exc
                    )


                    raise



        self.register_middleware(

            LoggingMiddleware,

            name="logging",

            priority=10,

        )


        return LoggingMiddleware



# ==========================================================
# Metrics Middleware
# ==========================================================


    def enable_metrics_middleware(
        self,
    ):
        """
        Enable request metrics.
        """

        if FastAPI is None:

            return None


        from starlette.middleware.base import (
            BaseHTTPMiddleware
        )


        server = self


        class MetricsMiddleware(
            BaseHTTPMiddleware
        ):


            async def dispatch(
                self,
                request,
                call_next,
            ):


                start = time.time()


                try:

                    response = await call_next(
                        request
                    )


                    elapsed = (

                        time.time()

                        -

                        start

                    )


                    server.metrics_requests += 1


                    server.metrics_latency += elapsed


                    return response



                except Exception:

                    server.metrics_errors += 1

                    raise



        self.register_middleware(

            MetricsMiddleware,

            name="metrics",

            priority=20,

        )


        return MetricsMiddleware



# ==========================================================
# CORS Middleware
# ==========================================================


    def enable_cors_middleware(
        self,
        *,
        origins=None,
    ):
        """
        Enable CORS support.
        """

        if FastAPI is None:

            return None



        from fastapi.middleware.cors import (
            CORSMiddleware
        )


        self.cors["enabled"] = True


        if origins:

            self.cors["origins"] = origins



        self.register_middleware(

            CORSMiddleware,

            name="cors",

            priority=30,

        )


        return CORSMiddleware



# ==========================================================
# Compression Middleware
# ==========================================================


    def enable_compression_middleware(
        self,
        *,
        minimum_size: int = 1000,
    ):
        """
        Enable gzip compression.
        """

        if FastAPI is None:

            return None


        from fastapi.middleware.gzip import (
            GZipMiddleware
        )


        self.compression = {

            "enabled":

                True,


            "minimum_size":

                minimum_size,

        }


        self.register_middleware(

            GZipMiddleware,

            name="compression",

            priority=40,

        )


        return GZipMiddleware



# ==========================================================
# Exception Middleware
# ==========================================================


    def enable_exception_middleware(
        self,
    ):
        """
        Global exception handler.
        """

        if FastAPI is None:

            return None


        from starlette.middleware.base import (
            BaseHTTPMiddleware
        )


        server = self


        class ExceptionMiddleware(
            BaseHTTPMiddleware
        ):


            async def dispatch(
                self,
                request,
                call_next,
            ):


                try:

                    return await call_next(
                        request
                    )


                except Exception as exc:


                    server.request_failed(
                        exc
                    )


                    raise



        self.register_middleware(

            ExceptionMiddleware,

            name="exception",

            priority=0,

        )


        return ExceptionMiddleware



# ==========================================================
# Middleware Diagnostics
# ==========================================================


    def middleware_state(
        self,
    ) -> dict:
        """
        Middleware diagnostics.
        """

        return {

            "count":

                len(
                    self._middlewares
                ),


            "middlewares":

                self.list_middlewares(),


            "metrics":

                {

                    "requests":

                        self.metrics_requests,


                    "errors":

                        self.metrics_errors,


                    "latency":

                        self.metrics_latency,

                },

        }
# ==========================================================
# Part 7
# Authentication Runtime
#
# • API Key
# • Bearer Token
# • Basic Auth
# • custom provider
# • permission helpers
#
# Authentication Pipeline
#
# Request / WebSocket
#          │
#          ▼
#   Authentication Layer
#          │
#  ┌───────┼────────┐
#  ▼       ▼        ▼
# APIKey Bearer   Basic
#          │
#          ▼
# Custom Provider
#          │
#          ▼
# Permission Check
#          │
#          ▼
# Dashboard Runtime
# ==========================================================


# ==========================================================
# Authentication Registry
# ==========================================================


    def _ensure_auth_registry(
        self,
    ) -> None:
        """
        Initialize authentication state.
        """

        if not hasattr(
            self,
            "_auth_providers",
        ):

            self._auth_providers = {}



        if not hasattr(
            self,
            "_permissions",
        ):

            self._permissions = {}



        if not hasattr(
            self,
            "_api_keys",
        ):

            self._api_keys = {}



        if not hasattr(
            self,
            "_tokens",
        ):

            self._tokens = {}



# ==========================================================
# Authentication Configuration
# ==========================================================


    def configure_auth(
        self,
        *,
        enabled: bool = True,
        mode: str = "bearer",
        provider=None,
        config: dict | None = None,
    ):
        """
        Configure authentication runtime.
        """

        self.auth = {

            "enabled":

                enabled,


            "mode":

                mode,


            "provider":

                provider,


            "config":

                config or {},

        }


        self.auth_enabled = enabled


        self.auth_mode = mode


        self.auth_provider = provider


        return self.auth



# ==========================================================
# API Key Authentication
# ==========================================================


    def register_api_key(
        self,
        key: str,
        *,
        identity: dict | None = None,
        permissions: list[str] | None = None,
    ):
        """
        Register API key.
        """

        self._ensure_auth_registry()


        self._api_keys[key] = {

            "identity":

                identity or {},


            "permissions":

                permissions or [],


            "created_at":

                self._now(),

        }


        return True



    def validate_api_key(
        self,
        key: str,
    ) -> dict | None:
        """
        Validate API key.
        """

        self._ensure_auth_registry()


        return self._api_keys.get(
            key
        )



# ==========================================================
# Bearer Token
# ==========================================================


    def register_token(
        self,
        token: str,
        *,
        identity: dict | None = None,
        permissions: list[str] | None = None,
        expires_at: float | None = None,
    ):
        """
        Register bearer token.
        """

        self._ensure_auth_registry()


        self._tokens[token] = {

            "identity":

                identity or {},


            "permissions":

                permissions or [],


            "expires_at":

                expires_at,

        }


        return True



    def validate_bearer_token(
        self,
        token: str,
    ) -> dict | None:
        """
        Validate bearer token.
        """

        self._ensure_auth_registry()


        data = self._tokens.get(
            token
        )


        if data is None:

            return None



        expires = data.get(
            "expires_at"
        )


        if expires:

            if self._now() > expires:

                return None



        return data



# ==========================================================
# Basic Authentication
# ==========================================================


    def register_basic_user(
        self,
        username: str,
        password: str,
        *,
        identity: dict | None = None,
        permissions: list[str] | None = None,
    ):
        """
        Register basic auth user.
        """

        self._ensure_auth_registry()


        if not hasattr(
            self,
            "_basic_users",
        ):

            self._basic_users = {}



        self._basic_users[username] = {

            "password":

                password,


            "identity":

                identity or {},


            "permissions":

                permissions or [],

        }


        return True



    def validate_basic_auth(
        self,
        username: str,
        password: str,
    ) -> dict | None:
        """
        Validate username/password.
        """

        users = getattr(

            self,

            "_basic_users",

            {},

        )


        user = users.get(
            username
        )


        if user is None:

            return None



        if user["password"] != password:

            return None



        return user



# ==========================================================
# Custom Authentication Provider
# ==========================================================


    def register_auth_provider(
        self,
        name: str,
        provider,
    ):
        """
        Register custom auth provider.
        """

        self._ensure_auth_registry()


        self._auth_providers[name] = provider


        return provider



    async def authenticate_custom(
        self,
        provider: str,
        credentials,
    ):
        """
        Execute custom provider.
        """

        self._ensure_auth_registry()


        handler = self._auth_providers.get(
            provider
        )


        if handler is None:

            return None



        if hasattr(
            handler,
            "__call__",
        ):

            result = handler(
                credentials
            )


            if inspect.isawaitable(
                result
            ):

                result = await result



            return result



        return None



# ==========================================================
# Unified Authentication API
# ==========================================================


    async def authenticate(
        self,
        credentials: dict,
    ) -> dict | None:
        """
        Unified authentication entry.

        Supports:
            api_key
            bearer
            basic
            custom
        """

        if not self.auth_enabled:

            return {

                "authenticated":

                    True,

                "anonymous":

                    True,

            }



        method = credentials.get(
            "type"
        )



        if method == "api_key":

            result = self.validate_api_key(

                credentials.get(
                    "key"
                )

            )


        elif method == "bearer":

            result = self.validate_bearer_token(

                credentials.get(
                    "token"
                )

            )


        elif method == "basic":

            result = self.validate_basic_auth(

                credentials.get(
                    "username"
                ),

                credentials.get(
                    "password"
                ),

            )


        else:

            result = None



        if result is None:

            return None



        return {

            "authenticated":

                True,


            **result,

        }



# ==========================================================
# Permission Helpers
# ==========================================================


    def grant_permission(
        self,
        identity: str,
        permission: str,
    ):
        """
        Grant permission.
        """

        self._ensure_auth_registry()


        self._permissions.setdefault(

            identity,

            set(),

        ).add(

            permission

        )



    def revoke_permission(
        self,
        identity: str,
        permission: str,
    ):
        """
        Revoke permission.
        """

        permissions = self._permissions.get(
            identity
        )


        if permissions:

            permissions.discard(
                permission
            )



    def has_permission(
        self,
        user: dict,
        permission: str,
    ) -> bool:
        """
        Check permission.
        """

        if user is None:

            return False



        permissions = user.get(

            "permissions",

            [],

        )


        return (

            permission in permissions

        )



    def require_permission(
        self,
        user: dict,
        permission: str,
    ):
        """
        Raise exception if denied.
        """

        if not self.has_permission(

            user,

            permission,

        ):

            raise PermissionError(

                f"Missing permission: {permission}"

            )


        return True



# ==========================================================
# Authentication Diagnostics
# ==========================================================


    def auth_state(
        self,
    ) -> dict:
        """
        Authentication diagnostics.
        """

        self._ensure_auth_registry()


        return {

            "enabled":

                self.auth_enabled,


            "mode":

                self.auth_mode,


            "providers":

                list(

                    self._auth_providers.keys()

                ),


            "api_keys":

                len(

                    self._api_keys

                ),


            "tokens":

                len(

                    self._tokens

                ),


            "permissions":

                len(

                    self._permissions

                ),

        }
# ==========================================================
# Part 8
# Static Assets Runtime
#
# • mount static
# • dashboard html
# • css
# • js
# • favicon
#
# Static Architecture
#
# Browser
#    │
#    ▼
# FastAPI Static Mount
#    │
#    ├── index.html
#    ├── css/
#    ├── js/
#    ├── assets/
#    └── favicon.ico
#
#    ▼
# Dashboard Runtime
# ==========================================================


# ==========================================================
# Static Registry Foundation
# ==========================================================


    def _ensure_static_registry(
        self,
    ) -> None:
        """
        Initialize static asset runtime.
        """

        if not hasattr(
            self,
            "static_config",
        ):

            self.static_config = {

                "enabled":

                    False,


                "directory":

                    None,


                "mount":

                    "/static",


                "html":

                    None,


                "css":

                    [],


                "js":

                    [],


                "favicon":

                    None,

            }



        if not hasattr(
            self,
            "_static_assets",
        ):

            self._static_assets = {}



# ==========================================================
# Static Configuration
# ==========================================================


    def configure_static(
        self,
        *,
        directory: str | None = None,
        mount: str = "/static",
        enabled: bool = True,
    ):
        """
        Configure static directory.
        """

        self._ensure_static_registry()


        self.static_config.update(

            {

                "enabled":

                    enabled,


                "directory":

                    directory,


                "mount":

                    mount,

            }

        )


        return self.static_config



# ==========================================================
# Mount Static
# ==========================================================


    def mount_static(
        self,
        app,
    ):
        """
        Mount static assets into FastAPI.
        """

        self._ensure_static_registry()


        if not self.static_config["enabled"]:

            return app



        if FastAPI is None:

            return app



        try:

            from fastapi.staticfiles import (
                StaticFiles
            )


            app.mount(

                self.static_config["mount"],

                StaticFiles(

                    directory=

                        self.static_config["directory"],

                ),

                name="static",

            )


            self.static_mounted = True



        except Exception as exc:

            self.last_error = str(
                exc
            )


        return app



# ==========================================================
# Dashboard HTML
# ==========================================================


    def configure_dashboard_html(
        self,
        html_path: str,
    ):
        """
        Configure dashboard entry html.
        """

        self._ensure_static_registry()


        self.static_config["html"] = html_path


        return html_path



    def dashboard_html(
        self,
    ) -> str:
        """
        Return dashboard HTML.

        Supports:
            file based
            embedded fallback
        """

        html_file = self.static_config.get(
            "html"
        )


        if html_file:

            try:

                with open(

                    html_file,

                    "r",

                    encoding="utf-8",

                ) as f:

                    return f.read()


            except Exception:

                pass



        return self.default_dashboard_html()



    def default_dashboard_html(
        self,
    ) -> str:
        """
        Embedded dashboard page.
        """

        return """
<!DOCTYPE html>
<html>
<head>
<title>SciOS-NG Dashboard</title>
<link rel="stylesheet" href="/static/css/dashboard.css">
</head>

<body>

<h1>SciOS-NG Dashboard</h1>

<div id="app">
Loading...
</div>

<script src="/static/js/dashboard.js"></script>

</body>
</html>
"""



# ==========================================================
# CSS Management
# ==========================================================


    def register_css(
        self,
        path: str,
    ):
        """
        Register css asset.
        """

        self._ensure_static_registry()


        self.static_config["css"].append(
            path
        )


        return path



    def css_assets(
        self,
    ) -> list:
        """
        Return css files.
        """

        return self.static_config.get(

            "css",

            [],

        )



# ==========================================================
# JavaScript Management
# ==========================================================


    def register_js(
        self,
        path: str,
    ):
        """
        Register javascript asset.
        """

        self._ensure_static_registry()


        self.static_config["js"].append(
            path
        )


        return path



    def js_assets(
        self,
    ) -> list:
        """
        Return javascript files.
        """

        return self.static_config.get(

            "js",

            [],

        )



# ==========================================================
# Favicon
# ==========================================================


    def configure_favicon(
        self,
        path: str,
    ):
        """
        Configure favicon.
        """

        self._ensure_static_registry()


        self.static_config["favicon"] = path


        return path



    def favicon(
        self,
    ):
        """
        Return favicon path.
        """

        return self.static_config.get(

            "favicon"

        )



# ==========================================================
# Asset Registry
# ==========================================================


    def register_asset(
        self,
        name: str,
        path: str,
        asset_type: str = "file",
    ):
        """
        Register custom asset.
        """

        self._ensure_static_registry()


        self._static_assets[name] = {

            "path":

                path,


            "type":

                asset_type,


            "created_at":

                self._now(),

        }


        return self._static_assets[name]



    def get_asset(
        self,
        name: str,
    ):
        """
        Get asset metadata.
        """

        return self._static_assets.get(
            name
        )



    def list_assets(
        self,
    ) -> list:
        """
        List static assets.
        """

        return list(

            self._static_assets.values()

        )



# ==========================================================
# Static Router
# ==========================================================


    def register_static_routes(
        self,
        app,
    ):
        """
        Register dashboard static routes.
        """

        if APIRouter is None:

            return app



        @app.get(
            "/",
        )
        async def dashboard_index():

            from fastapi.responses import (
                HTMLResponse
            )

            return HTMLResponse(

                self.dashboard_html()

            )



        @app.get(
            "/favicon.ico",
        )
        async def favicon_route():

            from fastapi.responses import (
                FileResponse
            )


            icon = self.favicon()


            if icon:

                return FileResponse(
                    icon
                )


            return {
                "status":
                    "no favicon"
            }



        return app



# ==========================================================
# Static Diagnostics
# ==========================================================


    def static_state(
        self,
    ) -> dict:
        """
        Static runtime diagnostics.
        """

        self._ensure_static_registry()


        return {

            "enabled":

                self.static_config["enabled"],


            "directory":

                self.static_config["directory"],


            "mount":

                self.static_config["mount"],


            "html":

                self.static_config["html"],


            "css":

                len(

                    self.static_config["css"]

                ),


            "js":

                len(

                    self.static_config["js"]

                ),


            "favicon":

                self.static_config["favicon"],


            "mounted":

                getattr(

                    self,

                    "static_mounted",

                    False,

                ),

        }
# ==========================================================
# Part 9
# Events & Hooks Runtime
#
# • before_start
# • after_start
# • before_request
# • after_request
# • before_shutdown
# • emit_event
#
# Event Architecture
#
# Runtime
#    │
#    ▼
# Event Dispatcher
#    │
# ├── Lifecycle Events
# │
# ├── HTTP Events
# │
# ├── WebSocket Events
# │
# └── Custom Events
#    │
#    ▼
# Hook Handlers
# ==========================================================


# ==========================================================
# Event Registry Foundation
# ==========================================================


    def _ensure_event_registry(
        self,
    ) -> None:
        """
        Initialize event runtime.
        """

        if not hasattr(
            self,
            "_event_handlers",
        ):

            self._event_handlers = {}


        if not hasattr(
            self,
            "_event_history",
        ):

            self._event_history = []



# ==========================================================
# Register Hook
# ==========================================================


    def register_hook(
        self,
        event: str,
        handler,
    ):
        """
        Register event hook.

        Example:

        register_hook(
            "before_start",
            callback
        )
        """

        self._ensure_event_registry()


        self._event_handlers.setdefault(

            event,

            []

        ).append(

            handler

        )


        return handler



# ==========================================================
# Unregister Hook
# ==========================================================


    def unregister_hook(
        self,
        event: str,
        handler,
    ) -> bool:
        """
        Remove hook handler.
        """

        self._ensure_event_registry()


        handlers = self._event_handlers.get(
            event
        )


        if not handlers:

            return False



        if handler in handlers:

            handlers.remove(
                handler
            )


            return True



        return False



# ==========================================================
# Event Dispatcher
# ==========================================================


    async def emit_event(
        self,
        event: str,
        payload=None,
    ):
        """
        Emit runtime event.

        Executes all registered hooks.
        """

        self._ensure_event_registry()


        timestamp = self._now()


        record = {

            "event":

                event,


            "payload":

                payload,


            "timestamp":

                timestamp,

        }


        self._event_history.append(
            record
        )


        if len(
            self._event_history
        ) > 1000:

            self._event_history.pop(
                0
            )



        handlers = self._event_handlers.get(

            event,

            []

        )


        results = []



        for handler in handlers:

            try:

                result = handler(
                    payload
                )


                if inspect.isawaitable(
                    result
                ):

                    result = await result



                results.append(
                    result
                )



            except Exception as exc:

                self.request_failed(
                    exc
                )


        self.event_count += 1


        self.last_event = event


        return results



# ==========================================================
# Lifecycle Hooks
# ==========================================================


    async def before_start(
        self,
    ):
        """
        Before runtime startup.
        """

        return await self.emit_event(

            "before_start",

            {

                "server":

                    self.identity,

                "time":

                    self._now(),

            },

        )



    async def after_start(
        self,
    ):
        """
        After runtime startup.
        """

        return await self.emit_event(

            "after_start",

            {

                "state":

                    self.state,


                "started_at":

                    self.started_at,

            },

        )



    async def before_shutdown(
        self,
    ):
        """
        Before runtime shutdown.
        """

        return await self.emit_event(

            "before_shutdown",

            {

                "state":

                    self.state,


                "time":

                    self._now(),

            },

        )



# ==========================================================
# Request Hooks
# ==========================================================


    async def before_request(
        self,
        request=None,
    ):
        """
        Execute before HTTP request.
        """

        self.request_hook_count += 1


        return await self.emit_event(

            "before_request",

            request,

        )



    async def after_request(
        self,
        request=None,
        response=None,
    ):
        """
        Execute after HTTP request.
        """

        self.response_hook_count += 1


        return await self.emit_event(

            "after_request",

            {

                "request":

                    request,


                "response":

                    response,

            },

        )



# ==========================================================
# WebSocket Hooks
# ==========================================================


    async def websocket_event(
        self,
        event: str,
        client=None,
    ):
        """
        Emit websocket event.
        """

        return await self.emit_event(

            f"websocket.{event}",

            client,

        )



# ==========================================================
# Runtime Event Helpers
# ==========================================================


    async def on_client_connected(
        self,
        client,
    ):
        """
        Client connection hook.
        """

        return await self.emit_event(

            "client_connected",

            client,

        )



    async def on_client_disconnected(
        self,
        client,
    ):
        """
        Client disconnect hook.
        """

        return await self.emit_event(

            "client_disconnected",

            client,

        )



# ==========================================================
# Event Query
# ==========================================================


    def list_events(
        self,
    ) -> list:
        """
        Return event history.
        """

        return self._event_history



    def registered_events(
        self,
    ) -> list:
        """
        Return registered hook names.
        """

        self._ensure_event_registry()


        return list(

            self._event_handlers.keys()

        )



# ==========================================================
# Event Diagnostics
# ==========================================================


    def event_state(
        self,
    ) -> dict:
        """
        Event runtime diagnostics.
        """

        self._ensure_event_registry()


        return {

            "events":

                list(

                    self._event_handlers.keys()

                ),


            "handlers":

                sum(

                    len(v)

                    for v in self._event_handlers.values()

                ),


            "history":

                len(

                    self._event_history

                ),


            "count":

                self.event_count,


            "last_event":

                self.last_event,

        }
# ==========================================================
# Part 10
# Lifecycle Runtime
#
# • start()
# • stop()
# • restart()
# • shutdown()
# • freeze()
# • reopen()
#
# Lifecycle State Machine
#
#              created
#                  │
#                  ▼
#              initialized
#                  │
#                  ▼
#                ready
#                  │
#                  ▼
#               running
#              /       \
#             ▼         ▼
#          stopped    frozen
#             │         │
#             └────┬────┘
#                  ▼
#               closed
#
# ==========================================================


# ==========================================================
# Lifecycle State Foundation
# ==========================================================


    def _ensure_lifecycle_state(
        self,
    ):
        """
        Initialize lifecycle runtime.
        """

        if not hasattr(
            self,
            "lifecycle_state",
        ):

            self.lifecycle_state = "created"



        if not hasattr(
            self,
            "previous_state",
        ):

            self.previous_state = None



        if not hasattr(
            self,
            "frozen",
        ):

            self.frozen = False



# ==========================================================
# State Transition
# ==========================================================


    def transition_to(
        self,
        state: str,
    ):
        """
        Change lifecycle state.
        """

        self._ensure_lifecycle_state()


        self.previous_state = (
            self.lifecycle_state
        )


        self.lifecycle_state = state


        self.state = state


        self.touch()


        return self.lifecycle_state



# ==========================================================
# Start Runtime
# ==========================================================


    async def start(
        self,
    ):
        """
        Start dashboard runtime.
        """

        self._ensure_lifecycle_state()


        if self.closed:

            raise RuntimeError(
                "Cannot start closed runtime"
            )



        if self.running:

            return self



        await self.before_start()



        self.enabled = True


        self.running = True


        self.started_at = (
            self._now()
        )


        self.stopped_at = None



        self.transition_to(
            "running"
        )



        await self.after_start()



        return self



# ==========================================================
# Stop Runtime
# ==========================================================


    async def stop(
        self,
    ):
        """
        Stop runtime execution.
        """

        self._ensure_lifecycle_state()



        if not self.running:

            return self



        self.running = False


        self.stopped_at = (
            self._now()
        )


        self.transition_to(
            "stopped"
        )


        return self



# ==========================================================
# Restart Runtime
# ==========================================================


    async def restart(
        self,
    ):
        """
        Restart runtime.

        stop -> start
        """

        await self.stop()



        await self.start()



        return self



# ==========================================================
# Shutdown Runtime
# ==========================================================


    async def shutdown(
        self,
    ):
        """
        Permanent runtime shutdown.
        """

        self._ensure_lifecycle_state()



        await self.before_shutdown()



        #
        # Stop websocket clients
        #

        if hasattr(

            self,

            "clear_clients",

        ):

            await self.clear_clients()



        #
        # Stop runtime
        #

        self.running = False


        self.enabled = False


        self.closed = True



        self.stopped_at = (
            self._now()
        )



        self.transition_to(
            "closed"
        )


        return self



# ==========================================================
# Freeze Runtime
# ==========================================================


    def freeze(
        self,
    ):
        """
        Freeze runtime.

        Prevent new execution.
        """

        self._ensure_lifecycle_state()


        if self.closed:

            raise RuntimeError(
                "Cannot freeze closed runtime"
            )



        self.frozen = True



        self.transition_to(
            "frozen"
        )


        return self



# ==========================================================
# Reopen Runtime
# ==========================================================


    def reopen(
        self,
    ):
        """
        Reopen frozen/stopped runtime.
        """

        self._ensure_lifecycle_state()


        if self.closed:

            raise RuntimeError(
                "Cannot reopen closed runtime"
            )



        self.frozen = False


        self.enabled = True



        self.transition_to(
            "ready"
        )


        return self



# ==========================================================
# Enable / Disable
# ==========================================================


    def enable(
        self,
    ):
        """
        Enable runtime.
        """

        self.enabled = True


        if self.state == "disabled":

            self.transition_to(
                "ready"
            )


        return self



    def disable(
        self,
    ):
        """
        Disable runtime.
        """

        self.enabled = False


        self.transition_to(
            "disabled"
        )


        return self



# ==========================================================
# Lifecycle Queries
# ==========================================================


    def is_running(
        self,
    ) -> bool:
        """
        Check running state.
        """

        return (

            self.running

            and

            not self.closed

        )



    def is_ready(
        self,
    ) -> bool:
        """
        Check ready state.
        """

        return self.state in (

            "ready",

            "running",

        )



    def is_frozen(
        self,
    ) -> bool:
        """
        Check frozen state.
        """

        return self.frozen



    def is_closed(
        self,
    ) -> bool:
        """
        Check closed state.
        """

        return self.closed



# ==========================================================
# Lifecycle Snapshot
# ==========================================================


    def lifecycle_snapshot(
        self,
    ) -> dict:
        """
        Export lifecycle state.
        """

        return {

            "state":

                self.state,


            "previous_state":

                self.previous_state,


            "running":

                self.running,


            "enabled":

                self.enabled,


            "frozen":

                self.frozen,


            "closed":

                self.closed,


            "started_at":

                self.started_at,


            "stopped_at":

                self.stopped_at,


            "uptime":

                self.uptime,

        }



# ==========================================================
# Lifecycle Diagnostics
# ==========================================================


    def lifecycle_diagnostics(
        self,
    ) -> dict:
        """
        Full lifecycle diagnostics.
        """

        return {

            "lifecycle":

                self.lifecycle_snapshot(),


            "runtime":

                {

                    "name":

                        self.name,


                    "version":

                        self.version,


                    "revision":

                        self.revision,

                },



            "health":

                self.health(),

        }
# ==========================================================
# Part 11
# Python Protocols
#
# • __repr__
# • __str__
# • __len__
# • __iter__
# • __contains__
# • __getitem__
# • __call__
# • __copy__
# • __deepcopy__
#
# SciOS-NG Runtime Object Protocol Layer
#
# DashboardWebServer behaves as:
#
#   Object
#      |
#      ├── Printable
#      ├── Iterable
#      ├── Container
#      ├── Mapping-like
#      ├── Callable Runtime
#      └── Cloneable
#
# ==========================================================


# ==========================================================
# __repr__
# ==========================================================


    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.

        Example:

        DashboardWebServer(
            name='SciOS Dashboard Web',
            state='running'
        )
        """

        return (

            f"{self.__class__.__name__}("

            f"id='{self.id}', "

            f"name='{self.name}', "

            f"state='{self.state}', "

            f"running={self.running}, "

            f"closed={self.closed}"

            ")"

        )



# ==========================================================
# __str__
# ==========================================================


    def __str__(
        self,
    ) -> str:
        """
        Human readable representation.
        """

        return (

            f"{self.name} "

            f"[{self.state}]"

        )



# ==========================================================
# __len__
# ==========================================================


    def __len__(
        self,
    ) -> int:
        """
        Return runtime resource size.

        Includes:

        - clients
        - routes
        - middleware
        - events
        """

        size = 0


        #
        # websocket clients
        #

        if hasattr(

            self,

            "_websocket_clients",

        ):

            size += len(

                self._websocket_clients

            )



        #
        # routes
        #

        if hasattr(

            self,

            "request_routes",

        ):

            size += len(

                self.request_routes

            )



        #
        # middleware
        #

        if hasattr(

            self,

            "_middlewares",

        ):

            size += len(

                self._middlewares

            )



        return size



# ==========================================================
# __iter__
# ==========================================================


    def __iter__(
        self,
    ):
        """
        Iterate runtime components.

        Example:

        for item in server:
            ...
        """

        yield from (

            {

                "identity":

                    self.identity,

            },


            {

                "state":

                    self.state,

            },


            {

                "runtime":

                    self.runtime_snapshot(),

            },


            {

                "websocket":

                    self.websocket_state()

            },


            {

                "middleware":

                    self.middleware_state()

            },


        )



# ==========================================================
# __contains__
# ==========================================================


    def __contains__(
        self,
        item,
    ) -> bool:
        """
        Check runtime capability.

        Examples:

        "websocket" in server

        "auth" in server
        """

        capabilities = {

            "websocket":

                hasattr(

                    self,

                    "websocket_endpoint",

                ),


            "router":

                hasattr(

                    self,

                    "router",

                ),


            "middleware":

                hasattr(

                    self,

                    "_middlewares",

                ),


            "auth":

                hasattr(

                    self,

                    "auth",

                ),


            "static":

                hasattr(

                    self,

                    "static_config",

                ),


            "events":

                hasattr(

                    self,

                    "_event_handlers",

                ),

        }


        return capabilities.get(

            item,

            False,

        )



# ==========================================================
# __getitem__
# ==========================================================


    def __getitem__(
        self,
        key,
    ):
        """
        Dictionary-like access.

        Example:

        server["state"]

        server["config"]

        server["health"]
        """

        mapping = {

            "identity":

                self.identity,


            "metadata":

                self.metadata(),


            "state":

                self.state,


            "config":

                self.configuration_state(),


            "health":

                self.health(),


            "diagnostics":

                self.diagnostics(),


            "runtime":

                self.runtime_snapshot(),


            "websocket":

                self.websocket_snapshot(),


            "auth":

                self.auth_state(),


            "static":

                self.static_state(),


            "events":

                self.event_state(),

        }


        if key not in mapping:

            raise KeyError(

                f"Unknown runtime key: {key}"

            )


        return mapping[key]



# ==========================================================
# __call__
# ==========================================================


    async def __call__(
        self,
        action=None,
        **kwargs,
    ):
        """
        Runtime callable interface.

        Examples:

        await server()

        await server("start")

        await server("health")
        """

        if action is None:

            return self.runtime_snapshot()



        if action == "start":

            return await self.start()



        if action == "stop":

            return await self.stop()



        if action == "restart":

            return await self.restart()



        if action == "shutdown":

            return await self.shutdown()



        if action == "freeze":

            return self.freeze()



        if action == "reopen":

            return self.reopen()



        if action == "health":

            return self.health()



        if action == "diagnostics":

            return self.diagnostics()



        raise ValueError(

            f"Unknown runtime action: {action}"

        )



# ==========================================================
# __copy__
# ==========================================================


    def __copy__(
        self,
    ):
        """
        Shallow copy.

        Keeps:
            - viewer reference
            - app reference
        """

        import copy


        cls = self.__class__


        new = cls.__new__(
            cls
        )


        new.__dict__.update(

            self.__dict__

        )


        return new



# ==========================================================
# __deepcopy__
# ==========================================================


    def __deepcopy__(
        self,
        memo,
    ):
        """
        Deep copy runtime.

        Excludes external resources:

        - FastAPI app
        - websocket connections
        - viewer socket
        """

        import copy


        cls = self.__class__


        new = cls.__new__(
            cls
        )


        memo[id(self)] = new



        for key, value in self.__dict__.items():


            if key in (

                "app",

                "router",

                "viewer",

                "_websocket_clients",

            ):

                setattr(

                    new,

                    key,

                    value,

                )


            else:

                setattr(

                    new,

                    key,

                    copy.deepcopy(

                        value,

                        memo,

                    ),

                )



        return new
# ==========================================================
# Part 12
# Diagnostics & Serialization
#
# • to_dict()
# • to_json()
# • from_dict()
# • snapshot()
# • restore()
# • clone()
# • copy()
# • export()
#
# Serialization Architecture
#
# DashboardWebServer
#          │
#          ▼
#   Runtime State
#          │
# ┌────────┼─────────┐
# ▼        ▼         ▼
# dict     JSON    snapshot
#          │
#          ▼
#    Persistence
#          │
#          ▼
#      Restore
#
# ==========================================================


import json
import copy as _copy



# ==========================================================
# to_dict()
# ==========================================================


    def to_dict(
        self,
        *,
        include_runtime: bool = True,
        include_diagnostics: bool = True,
    ) -> dict:
        """
        Serialize DashboardWebServer
        into dictionary.

        Safe serialization:
            - no socket objects
            - no FastAPI app object
            - no callbacks
        """

        data = {

            "identity":

                self.identity,


            "metadata":

                self.metadata(),


            "state":

                {

                    "state":

                        self.state,


                    "previous_state":

                        getattr(

                            self,

                            "previous_state",

                            None,

                        ),


                    "running":

                        self.running,


                    "enabled":

                        self.enabled,


                    "frozen":

                        getattr(

                            self,

                            "frozen",

                            False,

                        ),


                    "closed":

                        self.closed,

                },



            "config":

                self.configuration_state(),

        }



        if include_runtime:

            data["runtime"] = {

                "uptime":

                    self.uptime,


                "started_at":

                    self.started_at,


                "stopped_at":

                    self.stopped_at,


                "revision":

                    self.revision,

            }



        if include_diagnostics:

            data["diagnostics"] = {

                "health":

                    self.health(),


                "statistics":

                    self.runtime_snapshot(),

            }



        return data



# ==========================================================
# to_json()
# ==========================================================


    def to_json(
        self,
        *,
        indent: int = 2,
    ) -> str:
        """
        Serialize runtime into JSON.
        """

        return json.dumps(

            self.to_dict(),

            indent=indent,

            default=str,

        )



# ==========================================================
# from_dict()
# ==========================================================


    def from_dict(
        self,
        data: dict,
    ):
        """
        Restore configuration/state
        from dictionary.

        Existing runtime identity
        is preserved.
        """

        if not data:

            return self



        #
        # State
        #

        state = data.get(
            "state",
            {},
        )


        if "state" in state:

            self.state = state["state"]



        if "previous_state" in state:

            self.previous_state = (

                state["previous_state"]

            )



        self.running = state.get(

            "running",

            self.running,

        )


        self.enabled = state.get(

            "enabled",

            self.enabled,

        )


        self.frozen = state.get(

            "frozen",

            getattr(

                self,

                "frozen",

                False,

            ),

        )


        self.closed = state.get(

            "closed",

            self.closed,

        )



        #
        # Config
        #

        config = data.get(

            "config",

            {},

        )


        if config:

            self.update_config(

                **config

            )



        self.touch()


        return self



# ==========================================================
# snapshot()
# ==========================================================


    def snapshot(
        self,
    ) -> dict:
        """
        Create complete runtime snapshot.

        Used for:
            - backup
            - recovery
            - migration
        """

        return {

            "version":

                self.version,


            "created_at":

                self.created_at,


            "server":

                self.to_dict(),


            "websocket":

                self.websocket_snapshot(),


            "middleware":

                self.middleware_state(),


            "auth":

                self.auth_state(),


            "static":

                self.static_state(),


            "events":

                self.event_state(),


            "lifecycle":

                self.lifecycle_snapshot(),


            "timestamp":

                self._now(),

        }



# ==========================================================
# restore()
# ==========================================================


    def restore(
        self,
        snapshot: dict,
    ):
        """
        Restore runtime snapshot.

        External resources are not restored:

            - websocket clients
            - FastAPI app
            - sockets
        """

        if not snapshot:

            return self



        server_data = snapshot.get(

            "server",

            {},

        )


        self.from_dict(

            server_data

        )



        #
        # Restore lifecycle
        #

        lifecycle = snapshot.get(

            "lifecycle",

            {},

        )


        self.state = lifecycle.get(

            "state",

            self.state,

        )


        self.running = lifecycle.get(

            "running",

            False,

        )


        self.enabled = lifecycle.get(

            "enabled",

            True,

        )


        self.frozen = lifecycle.get(

            "frozen",

            False,

        )


        self.closed = lifecycle.get(

            "closed",

            False,

        )



        self.touch()


        return self



# ==========================================================
# clone()
# ==========================================================


    def clone(
        self,
        *,
        deep: bool = True,
    ):
        """
        Create runtime clone.
        """

        if deep:

            return self.__deepcopy__(

                {}

            )


        return self.__copy__()



# ==========================================================
# copy()
# ==========================================================


    def copy(
        self,
    ):
        """
        Public copy API.
        """

        return self.clone(

            deep=False

        )



# ==========================================================
# export()
# ==========================================================


    def export(
        self,
        path: str | None = None,
        *,
        format: str = "json",
    ):
        """
        Export runtime state.

        Supported:

            json
            dict
        """

        if format == "dict":

            result = self.snapshot()



        elif format == "json":

            result = json.dumps(

                self.snapshot(),

                indent=2,

                default=str,

            )



        else:

            raise ValueError(

                f"Unsupported export format: {format}"

            )



        if path:

            with open(

                path,

                "w",

                encoding="utf-8",

            ) as f:


                if isinstance(

                    result,

                    str,

                ):

                    f.write(

                        result

                    )


                else:

                    json.dump(

                        result,

                        f,

                        indent=2,

                        default=str,

                    )



        return result



# ==========================================================
# Import Helper
# ==========================================================


    @classmethod
    def load(
        cls,
        data: dict,
    ):
        """
        Create server from snapshot.
        """

        server = cls()


        server.restore(

            data

        )


        return server



# ==========================================================
# Serialization Diagnostics
# ==========================================================


    def serialization_state(
        self,
    ) -> dict:
        """
        Serialization diagnostics.
        """

        return {

            "identity":

                self.id,


            "version":

                self.version,


            "revision":

                self.revision,


            "snapshot_size":

                len(

                    json.dumps(

                        self.snapshot(),

                        default=str,

                    )

                ),


            "export_supported":

                [

                    "dict",

                    "json",

                ],

        }                                                                                                                                                                                                                                                                                                                                                                                        