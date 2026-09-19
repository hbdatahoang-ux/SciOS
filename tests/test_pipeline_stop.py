"""
SciOS Pipeline Tests - Stop
===========================

Unit test cho CognitivePipeline khi dừng.
Đảm bảo trạng thái pipeline chuyển sang CANCELLED.
"""

from scios.cognitive_core.kernel.pipeline import CognitivePipeline
from scios.cognitive_core.kernel.state import PipelineState


def test_pipeline_stop() -> None:
    """
    Pipeline nên chuyển sang trạng thái CANCELLED khi gọi stop().
    """
    pipeline = CognitivePipeline()

    # Ban đầu CREATED
    assert pipeline.status()["state"] == PipelineState.CREATED.name

    # Gọi stop()
    pipeline.stop()

    # Kiểm tra trạng thái
    status = pipeline.status()
    assert status["state"] == PipelineState.CANCELLED.name

    # __repr__ hiển thị đúng
    assert "CognitivePipeline" in repr(pipeline)
    assert "CANCELLED" in repr(pipeline)
