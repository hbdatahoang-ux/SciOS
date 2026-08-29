"""
SciOS Runtime Execution Context
===============================

Canonical execution context shared across SciOS Runtime.

Execution flow:

    ExecutionEngine
            |
            v
        Pipeline
            |
            v
          Stage


Core contract
-------------

ctx.result
    |
    v
ExecutionResult


ctx.result.value
    |
    v
Actual execution payload


Lifecycle
---------

    created
       |
       v
    running
     /    \
    v      v
completed failed


Design principles
-----------------

- One canonical execution result.
- One canonical execution error.
- Explicit lifecycle state.
- Monotonic execution timing.
- Fluent mutation API.
- Deep-copy snapshots.
- Plain-dictionary serialization.
- No duplicated state between public aliases.
- Python 3.11+.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from time import perf_counter
from typing import TYPE_CHECKING, Any
from uuid import uuid4


if TYPE_CHECKING:
    from .result import ExecutionResult


__all__ = [
    "ExecutionContext",
]


# ==========================================================
# Constants
# ==========================================================


STATE_CREATED = "created"
STATE_RUNNING = "running"
STATE_COMPLETED = "completed"
STATE_FAILED = "failed"


TERMINAL_STATES = frozenset(
    {
        STATE_COMPLETED,
        STATE_FAILED,
    }
)


# ==========================================================
# Helpers
# ==========================================================


def utc_now() -> str:
    """
    Return the current UTC timestamp as an ISO-8601 string.
    """

    return datetime.now(
        timezone.utc
    ).isoformat()


# ==========================================================
# Execution Context
# ==========================================================


@dataclass(
    slots=True,
)
class ExecutionContext:
    """
    Canonical SciOS Runtime execution context.

    The context is shared across:

        ExecutionEngine
              |
              v
          Pipeline
              |
              v
            Stage

    It contains:

    - task identity
    - lifecycle state
    - execution result
    - execution error
    - timing information
    - metadata
    - logs
    - events
    - history
    - tags
    - artifacts
    - worker information

    The canonical result contract is:

        ctx.result
            |
            v
        ExecutionResult

        ctx.result.value
            |
            v
        actual execution payload
    """

    # ======================================================
    # Task
    # ======================================================

    task: Any = None

    # ======================================================
    # Identity
    # ======================================================

    id: str = field(
        default_factory=lambda: str(uuid4())
    )

    # ======================================================
    # Metadata
    # ======================================================

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    # ======================================================
    # Result
    # ======================================================

    _result: ExecutionResult | None = field(
        default=None,
        repr=False,
    )

    # Compatibility/internal alias.
    #
    # This is intentionally kept for existing runtime
    # components, but is always synchronized with _result.
    _execution_result: ExecutionResult | None = field(
        default=None,
        repr=False,
    )

    # ======================================================
    # Error
    # ======================================================

    # IMPORTANT:
    #
    # Do NOT declare a public "error" dataclass field.
    #
    # The public error API is implemented as a property below.
    # Using both a dataclass field and a property named "error"
    # creates the exact property-object corruption previously
    # observed in to_dict().
    _error: BaseException | None = field(
        default=None,
        repr=False,
    )

    # ======================================================
    # Runtime State
    # ======================================================

    state: str = STATE_CREATED

    # ======================================================
    # Worker
    # ======================================================

    worker: str | None = None

    # ======================================================
    # Diagnostics
    # ======================================================

    logs: list[Any] = field(
        default_factory=list
    )

    events: list[str] = field(
        default_factory=list
    )

    history: list[dict[str, Any]] = field(
        default_factory=list
    )

    tags: list[str] = field(
        default_factory=list
    )

    artifacts: dict[str, Any] = field(
        default_factory=dict
    )

    # ======================================================
    # Timing
    # ======================================================

    created_at: str = field(
        default_factory=utc_now
    )

    started_at: str | None = None

    finished_at: str | None = None

    _start_perf: float | None = field(
        default=None,
        repr=False,
    )

    _finish_perf: float | None = field(
        default=None,
        repr=False,
    )

    # ==========================================================
    # State Properties
    # ==========================================================

    @property
    def status(self) -> str:
        """
        Compatibility alias for runtime state.

        Returns
        -------
        str
            Current lifecycle state.
        """

        return self.state

    @status.setter
    def status(
        self,
        value: str,
    ) -> None:
        self.state = str(value)

    @property
    def running(self) -> bool:
        """
        Whether execution is currently running.
        """

        return self.state == STATE_RUNNING

    @property
    def completed(self) -> bool:
        """
        Whether execution completed successfully.
        """

        return self.state == STATE_COMPLETED

    @property
    def failed(self) -> bool:
        """
        Whether execution failed.
        """

        return self.state == STATE_FAILED

    @property
    def done(self) -> bool:
        """
        Whether execution reached a terminal state.
        """

        return self.state in TERMINAL_STATES

    @property
    def succeeded(self) -> bool:
        """
        Alias for successful completion.
        """

        return self.completed

    # ==========================================================
    # Error Properties
    # ==========================================================

    @property
    def error(self) -> BaseException | None:
        """
        Return the canonical execution error.

        Error ownership is kept by the context and mirrored into
        the canonical ExecutionResult when execution fails.
        """

        return self._error

    @error.setter
    def error(
        self,
        value: BaseException | None,
    ) -> None:
        self._error = value

    # ==========================================================
    # Result Properties
    # ==========================================================

    @property
    def has_result(self) -> bool:
        """
        Whether a canonical execution result exists.
        """

        return self._result is not None

    @property
    def result(self) -> ExecutionResult | None:
        """
        Return the canonical ExecutionResult.
        """

        return self._result

    @result.setter
    def result(
        self,
        value: Any,
    ) -> None:
        """
        Set the canonical execution result.

        Accepted values:

        - None
        - ExecutionResult
        - raw execution payload

        Raw values are automatically wrapped using
        ExecutionResult.ok().
        """

        from .result import ExecutionResult

        if value is None:
            self._result = None
            self._execution_result = None
            return

        if isinstance(
            value,
            ExecutionResult,
        ):
            result = value
        else:
            result = ExecutionResult.ok(
                value
            )

        self._result = result
        self._execution_result = result

    @property
    def execution_result(self) -> ExecutionResult | None:
        """
        Compatibility alias for result.
        """

        return self._result

    @execution_result.setter
    def execution_result(
        self,
        value: Any,
    ) -> None:
        self.result = value

    @property
    def result_value(self) -> Any:
        """
        Return the raw execution payload.

        Equivalent to:

            ctx.result.value
        """

        if self._result is None:
            return None

        return self._result.value

    @property
    def value(self) -> Any:
        """
        Shortcut for the raw execution payload.
        """

        return self.result_value

    @property
    def success(self) -> bool:
        """
        Whether the canonical execution result succeeded.
        """

        return (
            self._result is not None
            and self._result.success
        )

    # ==========================================================
    # Timing Properties
    # ==========================================================

    @property
    def duration(self) -> float | None:
        """
        Return execution duration in seconds.

        Priority:

        1. measured monotonic runtime
        2. ExecutionResult.duration
        3. None
        """

        if (
            self._start_perf is not None
            and self._finish_perf is not None
        ):
            return (
                self._finish_perf
                - self._start_perf
            )

        if self._result is not None:
            return getattr(
                self._result,
                "duration",
                None,
            )

        return None

    # ==========================================================
    # Lifecycle
    # ==========================================================

    def start(
        self,
    ) -> "ExecutionContext":
        """
        Start execution.

        Transition:

            created -> running

        Repeated start() calls are rejected.
        """

        if self.state != STATE_CREATED:
            raise RuntimeError(
                "ExecutionContext can only start "
                f"from '{STATE_CREATED}', "
                f"current state is '{self.state}'."
            )

        self.state = STATE_RUNNING

        self.started_at = utc_now()

        self._start_perf = perf_counter()

        self.add_event(
            "execution.started"
        )

        self._record_state(
            STATE_RUNNING
        )

        return self

    def finish(
        self,
        result: Any,
    ) -> "ExecutionContext":
        """
        Complete execution successfully.

        Accepts:

        - raw payload
        - ExecutionResult

        Transition:

            running -> completed
        """

        from .result import ExecutionResult

        if self.state != STATE_RUNNING:
            raise RuntimeError(
                "ExecutionContext can only finish "
                f"from '{STATE_RUNNING}', "
                f"current state is '{self.state}'."
            )

        if not isinstance(
            result,
            ExecutionResult,
        ):
            result = ExecutionResult.ok(
                result
            )

        self._finish_perf = perf_counter()

        measured_duration = (
            self._finish_perf
            - self._start_perf
            if self._start_perf is not None
            else getattr(
                result,
                "duration",
                0.0,
            )
        )

        # ExecutionResult is mutable in the current SciOS
        # contract, so keep its duration synchronized with
        # the context's measured duration.
        result.duration = measured_duration

        self.result = result

        self.error = None

        self.state = STATE_COMPLETED

        self.finished_at = utc_now()

        self.add_event(
            "execution.completed"
        )

        self._record_state(
            STATE_COMPLETED
        )

        return self

    def fail(
        self,
        error: BaseException,
    ) -> "ExecutionContext":
        """
        Mark execution as failed.

        Accepts any BaseException.

        Transition:

            running -> failed
        """

        from .result import ExecutionResult

        if not isinstance(
            error,
            BaseException,
        ):
            raise TypeError(
                "error must be a BaseException"
            )

        if self.state != STATE_RUNNING:
            raise RuntimeError(
                "ExecutionContext can only fail "
                f"from '{STATE_RUNNING}', "
                f"current state is '{self.state}'."
            )

        self._finish_perf = perf_counter()

        measured_duration = (
            self._finish_perf
            - self._start_perf
            if self._start_perf is not None
            else 0.0
        )

        result = ExecutionResult.fail(
            error,
            duration=measured_duration,
        )

        self.error = error

        self.result = result

        self.state = STATE_FAILED

        self.finished_at = utc_now()

        self.add_event(
            "execution.failed"
        )

        self._record_state(
            STATE_FAILED
        )

        return self

    def reset(
        self,
        *,
        clear_logs: bool = False,
    ) -> "ExecutionContext":
        """
        Reset execution lifecycle.

        Transition:

            any state -> created

        Persistent identity and task are retained.

        Metadata is retained because it represents context
        configuration rather than execution output.

        Logs are retained by default.
        """

        self.result = None

        self.error = None

        self.state = STATE_CREATED

        self.worker = None

        self.started_at = None

        self.finished_at = None

        self._start_perf = None

        self._finish_perf = None

        self.events.clear()

        self.history.clear()

        self.tags.clear()

        self.artifacts.clear()

        if clear_logs:
            self.logs.clear()

        return self

    # ==========================================================
    # Result API
    # ==========================================================

    def set_result(
        self,
        result: Any,
    ) -> "ExecutionContext":
        """
        Attach a canonical execution result.

        Accepts:

        - None
        - ExecutionResult
        - raw payload
        """

        self.result = result

        return self

    def get_result(
        self,
        default: Any = None,
    ) -> ExecutionResult | Any:
        """
        Return the canonical ExecutionResult.

        If no result exists, return default.
        """

        if self._result is None:
            return default

        return self._result

    def get_execution_result(
        self,
    ) -> ExecutionResult | None:
        """
        Return the canonical ExecutionResult.
        """

        return self._result

    # ==========================================================
    # Logging API
    # ==========================================================

    def log(
        self,
        message: str,
        *,
        level: str = "INFO",
    ) -> "ExecutionContext":
        """
        Append a plain runtime log.

        The level argument is accepted for API compatibility.
        Structured logging should use structured_log().
        """

        self.logs.append(
            message
        )

        return self

    def structured_log(
        self,
        message: str,
        *,
        level: str = "INFO",
    ) -> "ExecutionContext":
        """
        Append a structured runtime log.
        """

        self.logs.append(
            {
                "time": utc_now(),
                "level": level,
                "message": message,
            }
        )

        return self

    # ==========================================================
    # Events API
    # ==========================================================

    def add_event(
        self,
        event: str,
    ) -> "ExecutionContext":
        """
        Add a runtime event name.

        Events are intentionally stored as strings in the
        ExecutionContext. Rich RuntimeEvent objects belong to
        the runtime event bus/event layer.
        """

        event_name = (
            event.name
            if hasattr(event, "name")
            else str(event)
        )

        self.events.append(
            event_name
        )

        return self

    def has_event(
        self,
        event: str,
    ) -> bool:
        """
        Check whether an event exists.
        """

        event_name = (
            event.name
            if hasattr(event, "name")
            else str(event)
        )

        return event_name in self.events

    def clear_events(
        self,
    ) -> "ExecutionContext":
        """
        Clear all runtime events.
        """

        self.events.clear()

        return self

    # ==========================================================
    # History API
    # ==========================================================

    def _record_state(
        self,
        state: str,
    ) -> None:
        """
        Record a lifecycle transition.
        """

        self.history.append(
            {
                "state": state,
                "time": utc_now(),
            }
        )

    def history_snapshot(
        self,
    ) -> list[dict[str, Any]]:
        """
        Return a deep copy of lifecycle history.
        """

        return deepcopy(
            self.history
        )

    # ==========================================================
    # Metadata API
    # ==========================================================

    def set(
        self,
        key: str,
        value: Any,
    ) -> "ExecutionContext":
        """
        Set a metadata value.
        """

        self.metadata[key] = value

        return self

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve a metadata value.
        """

        return self.metadata.get(
            key,
            default,
        )

    def update_metadata(
        self,
        values: dict[str, Any],
    ) -> "ExecutionContext":
        """
        Update metadata in bulk.
        """

        self.metadata.update(
            values
        )

        return self

    def clear_metadata(
        self,
    ) -> "ExecutionContext":
        """
        Clear all metadata.
        """

        self.metadata.clear()

        return self

    # ==========================================================
    # Artifact API
    # ==========================================================

    def set_artifact(
        self,
        name: str,
        value: Any,
    ) -> "ExecutionContext":
        """
        Store an execution artifact.
        """

        self.artifacts[name] = value

        return self

    def get_artifact(
        self,
        name: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve an execution artifact.
        """

        return self.artifacts.get(
            name,
            default,
        )

    def remove_artifact(
        self,
        name: str,
    ) -> "ExecutionContext":
        """
        Remove an execution artifact.
        """

        self.artifacts.pop(
            name,
            None,
        )

        return self

    def clear_artifacts(
        self,
    ) -> "ExecutionContext":
        """
        Clear all execution artifacts.
        """

        self.artifacts.clear()

        return self

    # ==========================================================
    # Tags API
    # ==========================================================

    def add_tag(
        self,
        tag: str,
    ) -> "ExecutionContext":
        """
        Add a unique runtime tag.
        """

        if tag not in self.tags:
            self.tags.append(
                tag
            )

        return self

    def remove_tag(
        self,
        tag: str,
    ) -> "ExecutionContext":
        """
        Remove a runtime tag.
        """

        if tag in self.tags:
            self.tags.remove(
                tag
            )

        return self

    def has_tag(
        self,
        tag: str,
    ) -> bool:
        """
        Check tag existence.
        """

        return tag in self.tags

    def clear_tags(
        self,
    ) -> "ExecutionContext":
        """
        Clear all runtime tags.
        """

        self.tags.clear()

        return self

    # ==========================================================
    # Worker API
    # ==========================================================

    def attach_worker(
        self,
        worker: str,
    ) -> "ExecutionContext":
        """
        Attach a runtime worker identifier.
        """

        self.worker = worker

        return self

    # ==========================================================
    # Copy API
    # ==========================================================

    def copy(
        self,
    ) -> "ExecutionContext":
        """
        Create a deep copy of the execution context.

        Useful for:

        - snapshots
        - rollback
        - branching execution
        - speculative execution
        """

        return deepcopy(
            self
        )

    # ==========================================================
    # Serialization API
    # ==========================================================

    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Serialize the context into a plain dictionary.

        The returned structure contains no RuntimeState or
        ExecutionResult objects at the top-level result fields.
        """

        return {
            "id": self.id,

            "task": self.task,

            "state": self.state,

            "status": self.status,

            "worker": self.worker,

            "result": (
                self.result.to_dict()
                if self.result is not None
                else None
            ),

            "value": self.value,

            "error": (
                str(self.error)
                if self.error is not None
                else None
            ),

            "metadata": deepcopy(
                self.metadata
            ),

            "logs": deepcopy(
                self.logs
            ),

            "events": list(
                self.events
            ),

            "history": deepcopy(
                self.history
            ),

            "tags": list(
                self.tags
            ),

            "artifacts": deepcopy(
                self.artifacts
            ),

            "created_at": self.created_at,

            "started_at": self.started_at,

            "finished_at": self.finished_at,

            "duration": self.duration,
        }

    # ==========================================================
    # Representation API
    # ==========================================================

    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.
        """

        return (
            "ExecutionContext("
            f"id={self.id!r}, "
            f"state={self.state!r}, "
            f"task={self.task!r}, "
            f"worker={self.worker!r}"
            ")"
        )

    def __str__(
        self,
    ) -> str:
        """
        Human-readable representation.
        """

        return (
            "ExecutionContext<"
            f"state={self.state}, "
            f"task={self.task!r}, "
            f"worker={self.worker!r}"
            ">"
        )