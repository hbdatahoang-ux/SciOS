"""
SciOS-NG
Runtime Observability - Tracing Status

File:
    scios/runtime/observability/tracing/status.py

Part 1. Foundation
"""

from __future__ import annotations

# ==============================================================================
# Imports
# ==============================================================================

import time
import uuid
import threading

from copy import deepcopy

from dataclasses import (
    dataclass,
    field,
)

from enum import (
    Enum,
    IntFlag,
    auto,
)

from typing import (
    Any,
    Callable,
    Dict,
    List,
    Mapping,
    MutableMapping,
    Optional,
    TypeAlias,
    Union,
)

# ==============================================================================
# Constants
# ==============================================================================

STATUS_VERSION: str = "0.3.0-alpha"

DEFAULT_STATUS_NAME: str = "TraceStatus"

DEFAULT_DESCRIPTION: str = ""

DEFAULT_MESSAGE: str = ""

DEFAULT_REASON: str = ""

DEFAULT_SOURCE: str = "runtime"

DEFAULT_HISTORY_LIMIT: int = 1024

# ==============================================================================
# Type Aliases
# ==============================================================================

StatusMetadata: TypeAlias = Dict[str, Any]

StatusAttributes: TypeAlias = Dict[str, Any]

StatusContext: TypeAlias = Dict[str, Any]

StatusSnapshot: TypeAlias = Dict[str, Any]

StatusHook: TypeAlias = Callable[..., Any]

StatusCallback: TypeAlias = Callable[..., None]

# ==============================================================================
# Exceptions
# ==============================================================================


class TraceStatusError(Exception):
    """Base tracing status exception."""


class StatusValidationError(TraceStatusError):
    """Invalid status."""


class StatusRuntimeError(TraceStatusError):
    """Runtime status error."""


class StatusClosedError(TraceStatusError):
    """Status object already closed."""


class StatusFrozenError(TraceStatusError):
    """Status object is frozen."""


# ==============================================================================
# Enums
# ==============================================================================


class TraceStatusCode(str, Enum):
    """
    Trace status code.

    Compatible with OpenTelemetry while allowing SciOS extensions.
    """

    UNSET = "UNSET"

    OK = "OK"

    ERROR = "ERROR"

    CANCELLED = "CANCELLED"

    TIMEOUT = "TIMEOUT"

    DROPPED = "DROPPED"

    INTERNAL_ERROR = "INTERNAL_ERROR"


class TraceStatusState(str, Enum):
    """
    Runtime lifecycle state.
    """

    CREATED = "created"

    INITIALIZED = "initialized"

    READY = "ready"

    RUNNING = "running"

    UPDATED = "updated"

    CLOSED = "closed"


class TraceStatusFlag(IntFlag):
    """
    Runtime capability flags.
    """

    NONE = 0

    MUTABLE = auto()

    SERIALIZABLE = auto()

    VALIDATABLE = auto()

    SNAPSHOTTABLE = auto()

    DIAGNOSTIC = auto()

    THREAD_SAFE = auto()

# ==============================================================================
# Dataclasses
# ==============================================================================


@dataclass(slots=True)
class TraceStatusStatistics:
    """
    Runtime statistics.
    """

    updates: int = 0

    transitions: int = 0

    validations: int = 0

    failures: int = 0

    created_at: float = field(default_factory=time.time)

    updated_at: float = field(default_factory=time.time)


@dataclass(slots=True)
class TraceStatusSnapshotData:
    """
    Snapshot container.
    """

    id: str

    code: str

    description: str

    message: str

    reason: str

    metadata: StatusMetadata = field(default_factory=dict)

    attributes: StatusAttributes = field(default_factory=dict)


