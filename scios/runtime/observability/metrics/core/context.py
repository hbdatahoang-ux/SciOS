"""
SciOS-NG Observability
======================

Metric Context
--------------

Foundation module providing the runtime execution context for metrics.

`MetricContext` captures the metadata describing *where* and *under what
conditions* a metric was produced. It is intentionally independent from
Metric, Labels, Attributes and Snapshot so that it can be reused by the
entire observability stack.

Typical information stored inside a MetricContext includes

- Service information
- Runtime information
- Host information
- Environment
- Process / Thread
- Request identifiers
- Distributed tracing identifiers
- Custom metadata

Design Goals
------------

- Production-ready
- Thread-safe
- Immutable-aware
- Serializable
- OpenTelemetry compatible
- Snapshot friendly
- Namespace aware
- Zero external dependencies

SciOS-NG
Copyright (c) SciOS Project
"""

from __future__ import annotations

import copy
import json
import os
import platform
import socket
import threading
import time
import uuid

from collections.abc import (
    Iterator,
    Mapping,
    MutableMapping,
)
from threading import RLock
from typing import (
    Any,
    Final,
    TypeAlias,
)

from .exceptions import (
    MetricFrozenError,
)

from .validation import (
    MetricValidator,
)

# ==========================================================
# Constants
# ==========================================================

DEFAULT_NAMESPACE: Final[str] = "default"

DEFAULT_SERVICE_NAME: Final[str] = "scios"

DEFAULT_SERVICE_VERSION: Final[str] = "0.1.0"

UNKNOWN: Final[str] = "unknown"

MAX_CONTEXT_SIZE: Final[int] = 4096

DEFAULT_ENCODING: Final[str] = "utf-8"

CURRENT_SCHEMA_VERSION: Final[int] = 1

# ==========================================================
# Type aliases
# ==========================================================

ContextValue: TypeAlias = (
    str
    | int
    | float
    | bool
    | None
)

ContextMapping: TypeAlias = dict[
    str,
    Any,
]

ReadonlyContext: TypeAlias = Mapping[
    str,
    Any,
]

JSONType: TypeAlias = dict[
    str,
    Any,
]

# ==========================================================
# Helper functions
# ==========================================================


def _utc_timestamp() -> float:
    """
    Return current UTC timestamp.
    """

    return time.time()


def _generate_uuid() -> str:
    """
    Generate UUID4 string.
    """

    return str(uuid.uuid4())


def _hostname() -> str:
    """
    Current hostname.
    """

    try:
        return socket.gethostname()
    except Exception:
        return UNKNOWN


def _platform_name() -> str:
    """
    Current operating system.
    """

    try:
        return platform.system()
    except Exception:
        return UNKNOWN


def _python_version() -> str:
    """
    Running Python version.
    """

    try:
        return platform.python_version()
    except Exception:
        return UNKNOWN


def _process_id() -> int:
    """
    Current process id.
    """

    try:
        return os.getpid()
    except Exception:
        return -1


def _thread_id() -> int:
    """
    Current thread id.
    """

    try:
        return threading.get_ident()
    except Exception:
        return -1


