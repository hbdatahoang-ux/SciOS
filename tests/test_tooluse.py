"""
SciOS Tool Use Tests
====================

Unit tests for the Tool Use module.
Validate that pipeline can call external tools.
"""

import pytest
from scios.cognitive_core.tooluse.tooluse import ToolUseStage
from scios.cognitive_core.pipeline.pipeline import CognitivePipeline

def test_tooluse_stage_runs():
    pipeline = CognitivePipeline([ToolUseStage()])
    result = pipeline.run("calculate 2+2")

    assert result is not None
    assert "tooluse" in result
    assert result["tooluse"]["output"] == "4"

def test_tooluse_multiple_calls():
    pipeline = CognitivePipeline([ToolUseStage()])
    outputs = []
    for expr in ["1+1", "2*3", "10-4"]:
        outputs.append(pipeline.run(expr)["tooluse"]["output"])

    assert outputs == ["2", "6", "6"]
