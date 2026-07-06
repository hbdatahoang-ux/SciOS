# tests/test_planner_stage.py
import pytest
from scios.cognitive_core.reasoning.PlannerStage import PlannerStage

def test_planner_stage_run_creates_plan():
    stage = PlannerStage()
    query = "What is the capital of France?"
    context = {"topic": "geography"}

    result = stage.run(query, context)

    # Kiểm tra schema cơ bản
    assert isinstance(result, dict)
    assert result["stage"] == "PlannerStage"
    assert result["query"] == query
    assert "plan" in result
    assert "steps" in result["plan"]
    assert isinstance(result["plan"]["steps"], list)
    assert "analyze query" in result["plan"]["steps"]

def test_planner_stage_status_and_reset():
    stage = PlannerStage()
    stage.run("Test query", {})
    status_before = stage.status()
    assert status_before["stage"] == "PlannerStage"
    assert status_before["planner"]["plans_generated"] >= 1

    stage.reset()
    status_after = stage.status()
    assert status_after["planner"]["plans_generated"] == 0
