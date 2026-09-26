"""
SciOS Pipeline Tests - Middleware
=================================

Unit test cho CognitivePipeline khi middleware được áp dụng.
Đảm bảo middleware chạy trước và sau stage, thay đổi context.
"""

from scios.cognitive_core.kernel.pipeline import CognitivePipeline
from scios.cognitive_core.kernel.stage import CognitiveStage
from scios.cognitive_core.kernel.context import CognitiveContext
from scios.cognitive_core.kernel.request import CognitiveRequest


class DummyStage(CognitiveStage):
    def __init__(self, name: str = "dummy") -> None:
        super().__init__(name)

    def run(self, context: CognitiveContext):
        context.state[self.name] = f"Stage processed: {context.request.query}"
        context.trace.append(self.name)
        return context


def test_pipeline_middleware_applied() -> None:
    """
    Pipeline nên áp dụng middleware trước và sau stage.
    """
    pipeline = CognitivePipeline()
    pipeline.add_stage(DummyStage())

    # Middleware trước stage
    def before_middleware(context: CognitiveContext):
        context.state["before"] = "middleware before"
        context.trace.append("before")
        return context

    # Middleware sau stage
    def after_middleware(context: CognitiveContext):
        context.state["after"] = "middleware after"
        context.trace.append("after")
        return context

    pipeline.middleware.add_before(before_middleware)
    pipeline.middleware.add_after(after_middleware)

    request = CognitiveRequest(query="middleware test")
    context = CognitiveContext(request)

    result = pipeline.run(context)

    # Kiểm tra middleware trước
    assert "before" in result.state
    assert result.state["before"] == "middleware before"
    assert "before" in result.trace

    # Kiểm tra stage
    assert "dummy" in result.state
    assert "dummy" in result.trace

    # Kiểm tra middleware sau
    assert "after" in result.state
    assert result.state["after"] == "middleware after"
    assert "after" in result.trace
