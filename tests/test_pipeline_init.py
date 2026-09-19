"""
SciOS Pipeline Tests - Initialization
=====================================

Unit test cho CognitivePipeline khi khởi tạo.
Đảm bảo pipeline bắt đầu ở trạng thái CREATED,
không có stage, middleware và dispatcher sẵn sàng.
"""

from scios.cognitive_core.kernel.pipeline import CognitivePipeline
from scios.cognitive_core.kernel.state import PipelineState


def test_pipeline_initialization() -> None:
    """
    Pipeline nên khởi tạo thành công với trạng thái CREATED.
    """

    pipeline = CognitivePipeline()

    # Trạng thái ban đầu
    status = pipeline.status()
    assert status["state"] == PipelineState.CREATED.name

    # Không có stage nào
    assert len(pipeline) == 0

    # Middleware và Dispatcher tồn tại
    assert pipeline.middleware is not None
    assert pipeline.dispatcher is not None

    # EventBus được gắn
    assert pipeline.event_bus is not None

    # __repr__ hiển thị đúng
    assert "CognitivePipeline" in repr(pipeline)
