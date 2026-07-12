"""
SciOS Runtime Execution Engine
==============================

Central orchestration engine for SciOS Runtime.

Features
--------
- Scheduler coordination
- Worker execution
- ExecutionContext lifecycle
- EventBus integration
- HookRegistry integration
- Plugin-ready architecture

Python 3.11+
"""

from __future__ import annotations

from typing import Any

from scios.shared import EventBus

from .context import ExecutionContext
from .exceptions import (
    ExecutionError,
    InvalidTaskError,
)
from .hook_registry import HookRegistry
from .result import ExecutionResult
from .scheduler import Scheduler
from .state import RuntimeState
from .worker import Worker


__all__ = [
    "ExecutionEngine",
]


class ExecutionEngine:
    """
    SciOS Runtime execution coordinator.

    Pipeline

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
    ExecutionResult
    """

    # ------------------------------------------------------
    # Runtime hooks
    # ------------------------------------------------------

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


        #
        # Phase 3 Hook System
        #
        self._hook_registry = HookRegistry()


        #
        # Supported hook names
        #
        self._valid_hooks = set(
            self.DEFAULT_HOOKS
        )


    # ======================================================
    # Properties
    # ======================================================

    @property
    def scheduler(self):
        return self._scheduler


    @property
    def worker(self):
        return self._worker


    @property
    def state(self):
        return self._state


    @property
    def executions(self):
        return self._executions


    @property
    def hooks(self) -> HookRegistry:
        """
        Plugin access point.
        """

        return self._hook_registry


    @property
    def pending(self) -> int:
        return self._scheduler.pending


    # ======================================================
    # Hook Compatibility API
    # ======================================================

    def register_hook(
        self,
        name: str,
        handler,
    ):
        """
        Backward compatible hook API.

        Used by runtime tests.
        """

        if name not in self._valid_hooks:
            raise ValueError(
                f"Unknown hook: {name}"
            )

        return self._hook_registry.register(
            name,
            handler,
        )


    def unregister_hook(
        self,
        name: str,
        handler,
    ):
        return self._hook_registry.unregister(
            name,
            handler,
        )


    def _emit_hook(
        self,
        name: str,
        *args,
        **kwargs,
    ):
        self._hook_registry.emit(
            name,
            *args,
            **kwargs,
        )


    def clear_hooks(self):

        return self._hook_registry.clear()


    # ======================================================
    # Lifecycle
    # ======================================================

    def initialize(self):

        self._scheduler.initialize()

        self._worker.initialize()

        self._state = "idle"



    def shutdown(self):

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
        metadata=None,
    ):

        if task is None:
            raise InvalidTaskError(
                "Task cannot be None."
            )

        return ExecutionContext(
            task=task,
            metadata=dict(metadata or {}),
        )



    # ======================================================
    # Submit
    # ======================================================

    def submit(
        self,
        task,
        *,
        metadata=None,
    ):

        ctx = self.create_context(
            task,
            metadata=metadata,
        )


        self._emit_hook(
            "before_submit",
            ctx,
        )


        self._scheduler.submit(
            ctx
        )


        self._publish(
            "task.submitted",
            context=ctx,
        )


        return ctx



    # ======================================================
    # Execute
    # ======================================================

    def run(
        self,
        task,
        *,
        metadata=None,
    ):

        if self._state == "created":
            self.initialize()


        self._state = "running"


        ctx = self.submit(
            task,
            metadata=metadata,
        )


        current = self._scheduler.next()


        current.start()


        self._emit_hook(
            "before_execute",
            current,
        )


        self._publish(
            "task.started",
            context=current,
        )


        try:

            result = self._worker.execute(
                current
            )


            if not isinstance(
                result,
                ExecutionResult,
            ):
                raise ExecutionError(
                    "Invalid ExecutionResult"
                )


            if result.success:

                current.finish(
                    result
                )


                self._scheduler.complete(
                    current
                )


                self._executions += 1


                self._emit_hook(
                    "after_execute",
                    current,
                    result,
                )


                self._publish(
                    "task.completed",
                    context=current,
                    result=result,
                )


            else:

                error = result.error or ExecutionError(
                    result.message
                )


                current.fail(
                    error
                )


                self._emit_hook(
                    "after_failure",
                    current,
                    error,
                )


            return current


        except Exception as exc:

            current.fail(
                exc
            )


            failed = ExecutionResult.fail(
                exc
            )

            current.result = failed


            self._emit_hook(
                "after_failure",
                current,
                exc,
            )


            return current


        finally:

            if self._state != "stopped":
                self._state = "idle"



    # ======================================================
    # EventBus
    # ======================================================

    def _publish(
        self,
        topic: str,
        **payload,
    ):

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

    def status(self):

        return {

            "state": self._state,

            "executions": self._executions,

            "pending": self.pending,

            "hooks":
                self._hook_registry.status(),

        }



    # ======================================================
    # Protocols
    # ======================================================

    def __len__(self):

        return self._executions


    def __bool__(self):

        return self._state not in {
            "created",
            "stopped",
        }


    def __repr__(self):

        return (
            "ExecutionEngine("
            f"state={self._state!r}, "
            f"executions={self._executions}"
            ")"
        )
    