@dataclass(slots=True)
class TraceStatusRecord:
    """
    Immutable status record.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    timestamp: float = field(default_factory=time.time)

    code: TraceStatusCode = TraceStatusCode.UNSET

    description: str = DEFAULT_DESCRIPTION

    message: str = DEFAULT_MESSAGE

    reason: str = DEFAULT_REASON

    source: str = DEFAULT_SOURCE

    metadata: StatusMetadata = field(default_factory=dict)

    attributes: StatusAttributes = field(default_factory=dict)

# ==============================================================================
# Execution Phase
# ==============================================================================


class ExecutionPhase(str, Enum):
    """
    Trace execution lifecycle phase.
    """

    CREATED = "created"

    INITIALIZING = "initializing"

    RUNNING = "running"

    PROCESSING = "processing"

    EXPORTING = "exporting"

    COMPLETED = "completed"

    FAILED = "failed"

    CANCELLED = "cancelled"

    CLOSED = "closed"
# ==============================================================================
# Status
# ==============================================================================


class Status(str, Enum):
    """
    Generic tracing status.
    """

    OK = "ok"

    ERROR = "error"

    UNKNOWN = "unknown"

    UNSET = "unset"    

# ==============================================================================
# Compatibility Aliases
# ==============================================================================

StatusCode = TraceStatusCode

# ==============================================================================
# Public API
# ==============================================================================

__all__ = [

    # Constants

    "STATUS_VERSION",

    "DEFAULT_STATUS_NAME",

    "DEFAULT_DESCRIPTION",

    "DEFAULT_MESSAGE",

    "DEFAULT_REASON",

    "DEFAULT_SOURCE",

    "DEFAULT_HISTORY_LIMIT",

    # Enums

    "TraceStatusCode",

    "StatusCode",

    "TraceStatusState",

    "TraceStatusFlag",

    # Dataclasses

    "TraceStatusStatistics",

    "TraceStatusSnapshotData",

    "TraceStatusRecord",

    # Exceptions

    "TraceStatusError",

    "StatusValidationError",

    "StatusRuntimeError",

    "StatusClosedError",

    "StatusFrozenError",

]
# ==============================================================================
# Part 2. Constructor
# ==============================================================================

class TraceStatus:
    """
    Runtime trace status.

    Represents the current execution status of a trace/span.
    """

    def __init__(
        self,
        code: TraceStatusCode = TraceStatusCode.UNSET,
        *,
        description: str = DEFAULT_DESCRIPTION,
        message: str = DEFAULT_MESSAGE,
        reason: str = DEFAULT_REASON,
        source: str = DEFAULT_SOURCE,
        metadata: Optional[StatusMetadata] = None,
        attributes: Optional[StatusAttributes] = None,
    ) -> None:

        # ------------------------------------------------------------------
        # Identity
        # ------------------------------------------------------------------

        self._id: str = str(uuid.uuid4())

        self._uuid: uuid.UUID = uuid.UUID(self._id)

        self._name: str = DEFAULT_STATUS_NAME

        self._version: str = STATUS_VERSION

        # ------------------------------------------------------------------
        # Runtime State
        # ------------------------------------------------------------------

        self._code: TraceStatusCode = TraceStatusCode(code)

        self._state: TraceStatusState = (
            TraceStatusState.CREATED
        )

        self._description: str = str(description)

        self._message: str = str(message)

        self._reason: str = str(reason)

        self._source: str = str(source)

        self._enabled: bool = True

        self._frozen: bool = False

        self._closed: bool = False

        self._active: bool = False

        self._created_at: float = time.time()

        self._updated_at: float = self._created_at

        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------

        self._statistics = (
            TraceStatusStatistics()
        )

        self._update_count: int = 0

        self._transition_count: int = 0

        self._validation_count: int = 0

        self._failure_count: int = 0

        self._last_update: Optional[float] = None

        # ------------------------------------------------------------------
        # Metadata
        # ------------------------------------------------------------------

        self._metadata: StatusMetadata = dict(
            metadata or {}
        )

        self._attributes: StatusAttributes = dict(
            attributes or {}
        )

        self._context: StatusContext = {}

        self._tags: list[str] = []

        self._history: list[TraceStatusRecord] = []

        # ------------------------------------------------------------------
        # Runtime Objects
        # ------------------------------------------------------------------

        self._flags: TraceStatusFlag = (
            TraceStatusFlag.MUTABLE
            | TraceStatusFlag.SERIALIZABLE
            | TraceStatusFlag.VALIDATABLE
            | TraceStatusFlag.SNAPSHOTTABLE
        )

        self._hooks: dict[
            str,
            list[StatusHook],
        ] = {}

        self._callbacks: list[
            StatusCallback
        ] = []

        self._cache: MutableMapping[
            str,
            Any,
        ] = {}

        self._lock = threading.RLock()
    # ==============================================================================
    # Part 3. Properties
    # ==============================================================================

    # ------------------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------------------

    @property
    def id(self) -> str:
        """Unique status identifier."""
        return self._id


    @property
    def uuid(self) -> uuid.UUID:
        """UUID object."""
        return self._uuid


    @property
    def name(self) -> str:
        """Status object name."""
        return self._name


    @property
    def version(self) -> str:
        """Status implementation version."""
        return self._version


    # ------------------------------------------------------------------------------
    # Runtime
    # ------------------------------------------------------------------------------

    @property
    def code(self) -> TraceStatusCode:
        """Current trace status code."""
        return self._code


    @property
    def state(self) -> TraceStatusState:
        """Current runtime state."""
        return self._state


    @property
    def description(self) -> str:
        """Status description."""
        return self._description


    @description.setter
    def description(
        self,
        value: str,
    ) -> None:
        self._description = str(value)
        self._updated_at = time.time()


    @property
    def message(self) -> str:
        """Status message."""
        return self._message


    @message.setter
    def message(
        self,
        value: str,
    ) -> None:
        self._message = str(value)
        self._updated_at = time.time()


    @property
    def reason(self) -> str:
        """Reason for current status."""
        return self._reason


    @reason.setter
    def reason(
        self,
        value: str,
    ) -> None:
        self._reason = str(value)
        self._updated_at = time.time()


    @property
    def source(self) -> str:
        """Status source."""
        return self._source


    @property
    def enabled(self) -> bool:
        return self._enabled


    @property
    def frozen(self) -> bool:
        return self._frozen


    @property
    def closed(self) -> bool:
        return self._closed


    @property
    def active(self) -> bool:
        return self._active


    @property
    def created_at(self) -> float:
        return self._created_at


    @property
    def updated_at(self) -> float:
        return self._updated_at


    @property
    def last_update(self) -> Optional[float]:
        return self._last_update


    @property
    def uptime(self) -> float:
        """Lifetime in seconds."""
        return time.time() - self._created_at


    # ------------------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------------------

    @property
    def statistics(self) -> TraceStatusStatistics:
        """Runtime statistics."""
        return deepcopy(self._statistics)


    @property
    def update_count(self) -> int:
        return self._update_count


    @property
    def transition_count(self) -> int:
        return self._transition_count


    @property
    def validation_count(self) -> int:
        return self._validation_count


    @property
    def failure_count(self) -> int:
        return self._failure_count


    # ------------------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------------------

    @property
    def metadata(self) -> StatusMetadata:
        """Metadata (defensive copy)."""
        return deepcopy(self._metadata)


    @property
    def attributes(self) -> StatusAttributes:
        """Attributes (defensive copy)."""
        return deepcopy(self._attributes)


    @property
    def context(self) -> StatusContext:
        """Runtime context."""
        return deepcopy(self._context)


    @property
    def tags(self) -> list[str]:
        """Status tags."""
        return list(self._tags)


    @property
    def history(self) -> list[TraceStatusRecord]:
        """Status history."""
        return list(self._history)


    @property
    def flags(self) -> TraceStatusFlag:
        """Capability flags."""
        return self._flags


    @property
    def callbacks(self) -> list[StatusCallback]:
        """Registered callbacks."""
        return list(self._callbacks)


    @property
    def hooks(self) -> dict[str, list[StatusHook]]:
        """Registered hooks."""
        return {
            name: list(hooks)
            for name, hooks in self._hooks.items()
        }


    @property
    def cache(self) -> dict[str, Any]:
        """Runtime cache."""
        return dict(self._cache)
    # ==============================================================================
    # Part 4. Status API
    # ==============================================================================

    def set_status(
        self,
        code: TraceStatusCode,
        *,
        description: Optional[str] = None,
        message: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> "TraceStatus":
        """
        Set the current trace status.

        Parameters
        ----------
        code
            New status code.

        description
            Optional status description.

        message
            Optional status message.

        reason
            Optional reason.

        Returns
        -------
        TraceStatus
        """

        if self._closed:
            raise StatusClosedError(
                "status object is closed"
            )

        if self._frozen:
            raise StatusFrozenError(
                "status object is frozen"
            )

        code = TraceStatusCode(code)

        previous = self._code

        self.before_update()

        self._code = code

        if description is not None:
            self._description = str(description)

        if message is not None:
            self._message = str(message)

        if reason is not None:
            self._reason = str(reason)

        self._state = TraceStatusState.UPDATED

        self._updated_at = time.time()

        self._last_update = self._updated_at

        self._update_count += 1

        if previous != code:
            self._transition_count += 1

        self._statistics.updates += 1
        self._statistics.transitions = (
            self._transition_count
        )
        self._statistics.updated_at = (
            self._updated_at
        )

        self._history.append(

            TraceStatusRecord(

                code=self._code,

                description=self._description,

                message=self._message,

                reason=self._reason,

                source=self._source,

                metadata=deepcopy(
                    self._metadata
                ),

                attributes=deepcopy(
                    self._attributes
                ),

            )

        )

        if len(self._history) > DEFAULT_HISTORY_LIMIT:

            self._history.pop(0)

        self.after_update()

        return self


    # ------------------------------------------------------------------------------

    def get_status(
        self,
    ) -> TraceStatusCode:
        """
        Return the current status code.
        """

        return self._code


    # ------------------------------------------------------------------------------

    def is_ok(
        self,
    ) -> bool:
        """
        Return True if status is OK.
        """

        return self._code is TraceStatusCode.OK


    # ------------------------------------------------------------------------------

    def is_error(
        self,
    ) -> bool:
        """
        Return True if current status represents an error.
        """

        return self._code in {

            TraceStatusCode.ERROR,

            TraceStatusCode.INTERNAL_ERROR,

            TraceStatusCode.TIMEOUT,

            TraceStatusCode.CANCELLED,

        }


    # ------------------------------------------------------------------------------

    def is_unset(
        self,
    ) -> bool:
        """
        Return True if status is UNSET.
        """

        return self._code is TraceStatusCode.UNSET


    # ------------------------------------------------------------------------------

    def clear(
        self,
    ) -> "TraceStatus":
        """
        Reset runtime status to UNSET.
        """

        return self.set_status(

            TraceStatusCode.UNSET,

            description=DEFAULT_DESCRIPTION,

            message=DEFAULT_MESSAGE,

            reason=DEFAULT_REASON,

        )


    # ------------------------------------------------------------------------------

    def update(
        self,
        *,
        code: Optional[
            TraceStatusCode
        ] = None,
        description: Optional[str] = None,
        message: Optional[str] = None,
        reason: Optional[str] = None,
        metadata: Optional[
            StatusMetadata
        ] = None,
        attributes: Optional[
            StatusAttributes
        ] = None,
    ) -> "TraceStatus":
        """
        Update the current status.

        Any parameter may be omitted.
        """

        if code is not None:

            self.set_status(

                code,

                description=description,

                message=message,

                reason=reason,

            )

        else:

            if description is not None:
                self._description = str(
                    description
                )

            if message is not None:
                self._message = str(
                    message
                )

            if reason is not None:
                self._reason = str(
                    reason
                )

            self._updated_at = time.time()

            self._last_update = (
                self._updated_at
            )

        if metadata:

            self._metadata.update(

                deepcopy(metadata)

            )

        if attributes:

            self._attributes.update(

                deepcopy(attributes)

            )

        return self
    # ==============================================================================
    # Part 5. Runtime Operations
    # ==============================================================================

    def snapshot(
        self,
    ) -> StatusSnapshot:
        """
        Create a runtime snapshot.

        Returns
        -------
        StatusSnapshot
            Serializable runtime state.
        """

        return {

            # ------------------------------------------------------------------
            # Identity
            # ------------------------------------------------------------------

            "id": self._id,

            "uuid": str(self._uuid),

            "name": self._name,

            "version": self._version,

            # ------------------------------------------------------------------
            # Runtime
            # ------------------------------------------------------------------

            "code": self._code.value,

            "state": self._state.value,

            "description": self._description,

            "message": self._message,

            "reason": self._reason,

            "source": self._source,

            "enabled": self._enabled,

            "frozen": self._frozen,

            "closed": self._closed,

            "active": self._active,

            "created_at": self._created_at,

            "updated_at": self._updated_at,

            "last_update": self._last_update,

            # ------------------------------------------------------------------
            # Statistics
            # ------------------------------------------------------------------

            "statistics": deepcopy(
                self._statistics
            ),

            "update_count": self._update_count,

            "transition_count": self._transition_count,

            "validation_count": self._validation_count,

            "failure_count": self._failure_count,

            # ------------------------------------------------------------------
            # Metadata
            # ------------------------------------------------------------------

            "metadata": deepcopy(
                self._metadata
            ),

            "attributes": deepcopy(
                self._attributes
            ),

            "context": deepcopy(
                self._context
            ),

            "tags": list(
                self._tags
            ),

        }


    # ------------------------------------------------------------------------------

    def restore(
        self,
        snapshot: Mapping[str, Any],
    ) -> "TraceStatus":
        """
        Restore runtime state from a snapshot.
        """

        self._code = TraceStatusCode(

            snapshot.get(
                "code",
                self._code.value,
            )

        )

        self._state = TraceStatusState(

            snapshot.get(
                "state",
                self._state.value,
            )

        )

        self._description = snapshot.get(
            "description",
            self._description,
        )

        self._message = snapshot.get(
            "message",
            self._message,
        )

        self._reason = snapshot.get(
            "reason",
            self._reason,
        )

        self._source = snapshot.get(
            "source",
            self._source,
        )

        self._enabled = snapshot.get(
            "enabled",
            self._enabled,
        )

        self._frozen = snapshot.get(
            "frozen",
            self._frozen,
        )

        self._closed = snapshot.get(
            "closed",
            self._closed,
        )

        self._active = snapshot.get(
            "active",
            self._active,
        )

        self._updated_at = snapshot.get(
            "updated_at",
            self._updated_at,
        )

        self._last_update = snapshot.get(
            "last_update",
            self._last_update,
        )

        statistics = snapshot.get(
            "statistics"
        )

        if isinstance(
            statistics,
            TraceStatusStatistics,
        ):
            self._statistics = deepcopy(
                statistics
            )

        self._update_count = snapshot.get(
            "update_count",
            self._update_count,
        )

        self._transition_count = snapshot.get(
            "transition_count",
            self._transition_count,
        )

        self._validation_count = snapshot.get(
            "validation_count",
            self._validation_count,
        )

        self._failure_count = snapshot.get(
            "failure_count",
            self._failure_count,
        )

        self._metadata = deepcopy(

            snapshot.get(
                "metadata",
                self._metadata,
            )

        )

        self._attributes = deepcopy(

            snapshot.get(
                "attributes",
                self._attributes,
            )

        )

        self._context = deepcopy(

            snapshot.get(
                "context",
                self._context,
            )

        )

        self._tags = list(

            snapshot.get(
                "tags",
                self._tags,
            )

        )

        return self


    # ------------------------------------------------------------------------------

    def clone(
        self,
    ) -> "TraceStatus":
        """
        Create a deep clone.
        """

        return deepcopy(
            self
        )


    # ------------------------------------------------------------------------------

    def copy(
        self,
    ) -> "TraceStatus":
        """
        Create a shallow copy.
        """

        return copy.copy(
            self
        )


    # ------------------------------------------------------------------------------

    def reset(
        self,
    ) -> "TraceStatus":
        """
        Reset runtime status.

        Statistics are preserved.
        """

        self._code = (
            TraceStatusCode.UNSET
        )

        self._state = (
            TraceStatusState.CREATED
        )

        self._description = (
            DEFAULT_DESCRIPTION
        )

        self._message = (
            DEFAULT_MESSAGE
        )

        self._reason = (
            DEFAULT_REASON
        )

        self._attributes.clear()

        self._metadata.clear()

        self._context.clear()

        self._tags.clear()

        self._history.clear()

        self._updated_at = time.time()

        self._last_update = None

        return self


    # ------------------------------------------------------------------------------

    def merge(
        self,
        other: "TraceStatus",
    ) -> "TraceStatus":
        """
        Merge another TraceStatus into this instance.

        Runtime state is updated using the newest information.
        Metadata and attributes are merged.
        """

        if not isinstance(
            other,
            TraceStatus,
        ):
            raise TypeError(
                "other must be TraceStatus"
            )

        if (
            other.updated_at
            > self.updated_at
        ):

            self._code = other.code

            self._state = other.state

            self._description = (
                other.description
            )

            self._message = (
                other.message
            )

            self._reason = (
                other.reason
            )

            self._updated_at = (
                other.updated_at
            )

            self._last_update = (
                other.last_update
            )

        self._metadata.update(

            deepcopy(
                other.metadata
            )

        )

        self._attributes.update(

            deepcopy(
                other.attributes
            )

        )

        for tag in other.tags:

            if tag not in self._tags:

                self._tags.append(
                    tag
                )

        return self
    # ==============================================================================
    # Part 6. Statistics & Diagnostics
    # ==============================================================================

    def summary(
        self,
    ) -> Dict[str, Any]:
        """
        Return a concise runtime summary.

        Returns
        -------
        Dict[str, Any]
            Lightweight status information.
        """

        return {

            "id": self._id,

            "name": self._name,

            "code": self._code.value,

            "state": self._state.value,

            "description": self._description,

            "enabled": self._enabled,

            "active": self._active,

            "updated_at": self._updated_at,

        }


    # ------------------------------------------------------------------------------

    def report(
        self,
    ) -> Dict[str, Any]:
        """
        Return a complete runtime report.
        """

        return {

            # ------------------------------------------------------------------
            # Identity
            # ------------------------------------------------------------------

            "identity": {

                "id": self._id,

                "uuid": str(self._uuid),

                "name": self._name,

                "version": self._version,

            },

            # ------------------------------------------------------------------
            # Runtime
            # ------------------------------------------------------------------

            "runtime": {

                "code": self._code.value,

                "state": self._state.value,

                "description": self._description,

                "message": self._message,

                "reason": self._reason,

                "source": self._source,

                "enabled": self._enabled,

                "frozen": self._frozen,

                "closed": self._closed,

                "active": self._active,

                "created_at": self._created_at,

                "updated_at": self._updated_at,

                "last_update": self._last_update,

                "uptime": time.time() - self._created_at,

            },

            # ------------------------------------------------------------------
            # Statistics
            # ------------------------------------------------------------------

            "statistics": {

                "updates": self._update_count,

                "transitions": self._transition_count,

                "validations": self._validation_count,

                "failures": self._failure_count,

            },

            # ------------------------------------------------------------------
            # Metadata
            # ------------------------------------------------------------------

            "metadata": deepcopy(
                self._metadata
            ),

            "attributes": deepcopy(
                self._attributes
            ),

            "context": deepcopy(
                self._context
            ),

            "tags": list(
                self._tags
            ),

        }


    # ------------------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> Dict[str, Any]:
        """
        Return runtime diagnostics.

        Intended for debugging and observability.
        """

        return {

            "healthy": (
                self._enabled
                and not self._closed
                and not self._frozen
            ),

            "code": self._code.value,

            "state": self._state.value,

            "history_size": len(
                self._history
            ),

            "hook_count": sum(
                len(v)
                for v in self._hooks.values()
            ),

            "callback_count": len(
                self._callbacks
            ),

            "cache_entries": len(
                self._cache
            ),

            "flags": int(
                self._flags
            ),

        }


    # ------------------------------------------------------------------------------

    def health(
        self,
    ) -> Dict[str, Any]:
        """
        Return health information.
        """

        healthy = (

            self._enabled

            and not self._closed

            and not self._frozen

            and self._code
            not in {

                TraceStatusCode.ERROR,

                TraceStatusCode.INTERNAL_ERROR,

            }

        )

        return {

            "healthy": healthy,

            "status": (
                "healthy"
                if healthy
                else "unhealthy"
            ),

            "code": self._code.value,

            "enabled": self._enabled,

            "active": self._active,

            "failures": self._failure_count,

            "last_update": self._last_update,

        }


    # ------------------------------------------------------------------------------

    def metrics(
        self,
    ) -> Dict[str, Any]:
        """
        Return metrics suitable for monitoring systems.
        """

        uptime = max(
            0.0,
            time.time() - self._created_at,
        )

        updates = self._update_count

        failures = self._failure_count

        successes = max(
            0,
            updates - failures,
        )

        success_rate = (
            successes / updates
            if updates
            else 1.0
        )

        failure_rate = (
            failures / updates
            if updates
            else 0.0
        )

        return {

            "updates": updates,

            "successes": successes,

            "failures": failures,

            "success_rate": success_rate,

            "failure_rate": failure_rate,

            "uptime_seconds": uptime,

            "history_size": len(
                self._history
            ),

            "metadata_entries": len(
                self._metadata
            ),

            "attribute_entries": len(
                self._attributes
            ),

        }
    # ==============================================================================
    # Part 7. Validation
    # ==============================================================================

    def validate(
        self,
        *,
        raise_error: bool = False,
    ) -> bool:
        """
        Validate the complete TraceStatus object.

        Parameters
        ----------
        raise_error
            Raise an exception instead of returning False.

        Returns
        -------
        bool
            True if validation succeeds.
        """

        self._validation_count += 1
        self._statistics.validations += 1

        validators = (

            self.validate_status,

            self.validate_description,

            self.check_integrity,

        )

        for validator in validators:

            try:

                validator(
                    raise_error=True,
                )

            except Exception:

                self._failure_count += 1
                self._statistics.failures += 1

                if raise_error:
                    raise

                return False

        return True


    # ------------------------------------------------------------------------------

    def validate_status(
        self,
        *,
        raise_error: bool = False,
    ) -> bool:
        """
        Validate the current status code and runtime state.
        """

        try:

            if not isinstance(
                self._code,
                TraceStatusCode,
            ):
                raise StatusValidationError(
                    "invalid TraceStatusCode"
                )

            if not isinstance(
                self._state,
                TraceStatusState,
            ):
                raise StatusValidationError(
                    "invalid TraceStatusState"
                )

            if self._closed and self._active:
                raise StatusValidationError(
                    "closed status cannot be active"
                )

            if self._frozen and not self._enabled:
                raise StatusValidationError(
                    "frozen status must remain enabled"
                )

            return True

        except Exception:

            if raise_error:
                raise

            return False


    # ------------------------------------------------------------------------------

    def validate_description(
        self,
        *,
        raise_error: bool = False,
    ) -> bool:
        """
        Validate status description fields.
        """

        try:

            if not isinstance(
                self._description,
                str,
            ):
                raise StatusValidationError(
                    "description must be a string"
                )

            if not isinstance(
                self._message,
                str,
            ):
                raise StatusValidationError(
                    "message must be a string"
                )

            if not isinstance(
                self._reason,
                str,
            ):
                raise StatusValidationError(
                    "reason must be a string"
                )

            if not isinstance(
                self._source,
                str,
            ):
                raise StatusValidationError(
                    "source must be a string"
                )

            return True

        except Exception:

            if raise_error:
                raise

            return False


    # ------------------------------------------------------------------------------

    def check_integrity(
        self,
        *,
        raise_error: bool = False,
    ) -> bool:
        """
        Verify internal runtime integrity.
        """

        try:

            required = {

                "_statistics": self._statistics,

                "_metadata": self._metadata,

                "_attributes": self._attributes,

                "_context": self._context,

                "_history": self._history,

                "_hooks": self._hooks,

                "_callbacks": self._callbacks,

                "_cache": self._cache,

                "_lock": self._lock,

            }

            for name, value in required.items():

                if value is None:

                    raise StatusRuntimeError(
                        f"{name} is None"
                    )

            if not isinstance(
                self._metadata,
                dict,
            ):
                raise StatusRuntimeError(
                    "metadata must be dict"
                )

            if not isinstance(
                self._attributes,
                dict,
            ):
                raise StatusRuntimeError(
                    "attributes must be dict"
                )

            if not isinstance(
                self._context,
                dict,
            ):
                raise StatusRuntimeError(
                    "context must be dict"
                )

            if not isinstance(
                self._history,
                list,
            ):
                raise StatusRuntimeError(
                    "history must be list"
                )

            if not isinstance(
                self._callbacks,
                list,
            ):
                raise StatusRuntimeError(
                    "callbacks must be list"
                )

            if not isinstance(
                self._hooks,
                dict,
            ):
                raise StatusRuntimeError(
                    "hooks must be dict"
                )

            return True

        except Exception:

            if raise_error:
                raise

            return False
    # ==============================================================================
    # Part 8. Events & Hooks
    # ==============================================================================

    def before_update(
        self,
    ) -> None:
        """
        Hook executed immediately before a status update.

        This method emits the ``before_update`` event.
        """

        self.emit_event(
            "before_update",
            self,
        )


    # ------------------------------------------------------------------------------

    def after_update(
        self,
    ) -> None:
        """
        Hook executed immediately after a status update.

        This method emits the ``after_update`` event.
        """

        self.emit_event(
            "after_update",
            self,
        )


    # ------------------------------------------------------------------------------

    def add_hook(
        self,
        event: str,
        hook: StatusHook,
    ) -> "TraceStatus":
        """
        Register a hook for an event.

        Parameters
        ----------
        event
            Event name.

        hook
            Callable executed when the event is emitted.

        Returns
        -------
        TraceStatus
        """

        if not callable(hook):
            raise TypeError(
                "hook must be callable"
            )

        with self._lock:

            hooks = self._hooks.setdefault(
                str(event),
                [],
            )

            if hook not in hooks:

                hooks.append(
                    hook,
                )

        return self


    # ------------------------------------------------------------------------------

    def remove_hook(
        self,
        event: str,
        hook: StatusHook,
    ) -> "TraceStatus":
        """
        Remove a previously registered hook.

        Removing a missing hook is a no-op.
        """

        with self._lock:

            hooks = self._hooks.get(
                str(event),
            )

            if hooks is None:
                return self

            try:

                hooks.remove(
                    hook,
                )

            except ValueError:
                pass

            if not hooks:

                self._hooks.pop(
                    str(event),
                    None,
                )

        return self


    # ------------------------------------------------------------------------------

    def clear_hooks(
        self,
        event: Optional[str] = None,
    ) -> "TraceStatus":
        """
        Clear registered hooks.

        Parameters
        ----------
        event
            If provided, only hooks for the specified event
            are removed. Otherwise all hooks are removed.
        """

        with self._lock:

            if event is None:

                self._hooks.clear()

            else:

                self._hooks.pop(
                    str(event),
                    None,
                )

        return self


    # ------------------------------------------------------------------------------

    def emit_event(
        self,
        event: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Emit an event.

        Hook failures never interrupt runtime execution.
        Registered callbacks are notified after hooks.
        """

        hooks = list(

            self._hooks.get(
                str(event),
                [],
            )

        )

        for hook in hooks:

            try:

                hook(
                    self,
                    *args,
                    **kwargs,
                )

            except Exception:
                #
                # Hooks must never break tracing runtime.
                #
                continue

        self.notify_callbacks(

            str(event),

            *args,

            **kwargs,

        )
    # ==============================================================================
    # Part 9. Serialization Helpers
    # ==============================================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:
        """
        Serialize this TraceStatus into a dictionary.

        Returns
        -------
        Dict[str, Any]
            JSON-serializable representation.
        """

        return {

            # ------------------------------------------------------------------
            # Identity
            # ------------------------------------------------------------------

            "id": self._id,

            "uuid": str(self._uuid),

            "name": self._name,

            "version": self._version,

            # ------------------------------------------------------------------
            # Runtime
            # ------------------------------------------------------------------

            "code": self._code.value,

            "state": self._state.value,

            "description": self._description,

            "message": self._message,

            "reason": self._reason,

            "source": self._source,

            "enabled": self._enabled,

            "frozen": self._frozen,

            "closed": self._closed,

            "active": self._active,

            "created_at": self._created_at,

            "updated_at": self._updated_at,

            "last_update": self._last_update,

            # ------------------------------------------------------------------
            # Statistics
            # ------------------------------------------------------------------

            "statistics": {

                "updates": self._statistics.updates,

                "transitions": self._statistics.transitions,

                "validations": self._statistics.validations,

                "failures": self._statistics.failures,

                "created_at": self._statistics.created_at,

                "updated_at": self._statistics.updated_at,

            },

            "update_count": self._update_count,

            "transition_count": self._transition_count,

            "validation_count": self._validation_count,

            "failure_count": self._failure_count,

            # ------------------------------------------------------------------
            # Metadata
            # ------------------------------------------------------------------

            "metadata": deepcopy(
                self._metadata
            ),

            "attributes": deepcopy(
                self._attributes
            ),

            "context": deepcopy(
                self._context
            ),

            "tags": list(
                self._tags
            ),

            "flags": int(
                self._flags
            ),

        }


    # ------------------------------------------------------------------------------

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "TraceStatus":
        """
        Create a TraceStatus from a dictionary.
        """

        obj = cls(

            code=TraceStatusCode(

                data.get(
                    "code",
                    TraceStatusCode.UNSET.value,
                )

            ),

            description=data.get(
                "description",
                DEFAULT_DESCRIPTION,
            ),

            message=data.get(
                "message",
                DEFAULT_MESSAGE,
            ),

            reason=data.get(
                "reason",
                DEFAULT_REASON,
            ),

            source=data.get(
                "source",
                DEFAULT_SOURCE,
            ),

            metadata=deepcopy(

                data.get(
                    "metadata",
                    {},
                )

            ),

            attributes=deepcopy(

                data.get(
                    "attributes",
                    {},
                )

            ),

        )

        obj._state = TraceStatusState(

            data.get(
                "state",
                TraceStatusState.CREATED.value,
            )

        )

        obj._enabled = data.get(
            "enabled",
            True,
        )

        obj._frozen = data.get(
            "frozen",
            False,
        )

        obj._closed = data.get(
            "closed",
            False,
        )

        obj._active = data.get(
            "active",
            False,
        )

        obj._created_at = data.get(
            "created_at",
            obj._created_at,
        )

        obj._updated_at = data.get(
            "updated_at",
            obj._updated_at,
        )

        obj._last_update = data.get(
            "last_update",
        )

        statistics = data.get(
            "statistics",
            {},
        )

        obj._statistics.updates = statistics.get(
            "updates",
            0,
        )

        obj._statistics.transitions = statistics.get(
            "transitions",
            0,
        )

        obj._statistics.validations = statistics.get(
            "validations",
            0,
        )

        obj._statistics.failures = statistics.get(
            "failures",
            0,
        )

        obj._statistics.created_at = statistics.get(
            "created_at",
            obj._statistics.created_at,
        )

        obj._statistics.updated_at = statistics.get(
            "updated_at",
            obj._statistics.updated_at,
        )

        obj._update_count = data.get(
            "update_count",
            0,
        )

        obj._transition_count = data.get(
            "transition_count",
            0,
        )

        obj._validation_count = data.get(
            "validation_count",
            0,
        )

        obj._failure_count = data.get(
            "failure_count",
            0,
        )

        obj._context = deepcopy(

            data.get(
                "context",
                {},
            )

        )

        obj._tags = list(

            data.get(
                "tags",
                [],
            )

        )

        obj._flags = TraceStatusFlag(

            data.get(
                "flags",
                int(TraceStatusFlag.NONE),
            )

        )

        return obj


    # ------------------------------------------------------------------------------

    def to_json(
        self,
        *,
        indent: Optional[int] = 4,
        ensure_ascii: bool = False,
        sort_keys: bool = False,
    ) -> str:
        """
        Serialize this TraceStatus into a JSON string.
        """

        return json.dumps(

            self.to_dict(),

            indent=indent,

            ensure_ascii=ensure_ascii,

            sort_keys=sort_keys,

        )


    # ------------------------------------------------------------------------------

    @classmethod
    def from_json(
        cls,
        data: Union[str, bytes],
    ) -> "TraceStatus":
        """
        Deserialize a TraceStatus from JSON.
        """

        if isinstance(
            data,
            bytes,
        ):

            data = data.decode(
                "utf-8",
            )

        return cls.from_dict(

            json.loads(
                data,
            )

        )
    # ==============================================================================
    # Part 10. Utilities
    # ==============================================================================

    def has_error(self) -> bool:
        """
        Return True if the current status represents an error.

        Returns
        -------
        bool
        """

        return self._code in {

            TraceStatusCode.ERROR,

            TraceStatusCode.INTERNAL_ERROR,

            TraceStatusCode.TIMEOUT,

            TraceStatusCode.CANCELLED,

        }


    # ------------------------------------------------------------------------------

    def has_description(self) -> bool:
        """
        Return True if a non-empty description exists.

        Returns
        -------
        bool
        """

        return bool(

            self._description.strip()

        )


    # ------------------------------------------------------------------------------

    def clear_description(self) -> "TraceStatus":
        """
        Clear the status description, message and reason.

        Returns
        -------
        TraceStatus
        """

        self._description = DEFAULT_DESCRIPTION

        self._message = DEFAULT_MESSAGE

        self._reason = DEFAULT_REASON

        self.touch()

        return self


    # ------------------------------------------------------------------------------

    def age(self) -> float:
        """
        Return the age of this TraceStatus object in seconds.

        Returns
        -------
        float
        """

        return max(

            0.0,

            time.time() - self._created_at,

        )


    # ------------------------------------------------------------------------------

    def touch(self) -> "TraceStatus":
        """
        Update the modification timestamp.

        This method does not modify the status code.

        Returns
        -------
        TraceStatus
        """

        now = time.time()

        self._updated_at = now

        self._last_update = now

        self._statistics.updated_at = now

        return self


    # ------------------------------------------------------------------------------

    def timestamp(self) -> Dict[str, Optional[float]]:
        """
        Return runtime timestamps.

        Returns
        -------
        Dict[str, Optional[float]]
        """

        return {

            "created_at": self._created_at,

            "updated_at": self._updated_at,

            "last_update": self._last_update,

            "age": self.age(),

            "uptime": self.age(),

        }
    # ==============================================================================
    # Part 11. Python Protocols
    # ==============================================================================

    def __repr__(self) -> str:
        """
        Developer-friendly representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"id={self._id!r}, "
            f"code={self._code.value!r}, "
            f"state={self._state.value!r}, "
            f"enabled={self._enabled!r})"
        )


    # ------------------------------------------------------------------------------

    def __str__(self) -> str:
        """
        Human-readable representation.
        """

        description = self._description.strip()

        if description:

            return (
                f"{self._code.value}"
                f" ({description})"
            )

        return self._code.value


    # ------------------------------------------------------------------------------

    def __bool__(self) -> bool:
        """
        Truth value of TraceStatus.

        A status object is considered available only when it is enabled,
        not frozen, and not closed.
        """

        return (

            self._enabled

            and not self._frozen

            and not self._closed

        )


    # ------------------------------------------------------------------------------

    def __copy__(self) -> "TraceStatus":
        """
        Create a shallow copy.
        """

        cls = self.__class__

        obj = cls.__new__(cls)

        obj.__dict__.update(
            self.__dict__
        )

        return obj


    # ------------------------------------------------------------------------------

    def __deepcopy__(
        self,
        memo: Dict[int, Any],
    ) -> "TraceStatus":
        """
        Create a deep copy.

        Thread locks are recreated instead of copied.
        """

        cls = self.__class__

        obj = cls.__new__(cls)

        memo[id(self)] = obj

        for key, value in self.__dict__.items():

            if key == "_lock":

                setattr(
                    obj,
                    key,
                    threading.RLock(),
                )

            else:

                setattr(
                    obj,
                    key,
                    deepcopy(
                        value,
                        memo,
                    ),
                )

        return obj


    # ------------------------------------------------------------------------------

    def __eq__(
        self,
        other: object,
    ) -> bool:
        """
        Equality based on unique identifier.
        """

        if not isinstance(
            other,
            TraceStatus,
        ):

            return NotImplemented

        return self._id == other._id


    # ------------------------------------------------------------------------------

    def __hash__(self) -> int:
        """
        Hash based on unique identifier.
        """

        return hash(
            self._id
        )
# ==============================================================================
# Part 12. Public API
# ==============================================================================

__all__ = [

    # ------------------------------------------------------------------
    # Constants
    # ------------------------------------------------------------------

    "STATUS_VERSION",

    "DEFAULT_STATUS_NAME",

    "DEFAULT_DESCRIPTION",

    "DEFAULT_MESSAGE",

    "DEFAULT_REASON",

    "DEFAULT_SOURCE",

    "DEFAULT_HISTORY_LIMIT",

    # ------------------------------------------------------------------
    # Exceptions
    # ------------------------------------------------------------------

    "TraceStatusError",

    "StatusValidationError",

    "StatusRuntimeError",

    "StatusClosedError",

    "StatusFrozenError",

    # ------------------------------------------------------------------
    # Enums
    # ------------------------------------------------------------------

    "TraceStatusCode",

    "TraceStatusState",

    "TraceStatusFlag",

    # ------------------------------------------------------------------
    # Dataclasses
    # ------------------------------------------------------------------

    "TraceStatusStatistics",

    "TraceStatusSnapshotData",

    "TraceStatusRecord",

    # ------------------------------------------------------------------
    # Main Class
    # ------------------------------------------------------------------

    "TraceStatus",

] 
__all__ = [

    "Status",

    "ExecutionPhase",

]                                               