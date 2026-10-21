"""
SciOS Pipeline Tests - Remove Stage
===================================

Unit test cho CognitivePipeline khi xoá stage.
Đảm bảo stage được xoá thành công và không còn trong pipeline.
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


def test_pipeline_remove_stage() -> None:
    """
    Pipeline nên xoá stage thành công.
    """

    pipeline = CognitivePipeline()

    # Thêm stage
    stage = DummyStage()
    pipeline.add_stage(stage)
    assert "dummy" in pipeline
    assert len(pipeline) == 1

    # Xoá stage
    pipeline.remove_stage("dummy")

    # Kiểm tra stage đã bị xoá
    assert "dummy" not in pipeline
    assert pipeline.get_stage("dummy") is None
    assert len(pipeline) == 0

    # __repr__ hiển thị đúng
    assert "CognitivePipeline" in repr(pipeline)
    assert "dummy" not in str(pipeline.status()["stages"])
