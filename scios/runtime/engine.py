"""
SciOS Runtime Execution Engine
==============================

Central orchestration engine for SciOS Runtime.

Responsibilities
----------------
- Coordinate Scheduler, Worker and Executor.
- Manage ExecutionContext lifecycle.
- Execute tasks.
- Publish runtime events.
- Provide runtime hooks.
- Maintain execution statistics.

Design Goals
------------
- Python 3.11+
- Deterministic execution
- Event-driven
- Dependency Injection friendly
- Plugin-ready architecture
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from typing import Any

from scios.shared import EventBus

from .context import ExecutionContext
from .exceptions import (
    ExecutionError,
    InvalidTaskError,
)
from .result import ExecutionResult
from .scheduler import Scheduler
from .state import RuntimeState
from .worker import Worker


__all__ = [
    "ExecutionEngine",
]


HookHandler = Callable[..., None]


class ExecutionEngine:
    """
    Central Runtime coordinator.

    Pipeline
    --------

        Task
         |
         v
    ExecutionContext
         |
         v
      Scheduler
         |
         v
       Worker
         |
         v
     Executor
         |
         v
    ExecutionResult
    """


    # ======================================================
    # Supported Hooks
    # ======================================================

    DEFAULT_HOOKS = {
        "before_submit",
        "before_execute",
        "after_execute",
        "after_failure",
    }


    # ======================================================
    # Construction
    # ======================================================

    def __init__(
        self,
        *,
        scheduler: Scheduler | None = None,
        worker: Worker | None = None,
        event_bus: EventBus | None = None,
    ) -> None:

        self._scheduler = (
            scheduler
            or Scheduler()
        )

        self._worker = (
            worker
            or Worker()
        )

        self._event_bus = event_bus

        self._state: RuntimeState = "created"

        self._executions = 0


        # Hook registry
        self._hooks: dict[
            str,
            list[HookHandler],
        ] = defaultdict(list)


        # Allowed hooks (Phase 1)
        self._valid_hooks = set(
            self.DEFAULT_HOOKS
        )


    # ======================================================
    # Properties
    # ======================================================

    @property
    def scheduler(self) -> Scheduler:
        return self._scheduler


    @property
    def worker(self) -> Worker:
        return self._worker


    @property
    def state(self) -> RuntimeState:
        return self._state


    @property
    def executions(self) -> int:
        return self._executions


    @property
    def hooks(self):
        """
        Read-only hook snapshot.
        """

        return {
            name: tuple(items)
            for name, items
            in self._hooks.items()
        }


    @property
    def pending(self) -> int:
        return self._scheduler.pending



    # ======================================================
    # Hook System
    # ======================================================

    def register_hook(
        self,
        name: str,
        handler: HookHandler,
    ) -> None:
        """
        Register runtime hook.
        """

        if name not in self._valid_hooks:
            raise ValueError(
                f"Unknown hook: {name}"
            )

        if not callable(handler):
            raise TypeError(
                "Hook handler must be callable."
            )

        self._hooks[name].append(
            handler
        )


    def unregister_hook(
        self,
        name: str,
        handler: HookHandler,
    ) -> None:
        """
        Remove hook handler.
        """

        hooks = self._hooks.get(name)

        if not hooks:
            return


        if handler in hooks:
            hooks.remove(handler)



    def _emit_hook(
        self,
        name: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Execute hooks safely.

        Hook failure never breaks runtime.
        """

        for handler in tuple(
            self._hooks.get(name, ())
        ):

            try:

                handler(
                    *args,
                    **kwargs,
                )

            except Exception:
                pass



    def clear_hooks(self) -> int:
        """
        Remove all hooks.
        """

        count = sum(
            len(v)
            for v in self._hooks.values()
        )

        self._hooks.clear()

        return count



    # ======================================================
    # Lifecycle
    # ======================================================

    def initialize(self) -> None:

        self._scheduler.initialize()

        self._worker.initialize()

        self._state = "idle"



    def shutdown(self) -> None:

        self._scheduler.shutdown()

        self._worker.shutdown()

        self._state = "stopped"



    # ======================================================
    # Context
    # ======================================================

    def create_context(
        self,
        task: Any,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> ExecutionContext:
        """
        Create execution context.
        """

        if task is None:
            raise InvalidTaskError(
                "Task cannot be None."
            )


        return ExecutionContext(
            task=task,
            metadata=dict(
                metadata or {}
            ),
        )



    # ======================================================
    # Submit
    # ======================================================

    def submit(
        self,
        task: Any,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> ExecutionContext:

        context = self.create_context(
            task,
            metadata=metadata,
        )


        self._emit_hook(
            "before_submit",
            context,
        )


        self._scheduler.submit(
            context
        )


        self._publish(
            "task.submitted",
            context=context,
        )


        return context



    # ======================================================
    # Execute
    # ======================================================

    def run(
        self,
        task: Any,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> ExecutionContext:


        if self._state == "created":
            self.initialize()


        self._state = "running"


        context = self.submit(
            task,
            metadata=metadata,
        )


        scheduled = (
            self._scheduler.next()
        )


        scheduled.start()


        self._emit_hook(
            "before_execute",
            scheduled,
        )


        self._publish(
            "task.started",
            context=scheduled,
        )


        try:

            result = (
                self._worker.execute(
                    scheduled
                )
            )


            if not isinstance(
                result,
                ExecutionResult,
            ):
                raise ExecutionError(
                    "Worker returned invalid result."
                )



            if result.success:

                scheduled.finish(
                    result
                )


                self._scheduler.complete(
                    scheduled
                )


                self._executions += 1


                self._emit_hook(
                    "after_execute",
                    scheduled,
                    result,
                )


                self._publish(
                    "task.completed",
                    context=scheduled,
                    result=result,
                )



            else:

                error = (
                    result.error
                    or ExecutionError(
                        result.message
                        or "Execution failed."
                    )
                )


                scheduled.fail(
                    error
                )


                self._emit_hook(
                    "after_failure",
                    scheduled,
                    error,
                )


                self._publish(
                    "task.failed",
                    context=scheduled,
                    result=result,
                    error=error,
                )


            return scheduled



        except Exception as exc:


            scheduled.fail(
                exc
            )


            failed = ExecutionResult.fail(
                exc
            )


            scheduled.result = failed


            self._emit_hook(
                "after_failure",
                scheduled,
                exc,
            )


            self._publish(
                "task.failed",
                context=scheduled,
                result=failed,
                error=exc,
            )


            return scheduled



        finally:

            if self._state != "stopped":
                self._state = "idle"



    # ======================================================
    # EventBus
    # ======================================================

    def _publish(
        self,
        topic: str,
        **payload: Any,
    ) -> None:


        if self._event_bus is None:
            return


        try:

            self._event_bus.publish(
                topic,
                **payload,
            )

        except Exception:
            pass



    # ======================================================
    # Status
    # ======================================================

    def status(
        self,
    ) -> dict[str, Any]:

        return {

            "state": self._state,

            "executions": self._executions,

            "pending": self.pending,

            "scheduler":
                self._scheduler.status(),

            "worker":
                self._worker.status(),

            "hooks":
            {
                k: len(v)
                for k, v
                in self._hooks.items()
            },
        }



    # ======================================================
    # Maintenance
    # ======================================================

    def reset(self) -> None:

        self._executions = 0

        self._scheduler.clear()

        self._worker.reset()

        self.clear_hooks()

        self._state = "idle"



    # ======================================================
    # Helpers
    # ======================================================

    def is_initialized(self) -> bool:
        return self._state != "created"


    def is_running(self) -> bool:
        return self._state == "running"


    def is_idle(self) -> bool:
        return self._state == "idle"


    def is_stopped(self) -> bool:
        return self._state == "stopped"



    # ======================================================
    # Protocols
    # ======================================================

    def __len__(self) -> int:
        return self._executions


    def __bool__(self) -> bool:

        return self._state not in {
            "created",
            "stopped",
        }


    def __contains__(
        self,
        hook_name: str,
    ) -> bool:

        return bool(
            self._hooks.get(
                hook_name
            )
        )


    def __repr__(self) -> str:

        return (
            f"ExecutionEngine("
            f"state={self._state!r}, "
            f"executions={self._executions}, "
            f"pending={self.pending}, "
            f"hooks={len(self._hooks)}"
            f")"
        )         