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


@dataclass(slots=True)
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
    # Identity
    # ======================================================

    id: str = field(
        default_factory=lambda: str(uuid4())
    )



    # ======================================================
    # Task
    # ======================================================

    task: Any = None



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
    Public canonical result.

    Always:

        ExecutionResult | None
    """

    result: ExecutionResult | None = None



    """
    Internal alias.

    Kept for compatibility with
    ExecutionEngine and advanced runtime.
    """

    _execution_result: ExecutionResult | None = field(
        default=None,
        repr=False,
    )



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



    # ======================================================
    # Properties
    # ======================================================

    @property
    def status(self):
        return self.state


    @status.setter
    def status(
        self,
        value,
    ):
        self.state = value



    @property
    def running(self):
        return self.state == "running"



    @property
    def completed(self):
        return self.state == "completed"



    @property
    def failed(self):
        return self.state == "failed"



    @property
    def done(self):
        return (
            self.completed
            or self.failed
        )



    @property
    def succeeded(self):
        return self.completed



    @property
    def has_result(self):
        return self.result is not None



    @property
    def duration(self):

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
    # Lifecycle
    # ======================================================

    def start(self):

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
        result,
    ):

        from .result import ExecutionResult


        if not isinstance(
            result,
            ExecutionResult,
        ):

            result = ExecutionResult.ok(
                result
            )


        self.result = result


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
    ):

        from .result import ExecutionResult


        self.error = error


        self.result = ExecutionResult.fail(
            error
        )


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
        clear_logs=False,
    ):

        self.result = None

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
    # ======================================================
    # Result API
    # ======================================================

    def set_result(
        self,
        result,
    ):
        """
        Attach execution result.

        Contract:

            ctx.result
                |
                v
            ExecutionResult
        """

        from .result import ExecutionResult


        if isinstance(
            result,
            ExecutionResult,
        ):

            self.result = result


        else:

            self.result = ExecutionResult.ok(
                result
            )


        return self



    def get_result(
        self,
        default=None,
    ):

        if self.result is None:

            return default


        return self.result



    def get_execution_result(
        self,
    ):
        """
        Return canonical ExecutionResult.
        """

        return self.result



    @property
    def execution_result(
        self,
    ):
        """
        Compatibility alias.
        """

        return self.result



    # ======================================================
    # Logging
    # ======================================================

    def log(
        self,
        message: str,
        *,
        level: str = "INFO",
    ):

        self.logs.append(
            message
        )



    def structured_log(
        self,
        message: str,
        *,
        level: str = "INFO",
    ):

        self.logs.append(
            {
                "time": utc_now(),
                "level": level,
                "message": message,
            }
        )



    # ======================================================
    # Events
    # ======================================================

    def add_event(
        self,
        event: str,
    ):

        self.events.append(
            event
        )



    def has_event(
        self,
        event: str,
    ) -> bool:

        return event in self.events



    # ======================================================
    # History
    # ======================================================

    def _record_state(
        self,
        state: str,
    ):

        self.history.append(
            {
                "state": state,
                "time": utc_now(),
            }
        )
    # ======================================================
    # Metadata API
    # ======================================================

    def set(
        self,
        key: str,
        value: Any,
    ):

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
    ):

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
    ):

        if tag not in self.tags:

            self.tags.append(
                tag
            )



    def remove_tag(
        self,
        tag: str,
    ):

        if tag in self.tags:

            self.tags.remove(
                tag
            )



    def has_tag(
        self,
        tag: str,
    ) -> bool:

        return tag in self.tags



    # ======================================================
    # Worker
    # ======================================================

    def attach_worker(
        self,
        worker: str,
    ):

        self.worker = worker


        return self



    # ======================================================
    # Copy
    # ======================================================

    def copy(self):

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

            "id":
                self.id,


            "task":
                self.task,


            "state":
                self.state,


            "worker":
                self.worker,


            "result":
                (
                    self.result.to_dict()
                    if self.result
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


            "created_at":
                self.created_at,


            "started_at":
                self.started_at,


            "finished_at":
                self.finished_at,


            "duration":
                self.duration,

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
            f"worker={self.worker!r}"
            ")"
        )                    