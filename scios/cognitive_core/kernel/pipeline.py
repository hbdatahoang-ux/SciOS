"""
SciOS Cognitive Pipeline
========================

Execution Engine của CognitiveKernel.
Điều phối stage qua Registry, Dispatcher, Middleware.
Phát event qua EventBus.
"""

from typing import List, Dict, Any, Iterator
from .context import CognitiveContext
from .stage import CognitiveStage
from .dispatcher import StageDispatcher
from .middleware import MiddlewareManager
from .events import KernelEventType
from .state import PipelineState


class CognitivePipeline:
    """
    CognitivePipeline là Execution Engine của SciOS-NG.
    """

    def __init__(self, event_bus=None) -> None:
        self._stages: List[CognitiveStage] = []
        self.dispatcher = StageDispatcher()
        self.middleware = MiddlewareManager()
        self.event_bus = event_bus
        self._state: PipelineState = PipelineState.CREATED

    # -----------------------------------------------------
    # Stage Management
    # -----------------------------------------------------

    def add_stage(self, stage: CognitiveStage) -> None:
        self._stages.append(stage)

    def remove_stage(self, name: str) -> None:
        self._stages = [s for s in self._stages if s.name != name]

    def get_stage(self, name: str) -> CognitiveStage | None:
        for s in self._stages:
            if s.name == name:
                return s
        return None

    def clear(self) -> None:
        self._stages.clear()

    # -----------------------------------------------------
    # Runtime Control
    # -----------------------------------------------------

    def run(self, context: CognitiveContext) -> CognitiveContext:
        self._state = PipelineState.RUNNING
        if self.event_bus:
            self.event_bus.publish(KernelEventType.PIPELINE_STARTED, {"count": len(self._stages)})

        try:
            self.dispatcher.dispatch(
                context=context,
                stages=self._stages,
                middleware=self.middleware,
                event_bus=self.event_bus,
            )
            self._state = PipelineState.COMPLETED
            if self.event_bus:
                self.event_bus.publish(KernelEventType.PIPELINE_COMPLETED, {"success": True})
        except Exception as e:
            self._state = PipelineState.FAILED
            if self.event_bus:
                self.event_bus.publish(KernelEventType.PIPELINE_FAILED, {"error": str(e)})
            raise

        return context

    def stop(self) -> None:
        self._state = PipelineState.CANCELLED

    def pause(self) -> None:
        self._state = PipelineState.PAUSED

    def resume(self) -> None:
        self._state = PipelineState.RUNNING

    def reset(self) -> None:
        """Reset runtime state, giữ nguyên stage."""
        self._state = PipelineState.CREATED
        self.middleware = MiddlewareManager()
        self.dispatcher = StageDispatcher()

    # -----------------------------------------------------
    # Status & Serialization
    # -----------------------------------------------------

    def status(self) -> Dict[str, Any]:
        return {
            "state": self._state.name,
            "stages": [s.name for s in self._stages],
        }

    def to_dict(self) -> Dict[str, Any]:
        return self.status()

    # -----------------------------------------------------
    # Pythonic Helpers
    # -----------------------------------------------------

    def __len__(self) -> int:
        return len(self._stages)

    def __iter__(self) -> Iterator[CognitiveStage]:
        return iter(self._stages)

    def __contains__(self, name: str) -> bool:
        return any(s.name == name for s in self._stages)

    def __repr__(self) -> str:
        return f"<CognitivePipeline state={self._state.name} stages={len(self._stages)}>"
