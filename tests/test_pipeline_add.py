"""
SciOS Pipeline Tests - Add Stage
================================

Unit test cho CognitivePipeline khi thêm stage.
Đảm bảo stage được thêm thành công và có thể truy vấn.
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


def test_pipeline_add_stage() -> None:
    """
    Pipeline nên thêm stage thành công.
    """

    pipeline = CognitivePipeline()

    # Thêm stage
    stage = DummyStage()
    pipeline.add_stage(stage)

    # Kiểm tra số lượng stage
    assert len(pipeline) == 1

    # Kiểm tra stage có trong pipeline
    assert "dummy" in pipeline

    # Lấy stage bằng get_stage
    retrieved = pipeline.get_stage("dummy")
    assert retrieved is stage

    # __repr__ hiển thị đúng
    assert "CognitivePipeline" in repr(pipeline)
    assert "dummy" in pipeline.status()["stage_names"]
