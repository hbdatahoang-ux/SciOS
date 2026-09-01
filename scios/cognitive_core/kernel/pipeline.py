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
- Provide diagnostics and serialization

Python 3.11+
"""

from __future__ import annotations

from typing import Any, Iterator

from scios.shared import EventBus

from .context import CognitiveContext
from .dispatcher import StageDispatcher
from .events import KernelEventType
from .middleware import MiddlewareManager
from .stage import CognitiveStage
from .state import PipelineState


__all__ = [
    "CognitivePipeline",
    "Pipeline",
]


class CognitivePipeline:
    """
    Ordered execution pipeline for cognitive stages.

    Stages are uniquely identified by name.

    Adding a stage with an existing name replaces the
    previous stage while preserving its position.
    """

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
            if dispatcher is not None
            else StageDispatcher()
        )

        self.middleware = (
            middleware
            if middleware is not None
            else MiddlewareManager()
        )

        self.event_bus = (
            event_bus
            if event_bus is not None
            else EventBus()
        )

        self._state = PipelineState.CREATED

    # =========================================================
    # Properties
    # =========================================================

    @property
    def state(self) -> PipelineState:
        """Return the current pipeline state."""
        return self._state

    @property
    def stages(self) -> tuple[CognitiveStage, ...]:
        """Return registered stages in execution order."""
        return tuple(self._stages)

    # =========================================================
    # Stage Management
    # =========================================================

    def add(
        self,
        stage: CognitiveStage,
    ) -> CognitivePipeline:
        """
        Register a stage.

        If another stage has the same name, it is replaced.

        Returns
        -------
        CognitivePipeline
            This pipeline instance.

        Notes
        -----
        Returning ``self`` provides a fluent API:

        ``pipeline.add(first).add(second)``
        """
        if not isinstance(stage, CognitiveStage):
            raise TypeError(
                "stage must be an instance of CognitiveStage"
            )

        for index, existing in enumerate(self._stages):
            if existing.name == stage.name:
                self._stages[index] = stage
                return self

        self._stages.append(stage)

        return self

    def add_stage(
        self,
        stage: CognitiveStage,
    ) -> CognitivePipeline:
        """Compatibility alias for :meth:`add`."""
        return self.add(stage)

    def get(
        self,
        name: str,
    ) -> CognitiveStage | None:
        """Return the first stage matching ``name``."""
        for stage in self._stages:
            if stage.name == name:
                return stage

        return None

    def get_stage(
        self,
        name: str,
    ) -> CognitiveStage | None:
        """Compatibility alias for :meth:`get`."""
        return self.get(name)

    def remove(
        self,
        name: str,
    ) -> CognitivePipeline:
        """
        Remove a stage by name.

        The operation is idempotent. If the stage does not exist,
        the pipeline remains unchanged.

        Returns
        -------
        CognitivePipeline
            This pipeline instance.
        """
        for index, stage in enumerate(self._stages):
            if stage.name == name:
                self._stages.pop(index)
                break

        return self

    def remove_stage(
        self,
        name: str,
    ) -> CognitivePipeline:
        """Compatibility alias for :meth:`remove`."""
        return self.remove(name)

    def clear(self) -> CognitivePipeline:
        """
        Remove all registered stages.

        Returns
        -------
        CognitivePipeline
            This pipeline instance.
        """
        self._stages.clear()

        return self

    # =========================================================
    # Lifecycle
    # =========================================================

    def initialize(self) -> CognitivePipeline:
        """
        Initialize every registered stage.

        Stage execution count is preserved.

        Returns
        -------
        CognitivePipeline
            This pipeline instance.
        """
        for stage in self._stages:
            stage.initialize()

        self._state = PipelineState.INITIALIZED

        return self

    def reset(self) -> CognitivePipeline:
        """
        Reset pipeline runtime state.

        Registered stages remain in the pipeline.

        Execution counters are preserved according to the
        stage contract.

        Returns
        -------
        CognitivePipeline
            This pipeline instance.
        """
        self._state = PipelineState.CREATED

        self.dispatcher.reset()
        self.middleware.reset()

        for stage in self._stages:
            stage.reset()

        return self

    def stop(self) -> CognitivePipeline:
        """
        Move the pipeline to cancelled state.

        Returns
        -------
        CognitivePipeline
            This pipeline instance.
        """
        self._state = PipelineState.CANCELLED

        return self

    def pause(self) -> CognitivePipeline:
        """
        Move the pipeline to paused state.

        Returns
        -------
        CognitivePipeline
            This pipeline instance.
        """
        self._state = PipelineState.PAUSED

        return self

    def resume(self) -> CognitivePipeline:
        """
        Resume the pipeline.

        Returns
        -------
        CognitivePipeline
            This pipeline instance.
        """
        self._state = PipelineState.RUNNING

        return self

    # =========================================================
    # Events
    # =========================================================

    def _publish(
        self,
        event: KernelEventType | str,
        payload: dict[str, Any],
    ) -> None:
        """
        Publish an event without allowing event-bus failures
        to interrupt pipeline execution.

        ``EventBus.publish`` accepts keyword payload:

        ``publish(event, **payload)``
        """
        if self.event_bus is None:
            return

        try:
            event_name = (
                event.value
                if isinstance(event, KernelEventType)
                else event
            )

            self.event_bus.publish(
                event_name,
                **payload,
            )

        except Exception:
            # Observability/event delivery must never break
            # cognitive execution.
            pass

    # =========================================================
    # Execution
    # =========================================================

    def run(
        self,
        context: CognitiveContext,
    ) -> Any:
        """
        Execute all stages in registration order.

        The result of the final stage is returned.
        """
        if not isinstance(context, CognitiveContext):
            raise TypeError(
                "context must be an instance of CognitiveContext"
            )

        self._state = PipelineState.RUNNING

        self._publish(
            KernelEventType.PIPELINE_STARTED,
            {
                "count": len(self._stages),
            },
        )

        try:
            result = self.dispatcher.dispatch(
                context=context,
                stages=self._stages,
                middleware=self.middleware,
                event_bus=self.event_bus,
            )

        except Exception as exc:
            self._state = PipelineState.FAILED

            self._publish(
                KernelEventType.PIPELINE_FAILED,
                {
                    "error": str(exc),
                },
            )

            raise

        self._state = PipelineState.COMPLETED

        self._publish(
            KernelEventType.PIPELINE_COMPLETED,
            {
                "success": True,
            },
        )

        return result

    # =========================================================
    # Diagnostics
    # =========================================================

    def status(self) -> dict[str, Any]:
        """
        Return a diagnostic snapshot.

        Contract
        --------
        ``stages``
            Number of registered stages.

        ``stage_names``
            Names of registered stages in execution order.
        """
        return {
            "state": self._state.name,
            "stages": len(self._stages),
            "stage_names": [
                stage.name
                for stage in self._stages
            ],
            "stage_count": len(self._stages),
            "dispatcher": self.dispatcher.status(),
        }

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize pipeline diagnostics.

        Includes stage names and serialized stage state.
        """
        return {
            "state": self._state.name,
            "stages": [
                stage.to_dict()
                for stage in self._stages
            ],
            "stage_names": [
                stage.name
                for stage in self._stages
            ],
            "stage_count": len(self._stages),
            "dispatcher": self.dispatcher.status(),
        }

    # =========================================================
    # Python Protocols
    # =========================================================

    def __len__(self) -> int:
        return len(self._stages)

    def __iter__(self) -> Iterator[CognitiveStage]:
        return iter(self._stages)

    def __contains__(self, name: str) -> bool:
        return self.get(name) is not None

    def __repr__(self) -> str:
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


# =============================================================
# Backward Compatibility
# =============================================================

Pipeline = CognitivePipeline