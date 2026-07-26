"""
SciOS Runtime Execution Context
===============================

Canonical execution context shared across SciOS Runtime.

The ExecutionContext is the runtime state container
passing through:

    ExecutionEngine
            |
            v
        Pipeline
            |
            v
          Stage


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
    Current UTC timestamp.
    """

    return datetime.now(
        timezone.utc
    ).isoformat()



# ==========================================================
# Execution Context
# ==========================================================


@dataclass(slots=True)
class ExecutionContext:
    """
    Runtime execution context.

    Lifecycle:

        created
            |
            v
        running
            |
       +------------+
       |            |
       v            v
   completed      failed
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
    Public result.

    Compatibility:
        ctx.result == "ok"

    """

    result: Any = None



    """
    Rich internal result.

    Contains:
        status
        duration
        error
        metadata
    """

    _execution_result: ExecutionResult | None = field(
        default=None,
        repr=False,
    )



    error: BaseException | None = None



    # ======================================================
    # Runtime
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



    # ======================================================
    # State Properties
    # ======================================================

    @property
    def status(
        self,
    ) -> RuntimeState:

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

        return self.state == "running"



    @property
    def completed(
        self,
    ) -> bool:

        return self.state == "completed"



    @property
    def succeeded(
        self,
    ) -> bool:

        return self.completed



    @property
    def failed(
        self,
    ) -> bool:

        return self.state == "failed"



    @property
    def done(
        self,
    ) -> bool:

        return (
            self.completed
            or
            self.failed
        )



    @property
    def has_result(
        self,
    ) -> bool:

        return self.result is not None



    @property
    def duration(
        self,
    ) -> float | None:

        if (
            self._start_perf is None
            or self._finish_perf is None
        ):

            return None


        return (
            self._finish_perf
            -
            self._start_perf
        )



    # ======================================================
    # Events
    # ======================================================

    def add_event(
        self,
        event: str,
    ) -> None:

        self.events.append(
            event
        )



    def has_event(
        self,
        event: str,
    ) -> bool:

        return event in self.events



    # ======================================================
    # Lifecycle
    # ======================================================

    def start(
        self,
    ) -> None:

        if self.running:

            return


        self.state = "running"

        self.started_at = utc_now()

        self._start_perf = perf_counter()


        self._record_state(
            "running"
        )



    def finish(
        self,
        result: Any,
    ) -> None:
        """
        Complete execution.
        """

        self.set_result(
            result
        )


        self.state = "completed"


        self.finished_at = utc_now()


        self._finish_perf = perf_counter()


        self._record_state(
            "completed"
        )



    def fail(
        self,
        error: BaseException,
    ) -> None:


        self.error = error


        self.result = None


        self.state = "failed"


        self.finished_at = utc_now()


        self._finish_perf = perf_counter()


        self._record_state(
            "failed"
        )



    def reset(
        self,
        *,
        clear_logs: bool = False,
    ) -> None:


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



    # ======================================================
    # Result API
    # ======================================================

    def set_result(
        self,
        result: Any,
    ) -> None:
        """
        Attach result.

        Compatibility:

            ctx.result == raw value

        Internal:

            ctx._execution_result
        """

        from .result import ExecutionResult


        if isinstance(
            result,
            ExecutionResult,
        ):

            self._execution_result = result

            self.result = (
                result.value
                if hasattr(
                    result,
                    "value",
                )
                else result
            )

        else:

            self.result = result

            self._execution_result = (
                ExecutionResult.ok(
                    result
                )
            )



    def get_result(
        self,
        default=None,
    ) -> Any:


        if self.result is None:

            return default


        return self.result



    def get_execution_result(
        self,
    ):

        return self._execution_result



    # ======================================================
    # Logging
    # ======================================================

    def log(
        self,
        message: str,
        *,
        level: str = "INFO",
    ) -> None:

        self.logs.append(
            message
        )



    def structured_log(
        self,
        message: str,
        *,
        level: str = "INFO",
    ) -> None:

        self.logs.append(
            {
                "time": utc_now(),
                "level": level,
                "message": message,
            }
        )



    # ======================================================
    # History
    # ======================================================

    def _record_state(
        self,
        state: str,
    ) -> None:

        self.history.append(
            {
                "state": state,
                "time": utc_now(),
            }
        )



    # ======================================================
    # Metadata
    # ======================================================

    def set(
        self,
        key: str,
        value: Any,
    ) -> None:

        self.metadata[key] = value



    def get(
        self,
        key: str,
        default=None,
    ):

        return self.metadata.get(
            key,
            default,
        )



    # ======================================================
    # Artifact API
    # ======================================================

    def set_artifact(
        self,
        name: str,
        value: Any,
    ) -> None:

        self.artifacts[name] = value



    def get_artifact(
        self,
        name: str,
        default=None,
    ):

        return self.artifacts.get(
            name,
            default,
        )



    # ======================================================
    # Tags
    # ======================================================

    def add_tag(
        self,
        tag: str,
    ) -> None:

        if tag not in self.tags:

            self.tags.append(
                tag
            )



    # ======================================================
    # Worker
    # ======================================================

    def attach_worker(
        self,
        worker: str,
    ) -> None:

        self.worker = worker



    # ======================================================
    # Copy
    # ======================================================

    def copy(
        self,
    ) -> ExecutionContext:

        return deepcopy(
            self
        )



    # ======================================================
    # Serialization
    # ======================================================

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {

            "id": self.id,

            "task": self.task,

            "state": self.state,

            "worker": self.worker,

            "result": self.result,

            "execution_result":
                (
                    self._execution_result.to_dict()
                    if self._execution_result
                    else None
                ),

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

            "created_at": self.created_at,

            "started_at": self.started_at,

            "finished_at": self.finished_at,

            "duration": self.duration,
        }



    # ======================================================
    # Representation
    # ======================================================

    def __repr__(
        self,
    ) -> str:

        return (
            "ExecutionContext("
            f"id='{self.id}', "
            f"state='{self.state}', "
            f"worker={self.worker!r})"
        )