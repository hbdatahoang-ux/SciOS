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


Contract
--------

ctx.result
    |
    v
ExecutionResult


ctx.result.value
    |
    v
Actual execution payload


Python 3.11+
"""

from __future__ import annotations


from copy import deepcopy

from dataclasses import (
    dataclass,
    field,
)

from datetime import (
    datetime,
    timezone,
)

from time import perf_counter

from typing import (
    TYPE_CHECKING,
    Any,
)

from uuid import uuid4


from .state import RuntimeState


if TYPE_CHECKING:

    from .result import ExecutionResult



__all__ = [
    "ExecutionContext",
]



# ==========================================================
# Helpers
# ==========================================================


def utc_now() -> str:
    """
    Return current UTC timestamp.
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
    Runtime execution state container.

    Shared between:

        ExecutionEngine
              |
              v
          Pipeline
              |
              v
            Stage


    Lifecycle:

        created
            |
            v
        running
          /    \
         v      v
    completed  failed
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

    """
    Canonical execution result.

    Contract:

        ctx.result
            |
            v
        ExecutionResult


        ctx.result.value
            |
            v
        Actual payload
    """

    _result: ExecutionResult | None = field(
    default=None,
    repr=False,
)



    """
    Internal execution result alias.

    Used for compatibility with
    advanced runtime components.
    """

    _execution_result: ExecutionResult | None = field(
        default=None,
        repr=False,
    )



    # ======================================================
    # Error
    # ======================================================

    error: BaseException | None = None



    # ======================================================
    # Runtime State
    # ======================================================

    state: RuntimeState = "created"



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
    # Properties
    # ==========================================================

    @property
    def status(self) -> RuntimeState:
        """
        Compatibility alias for runtime state.
        """

        return self.state


    @status.setter
    def status(
        self,
        value: RuntimeState,
    ) -> None:
        self.state = value


    @property
    def running(
        self,
    ) -> bool:
        """
        True if execution is currently running.
        """

        return self.state == "running"


    @property
    def completed(
        self,
    ) -> bool:
        """
        True if execution completed successfully.
        """

        return self.state == "completed"


    @property
    def failed(
        self,
    ) -> bool:
        """
        True if execution failed.
        """

        return self.state == "failed"


    @property
    def done(
        self,
    ) -> bool:
        """
        True if execution reached a terminal state.
        """

        return self.completed or self.failed


    @property
    def succeeded(
        self,
    ) -> bool:
        """
        Alias for completed.
        """

        return self.completed


    @property
    def has_result(
        self,
    ) -> bool:
        """
        Whether an execution result exists.
        """

        return self._result is not None


    @property
    def result(
        self,
    ):
        """
        Canonical execution result.

        Returns
        -------
        ExecutionResult | None
        """

        return self._result


    @result.setter
    def result(
        self,
        value,
    ) -> None:
        """
        Accept either an ExecutionResult or a raw payload.
        """

        from .result import ExecutionResult

        if value is None:

            self._result = None

        elif isinstance(
            value,
            ExecutionResult,
        ):

            self._result = value

        else:

            self._result = ExecutionResult.ok(
                value
            )


    @property
    def result_value(
        self,
    ) -> Any:
        """
        Raw execution payload.

        Equivalent to:

            ctx.result.value
        """

        if self._result is None:
            return None

        return self._result.value


    @property
    def value(
        self,
    ) -> Any:
        """
        Shortcut for the raw execution payload.
        """

        if self._result is None:
            return None

        return self._result.value


    @property
    def error(
        self,
    ):
        """
        Execution error, if any.
        """

        if self._result is None:
            return None

        return self._result.error


    @property
    def success(
        self,
    ) -> bool:
        """
        Whether execution succeeded.
        """

        return (
            self._result is not None
            and self._result.success
        )


    @property
    def duration(
        self,
    ) -> float | None:
        """
        Execution duration in seconds.
        """

        if self._result is not None:

            result_duration = getattr(
                self._result,
                "duration",
                None,
            )

            if result_duration is not None:
                return result_duration

        if (
            self._start_perf is None
            or self._finish_perf is None
        ):
            return None

        return (
            self._finish_perf
            - self._start_perf
        )
