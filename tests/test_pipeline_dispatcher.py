"""
SciOS Pipeline Tests - Dispatcher
=================================

Unit test cho CognitivePipeline khi chạy stage qua StageDispatcher.
Đảm bảo dispatcher thực thi stage và cập nhật context.
"""

from scios.cognitive_core.kernel.pipeline import CognitivePipeline
from scios.cognitive_core.kernel.stage import CognitiveStage
from scios.cognitive_core.kernel.context import CognitiveContext
from scios.cognitive_core.kernel.request import CognitiveRequest


class DummyStage(CognitiveStage):
    def __init__(self, name: str = "dummy") -> None:
        super().__init__(name)

    def run(self, context: CognitiveContext):
        context.state[self.name] = f"Dispatched: {context.request.query}"
        context.trace.append(self.name)
        return context


def test_pipeline_dispatcher_runs_stage() -> None:
    """
    Pipeline nên dùng dispatcher để chạy stage.
    """
    pipeline = CognitivePipeline()
    stage = DummyStage()
    pipeline.add_stage(stage)

    request = CognitiveRequest(query="dispatcher test")
    context = CognitiveContext(request)

    result = pipeline.run(context)

    # Kiểm tra stage đã chạy qua dispatcher
    assert "dummy" in result.state
    assert result.state["dummy"] == "Dispatched: dispatcher test"
    assert "dummy" in result.trace

    # Dispatcher tồn tại và có thể gọi trực tiếp
    dispatched = pipeline.dispatcher.dispatch(stage, context)
    assert "dummy" in dispatched.state
    assert "dummy" in dispatched.trace
