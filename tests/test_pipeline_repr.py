"""
SciOS Pipeline Tests - Repr
===========================

Unit test cho CognitivePipeline khi gọi __repr__.
Đảm bảo __repr__ hiển thị thông tin pipeline và stage.
"""

from scios.cognitive_core.kernel.pipeline import CognitivePipeline
from scios.cognitive_core.kernel.stage import CognitiveStage


class DummyStage(CognitiveStage):
    def __init__(self, name: str = "dummy") -> None:
        super().__init__(name)

    def run(self, context):
        context.state[self.name] = "repr-test"
        context.trace.append(self.name)
        return context


def test_pipeline_repr_empty() -> None:
    """
    Pipeline mới khởi tạo nên __repr__ hiển thị CognitivePipeline và không có stage.
    """
    pipeline = CognitivePipeline()
    r = repr(pipeline)

    assert "CognitivePipeline" in r
    assert "stages=0" in r or "[]" in r


def test_pipeline_repr_with_stage() -> None:
    """
    Pipeline có stage nên __repr__ hiển thị tên stage.
    """
    pipeline = CognitivePipeline()
    pipeline.add_stage(DummyStage("s1"))
    pipeline.add_stage(DummyStage("s2"))

    r = repr(pipeline)

    assert "CognitivePipeline" in r
    assert "s1" in r
    assert "s2" in r
