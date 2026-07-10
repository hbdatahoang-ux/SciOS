"""
SciOS Stage Dispatcher
======================

Điều phối thực thi stage trong CognitivePipeline.
Quyết định stage tiếp theo, gọi middleware, phát event,
xử lý exception, retry, rollback.
"""

from typing import List
from .context import CognitiveContext
from .stage import CognitiveStage
from .middleware import MiddlewareManager
from .events import KernelEventType


class StageDispatcher:
    """
    StageDispatcher điều phối toàn bộ execution của pipeline.
    """

    def __init__(self) -> None:
        self._max_retries: int = 1

    def dispatch(
        self,
        context: CognitiveContext,
        stages: List[CognitiveStage],
        middleware: MiddlewareManager,
        event_bus=None,
    ) -> None:
        """
        Điều phối thực thi qua tất cả stage.
        """

        for stage in stages:
            try:
                # phát sự kiện StageStarted
                if event_bus:
                    event_bus.publish(KernelEventType.STAGE_STARTED, {"stage": stage.name})

                # middleware trước stage
                middleware.run_before_stage(stage, context)

                # chạy stage
                stage.run(context)

                # middleware sau stage
                middleware.run_after_stage(stage, context)

                # phát sự kiện StageCompleted
                if event_bus:
                    event_bus.publish(KernelEventType.STAGE_COMPLETED, {"stage": stage.name})

            except Exception as e:
                # phát sự kiện StageFailed
                if event_bus:
                    event_bus.publish(KernelEventType.STAGE_FAILED, {"stage": stage.name, "error": str(e)})

                # retry logic
                if self._max_retries > 0:
                    self._max_retries -= 1
                    continue  # thử lại stage
                else:
                    # rollback logic (placeholder)
                    if event_bus:
                        event_bus.publish(KernelEventType.STAGE_ROLLBACK, {"stage": stage.name})
                    raise
