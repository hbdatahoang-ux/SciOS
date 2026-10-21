"""
SciOS Pipeline Tests - Pause
============================

Unit test cho CognitivePipeline khi tạm dừng.
Đảm bảo trạng thái pipeline chuyển sang PAUSED.
"""

from scios.cognitive_core.kernel.pipeline import CognitivePipeline
from scios.cognitive_core.kernel.state import PipelineState


def test_pipeline_pause() -> None:
    """
    Pipeline nên chuyển sang trạng thái PAUSED khi gọi pause().
    """
    pipeline = CognitivePipeline()

    # Trạng thái ban đầu CREATED
    assert pipeline.status()["state"] == PipelineState.CREATED.name

    # Gọi pause()
    pipeline.pause()

    # Kiểm tra trạng thái
    status = pipeline.status()
    assert status["state"] == PipelineState.PAUSED.name

    # __repr__ hiển thị đúng
    assert "CognitivePipeline" in repr(pipeline)
    assert "PAUSED" in repr(pipeline)
