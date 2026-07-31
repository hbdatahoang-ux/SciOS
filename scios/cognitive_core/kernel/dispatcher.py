"""
SciOS Cognitive Stage Dispatcher
================================

Dispatcher layer for CognitivePipeline.

Responsibilities:
- Execute single stage
- Execute multiple stages
- Middleware support
- Event integration

Python 3.11+
"""

from __future__ import annotations

from typing import Iterable, Any


from .stage import CognitiveStage


__all__ = [
    "StageDispatcher",
]



class StageDispatcher:
    """
    Central dispatcher for cognitive stages.
    """


    def __init__(
        self,
    ) -> None:

        self.executed = 0



    # ======================================================
    # Single Stage Dispatch
    # ======================================================

    def dispatch(
        self,
        *args,
        **kwargs,
    ):
        """
        Universal dispatch API.

        Supported:

        1.
        dispatch(stage, context)

        2.
        dispatch(
            context=context,
            stages=[...],
            middleware=None,
            event_bus=None,
        )
        """


        # --------------------------------------------------
        # Single stage mode
        # --------------------------------------------------

        if len(args) == 2:

            stage, context = args

            return self._dispatch_stage(
                stage,
                context,
            )



        # --------------------------------------------------
        # Pipeline mode
        # --------------------------------------------------

        context = kwargs.get(
            "context"
        )

        stages = kwargs.get(
            "stages",
            []
        )

        middleware = kwargs.get(
            "middleware"
        )

        event_bus = kwargs.get(
            "event_bus"
        )


        result = None


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
        context,
        *,
        middleware=None,
        event_bus=None,
    ):
        """
        Execute one cognitive stage.
        """


        try:


            # middleware before

            if middleware:

                middleware.before_stage(
                    stage,
                    context,
                )


            if event_bus:

                event_bus.publish(
                    "stage.started",
                    {
                        "stage": stage.name
                    }
                )



            stage.status = "running"


            result = stage.run(
                context
            )


            stage.status = "completed"


            self.executed += 1



            if event_bus:

                event_bus.publish(
                    "stage.completed",
                    {
                        "stage": stage.name
                    }
                )



            # middleware after

            if middleware:

                middleware.after_stage(
                    stage,
                    context,
                )


            return result



        except Exception as exc:


            stage.status = "failed"

            stage.message = str(
                exc
            )


            raise



    # ======================================================
    # Diagnostics
    # ======================================================

    def status(
        self,
    ) -> dict:


        return {

            "executed":
                self.executed,

        }



    def reset(
        self,
    ) -> None:


        self.executed = 0



    def __repr__(
        self,
    ) -> str:


        return (
            "StageDispatcher("
            f"executed={self.executed}"
            ")"
        )