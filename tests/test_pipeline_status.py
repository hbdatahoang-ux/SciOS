"""
SciOS Pipeline Tests - Status
=============================

Unit test cho CognitivePipeline khi gọi status().
Đảm bảo status() trả về dict với state và danh sách stage.
"""

from scios.cognitive_core.kernel.pipeline import CognitivePipeline
from scios.cognitive_core.kernel.stage import CognitiveStage
from scios.cognitive_core.kernel.state import PipelineState


class DummyStage(CognitiveStage):
    def __init__(self, name: str = "dummy") -> None:
        super().__init__(name)

    def run(self, context):
        context.state[self.name] = "status-test"
        context.trace.append(self.name)
        return context


def test_pipeline_status_initial() -> None:
    """
    Pipeline mới khởi tạo nên có state CREATED và không có stage.
    """
    pipeline = CognitivePipeline()
    status = pipeline.status()

    assert isinstance(status, dict)
    assert status["state"] == PipelineState.CREATED.name
    assert status["stage_names"] == []


def test_pipeline_status_with_stage() -> None:
    """
    Pipeline có stage nên status() phản ánh đúng danh sách stage.
    """
    pipeline = CognitivePipeline()
    pipeline.add_stage(DummyStage("s1"))
    pipeline.add_stage(DummyStage("s2"))

    status = pipeline.status()
    assert status["state"] == PipelineState.CREATED.name
    assert "s1" in status["stage_names"]
    assert "s2" in status["stage_names"]
    assert status["stage_count"] == 2
