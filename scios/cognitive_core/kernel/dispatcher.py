"""
SciOS Cognitive Stage Dispatcher
================================

Dispatcher layer for CognitivePipeline.

Responsibilities
-----------------
- Execute a single cognitive stage.
- Execute multiple cognitive stages.
- Support middleware hooks.
- Support event bus integration.
- Track successful executions.
- Preserve stage failure state.

Python 3.11+
"""

from __future__ import annotations

from typing import Any, Iterable

from .stage import CognitiveStage
from .events import KernelEventType


__all__ = [
    "StageDispatcher",
]


class StageDispatcher:
    """
    Central dispatcher for cognitive stages.

    Supported APIs
    --------------

    Single stage::

        dispatcher.dispatch(stage, context)

    Single stage with middleware/event bus::

        dispatcher.dispatch(
            stage,
            context,
            middleware=middleware,
            event_bus=event_bus,
        )

    Multiple stages::

        dispatcher.dispatch(
            context=context,
            stages=stages,
            middleware=middleware,
            event_bus=event_bus,
        )
    """

    def __init__(self) -> None:
        self.executed: int = 0

    # ======================================================
    # Public Dispatch API
    # ======================================================

    def dispatch(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Dispatch one or more cognitive stages.

        Two calling conventions are supported.

        Single-stage mode
        ------------------
        ``dispatch(stage, context, ...)``

        Pipeline mode
        --------------
        ``dispatch(context=..., stages=[...], ...)``

        Returns
        -------
        Any
            Result of the last executed stage.

        Raises
        ------
        TypeError
            If the dispatch arguments are invalid.
        """

        # --------------------------------------------------
        # Single-stage mode
        # --------------------------------------------------

        if len(args) == 2:
            stage, context = args

            middleware = kwargs.get("middleware")
            event_bus = kwargs.get("event_bus")

            return self._dispatch_stage(
                stage,
                context,
                middleware=middleware,
                event_bus=event_bus,
            )

        # --------------------------------------------------
        # Reject unsupported positional arguments
        # --------------------------------------------------

        if args:
            raise TypeError(
                "dispatch() expects either "
                "(stage, context) or keyword-based "
                "(context=..., stages=...)"
            )

        # --------------------------------------------------
        # Pipeline mode
        # --------------------------------------------------

        context = kwargs.get("context")

        stages: Iterable[CognitiveStage] = kwargs.get(
            "stages",
            (),
        )

        middleware = kwargs.get("middleware")
        event_bus = kwargs.get("event_bus")

        result: Any = None

        for stage in stages:
            result = self._dispatch_stage(
                stage,
                context,
                middleware=middleware,
                event_bus=event_bus,
            )

        return result

    # ======================================================
    # Internal Stage Execution
    # ======================================================

    def _dispatch_stage(
        self,
        stage: CognitiveStage,
        context: Any,
        *,
        middleware: Any = None,
        event_bus: Any = None,
    ) -> Any:
        """
        Execute exactly one cognitive stage.

        Execution order
        ---------------

        1. middleware.before_stage
        2. stage_started event
        3. stage execution
        4. stage_completed event
        5. middleware.after_stage

        On failure:

        - stage.status becomes ``failed``
        - stage.message contains the exception message
        - exception is re-raised
        - execution counter is not incremented
        """

        try:
            # ------------------------------------------------
            # Middleware: before
            # ------------------------------------------------

            if middleware is not None:
                before_stage = getattr(
                    middleware,
                    "before_stage",
                    None,
                )

                if before_stage is not None:
                    before_stage(
                        stage,
                        context,
                    )

            # ------------------------------------------------
            # Event: started
            # ------------------------------------------------

            if event_bus is not None:
                publish = getattr(
                    event_bus,
                    "publish",
                    None,
                )

                if publish is not None:
                    publish(
                        KernelEventType.STAGE_STARTED.value,
                        stage=stage.name,
                    )

            # ------------------------------------------------
            # Stage execution
            # ------------------------------------------------

            stage.status = "running"

            result = stage.run(context)

            stage.status = "completed"

            # Successful execution only.
            self.executed += 1

            # ------------------------------------------------
            # Event: completed
            # ------------------------------------------------

            if event_bus is not None:
                publish = getattr(
                    event_bus,
                    "publish",
                    None,
                )

                if publish is not None:
                    publish(
                        KernelEventType.STAGE_COMPLETED.value,
                        stage=stage.name,
                    )

            # ------------------------------------------------
            # Middleware: after
            # ------------------------------------------------

            if middleware is not None:
                after_stage = getattr(
                    middleware,
                    "after_stage",
                    None,
                )

                if after_stage is not None:
                    after_stage(
                        stage,
                        context,
                    )

            return result

        except Exception as exc:
            # ------------------------------------------------
            # Failure state
            # ------------------------------------------------

            stage.status = "failed"
            stage.message = str(exc)

            raise

    # ======================================================
    # Diagnostics
    # ======================================================

    def status(self) -> dict[str, int]:
        """
        Return dispatcher runtime statistics.
        """

        return {
            "executed": self.executed,
        }

    # ======================================================
    # Lifecycle
    # ======================================================

    def reset(self) -> None:
        """
        Reset dispatcher execution statistics.
        """

        self.executed = 0

    # ======================================================
    # Python Protocols
    # ======================================================

    def __repr__(self) -> str:
        return (
            "StageDispatcher("
            f"executed={self.executed}"
            ")"
        )