# ==========================================================
# Lifecycle
# ==========================================================


    def start(
        self,
    ) -> "ExecutionContext":
        """
        Start execution lifecycle.

        Transition:

            created
                |
                v
            running
        """

        self.state = "running"

        self.started_at = utc_now()

        self._start_perf = perf_counter()


        self.add_event(
            "execution.started"
        )


        self._record_state(
            "running"
        )


        return self



    def finish(
        self,
        result: Any,
    ) -> "ExecutionContext":
        """
        Complete execution successfully.

        Accept:

            raw value
            ExecutionResult
        """

        from .result import ExecutionResult


        if not isinstance(
            result,
            ExecutionResult,
        ):

            result = ExecutionResult.ok(
                result
            )


        self.result = result

        self._execution_result = result


        self.state = "completed"


        self.finished_at = utc_now()

        self._finish_perf = perf_counter()


        self.add_event(
            "execution.completed"
        )


        self._record_state(
            "completed"
        )


        return self



    def fail(
        self,
        error: BaseException,
    ) -> "ExecutionContext":
        """
        Mark execution failed.

        Transition:

            running
                |
                v
             failed
        """

        from .result import ExecutionResult


        self.error = error


        self.result = ExecutionResult.fail(
            error
        )

        self._execution_result = self.result


        self.state = "failed"


        self.finished_at = utc_now()

        self._finish_perf = perf_counter()


        self.add_event(
            "execution.failed"
        )


        self._record_state(
            "failed"
        )


        return self



    def reset(
        self,
        *,
        clear_logs: bool = False,
    ) -> "ExecutionContext":
        """
        Reset context lifecycle.

        Transition:

            any state
                |
                v
             created
        """

        self.result = None

        self._execution_result = None


        self.error = None


        self.state = "created"


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
        Attach canonical execution result.

        Accepts:

            • ExecutionResult
            • raw payload

        Always stores an ExecutionResult internally.
        """

        from .result import ExecutionResult

        if result is None:

            self._result = None

        elif isinstance(
            result,
            ExecutionResult,
        ):

            self._result = result

        else:

            self._result = ExecutionResult.ok(
                result
            )

        return self



    def get_result(
        self,
        default: Any = None,
    ):
        """
        Return canonical ExecutionResult.

        Returns
        -------
        ExecutionResult | default
        """

        if self._result is None:

            return default

        return self._result



    def get_execution_result(
        self,
    ):
        """
        Return canonical ExecutionResult.

        Alias of get_result().
        """

        return self._result



    @property
    def execution_result(
        self,
    ):
        """
        Compatibility alias.

        Returns
        -------
        ExecutionResult | None
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
        Append plain runtime log.

        Compatible with:

            ctx.logs
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
        Append structured runtime log.
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
        Add runtime event.
        """

        self.events.append(
            event
        )


        return self



    def has_event(
        self,
        event: str,
    ) -> bool:
        """
        Check event existence.
        """

        return event in self.events



    def clear_events(
        self,
    ) -> "ExecutionContext":
        """
        Clear runtime events.
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
        Record lifecycle transition.
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
        Return immutable history copy.
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
        Set metadata value.
        """

        self.metadata[key] = value


        return self



    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Get metadata value.
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
        Clear metadata.
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
        Store execution artifact.
        """

        self.artifacts[name] = value


        return self



    def get_artifact(
        self,
        name: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve execution artifact.
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
        Remove artifact.
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
        Clear all artifacts.
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
        Add unique runtime tag.
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
        Remove runtime tag.
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
        Clear all tags.
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
        Attach runtime worker identifier.
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
        Create deep copy of execution context.

        Used for:

            snapshot
            rollback
            branching execution
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
        Serialize execution context.

        Returns plain dictionary.
        """

        return {

            "id":
                self.id,


            "task":
                self.task,


            "state":
                self.state,


            "status":
                self.status,


            "worker":
                self.worker,


            "result":
                (
                    self.result.to_dict()
                    if self.result
                    else None
                ),


            "value":
                self.value,


            "error":
                (
                    str(self.error)
                    if self.error
                    else None
                ),


            "metadata":
                deepcopy(
                    self.metadata
                ),


            "logs":
                deepcopy(
                    self.logs
                ),


            "events":
                list(
                    self.events
                ),


            "history":
                deepcopy(
                    self.history
                ),


            "tags":
                list(
                    self.tags
                ),


            "artifacts":
                deepcopy(
                    self.artifacts
                ),


            "created_at":
                self.created_at,


            "started_at":
                self.started_at,


            "finished_at":
                self.finished_at,


            "duration":
                self.duration,

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
            f"id='{self.id}', "
            f"state='{self.state}', "
            f"task={self.task!r}, "
            f"worker={self.worker!r}"
            ")"
        )



    def __str__(
        self,
    ) -> str:
        """
        Human readable representation.
        """

        return (
            f"ExecutionContext<"
            f"state={self.state}, "
            f"task={self.task!r}, "
            f"worker={self.worker!r}"
            ">"
        )