import pytest
from scios.cognitive_core.reasoning.engine import ReasoningEngine

def test_engine_reason_pipeline():
    engine = ReasoningEngine()
    result = engine.reason("test query", {"context": "demo"})
    assert "query" in result
    assert "plan" in result
    assert "inference" in result
    assert "hypothesis" in result
    assert "verification" in result
    assert "accepted" in result

def test_engine_infer_alias():
    engine = ReasoningEngine()
    result = engine.infer("alias query")
    assert result["query"] == "alias query"

def test_engine_reset_and_state():
    engine = ReasoningEngine()
    engine.reset()
    assert isinstance(engine.state.status(), dict)

def test_engine_status_schema():
    engine = ReasoningEngine()
    status = engine.status()
    required = {"component", "planner", "inference", "hypothesis", "verifier", "state"}
    assert required.issubset(status.keys())
