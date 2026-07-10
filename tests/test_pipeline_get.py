"""
SciOS Pipeline Tests - Get Stage
================================

Unit test cho CognitivePipeline khi truy vấn stage.
Đảm bảo get_stage trả về đúng stage hoặc None nếu không tồn tại.
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


def test_pipeline_get_existing_stage() -> None:
    """
    Pipeline nên trả về stage khi tồn tại.
    """
    pipeline = CognitivePipeline()
    stage = DummyStage()
    pipeline.add_stage(stage)

    retrieved = pipeline.get_stage("dummy")
    assert retrieved is stage
    assert retrieved.name == "dummy"


def test_pipeline_get_nonexistent_stage() -> None:
    """
    Pipeline nên trả về None khi stage không tồn tại.
    """
    pipeline = CognitivePipeline()

    retrieved = pipeline.get_stage("missing")
    assert retrieved is None
