"""
SciOS Pipeline Tests - Resume
=============================

Unit test cho CognitivePipeline khi resume sau pause.
Đảm bảo trạng thái pipeline chuyển từ PAUSED sang RUNNING.
"""

from scios.cognitive_core.kernel.pipeline import CognitivePipeline
from scios.cognitive_core.kernel.state import PipelineState


def test_pipeline_resume_after_pause() -> None:
    """
    Pipeline nên chuyển sang trạng thái RUNNING khi gọi resume() sau pause().
    """
    pipeline = CognitivePipeline()

    # Ban đầu CREATED
    assert pipeline.status()["state"] == PipelineState.CREATED.name

    # Pause
    pipeline.pause()
    assert pipeline.status()["state"] == PipelineState.PAUSED.name

    # Resume
    pipeline.resume()
    status = pipeline.status()
    assert status["state"] == PipelineState.RUNNING.name

    # __repr__ hiển thị đúng
    assert "CognitivePipeline" in repr(pipeline)
    assert "RUNNING" in repr(pipeline)
