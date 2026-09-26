"""
SciOS Kernel Dispatcher
=======================

Task dispatcher for SciOS Kernel.

Responsibilities
-----------------
- Bridge Scheduler and ExecutionEngine.
- Dispatch queued tasks.
- Maintain execution statistics.
- Provide lifecycle control.

Design Goals
------------
- Runtime agnostic
- Test friendly
- Thread safe
- Extensible
"""

from __future__ import annotations

from threading import RLock
from typing import Any

from scios.runtime import ExecutionContext

from .scheduler import Scheduler


class Dispatcher:
    """
    Scheduler -> ExecutionEngine bridge.
    """

    def __init__(
        self,
        *,
        scheduler: Scheduler,
        engine: Any | None = None,
    ) -> None:

        self.scheduler = scheduler
        self.engine = engine

        self._lock = RLock()

        self._running = False

        self._tasks_dispatched = 0
        self._tasks_failed = 0


    # ======================================================
    # Lifecycle
    # ======================================================

    def initialize(self) -> None:
        """
        Prepare dispatcher.
        """

        self._running = True


    def start(self) -> None:
        """
        Start dispatcher.
        """

        self._running = True


    def shutdown(self) -> None:
        """
        Stop dispatcher.
        """

        self._running = False



    # ======================================================
    # Internal helpers
    # ======================================================

    def _ensure_engine(self) -> None:

        if self.engine is None:
            raise RuntimeError(
                "ExecutionEngine is not configured."
            )


    def _scheduler_empty(self) -> bool:
        """
        Compatible with multiple Scheduler implementations.
        """

        if hasattr(self.scheduler, "empty"):
            return self.scheduler.empty()

        if hasattr(self.scheduler, "__len__"):
            return len(self.scheduler) == 0

        if hasattr(self.scheduler, "queue"):
            return len(self.scheduler.queue) == 0

        return True



    def _dequeue(self):

        if hasattr(self.scheduler, "dequeue"):
            return self.scheduler.dequeue()

        if hasattr(self.scheduler, "next"):
            return self.scheduler.next()

        if hasattr(self.scheduler, "pop"):
            return self.scheduler.pop()

        raise RuntimeError(
            "Scheduler does not provide dequeue operation."
        )



    # ======================================================
    # Dispatch
    # ======================================================

    def dispatch(
        self,
        task: Any,
        **metadata: Any,
    ) -> ExecutionContext:
        """
        Execute one task immediately.
        """

        self._ensure_engine()

        with self._lock:

            try:

                #
                # Compatibility:
                # real engine:
                # run(task, metadata=...)
                #
                # dummy engine:
                # run(task)
                #

                try:

                    context = self.engine.run(
                        task=task,
                        metadata=metadata,
                    )

                except TypeError:

                    context = self.engine.run(
                        task
                    )


                self._tasks_dispatched += 1

                return context


            except Exception:

                self._tasks_failed += 1

                raise



    def dispatch_next(
        self,
    ) -> ExecutionContext | None:
        """
        Execute next queued task.
        """

        self._ensure_engine()


        if self._scheduler_empty():

            return None


        task = self._dequeue()

        return self.dispatch(task)



    def dispatch_all(self) -> list[ExecutionContext]:
        """
        Execute all queued tasks.
        """

        results = []


        while not self._scheduler_empty():

            result = self.dispatch_next()

            if result is not None:
                results.append(result)


        return results



    # ======================================================
    # Scheduler interface
    # ======================================================

    def submit(
        self,
        task: Any,
    ) -> None:
        """
        Submit task.
        """

        if hasattr(self.scheduler, "enqueue"):

            self.scheduler.enqueue(task)

            return


        if hasattr(self.scheduler, "submit"):

            self.scheduler.submit(task)

            return


        raise RuntimeError(
            "Scheduler does not support submit."
        )



    # ======================================================
    # Statistics
    # ======================================================

    @property
    def tasks_dispatched(self) -> int:

        return self._tasks_dispatched



    @property
    def tasks_failed(self) -> int:

        return self._tasks_failed



    # ======================================================
    # Status
    # ======================================================

    @property
    def running(self) -> bool:

        return self._running



    def status(self) -> dict[str, Any]:

        return {
            "running": self._running,
            "queued_tasks": len(self),
            "tasks_dispatched": self._tasks_dispatched,
            "tasks_failed": self._tasks_failed,
        }



    # ======================================================
    # Utilities
    # ======================================================

    def reset(self) -> None:

        self._tasks_dispatched = 0
        self._tasks_failed = 0



    # ======================================================
    # Protocols
    # ======================================================

    def __len__(self) -> int:

        try:

            return len(self.scheduler)

        except TypeError:

            return 0



    def __bool__(self) -> bool:

        return self._running



    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"running={self._running}, "
            f"queued={len(self)}, "
            f"dispatched={self._tasks_dispatched}, "
            f"failed={self._tasks_failed})"
        )