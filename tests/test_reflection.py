# tests/test_reflection.py
import pytest
from scios.cognitive_core.reflection.reflection import ReflectionEngine

def test_reflection_engine_initialization():
    engine = ReflectionEngine()
    assert engine is not None

def test_reflection_engine_run_successful_execution():
    engine = ReflectionEngine()
    data = {
        "execution_result": {"success": True, "output": "Expected outcome"},
        "reasoning": {"prediction": "Expected outcome"},
        "plan": {"steps": ["step1", "step2"]},
    }
    report = engine.run(data)

    # Báo cáo phải chứa các phần chính
    assert "evaluation" in report
    assert "critique" in report
    assert "analysis" in report
    assert "metrics" in report
    assert "score" in report
    assert "feedback" in report
    assert "summary" in report

    # Score phải hợp lệ
    assert 0.0 <= report["score"]["final_score"] <= 1.0

def test_reflection_engine_run_failed_execution():
    engine = ReflectionEngine()
    data = {
        "execution_result": {"success": False, "error": "Runtime error"},
        "reasoning": {"prediction": "Expected outcome"},
        "plan": {"steps": ["step1"]},
    }
    report = engine.run(data)

    assert report["evaluation"]["success"] is False
    assert any("Execution failed" in w for w in report["critique"]["weaknesses"])
    assert report["score"]["final_score"] < 0.5

def test_reflection_engine_run_with_minimal_data():
    engine = ReflectionEngine()
    data = {}
    report = engine.run(data)

    # Báo cáo vẫn phải có đủ key, nhưng có thể rỗng
    required_keys = {"evaluation", "critique", "analysis", "metrics", "score", "feedback", "summary"}
    assert required_keys.issubset(report.keys())
