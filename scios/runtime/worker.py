"""
SciOS Runtime Worker
====================

Runtime worker responsible for executing execution contexts.

Responsibilities
----------------
- Execute ExecutionContext.
- Own execution Executor.
- Manage worker lifecycle.
- Maintain execution statistics.
- Support repeated runtime boot cycles.
- Provide thread-safe execution boundary.

Design Goals
------------
- Python 3.11+
- Reusable lifecycle
- Thread-safe
- Runtime independent
- Lightweight
"""

from __future__ import annotations


from datetime import datetime, timezone
from threading import RLock
from typing import Any
from uuid import uuid4


from .context import ExecutionContext
from .exceptions import WorkerUnavailableError
from .executor import Executor
from .result import ExecutionResult
from .state import RuntimeState


__all__ = [
    "Worker",
]



class Worker:
    """
    SciOS Runtime Worker.

    Worker owns an Executor and executes
    ExecutionContext objects sequentially.

    Lifecycle:

        created
           |
           v
        idle
           |
           v
        running
           |
           v
        idle

        shutdown()
           |
           v
        stopped

        initialize()
           |
           v
        idle
    """



    def __init__(
        self,
        *,
        name: str | None = None,
        executor: Executor | None = None,
    ) -> None:


        self._id = str(uuid4())


        self._name = (
            name
            or f"worker-{self._id[:8]}"
        )


        self._executor = (
            executor
            or Executor()
        )


        self._state: RuntimeState = "idle"


        # Worker is enabled after creation.
        # shutdown() does not disable worker.
        self._enabled = True


        self._tasks_completed = 0


        self._created_at = datetime.now(
            timezone.utc
        )


        self._lock = RLock()



    # ======================================================
    # Properties
    # ======================================================

    @property
    def id(self) -> str:
        return self._id



    @property
    def name(self) -> str:
        return self._name



    @property
    def state(self) -> RuntimeState:
        return self._state



    @property
    def enabled(self) -> bool:
        return self._enabled



    @property
    def executor(self) -> Executor:
        return self._executor



    @property
    def tasks_completed(self) -> int:
        return self._tasks_completed



    # ======================================================
    # Lifecycle
    # ======================================================

    def initialize(self) -> None:
        """
        Initialize or restore worker.

        Used by repeated SciOS boot cycles.
        """

        with self._lock:

            self._enabled = True

            self._state = "idle"



    def start(self) -> None:
        """
        Start worker.
        """

        with self._lock:

            self._enabled = True


            if self._state == "stopped":

                self._state = "idle"



    def shutdown(self) -> None:
        """
        Shutdown worker gracefully.

        Worker remains reusable.
        """

        with self._lock:

            self._state = "stopped"



    def enable(self) -> None:
        """
        Enable worker execution.
        """

        with self._lock:

            self._enabled = True


            if self._state == "stopped":

                self._state = "idle"



    def disable(self) -> None:
        """
        Disable worker permanently.

        Used for failure isolation.
        """

        with self._lock:

            self._enabled = False

            self._state = "stopped"



    # ======================================================
    # Execution
    # ======================================================

    def execute(
        self,
        context: ExecutionContext,
    ) -> ExecutionResult:
        """
        Execute one ExecutionContext.
        """


        with self._lock:


            if not self._enabled:

                raise WorkerUnavailableError(
                    "Worker is disabled."
                )


            # Recover from shutdown
            if self._state == "stopped":

                self._state = "idle"


            self._state = "running"



        try:


            result = self._executor.execute(
                context
            )


            with self._lock:

                self._tasks_completed += 1



            return result



        finally:


            with self._lock:


                if self._enabled:

                    self._state = "idle"


                else:

                    self._state = "stopped"




    # ======================================================
    # Statistics
    # ======================================================

    def status(
        self,
    ) -> dict[str, Any]:
        """
        Return worker status snapshot.
        """

        with self._lock:

            return {

                "id": self._id,

                "name": self._name,

                "state": self._state,

                "enabled": self._enabled,

                "tasks_completed":
                    self._tasks_completed,

                "executor_executions":
                    self._executor.executions,

                "created_at":
                    self._created_at.isoformat(),

            }



    def reset(self) -> None:
        """
        Reset worker statistics.
        """

        with self._lock:


            self._tasks_completed = 0


            self._executor.reset()


            self._enabled = True


            self._state = "idle"



    # ======================================================
    # Protocols
    # ======================================================

    def __call__(
        self,
        context: ExecutionContext,
    ) -> ExecutionResult:

        return self.execute(context)



    def __repr__(self) -> str:

        return (

            f"{self.__class__.__name__}("

            f"id={self._id!r}, "

            f"name={self._name!r}, "

            f"state={self._state!r}, "

            f"tasks_completed="
            f"{self._tasks_completed}"

            ")"

        )