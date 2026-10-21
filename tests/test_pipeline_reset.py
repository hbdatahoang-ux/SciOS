"""
SciOS Pipeline Tests - Reset
============================

Unit test cho CognitivePipeline khi reset.
Đảm bảo reset() chỉ reset runtime state, không xoá stage.
"""

from scios.cognitive_core.kernel.pipeline import CognitivePipeline
from scios.cognitive_core.kernel.stage import CognitiveStage
from scios.cognitive_core.kernel.state import PipelineState


class DummyStage(CognitiveStage):
    def __init__(self, name: str = "dummy") -> None:
        super().__init__(name)

    def run(self, context):
        context.state[self.name] = "reset-test"
        context.trace.append(self.name)
        return context


def test_pipeline_reset_keeps_stages() -> None:
    """
    Pipeline reset() không xoá stage, chỉ reset runtime.
    """
    pipeline = CognitivePipeline()
    stage = DummyStage()
    pipeline.add_stage(stage)

    # Chạy pipeline để thay đổi state
    from scios.cognitive_core.kernel.context import CognitiveContext
    from scios.cognitive_core.kernel.request import CognitiveRequest
    request = CognitiveRequest(query="hello")
    context = CognitiveContext(request)
    pipeline.run(context)
    assert pipeline.status()["state"] == PipelineState.COMPLETED.name

    # Reset pipeline
    pipeline.reset()

    # Stage vẫn còn
    assert "dummy" in pipeline
    assert pipeline.get_stage("dummy") is stage
    assert len(pipeline) == 1

    # Trạng thái quay về CREATED
    status = pipeline.status()
    assert status["state"] == PipelineState.CREATED.name

    # __repr__ hiển thị đúng
    assert "CognitivePipeline" in repr(pipeline)
    assert "CREATED" in repr(pipeline)
