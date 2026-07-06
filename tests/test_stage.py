# tests/test_stage.py
import pytest
from scios.cognitive_core.reasoning.stage import ReasoningStage

def test_stage_run_returns_expected_schema():
    stage = ReasoningStage()
    query = "Sample query"
    context = {"topic": "demo"}

    result = stage.run(query, context)

    # Kiểm tra schema cơ bản
    assert isinstance(result, dict)
    assert result["stage"] == "ReasoningStage"
    assert result["query"] == query

    # Các bước reasoning phải có
    assert "plan" in result
    assert "inference" in result
    assert "hypothesis" in result
    assert "verification" in result

    # Plan phải có steps và chứa "analyze query"
    assert isinstance(result["plan"]["steps"], list)
    assert "analyze query" in result["plan"]["steps"]

def test_stage_status_and_reset_behavior():
    stage = ReasoningStage()
    stage.run("Test query", {})
    status_before = stage.status()
    assert status_before["stage"] == "ReasoningStage"
    assert status_before["records"] >= 1

    stage.reset()
    status_after = stage.status()
    assert status_after["records"] == 0
