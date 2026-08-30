"""
SciOS Runtime Execution Engine
==============================

Central orchestration engine for SciOS Runtime.

Responsibilities:
- Task lifecycle
- Context management
- Scheduler coordination
- Worker execution
- Pipeline orchestration
- EventBus integration
- Hook lifecycle

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
    Main SciOS Runtime coordinator.
    """



    DEFAULT_HOOKS = {
        "before_submit",
        "execution_started",
        "before_execute",
        "execution_completed",
        "execution_failed",
        "execution_finished",
        "after_execute",
        "after_success",
        "after_failure",
    }



    # ======================================================
    # Construction
    # ======================================================

    def __init__(
        self,
        *,
        pipeline=None,
        scheduler: Scheduler | None = None,
        worker: Worker | None = None,
        event_bus: EventBus | None = None,
    ):


        self._pipeline = pipeline

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


        self._hook_registry = HookRegistry()


        self._valid_hooks = set(
            self.DEFAULT_HOOKS
        )



    # ======================================================
    # Properties
    # ======================================================

    @property
    def pipeline(self):

        return self._pipeline



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
    def pending(self):

        return self._scheduler.pending



    @property
    def hooks(self):

        return self._hook_registry



    # ======================================================
    # Lifecycle
    # ======================================================

    def initialize(self):

        if self._state != "created":

            return self


        self._scheduler.initialize()

        self._worker.initialize()


        self._state = "idle"


        return self



    def shutdown(self):

        if self._state == "stopped":

            return


        self._scheduler.shutdown()

        self._worker.shutdown()


        self._state = "stopped"



    def reset(self):

        self._executions = 0


        if hasattr(
            self._scheduler,
            "reset",
        ):

            self._scheduler.reset()


        if hasattr(
            self._worker,
            "reset",
        ):

            self._worker.reset()


        self._state = "idle"


        return self



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
                "Task cannot be None"
            )


        return ExecutionContext(
            task=task,
            metadata=dict(
                metadata or {}
            ),
        )



    # ======================================================
    # Hooks
    # ======================================================

    def register_hook(
        self,
        name,
        handler,
    ):


        if name not in self._valid_hooks:

            raise ValueError(
                f"Unknown hook: {name}"
            )


        return self._hook_registry.register(
            name,
            handler,
        )



    def _emit_hook(
        self,
        name,
        *args,
        **kwargs,
    ):


        try:

            self._hook_registry.emit(
                name,
                *args,
                **kwargs,
            )

        except Exception:

            pass



    # ======================================================
    # Submit
    # ======================================================

    def submit(
        self,
        task,
        *,
        metadata=None,
    ):


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
    # Run
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

        context = None

        try:

            self.submit(
                task,
                metadata=metadata,
            )

            context = self._scheduler.next()

            if context is None:
                raise ExecutionError(
                    "No scheduled task"
                )

            # --------------------------------------------------
            # Lifecycle
            # --------------------------------------------------

            context.log(
                f"Task received: {task}"
            )

            context.start()

            self._emit_hook(
                "execution_started",
                context,
            )

            # --------------------------------------------------
            # Pipeline
            # --------------------------------------------------

            if self._pipeline is not None:

                context.log(
                    "Pipeline started"
                )

                self._pipeline.execute(
                    context
                )

                context.log(
                    "Pipeline completed"
                )

            # --------------------------------------------------
            # Worker
            # --------------------------------------------------

            if not context.has_result:

                self._emit_hook(
                    "before_execute",
                    context,
                )

                raw = self._worker.execute(
                    context
                )

                self._emit_hook(
                    "after_execute",
                    context,
                    raw,
                )

            else:

                raw = (
                    context.get_execution_result()
                    or context.execution_result
                )

            # --------------------------------------------------
            # Normalize
            # --------------------------------------------------

            if isinstance(
                raw,
                ExecutionResult,
            ):

                result = raw

            else:

                result = ExecutionResult.ok(
                    raw
                )

            context.set_result(
                result
            )

            # --------------------------------------------------
            # Success
            # --------------------------------------------------

            if result.success:

                context.finish(
                    result
                )

                self._scheduler.complete(
                    context
                )

                self._executions += 1

                self._emit_hook(
                    "execution_completed",
                    context,
                    result,
                )

                self._emit_hook(
                    "after_success",
                    context,
                    result,
                )

                self._publish(
                    "task.completed",
                    context=context,
                    result=result,
                )

            # --------------------------------------------------
            # Failure Result
            # --------------------------------------------------

            else:

                error = (
                    result.error
                    or ExecutionError(
                        result.message
                    )
                )

                context.fail(
                    error
                )

                self._emit_hook(
                    "execution_failed",
                    context,
                    error,
                )

                self._emit_hook(
                    "after_failure",
                    context,
                    error,
                )

                self._publish(
                    "task.failed",
                    context=context,
                    error=error,
                )

            return context

        except Exception as exc:

            if context is not None:

                failure = ExecutionResult.fail(
                    exc
                )

                context.set_result(
                    failure
                )

                context.fail(
                    exc
                )

            self._emit_hook(
                "execution_failed",
                context,
                exc,
            )

            self._emit_hook(
                "after_failure",
                context,
                exc,
            )

            raise

        finally:

            if context is not None:

                self._emit_hook(
                    "execution_finished",
                    context,
                )

            if self._state != "stopped":

                self._state = "idle"


    # ======================================================
    # Execute
    # ======================================================

    def execute(
        self,
        task,
        *,
        metadata=None,
    ):


        ctx = self.run(
            task,
            metadata=metadata,
        )


        return ctx.get_execution_result()



    # ======================================================
    # EventBus
    # ======================================================

    def _publish(
        self,
        topic,
        **payload,
    ):


        if self._event_bus is None:

            return


        try:

            self._event_bus.publish(
                topic,
                **payload,
            )


        except TypeError:

            self._event_bus.publish(
                topic,
                payload,
            )


        except Exception:

            pass



    # ======================================================
    # Diagnostics
    # ======================================================

    def status(self):

        return {

            "state":
                self._state,

            "executions":
                self._executions,

            "scheduler":
                self._scheduler,

            "worker":
                self._worker,

            "pending":
                self.pending,

            "hooks":
                self._hook_registry.status(),

        }



    # ======================================================
    # Protocol
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