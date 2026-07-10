"""
SciOS Pipeline Tests - Clear Stages
===================================

Unit test cho CognitivePipeline khi xoá toàn bộ stage.
Đảm bảo clear() xoá hết stage và pipeline trở về rỗng.
"""

from scios.cognitive_core.kernel.pipeline import CognitivePipeline
from scios.cognitive_core.kernel.stage import CognitiveStage


class DummyStage(CognitiveStage):
    def __init__(self, name: str = "dummy") -> None:
        super().__init__(name)

    def run(self, context):
        context.state[self.name] = f"Processed: {context.request.query}"
        context.trace.append(self.name)
        return context


def test_pipeline_clear_stages() -> None:
    """
    Pipeline nên xoá toàn bộ stage khi gọi clear().
    """
    pipeline = CognitivePipeline()

    # Thêm nhiều stage
    pipeline.add_stage(DummyStage("s1"))
    pipeline.add_stage(DummyStage("s2"))
    pipeline.add_stage(DummyStage("s3"))

    assert len(pipeline) == 3
    assert "s1" in pipeline
    assert "s2" in pipeline
    assert "s3" in pipeline

    # Gọi clear()
    pipeline.clear()

    # Kiểm tra pipeline rỗng
    assert len(pipeline) == 0
    assert "s1" not in pipeline
    assert "s2" not in pipeline
    assert "s3" not in pipeline

    # __repr__ hiển thị đúng
    assert "CognitivePipeline" in repr(pipeline)
    assert pipeline.status()["stages"] == []
