# tests/test_tool_pipeline.py

import pytest
from scios.cognitive_core.tool_use.pipeline import ToolPipeline
from scios.cognitive_core.tool_use.stage import ToolStage
from scios.cognitive_core.tool_use.request import ToolRequest
from scios.cognitive_core.tool_use.response import ToolResponse


class DummyStage(ToolStage):
    def __init__(self, name="dummy"):
        super().__init__()
        self.name = name

    def run(self, request: ToolRequest):
        if request.action == "fail":
            self.error("Stage failed")
            raise RuntimeError("Stage failed")
        self.complete(f"Stage {self.name} executed")
        return ToolResponse.success(tool=request.tool, result=f"{self.name} ok")


def test_pipeline_initialization_and_schema():
    pipeline = ToolPipeline()
    assert pipeline.stages == []
    data = pipeline.to_dict()
    required_keys = {"stages"}
    assert required_keys.issubset(data.keys())
    assert isinstance(data["stages"], list)


def test_pipeline_add_and_run_success():
    pipeline = ToolPipeline()
    stage1 = DummyStage(name="alpha")
    stage2 = DummyStage(name="beta")
    pipeline.add_stage(stage1)
    pipeline.add_stage(stage2)

    req = ToolRequest(tool="calculator", action="evaluate", params={"x": 1})
    resp = pipeline.run(req)

    assert isinstance(resp, ToolResponse)
    assert resp.status == "success"
    assert "beta ok" in resp.result
    assert stage1.status == "success"
    assert stage2.status == "success"


def test_pipeline_run_with_failure_stage():
    pipeline = ToolPipeline()
    stage1 = DummyStage(name="alpha")
    stage2 = DummyStage(name="beta")
    pipeline.add_stage(stage1)
    pipeline.add_stage(stage2)

    req = ToolRequest(tool="calculator", action="fail", params={})
    with pytest.raises(RuntimeError):
        pipeline.run(req)

    assert stage1.status == "error"
    # stage2 chưa chạy
    assert stage2.status == "idle"


def test_pipeline_reset():
    pipeline = ToolPipeline()
    stage = DummyStage(name="gamma")
    pipeline.add_stage(stage)

    req = ToolRequest(tool="echo", action="say", params={"msg": "hi"})
    pipeline.run(req)
    assert stage.status == "success"

    pipeline.reset()
    assert stage.status == "idle"
    assert pipeline.stages[0].message is None


def test_pipeline_repr_shows_stage_count():
    pipeline = ToolPipeline()
    pipeline.add_stage(DummyStage(name="delta"))
    repr_str = repr(pipeline)
    assert "stages=1" in repr_str
