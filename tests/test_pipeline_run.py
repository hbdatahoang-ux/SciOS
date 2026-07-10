"""
SciOS Pipeline Tests - Run
==========================

Unit test cho CognitivePipeline khi chạy với context.
Đảm bảo stage được thực thi, middleware được gọi,
và trạng thái pipeline thay đổi đúng.
"""

from scios.cognitive_core.kernel.pipeline import CognitivePipeline
from scios.cognitive_core.kernel.stage import CognitiveStage
from scios.cognitive_core.kernel.context import CognitiveContext
from scios.cognitive_core.kernel.request import CognitiveRequest
from scios.cognitive_core.kernel.state import PipelineState


class DummyStage(CognitiveStage):
    def __init__(self, name: str = "dummy") -> None:
        super().__init__(name)

    def run(self, context: CognitiveContext):
        context.state[self.name] = f"Processed: {context.request.query}"
        context.trace.append(self.name)
        return context


def test_pipeline_run_single_stage() -> None:
    """
    Pipeline nên chạy stage và cập nhật context.
    """
    pipeline = CognitivePipeline()
    pipeline.add_stage(DummyStage())

    request = CognitiveRequest(query="hello world")
    context = CognitiveContext(request)

    result = pipeline.run(context)

    # Kiểm tra stage đã chạy
    assert "dummy" in result.state
    assert result.state["dummy"] == "Processed: hello world"
    assert "dummy" in result.trace

    # Kiểm tra trạng thái pipeline
    status = pipeline.status()
    assert status["state"] == PipelineState.COMPLETED.name
    assert "dummy" in status["stages"]


def test_pipeline_run_empty() -> None:
    """
    Pipeline không có stage vẫn chạy và hoàn thành.
    """
    pipeline = CognitivePipeline()

    request = CognitiveRequest(query="no stages")
    context = CognitiveContext(request)

    result = pipeline.run(context)

    # Không có stage nào được chạy
    assert result.state == {}
    assert result.trace == []

    # Trạng thái pipeline vẫn COMPLETED
    status = pipeline.status()
    assert status["state"] == PipelineState.COMPLETED.name
    assert status["stages"] == []
