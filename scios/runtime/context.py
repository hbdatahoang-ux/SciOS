"""
SciOS Runtime Execution Context
===============================

Canonical execution context shared across the SciOS Runtime.

Responsibilities
----------------
- Hold task input.
- Track execution lifecycle.
- Store execution result.
- Maintain runtime metadata.
- Provide structured diagnostics.
- Support serialization.
- Serve as shared state between Runtime components.

Design Goals
------------
- Python 3.11+
- Serializable
- Distributed-runtime ready
- Plugin friendly
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from time import perf_counter
from typing import TYPE_CHECKING, Any
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
    Return UTC ISO timestamp.
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

    Lifecycle

        created
            |
            v
        running
            |
      +-------------+
      |             |
      v             v
 completed       failed
    """

    # ------------------------------------------------------
    # Identity
    # ------------------------------------------------------

    id: str = field(
        default_factory=lambda: str(uuid4())
    )


    # ------------------------------------------------------
    # Task
    # ------------------------------------------------------

    task: Any = None


    metadata: dict[str, Any] = field(
        default_factory=dict
    )


    # ------------------------------------------------------
    # Result
    # ------------------------------------------------------

    result: "ExecutionResult | None" = None


    error: BaseException | None = None


    # ------------------------------------------------------
    # Runtime state
    # ------------------------------------------------------

    state: RuntimeState = "created"


    worker: str | None = None


    # ------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------

    logs: list[dict[str, Any]] = field(
        default_factory=list
    )


    history: list[dict[str, Any]] = field(
        default_factory=list
    )


    tags: list[str] = field(
        default_factory=list
    )


    # ------------------------------------------------------
    # Timing
    # ------------------------------------------------------

    created_at: str = field(
        default_factory=utc_now
    )


    started_at: str | None = None


    finished_at: str | None = None


    _start_perf: float | None = field(
        default=None,
        repr=False
    )


    _finish_perf: float | None = field(
        default=None,
        repr=False
    )


    # ======================================================
    # Compatibility
    # ======================================================

    @property
    def status(self) -> RuntimeState:
        """
        Backward compatible alias.
        """

        return self.state


    @status.setter
    def status(
        self,
        value: RuntimeState,
    ) -> None:

        self.state = value


    # ======================================================
    # Lifecycle
    # ======================================================

    def start(self) -> None:
        """
        Start execution.
        """

        if self.state == "running":
            return


        self.state = "running"

        self.started_at = utc_now()

        self._start_perf = perf_counter()


        self._record_state(
            "running"
        )


    def finish(
        self,
        result: "ExecutionResult",
    ) -> None:
        """
        Complete execution.
        """

        self.result = result

        self.error = (
            result.error
            if result
            else None
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
        """
        Mark execution failed.
        """

        self.result = None

        self.error = error


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
        """
        Reset lifecycle state.
        """

        self.result = None

        self.error = None

        self.state = "created"


        self.started_at = None

        self.finished_at = None


        self._start_perf = None

        self._finish_perf = None


        self.history.clear()

        self.tags.clear()


        if clear_logs:
            self.logs.clear()


    # ======================================================
    # Diagnostics
    # ======================================================

    def log(
        self,
        message: str,
        *,
        level: str = "INFO",
    ) -> None:
        """
        Add structured runtime log.
        """

        self.logs.append(
            {
                "time": utc_now(),
                "level": level,
                "message": message,
            }
        )


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
    # Worker
    # ======================================================

    def attach_worker(
        self,
        worker: str,
    ) -> None:

        self.worker = worker


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
        default: Any = None,
    ) -> Any:

        return self.metadata.get(
            key,
            default,
        )


    def add_tag(
        self,
        tag: str,
    ) -> None:

        if tag not in self.tags:
            self.tags.append(tag)


    # ======================================================
    # State helpers
    # ======================================================

    @property
    def running(self) -> bool:
        return self.state == "running"


    @property
    def succeeded(self) -> bool:
        return self.state == "completed"


    @property
    def failed(self) -> bool:
        return self.state == "failed"


    @property
    def completed(self) -> bool:
        return self.succeeded


    # ======================================================
    # Timing
    # ======================================================

    @property
    def duration(self) -> float | None:

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
    # Copy
    # ======================================================

    def copy(self) -> "ExecutionContext":
        """
        Deep copy context.
        """

        return deepcopy(self)


    # ======================================================
    # Serialization
    # ======================================================

    def to_dict(self) -> dict[str, Any]:

        return {

            "id": self.id,

            "task": self.task,

            "metadata": deepcopy(
                self.metadata
            ),

            "result":
                self.result.to_dict()
                if self.result
                else None,

            "error":
                str(self.error)
                if self.error
                else None,


            "state": self.state,

            "worker": self.worker,

            "logs": deepcopy(
                self.logs
            ),

            "history": deepcopy(
                self.history
            ),

            "tags": list(
                self.tags
            ),

            "created_at": self.created_at,

            "started_at": self.started_at,

            "finished_at": self.finished_at,

            "duration": self.duration,
        }


    # ======================================================
    # Representation
    # ======================================================

    def __repr__(self) -> str:

        return (
            f"ExecutionContext("
            f"id='{self.id}', "
            f"state='{self.state}', "
            f"worker={self.worker!r})"
        )