def _deepcopy_mapping(
    value: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Safe deep copy for mappings.
    """

    return copy.deepcopy(dict(value))


def _ensure_mapping(
    value: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """
    Normalize mapping input.
    """

    if value is None:
        return {}

    MetricValidator.validate_mapping(value)

    return dict(value)


# ==========================================================
# MetricContext
# ==========================================================


class MetricContext(MutableMapping[str, Any]):
    """
    Production runtime metric context.

    MetricContext stores execution metadata describing the
    environment in which a metric was generated.

    Example
    -------

    >>> ctx = MetricContext(
    ...     service_name="SciOS",
    ...     namespace="kernel",
    ... )

    >>> ctx["request_id"] = "abc"

    >>> ctx["trace_id"] = "xyz"

    The context object is designed to be

    - thread-safe
    - snapshot friendly
    - immutable-aware
    - serialization friendly
    - OpenTelemetry compatible
    """

    __slots__ = (
        "_lock",
        "_data",
        "_namespace",
        "_uuid",
        "_created_at",
        "_version",
        "_frozen",
    )
# ==========================================================
# Construction API
# ==========================================================

    def __init__(
        self,
        *,
        namespace: str = DEFAULT_NAMESPACE,
        service_name: str = DEFAULT_SERVICE_NAME,
        service_version: str = DEFAULT_SERVICE_VERSION,
        version: int = CURRENT_SCHEMA_VERSION,
        data: Mapping[str, Any] | None = None,
        frozen: bool = False,
    ) -> None:
        """
        Create a MetricContext.

        Parameters
        ----------
        namespace:
            Logical namespace.

        service_name:
            Service producing the metric.

        service_version:
            Service version.

        version:
            Schema version.

        data:
            Optional runtime metadata.

        frozen:
            Whether the context starts immutable.
        """

        MetricValidator.validate_string(
            namespace,
            name="namespace",
        )

        MetricValidator.validate_string(
            service_name,
            name="service_name",
        )

        MetricValidator.validate_string(
            service_version,
            name="service_version",
        )

        self._lock = RLock()

        self._uuid = _generate_uuid()

        self._created_at = _utc_timestamp()

        self._version = int(version)

        self._namespace = namespace

        self._frozen = bool(frozen)

        self._data: dict[str, Any] = _ensure_mapping(
            data,
        )

        # --------------------------------------------------
        # Standard runtime fields
        # --------------------------------------------------

        self._data.setdefault(
            "service.name",
            service_name,
        )

        self._data.setdefault(
            "service.version",
            service_version,
        )

        self._data.setdefault(
            "host.name",
            _hostname(),
        )

        self._data.setdefault(
            "os.name",
            _platform_name(),
        )

        self._data.setdefault(
            "python.version",
            _python_version(),
        )

        self._data.setdefault(
            "process.pid",
            _process_id(),
        )

        self._data.setdefault(
            "thread.id",
            _thread_id(),
        )

        self._data.setdefault(
            "context.uuid",
            self._uuid,
        )

        self._data.setdefault(
            "context.created_at",
            self._created_at,
        )

        self._data.setdefault(
            "context.version",
            self._version,
        )

        self._data.setdefault(
            "context.namespace",
            self._namespace,
        )

        MetricValidator.validate_mapping(
            self._data,
        )

    # =====================================================
    # Factory Methods
    # =====================================================

    @classmethod
    def empty(
        cls,
    ) -> "MetricContext":
        """
        Create an empty context.
        """

        return cls()

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "MetricContext":
        """
        Construct from dictionary.
        """

        MetricValidator.validate_mapping(
            data,
        )

        namespace = data.get(
            "context.namespace",
            DEFAULT_NAMESPACE,
        )

        version = data.get(
            "context.version",
            CURRENT_SCHEMA_VERSION,
        )

        service_name = data.get(
            "service.name",
            DEFAULT_SERVICE_NAME,
        )

        service_version = data.get(
            "service.version",
            DEFAULT_SERVICE_VERSION,
        )

        return cls(
            namespace=namespace,
            service_name=service_name,
            service_version=service_version,
            version=version,
            data=data,
        )

    @classmethod
    def from_environment(
        cls,
    ) -> "MetricContext":
        """
        Build a context using the current OS environment.
        """

        env: dict[str, Any] = {
            "host.name": _hostname(),
            "os.name": _platform_name(),
            "python.version": _python_version(),
            "process.pid": _process_id(),
            "thread.id": _thread_id(),
            "user.name": os.getenv(
                "USERNAME",
                UNKNOWN,
            ),
            "user.home": os.path.expanduser(
                "~",
            ),
        }

        return cls(
            data=env,
        )

    @classmethod
    def from_runtime(
        cls,
        runtime: Mapping[str, Any],
    ) -> "MetricContext":
        """
        Create a MetricContext from a runtime dictionary.

        Examples
        --------
        {
            "runtime.name": "SciOS",
            "runtime.version": "0.5",
            "device": "GPU0"
        }
        """

        MetricValidator.validate_mapping(
            runtime,
        )

        return cls(
            data=runtime,
        )

    # =====================================================
    # Validation Helpers
    # =====================================================

    @staticmethod
    def validate(
        data: Mapping[str, Any],
    ) -> None:
        """
        Validate context mapping.
        """

        MetricValidator.validate_mapping(
            data,
        )

    @staticmethod
    def is_valid(
        data: Mapping[str, Any],
    ) -> bool:
        """
        Safe validation.
        """

        try:
            MetricValidator.validate_mapping(
                data,
            )
            return True

        except Exception:
            return False

    # =====================================================
    # Internal Storage
    # =====================================================

    @property
    def storage(
        self,
    ) -> Mapping[str, Any]:
        """
        Read-only storage.
        """

        return self._data

    @property
    def namespace(
        self,
    ) -> str:
        """
        Context namespace.
        """

        return self._namespace

    @property
    def service_name(
        self,
    ) -> str:
        """
        Service name.
        """

        return self._data.get(
            "service.name",
            DEFAULT_SERVICE_NAME,
        )

    @property
    def service_version(
        self,
    ) -> str:
        """
        Service version.
        """

        return self._data.get(
            "service.version",
            DEFAULT_SERVICE_VERSION,
        )

    @property
    def version(
        self,
    ) -> int:
        """
        Context schema version.
        """

        return self._version

    @property
    def uuid(
        self,
    ) -> str:
        """
        Context UUID.
        """

        return self._uuid

    @property
    def created_at(
        self,
    ) -> float:
        """
        Creation timestamp.
        """

        return self._created_at

    @property
    def frozen(
        self,
    ) -> bool:
        """
        Frozen state.
        """

        return self._frozen
# ==========================================================
# Context Properties
# ==========================================================

@property
def service_name(self) -> str:
    """Service name."""
    return self._data.get(
        "service.name",
        DEFAULT_SERVICE_NAME,
    )


@property
def service_version(self) -> str:
    """Service version."""
    return self._data.get(
        "service.version",
        DEFAULT_SERVICE_VERSION,
    )


@property
def namespace(self) -> str:
    """Logical namespace."""
    return self._namespace


@property
def environment(self) -> str:
    """Deployment environment."""
    return self._data.get(
        "deployment.environment",
        UNKNOWN,
    )


@property
def instance_id(self) -> str:
    """Service instance identifier."""
    return self._data.get(
        "service.instance.id",
        "",
    )


@property
def host(self) -> str:
    """Hostname."""
    return self._data.get(
        "host.name",
        "",
    )


@property
def pid(self) -> int:
    """Process identifier."""
    return int(
        self._data.get(
            "process.pid",
            0,
        )
    )


@property
def thread_id(self) -> int:
    """Thread identifier."""
    return int(
        self._data.get(
            "thread.id",
            0,
        )
    )


@property
def process_name(self) -> str:
    """Current process name."""
    return self._data.get(
        "process.name",
        "",
    )


@property
def runtime(self) -> str:
    """Runtime implementation."""
    return self._data.get(
        "runtime.name",
        "Python",
    )


@property
def language(self) -> str:
    """Programming language."""
    return self._data.get(
        "runtime.language",
        "python",
    )


@property
def platform(self) -> str:
    """Operating platform."""
    return self._data.get(
        "os.name",
        "",
    )


@property
def region(self) -> str:
    """Cloud or deployment region."""
    return self._data.get(
        "cloud.region",
        "",
    )


@property
def zone(self) -> str:
    """Availability zone."""
    return self._data.get(
        "cloud.zone",
        "",
    )


@property
def node(self) -> str:
    """Node identifier."""
    return self._data.get(
        "node.name",
        "",
    )


@property
def cluster(self) -> str:
    """Cluster identifier."""
    return self._data.get(
        "cluster.name",
        "",
    )


@property
def tenant(self) -> str:
    """Tenant identifier."""
    return self._data.get(
        "tenant.id",
        "",
    )


@property
def session_id(self) -> str:
    """Current session."""
    return self._data.get(
        "session.id",
        "",
    )


@property
def request_id(self) -> str:
    """Current request identifier."""
    return self._data.get(
        "request.id",
        "",
    )


@property
def trace_id(self) -> str:
    """Distributed trace identifier."""
    return self._data.get(
        "trace.id",
        "",
    )


@property
def span_id(self) -> str:
    """Current span identifier."""
    return self._data.get(
        "span.id",
        "",
    )


@property
def parent_span_id(self) -> str:
    """Parent span identifier."""
    return self._data.get(
        "span.parent.id",
        "",
    )


@property
def uuid(self) -> str:
    """Context UUID."""
    return self._uuid


@property
def version(self) -> int:
    """Schema version."""
    return self._version


@property
def created_at(self) -> float:
    """Creation timestamp."""
    return self._created_at


@property
def frozen(self) -> bool:
    """Frozen state."""
    return self._frozen
# ==========================================================
# CRUD API
# ==========================================================

def set(
    self,
    key: str,
    value: Any,
) -> None:
    """
    Set a context value.
    """

    with self._lock:

        self._require_mutable()

        MetricValidator.validate_attribute_key(key)
        MetricValidator.validate_attribute_value(value)

        self._data[key] = value


def get(
    self,
    key: str,
    default: Any = None,
) -> Any:
    """
    Get a context value.
    """

    return self._data.get(
        key,
        default,
    )


def update(
    self,
    values: Mapping[str, Any],
) -> None:
    """
    Bulk update.
    """

    with self._lock:

        self._require_mutable()

        for key, value in values.items():

            MetricValidator.validate_attribute_key(key)
            MetricValidator.validate_attribute_value(value)

        self._data.update(values)


def pop(
    self,
    key: str,
    default: Any = None,
) -> Any:
    """
    Remove and return a value.
    """

    with self._lock:

        self._require_mutable()

        return self._data.pop(
            key,
            default,
        )


def remove(
    self,
    key: str,
) -> bool:
    """
    Remove a key.

    Returns
    -------
    bool
        True if removed.
    """

    with self._lock:

        self._require_mutable()

        return (
            self._data.pop(
                key,
                None,
            )
            is not None
        )


def clear(
    self,
) -> None:
    """
    Remove every context entry.
    """

    with self._lock:

        self._require_mutable()

        self._data.clear()


def setdefault(
    self,
    key: str,
    default: Any = None,
) -> Any:
    """
    Dictionary-compatible setdefault.
    """

    with self._lock:

        self._require_mutable()

        MetricValidator.validate_attribute_key(key)

        if default is not None:
            MetricValidator.validate_attribute_value(
                default
            )

        return self._data.setdefault(
            key,
            default,
        )


def replace(
    self,
    values: Mapping[str, Any],
) -> None:
    """
    Replace the entire context.
    """

    with self._lock:

        self._require_mutable()

        for key, value in values.items():

            MetricValidator.validate_attribute_key(key)
            MetricValidator.validate_attribute_value(value)

        self._data.clear()

        self._data.update(values)


def rename(
    self,
    old_key: str,
    new_key: str,
) -> bool:
    """
    Rename a context key.
    """

    with self._lock:

        self._require_mutable()

        if old_key not in self._data:
            return False

        MetricValidator.validate_attribute_key(
            new_key
        )

        value = self._data.pop(
            old_key
        )

        self._data[new_key] = value

        return True


def move(
    self,
    old_key: str,
    new_key: str,
) -> bool:
    """
    Move a value to another key.

    Equivalent to rename().
    """

    return self.rename(
        old_key,
        new_key,
    )
# ==========================================================
# Freeze / Snapshot API
# ==========================================================

def freeze(
    self,
) -> None:
    """
    Freeze this context.

    Frozen contexts become immutable until
    :meth:`unfreeze` is called.
    """

    with self._lock:

        self._frozen = True


def unfreeze(
    self,
) -> None:
    """
    Unfreeze this context.
    """

    with self._lock:

        self._frozen = False


def snapshot(
    self,
) -> dict[str, Any]:
    """
    Return an immutable snapshot.

    Returns
    -------
    dict
        Deep copy of the internal storage.
    """

    with self._lock:

        return copy.deepcopy(
            self._data
        )


def restore(
    self,
    snapshot: Mapping[str, Any],
) -> None:
    """
    Restore from a snapshot.
    """

    with self._lock:

        self._require_mutable()

        MetricValidator.validate_mapping(
            snapshot
        )

        self._data.clear()

        self._data.update(
            copy.deepcopy(snapshot)
        )


def copy(
    self,
) -> "MetricContext":
    """
    Create a shallow logical copy.

    Runtime metadata is preserved.
    """

    with self._lock:

        ctx = self.__class__(
            namespace=self._namespace,
            service_name=self.service_name,
            service_version=self.service_version,
            version=self._version,
            data=self.snapshot(),
            frozen=self._frozen,
        )

        return ctx


def clone(
    self,
) -> "MetricContext":
    """
    Create a deep clone.

    Equivalent to copy() for immutable
    values but future-proof for complex
    nested objects.
    """

    return copy.deepcopy(
        self.copy()
    )


def merge(
    self,
    other: Mapping[str, Any],
    *,
    overwrite: bool = True,
) -> "MetricContext":
    """
    Merge into a new MetricContext.

    Parameters
    ----------
    other:
        Context values.

    overwrite:
        Existing keys are replaced if True.
    """

    MetricValidator.validate_mapping(
        other
    )

    ctx = self.copy()

    for key, value in other.items():

        if overwrite or key not in ctx._data:

            ctx._data[key] = copy.deepcopy(
                value
            )

    return ctx


def merge_inplace(
    self,
    other: Mapping[str, Any],
    *,
    overwrite: bool = True,
) -> None:
    """
    Merge directly into this context.
    """

    with self._lock:

        self._require_mutable()

        MetricValidator.validate_mapping(
            other
        )

        for key, value in other.items():

            if overwrite or key not in self._data:

                self._data[key] = copy.deepcopy(
                    value
                )
# ==========================================================
# Serialization API
# ==========================================================

def to_dict(
    self,
) -> dict[str, Any]:
    """
    Serialize the context to a dictionary.
    """

    with self._lock:

        return {
            "namespace": self._namespace,
            "service_name": self.service_name,
            "service_version": self.service_version,
            "version": self._version,
            "uuid": self._uuid,
            "created_at": self._created_at,
            "frozen": self._frozen,
            "data": copy.deepcopy(
                self._data
            ),
        }


@classmethod
def from_dict(
    cls,
    data: Mapping[str, Any],
) -> "MetricContext":
    """
    Deserialize from a dictionary.
    """

    MetricValidator.validate_mapping(
        data,
    )

    ctx = cls(
        namespace=data.get(
            "namespace",
            DEFAULT_NAMESPACE,
        ),
        service_name=data.get(
            "service_name",
            DEFAULT_SERVICE_NAME,
        ),
        service_version=data.get(
            "service_version",
            DEFAULT_SERVICE_VERSION,
        ),
        version=data.get(
            "version",
            CURRENT_SCHEMA_VERSION,
        ),
        data=data.get(
            "data",
            {},
        ),
        frozen=data.get(
            "frozen",
            False,
        ),
    )

    ctx._uuid = data.get(
        "uuid",
        _generate_uuid(),
    )

    ctx._created_at = data.get(
        "created_at",
        _utc_timestamp(),
    )

    return ctx


def to_json(
    self,
    *,
    indent: int | None = None,
    sort_keys: bool = True,
) -> str:
    """
    Serialize the context to JSON.
    """

    return json.dumps(
        self.to_dict(),
        indent=indent,
        sort_keys=sort_keys,
        ensure_ascii=False,
        default=str,
    )


@classmethod
def from_json(
    cls,
    text: str,
) -> "MetricContext":
    """
    Deserialize from JSON.
    """

    payload = json.loads(
        text,
    )

    return cls.from_dict(
        payload,
    )


def to_bytes(
    self,
    *,
    encoding: str = DEFAULT_ENCODING,
) -> bytes:
    """
    Serialize to UTF-8 bytes.
    """

    return self.to_json().encode(
        encoding,
    )


@classmethod
def from_bytes(
    cls,
    payload: bytes,
    *,
    encoding: str = DEFAULT_ENCODING,
) -> "MetricContext":
    """
    Deserialize from bytes.
    """

    return cls.from_json(
        payload.decode(
            encoding,
        )
    )


# ==========================================================
# Pickle Support
# ==========================================================

def __getstate__(
    self,
):
    """
    Support pickle serialization.

    Locks cannot be pickled, so they are
    intentionally omitted.
    """

    state = self.to_dict()

    return state


def __setstate__(
    self,
    state,
):
    """
    Restore from pickle.
    """

    self._lock = RLock()

    self._namespace = state["namespace"]

    self._version = state["version"]

    self._uuid = state["uuid"]

    self._created_at = state["created_at"]

    self._frozen = state["frozen"]

    self._data = copy.deepcopy(
        state["data"]
    )
# ==========================================================
# Context Propagation API
# ==========================================================

# ----------------------------------------------------------
# OpenTelemetry-style Context
# ----------------------------------------------------------

def inject(
    self,
    carrier: dict[str, str],
) -> dict[str, str]:
    """
    Inject this context into a carrier.

    Parameters
    ----------
    carrier
        Mutable carrier (HTTP headers, RPC metadata, etc.)

    Returns
    -------
    dict
    """

    carrier["trace-id"] = self.trace_id

    carrier["span-id"] = self.span_id

    carrier["parent-span-id"] = self.parent_span_id

    carrier["request-id"] = self.request_id

    carrier["session-id"] = self.session_id

    return carrier


@classmethod
def extract(
    cls,
    carrier: Mapping[str, str],
) -> "MetricContext":
    """
    Extract context from a carrier.
    """

    ctx = cls()

    ctx.set(
        "trace.id",
        carrier.get(
            "trace-id",
            "",
        ),
    )

    ctx.set(
        "span.id",
        carrier.get(
            "span-id",
            "",
        ),
    )

    ctx.set(
        "span.parent.id",
        carrier.get(
            "parent-span-id",
            "",
        ),
    )

    ctx.set(
        "request.id",
        carrier.get(
            "request-id",
            "",
        ),
    )

    ctx.set(
        "session.id",
        carrier.get(
            "session-id",
            "",
        ),
    )

    return ctx


# ----------------------------------------------------------
# Baggage
# ----------------------------------------------------------

def baggage(
    self,
) -> dict[str, Any]:
    """
    Return baggage entries.
    """

    return {

        k: v

        for k, v in self._data.items()

        if k.startswith(
            "baggage."
        )

    }


def set_baggage(
    self,
    key: str,
    value: Any,
) -> None:

    self.set(
        f"baggage.{key}",
        value,
    )


def get_baggage(
    self,
    key: str,
    default=None,
):

    return self.get(
        f"baggage.{key}",
        default,
    )


def clear_baggage(
    self,
) -> None:

    keys = [

        k

        for k in self._data

        if k.startswith(
            "baggage."
        )

    ]

    for key in keys:

        self.remove(
            key
        )


# ----------------------------------------------------------
# Trace Propagation
# ----------------------------------------------------------

def new_trace(
    self,
) -> None:
    """
    Create a new trace.
    """

    self.set(
        "trace.id",
        _generate_uuid(),
    )

    self.set(
        "span.id",
        _generate_uuid(),
    )

    self.set(
        "span.parent.id",
        "",
    )


def child_span(
    self,
) -> None:
    """
    Advance to a child span.
    """

    parent = self.span_id

    self.set(
        "span.parent.id",
        parent,
    )

    self.set(
        "span.id",
        _generate_uuid(),
    )


# ----------------------------------------------------------
# Correlation
# ----------------------------------------------------------

def correlation_id(
    self,
) -> str:
    """
    Unified correlation identifier.
    """

    return (

        self.request_id

        or self.trace_id

        or self.session_id

    )


def correlation(
    self,
) -> dict[str, str]:

    return {

        "trace_id":
            self.trace_id,

        "span_id":
            self.span_id,

        "request_id":
            self.request_id,

        "session_id":
            self.session_id,

    }


# ----------------------------------------------------------
# Request Context
# ----------------------------------------------------------

def begin_request(
    self,
    request_id: str | None = None,
):

    self.set(

        "request.id",

        request_id

        or _generate_uuid(),

    )


def end_request(
    self,
):

    self.remove(
        "request.id"
    )


# ----------------------------------------------------------
# Task Context
# ----------------------------------------------------------

def begin_task(
    self,
    task_id: str,
):

    self.set(
        "task.id",
        task_id,
    )


def end_task(
    self,
):

    self.remove(
        "task.id",
    )


# ----------------------------------------------------------
# Async Context
# ----------------------------------------------------------

def fork(
    self,
) -> "MetricContext":
    """
    Copy context for async execution.
    """

    ctx = self.copy()

    ctx.child_span()

    return ctx


def attach(
    self,
    other: "MetricContext",
):

    self.merge_inplace(
        other.snapshot()
    )


def detach(
    self,
):

    self.clear()
# ==========================================================
# Debug Helpers
# ==========================================================

def __bool__(
    self,
) -> bool:
    """
    Context is truthy when it contains
    meaningful runtime information.
    """

    return bool(
        self._data
    )
def __str__(
    self,
) -> str:
    """
    Human readable representation.
    """

    return (
        f"MetricContext("
        f"service={self.service_name}, "
        f"namespace={self.namespace}, "
        f"trace={self.trace_id}, "
        f"keys={len(self._data)}"
        f")"
    )
def __repr__(
    self,
) -> str:
    """
    Developer representation.
    """

    return (
        f"<{self.__class__.__name__} "
        f"id={self._uuid} "
        f"service={self.service_name!r} "
        f"version={self._version} "
        f"frozen={self._frozen} "
        f"items={len(self._data)}>"
    )
def statistics(
    self,
) -> dict[str, Any]:
    """
    Return runtime statistics.
    """

    with self._lock:

        keys = list(
            self._data.keys()
        )

        return {

            "size":
                len(self._data),

            "keys":
                len(keys),

            "empty":
                not bool(self._data),

            "frozen":
                self._frozen,

            "namespace":
                self.namespace,

            "service":
                self.service_name,

            "version":
                self._version,

            "created_at":
                self._created_at,

            "age_seconds":
                self.age(),

            "trace_present":
                bool(
                    self.trace_id
                ),

            "request_present":
                bool(
                    self.request_id
                ),

        }
def diagnostics(
    self,
    *,
    include_values: bool = False,
) -> dict[str, Any]:
    """
    Generate diagnostic information.

    Safe by default.
    """

    with self._lock:

        result = {

            "identity": {

                "uuid":
                    self._uuid,

                "namespace":
                    self.namespace,

                "service":
                    self.service_name,

                "version":
                    self._version,

            },


            "runtime": {

                "frozen":
                    self._frozen,

                "size":
                    len(self._data),

                "age":
                    self.age(),

            },


            "trace": {

                "trace_id":
                    self.trace_id,

                "span_id":
                    self.span_id,

                "request_id":
                    self.request_id,

            },


            "keys":
                list(
                    self._data.keys()
                ),

        }


        if include_values:

            result["data"] = (
                self.safe_dict()
            )


        return result
def dump(
    self,
    *,
    format: str = "json",
    include_values: bool = False,
) -> str:
    """
    Dump context state.
    """

    payload = self.diagnostics(
        include_values=include_values
    )


    if format == "json":

        return json.dumps(
            payload,
            indent=2,
            default=str,
        )


    if format == "repr":

        return repr(
            payload
        )


    raise ValueError(
        f"Unsupported format: {format}"
    )
def pretty(
    self,
) -> str:
    """
    Human friendly formatted output.
    """

    lines = [

        "MetricContext",

        "==============",

        f"Service: {self.service_name}",

        f"Namespace: {self.namespace}",

        f"Trace: {self.trace_id}",

        f"Span: {self.span_id}",

        f"Frozen: {self._frozen}",

        f"Attributes: {len(self._data)}",

    ]


    return "\n".join(
        lines
    )
def inspect(
    self,
    *,
    depth: int = 2,
    redact: bool = True,
) -> dict[str, Any]:
    """
    Deep inspection.

    Used by:
    - debugger
    - CLI
    - telemetry console
    """


    with self._lock:

        data = {}

        for key, value in self._data.items():

            if redact and self._is_sensitive(key):

                data[key] = "***"

            else:

                data[key] = value


        return {

            "type":
                self.__class__.__name__,


            "identity":
                self._uuid,


            "namespace":
                self.namespace,


            "runtime":
                {
                    "frozen":
                        self._frozen,

                    "version":
                        self._version,
                },


            "data":
                data,

        }
def _is_sensitive(
    self,
    key: str,
) -> bool:

    blacklist = {

        "password",

        "secret",

        "token",

        "api_key",

        "credential",

        "private_key",

    }


    key = key.lower()


    return any(
        item in key
        for item in blacklist
    )
debug_id()

summary()

fingerprint()

checksum()

memory_usage()

export_debug()

validate_integrity()

health()
self._lock = RLock()

self._version = 0

self._mutation_count = 0

self._last_modified = time.time()
# ==========================================================
# Lock Helpers
# ==========================================================

def acquire(
    self,
    timeout: float | None = None,
) -> bool:
    """
    Acquire context lock.
    """

    return self._lock.acquire(
        timeout=timeout
        if timeout is not None
        else -1
    )


def release(
    self,
) -> None:
    """
    Release context lock.
    """

    self._lock.release()


def locked(
    self,
):
    """
    Lock context manager.
    """

    return self._lock
with ctx:

    ctx.set(
        "runtime.worker",
        "gpu-01"
    )
def __enter__(
    self,
):

    self._lock.acquire()

    return self



def __exit__(
    self,
    exc_type,
    exc,
    traceback,
):

    self._lock.release()

    return False
ctx.atomic_update(
    {
        "worker.id": 10,
        "gpu.id": 2,
        "task.id": "abc"
    }
)
def atomic_update(
    self,
    updates: Mapping[str, Any],
) -> None:
    """
    Apply multiple mutations atomically.
    """

    with self._lock:

        self._require_mutable()


        backup = copy.deepcopy(
            self._data
        )


        try:

            for key, value in updates.items():

                self._validate_key_value(
                    key,
                    value,
                )

                self._data[key] = value


            self._bump_version()


        except Exception:

            self._data = backup

            raise
def transaction(
    self,
):
    """
    Transaction context.

    Rollback automatically on error.
    """

    return ContextTransaction(
        self
    )
with ctx.transaction():

    ctx.set(
        "a",
        1
    )

    ctx.set(
        "b",
        2
    )
rollback
success = ctx.compare_and_swap(
    expected_version=10,
    updates={
        "state":"running"
    }
)
def compare_and_swap(
    self,
    expected_version: int,
    updates: Mapping[str, Any],
) -> bool:
    """
    Atomic CAS update.
    """

    with self._lock:


        if self._version != expected_version:

            return False


        self.atomic_update(
            updates
        )


        return True
def _bump_version(
    self,
):
    """
    Internal version increment.
    """

    self._version += 1

    self._mutation_count += 1

    self._last_modified = (
        time.time()
    )
@property
def version(
    self,
):

    return self._version


@property
def mutation_count(
    self,
):

    return self._mutation_count


@property
def last_modified(
    self,
):

    return self._last_modified
_require_mutable()
def _require_mutable(
    self,
):
    """
    Verify mutation is allowed.
    """

    if self._frozen:

        raise MetricFrozenError(
            "Context is frozen"
        )
def _mutate(
    self,
    callback,
):
    """
    Execute protected mutation.
    """

    with self._lock:

        self._require_mutable()


        result = callback()


        self._bump_version()


        return result
self._owner_thread = None
def _check_owner(
    self,
):

    current = threading.get_ident()


    if self._owner_thread is None:

        self._owner_thread = current


    elif self._owner_thread != current:

        return False


    return True
def concurrency_stats(
    self,
):

    return {

        "version":
            self._version,

        "mutations":
            self._mutation_count,

        "last_modified":
            self._last_modified,

        "locked":
            self._lock.locked(),

    }
# ==========================================================
# Part 10A - Production Utilities
# Immutable View
# Namespace Helpers
# Prefix Helpers
# Dot Path Access
# ==========================================================


# ==========================================================
# Immutable View
# ==========================================================

@property
def immutable(
    self,
):
    """
    Return immutable view of context.

    Used by:
    - exporters
    - collectors
    - tracing
    """

    return MappingProxyType(
        self.snapshot()
    )


def readonly(
    self,
):
    """
    Alias for immutable view.
    """

    return self.immutable



def freeze_view(
    self,
):
    """
    Create frozen clone.

    Original context unchanged.
    """

    clone = self.clone()

    clone.freeze()

    return clone



# ==========================================================
# Namespace Helpers
# ==========================================================

def namespace_key(
    self,
    key: str,
) -> str:
    """
    Build namespace-qualified key.

    Example:

    namespace=scios.runtime

    key=gpu.id

    result:
    scios.runtime.gpu.id
    """

    if not self.namespace:

        return key


    return (
        f"{self.namespace}."
        f"{key}"
    )



def set_namespace(
    self,
    namespace: str,
):
    """
    Update namespace.
    """

    with self._lock:

        self._require_mutable()

        MetricValidator.validate_attribute_key(
            namespace
        )

        self._namespace = namespace



def child_namespace(
    self,
    name: str,
):
    """
    Create child namespace.

    Example:

    parent:
        scios.runtime

    child:
        gpu

    result:
        scios.runtime.gpu
    """

    namespace = self.namespace_key(
        name
    )


    ctx = self.copy()

    ctx.set_namespace(
        namespace
    )

    return ctx



def in_namespace(
    self,
    namespace: str,
) -> bool:
    """
    Check namespace prefix.
    """

    return (

        self.namespace == namespace

        or

        self.namespace.startswith(
            namespace + "."
        )

    )



# ==========================================================
# Prefix Helpers
# ==========================================================

def prefix(
    self,
    value: str,
) -> "MetricContext":
    """
    Create context with prefixed keys.

    Example:

    cpu.load

    ->
    
    host.cpu.load
    """

    ctx = self.__class__(
        namespace=self.namespace,
        service_name=self.service_name,
        service_version=self.service_version,
    )


    for key, val in self.items():

        ctx.set(
            f"{value}.{key}",
            val,
        )


    return ctx



def has_prefix(
    self,
    prefix: str,
) -> bool:
    """
    Check key prefix.
    """

    return any(

        key.startswith(
            prefix
        )

        for key in self._data

    )



def remove_prefix(
    self,
    prefix: str,
):
    """
    Remove prefix from keys.
    """

    result = {}


    for key, value in self._data.items():

        if key.startswith(
            prefix
        ):

            new_key = (
                key[len(prefix):]
                .lstrip(".")
            )

            result[new_key] = value



    return result



# ==========================================================
# Dot Path Access
# ==========================================================

def get_path(
    self,
    path: str,
    default=None,
):
    """
    Access nested value.

    Example:

    runtime.device.id
    """

    parts = path.split(".")


    current = self._data


    for part in parts:

        if not isinstance(
            current,
            Mapping,
        ):

            return default


        if part not in current:

            return default


        current = current[part]


    return current



def set_path(
    self,
    path: str,
    value: Any,
):
    """
    Set nested value.
    """

    with self._lock:

        self._require_mutable()


        parts = path.split(".")


        current = self._data


        for part in parts[:-1]:

            if part not in current:

                current[part] = {}


            current = current[part]


        current[parts[-1]] = value


        self._bump_version()



def delete_path(
    self,
    path: str,
) -> bool:
    """
    Delete nested value.
    """

    with self._lock:

        self._require_mutable()


        parts = path.split(".")


        current = self._data


        for part in parts[:-1]:

            if part not in current:

                return False


            current = current[part]


        if parts[-1] not in current:

            return False


        del current[parts[-1]]


        self._bump_version()


        return True
# ==========================================================
# Part 10B - Production Utilities
# Flatten
# Unflatten
# Filtering
# Environment Helpers
# ==========================================================


# ==========================================================
# Flatten Helpers
# ==========================================================

def flatten(
    self,
    data: Mapping[str, Any] | None = None,
    *,
    separator: str = ".",
    prefix: str = "",
) -> dict[str, Any]:
    """
    Flatten nested dictionary.

    Example:

    {
        "runtime": {
            "gpu": {
                "id": 0
            }
        }
    }


    becomes:


    {
        "runtime.gpu.id": 0
    }

    """

    if data is None:

        data = self._data


    result = {}


    for key, value in data.items():

        full_key = (

            f"{prefix}{separator}{key}"

            if prefix

            else key

        )


        if isinstance(
            value,
            Mapping,
        ):

            result.update(

                self.flatten(

                    value,

                    separator=separator,

                    prefix=full_key,

                )

            )

        else:

            result[full_key] = value


    return result



def flatten_context(
    self,
    separator: str = ".",
):
    """
    Flatten current context.
    """

    return self.flatten(
        separator=separator
    )



# ==========================================================
# Unflatten Helpers
# ==========================================================

def unflatten(
    self,
    data: Mapping[str, Any],
    *,
    separator: str = ".",
) -> dict[str, Any]:
    """
    Convert flat dictionary into nested dictionary.

    Example:

    {
        "gpu.device.id": 1
    }


    becomes:


    {
        "gpu": {
            "device": {
                "id":1
            }
        }
    }

    """

    result = {}


    for key, value in data.items():

        parts = key.split(
            separator
        )


        current = result


        for part in parts[:-1]:

            if part not in current:

                current[part] = {}


            current = current[part]


        current[parts[-1]] = value


    return result



def restore_tree(
    self,
    flattened: Mapping[str, Any],
):
    """
    Restore nested structure
    into current context.
    """

    tree = self.unflatten(
        flattened
    )


    self.restore(
        tree
    )



# ==========================================================
# Filtering Engine
# ==========================================================

def filter(
    self,
    predicate=None,
    *,
    prefix: str | None = None,
    keys: Iterable[str] | None = None,
) -> dict[str, Any]:
    """
    Filter context values.

    Supports:

    - custom predicate
    - prefix matching
    - explicit keys

    """

    result = {}


    for key, value in self._data.items():


        if prefix:

            if not key.startswith(
                prefix
            ):

                continue



        if keys:

            if key not in keys:

                continue



        if predicate:

            if not predicate(
                key,
                value,
            ):

                continue



        result[key] = value


    return result



def select(
    self,
    keys: Iterable[str],
):
    """
    Select specific keys.
    """

    return {

        key: self._data[key]

        for key in keys

        if key in self._data

    }



def exclude(
    self,
    keys: Iterable[str],
):
    """
    Remove keys from view.
    """

    excluded = set(
        keys
    )


    return {

        key: value

        for key, value
        in self._data.items()

        if key not in excluded

    }



def filter_prefix(
    self,
    prefix: str,
):
    """
    Filter by prefix.
    """

    return self.filter(
        prefix=prefix
    )



def filter_sensitive(
    self,
):
    """
    Remove sensitive values.

    Used before export.
    """

    result = {}


    for key, value in self._data.items():

        if self._is_sensitive(
            key
        ):

            continue


        result[key] = value


    return result



# ==========================================================
# Environment Helpers
# ==========================================================

@classmethod
def from_environment(
    cls,
    prefix: str = "SCIOS_",
):
    """
    Build context from environment.

    Example:

    SCIOS_SERVICE_NAME=my-agent

    becomes:

    service.name=my-agent

    """

    import os


    data = {}


    for key, value in os.environ.items():


        if not key.startswith(
            prefix
        ):

            continue



        name = (

            key[len(prefix):]

            .lower()

            .replace(
                "_",
                ".",
            )

        )


        data[name] = value



    return cls(
        data=data
    )



def load_environment(
    self,
    prefix: str = "SCIOS_",
):
    """
    Merge environment variables.
    """

    env_ctx = self.from_environment(
        prefix
    )


    self.merge_inplace(
        env_ctx.snapshot()
    )



def env(
    self,
    key: str,
    default=None,
):
    """
    Read environment variable
    stored in context.
    """

    return self.get(
        f"env.{key}",
        default,
    )



def set_env(
    self,
    key: str,
    value: Any,
):
    """
    Store environment metadata.
    """

    self.set(
        f"env.{key}",
        value,
    )



# ==========================================================
# Configuration Helpers
# ==========================================================

def config(
    self,
    key: str,
    default=None,
):
    """
    Runtime configuration access.
    """

    return self.get_path(
        f"config.{key}",
        default,
    )



def set_config(
    self,
    key: str,
    value: Any,
):
    """
    Set runtime configuration.
    """

    self.set_path(
        f"config.{key}",
        value,
    )



def has_config(
    self,
    key: str,
):
    """
    Check configuration existence.
    """

    return (

        self.get_path(
            f"config.{key}"
        )

        is not None

    )
# ==========================================================
# Part 10C - Production Utilities
# Runtime Detection
# Host Detection
# Process Helpers
# Thread Helpers
# ==========================================================


# ==========================================================
# Runtime Detection
# ==========================================================

@staticmethod
def detect_runtime():
    """
    Detect execution runtime.

    Returns
    -------
    dict
        Runtime information.
    """

    import platform
    import sys


    return {

        "runtime.language":
            "python",


        "runtime.python.version":
            sys.version,


        "runtime.python.major":
            sys.version_info.major,


        "runtime.python.minor":
            sys.version_info.minor,


        "runtime.implementation":
            platform.python_implementation(),


        "runtime.platform":
            platform.platform(),


        "runtime.machine":
            platform.machine(),


        "runtime.architecture":
            platform.architecture()[0],

    }



def load_runtime(
    self,
):
    """
    Attach runtime information.
    """

    self.merge_inplace(
        self.detect_runtime()
    )



@property
def runtime(
    self,
):
    """
    Runtime metadata.
    """

    return self.filter_prefix(
        "runtime."
    )



# ==========================================================
# Host Detection
# ==========================================================

@staticmethod
def detect_host():
    """
    Detect host information.
    """

    import socket
    import platform


    hostname = socket.gethostname()


    return {

        "host.name":
            hostname,


        "host.hostname":
            hostname,


        "host.platform":
            platform.system(),


        "host.release":
            platform.release(),


        "host.version":
            platform.version(),


        "host.machine":
            platform.machine(),


        "host.processor":
            platform.processor(),

    }



def load_host(
    self,
):
    """
    Attach host metadata.
    """

    self.merge_inplace(
        self.detect_host()
    )



@property
def host(
    self,
):
    """
    Host metadata.
    """

    return self.filter_prefix(
        "host."
    )



# ==========================================================
# Container Detection
# ==========================================================

@staticmethod
def detect_container():
    """
    Detect container environment.

    Supports:

    - Docker
    - Kubernetes
    """

    import os


    result = {


        "container.enabled":
            False,

    }


    if os.path.exists(
        "/.dockerenv"
    ):

        result.update({

            "container.enabled":
                True,

            "container.type":
                "docker",

        })



    if "KUBERNETES_SERVICE_HOST" in os.environ:

        result.update({

            "container.enabled":
                True,

            "container.type":
                "kubernetes",

            "kubernetes.namespace":
                os.getenv(
                    "POD_NAMESPACE",
                    "",
                ),

            "kubernetes.pod":
                os.getenv(
                    "HOSTNAME",
                    "",
                ),

        })


    return result



def load_container(
    self,
):
    """
    Attach container metadata.
    """

    self.merge_inplace(
        self.detect_container()
    )



# ==========================================================
# Process Helpers
# ==========================================================

@staticmethod
def detect_process():
    """
    Detect process metadata.
    """

    import os


    return {

        "process.pid":
            os.getpid(),


        "process.parent_pid":
            os.getppid(),


        "process.cwd":
            os.getcwd(),


        "process.executable":
            os.sys.executable,

    }



def load_process(
    self,
):
    """
    Attach process metadata.
    """

    self.merge_inplace(
        self.detect_process()
    )



@property
def process(
    self,
):
    """
    Process information.
    """

    return self.filter_prefix(
        "process."
    )



def process_identity(
    self,
):
    """
    Unique process identity.
    """

    return {

        "pid":
            self.get(
                "process.pid"
            ),

        "parent_pid":
            self.get(
                "process.parent_pid"
            ),

    }



# ==========================================================
# Thread Helpers
# ==========================================================

@staticmethod
def detect_thread():
    """
    Detect current thread.
    """

    import threading


    thread = threading.current_thread()


    return {

        "thread.id":
            threading.get_ident(),


        "thread.name":
            thread.name,


        "thread.daemon":
            thread.daemon,


    }



def load_thread(
    self,
):
    """
    Attach thread metadata.
    """

    self.merge_inplace(
        self.detect_thread()
    )



@property
def thread(
    self,
):
    """
    Thread metadata.
    """

    return self.filter_prefix(
        "thread."
    )



def thread_identity(
    self,
):
    """
    Return thread identity.
    """

    return {

        "id":
            self.get(
                "thread.id"
            ),


        "name":
            self.get(
                "thread.name"
            ),

    }



# ==========================================================
# Worker Identity
# ==========================================================

def worker_identity(
    self,
):
    """
    Unified worker identity.

    Useful for:

    - distributed workers
    - GPU workers
    - schedulers
    """

    return {

        "service":
            self.service_name,


        "host":
            self.get(
                "host.name"
            ),


        "pid":
            self.get(
                "process.pid"
            ),


        "thread":
            self.get(
                "thread.id"
            ),


        "instance":
            self.instance_id,

    }



# ==========================================================
# Auto Runtime Bootstrap
# ==========================================================

def enrich_runtime(
    self,
):
    """
    Populate full runtime metadata.

    Called during bootstrap.
    """

    self.load_runtime()

    self.load_host()

    self.load_container()

    self.load_process()

    self.load_thread()

    return self
# ==========================================================
# Part 10D - Production Utilities
# Trace Helpers
# Tag Helpers
# Validation Helpers
# Final Polish
# ==========================================================


# ==========================================================
# Trace Helpers
# ==========================================================

def trace_context(
    self,
) -> dict[str, Any]:
    """
    Return trace related information.
    """

    return {

        "trace_id":
            self.get(
                "trace.id"
            ),

        "span_id":
            self.get(
                "span.id"
            ),

        "parent_span_id":
            self.get(
                "span.parent.id"
            ),

        "trace_state":
            self.get(
                "trace.state"
            ),

        "sampled":
            self.get(
                "trace.sampled",
                False,
            ),

    }



def has_trace(
    self,
) -> bool:
    """
    Check trace availability.
    """

    return bool(
        self.get(
            "trace.id"
        )
    )



def set_trace(
    self,
    trace_id: str,
    span_id: str | None = None,
):
    """
    Attach trace information.
    """

    self.set(
        "trace.id",
        trace_id,
    )


    if span_id:

        self.set(
            "span.id",
            span_id,
        )



def clear_trace(
    self,
):
    """
    Remove trace metadata.
    """

    keys = [

        "trace.id",

        "span.id",

        "span.parent.id",

        "trace.state",

        "trace.sampled",

    ]


    for key in keys:

        self.remove(
            key
        )



def trace_child(
    self,
):
    """
    Create child span context.
    """

    child = self.copy()


    child.child_span()


    return child



# ==========================================================
# Tag Helpers
# ==========================================================

def add_tag(
    self,
    key: str,
    value: Any,
):
    """
    Add runtime tag.
    """

    self.set(
        f"tag.{key}",
        value,
    )



def get_tag(
    self,
    key: str,
    default=None,
):
    """
    Get tag.
    """

    return self.get(
        f"tag.{key}",
        default,
    )



def remove_tag(
    self,
    key: str,
):
    """
    Remove tag.
    """

    return self.remove(
        f"tag.{key}"
    )



def tags(
    self,
):
    """
    Return all tags.
    """

    return self.filter_prefix(
        "tag."
    )



def clear_tags(
    self,
):
    """
    Remove all tags.
    """

    keys = [

        key

        for key in self._data

        if key.startswith(
            "tag."
        )

    ]


    for key in keys:

        self.remove(
            key
        )



def has_tag(
    self,
    key: str,
):
    """
    Check tag existence.
    """

    return (

        f"tag.{key}"

        in self._data

    )



# ==========================================================
# Validation Helpers
# ==========================================================

def validate(
    self,
) -> bool:
    """
    Validate context integrity.
    """

    checks = [

        self._validate_namespace(),

        self._validate_service(),

        self._validate_keys(),

        self._validate_trace(),

    ]


    return all(
        checks
    )



def _validate_namespace(
    self,
):
    """
    Validate namespace.
    """

    if not self.namespace:

        return True


    return (

        isinstance(
            self.namespace,
            str,
        )

        and

        len(
            self.namespace
        ) > 0

    )



def _validate_service(
    self,
):
    """
    Validate service metadata.
    """

    return (

        self.service_name

        is None

        or

        isinstance(
            self.service_name,
            str,
        )

    )



def _validate_keys(
    self,
):
    """
    Validate attribute keys.
    """

    for key in self._data.keys():

        if not isinstance(
            key,
            str,
        ):

            return False


    return True



def _validate_trace(
    self,
):
    """
    Validate trace fields.
    """

    trace_id = self.get(
        "trace.id"
    )


    if trace_id is None:

        return True


    return isinstance(
        trace_id,
        str,
    )



def assert_valid(
    self,
):
    """
    Raise exception if invalid.
    """

    if not self.validate():

        raise ValueError(
            "Invalid MetricContext"
        )



# ==========================================================
# Integrity Helpers
# ==========================================================

def checksum(
    self,
):
    """
    Generate deterministic checksum.
    """

    import hashlib
    import json


    payload = json.dumps(

        self.to_dict(),

        sort_keys=True,

        default=str,

    )


    return hashlib.sha256(

        payload.encode()

    ).hexdigest()



def fingerprint(
    self,
):
    """
    Short identity fingerprint.
    """

    return self.checksum()[:16]



# ==========================================================
# Health / Status
# ==========================================================

def health(
    self,
):
    """
    Runtime health status.
    """

    return {

        "healthy":
            self.validate(),

        "frozen":
            self._frozen,

        "version":
            self._version,

        "fingerprint":
            self.fingerprint(),

        "size":
            len(self._data),

    }



# ==========================================================
# Final Debug Helpers
# ==========================================================

def summary(
    self,
):
    """
    Compact runtime summary.
    """

    return {

        "service":
            self.service_name,

        "namespace":
            self.namespace,

        "trace":
            self.get(
                "trace.id"
            ),

        "items":
            len(self._data),

        "version":
            self._version,

    }



def finalize(
    self,
):
    """
    Finalize context before export.

    Used by:

    - exporters
    - collectors
    - snapshots
    """

    self.assert_valid()


    return self.freeze_view()



# ==========================================================
# Convenience Bootstrap
# ==========================================================

def production_context(
    self,
):
    """
    Prepare production ready context.
    """

    self.enrich_runtime()

    self.validate()

    return self                                                                                    