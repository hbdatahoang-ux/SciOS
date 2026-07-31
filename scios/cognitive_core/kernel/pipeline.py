"""
SciOS Cognitive Pipeline
========================

Execution engine of CognitiveKernel.

Responsibilities
-----------------
- Manage cognitive stages
- Dispatch stage execution
- Apply middleware
- Emit kernel events
- Manage lifecycle state

Python 3.11+
"""

from __future__ import annotations


from typing import (
    Iterator,
    Any,
)


from scios.shared import EventBus


from .context import CognitiveContext
from .stage import CognitiveStage
from .dispatcher import StageDispatcher
from .middleware import MiddlewareManager
from .events import KernelEventType
from .state import PipelineState



__all__ = [
    "CognitivePipeline",
]



class CognitivePipeline:
    """
    CognitivePipeline.

    Core execution engine of SciOS CognitiveKernel.
    """



    # =====================================================
    # Construction
    # =====================================================

    def __init__(
        self,
        *,
        dispatcher: StageDispatcher | None = None,
        middleware: MiddlewareManager | None = None,
        event_bus: EventBus | None = None,
    ) -> None:


        self._stages: list[CognitiveStage] = []


        self.dispatcher = (
            dispatcher
            or StageDispatcher()
        )


        self.middleware = (
            middleware
            or MiddlewareManager()
        )


        # EventBus is mandatory in Kernel layer

        self.event_bus = (
            event_bus
            or EventBus()
        )


        self._state = (
            PipelineState.CREATED
        )



    # =====================================================
    # Properties
    # =====================================================

    @property
    def state(
        self,
    ) -> PipelineState:

        return self._state


    @property
    def stages(
        self,
    ) -> tuple[CognitiveStage, ...]:

        return tuple(
            self._stages
        )



    # =====================================================
    # Stage Management
    # =====================================================

    def add_stage(
        self,
        stage: CognitiveStage,
    ) -> None:


        if not isinstance(
            stage,
            CognitiveStage,
        ):

            raise TypeError(
                "stage must be CognitiveStage"
            )


        self._stages.append(
            stage
        )



    def remove_stage(
        self,
        name: str,
    ) -> None:


        self._stages = [
            stage
            for stage in self._stages
            if stage.name != name
        ]



    def get_stage(
        self,
        name: str,
    ) -> CognitiveStage | None:


        for stage in self._stages:

            if stage.name == name:

                return stage


        return None



    def clear(
        self,
    ) -> None:

        self._stages.clear()



    # =====================================================
    # Event Helper
    # =====================================================

    def _publish(
        self,
        event,
        payload: dict[str, Any],
    ) -> None:


        if self.event_bus is None:

            return


        try:

            self.event_bus.publish(
                event,
                payload,
            )

        except Exception:

            # Observability must not
            # break execution

            pass



    # =====================================================
    # Execution
    # =====================================================

    def run(
        self,
        context: CognitiveContext,
    ) -> CognitiveContext:
        """
        Execute cognitive pipeline.
        """


        self._state = (
            PipelineState.RUNNING
        )


        self._publish(
            KernelEventType.PIPELINE_STARTED,
            {
                "count":
                    len(self._stages)
            },
        )


        try:


            self.dispatcher.dispatch(
                context=context,
                stages=self._stages,
                middleware=self.middleware,
                event_bus=self.event_bus,
            )


            self._state = (
                PipelineState.COMPLETED
            )


            self._publish(
                KernelEventType.PIPELINE_COMPLETED,
                {
                    "success":
                        True
                },
            )


            return context



        except Exception as exc:


            self._state = (
                PipelineState.FAILED
            )


            self._publish(
                KernelEventType.PIPELINE_FAILED,
                {
                    "error":
                        str(exc)
                },
            )


            raise



    # =====================================================
    # Lifecycle
    # =====================================================

    def stop(
        self,
    ) -> None:

        self._state = (
            PipelineState.CANCELLED
        )



    def pause(
        self,
    ) -> None:

        self._state = (
            PipelineState.PAUSED
        )



    def resume(
        self,
    ) -> None:

        self._state = (
            PipelineState.RUNNING
        )



    def reset(
        self,
    ) -> None:
        """
        Reset execution state.

        Keep stages and EventBus.
        """

        self._state = (
            PipelineState.CREATED
        )


        self.dispatcher.reset()


        self.middleware.reset()



        for stage in self._stages:

            stage.reset()



    # =====================================================
    # Diagnostics
    # =====================================================

    def status(
        self,
    ) -> dict[str, Any]:


        return {

            "state":
                self._state.name,

            "stages":
            [
                stage.name
                for stage in self._stages
            ],

            "stage_count":
                len(self._stages),

            "dispatcher":
                self.dispatcher.status(),

        }



    def to_dict(
        self,
    ) -> dict[str, Any]:

        return self.status()



    # =====================================================
    # Python Protocols
    # =====================================================

    def __len__(
        self,
    ) -> int:

        return len(
            self._stages
        )



    def __iter__(
        self,
    ) -> Iterator[CognitiveStage]:

        return iter(
            self._stages
        )



    def __contains__(
        self,
        name: str,
    ) -> bool:

        return any(
            stage.name == name
            for stage in self._stages
        )



    def __repr__(
        self,
    ) -> str:
        """
        Developer-friendly representation.
        """

        stage_names = [
            stage.name
            for stage in self._stages
        ]


        return (
            "<CognitivePipeline "
            f"state={self._state.name} "
            f"stages={len(self._stages)} "
            f"names={stage_names}>"
        )