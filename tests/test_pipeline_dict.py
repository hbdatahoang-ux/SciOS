"""
SciOS Pipeline Tests - Dict Representation
==========================================

Unit test cho CognitivePipeline khi chuyển sang dict.
Đảm bảo status() hoặc to_dict() trả về dict hợp lệ.
"""

from scios.cognitive_core.kernel.pipeline import CognitivePipeline
from scios.cognitive_core.kernel.stage import CognitiveStage
from scios.cognitive_core.kernel.state import PipelineState


class DummyStage(CognitiveStage):
    def __init__(self, name: str = "dummy") -> None:
        super().__init__(name)

    def run(self, context):
        context.state[self.name] = "dict-test"
        context.trace.append(self.name)
        return context


def test_pipeline_dict_empty() -> None:
    """
    Pipeline mới khởi tạo nên trả về dict với state CREATED và stages rỗng.
    """
    pipeline = CognitivePipeline()
    d = pipeline.status()  # hoặc pipeline.to_dict() nếu có

    assert isinstance(d, dict)
    assert d["state"] == PipelineState.CREATED.name
    assert d["stage_names"] == []


def test_pipeline_dict_with_stage() -> None:
    """
    Pipeline có stage nên dict phản ánh đúng danh sách stage.
    """
    pipeline = CognitivePipeline()
    pipeline.add_stage(DummyStage("s1"))
    pipeline.add_stage(DummyStage("s2"))

    d = pipeline.status()
    assert d["state"] == PipelineState.CREATED.name
    assert "s1" in d["stage_names"]
    assert "s2" in d["stage_names"]
    assert d["stage_count"] == 2
