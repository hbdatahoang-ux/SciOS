# tests/test_reflection_pipeline.py
import pytest
from scios.cognitive_core.reflection.reflection_pipeline import ReflectionPipeline

def test_pipeline_initialization():
    pipeline = ReflectionPipeline()
    assert pipeline is not None

def test_pipeline_run_successful_execution():
    pipeline = ReflectionPipeline()
    data = {
        "execution_result": {"success": True, "output": "Expected outcome"},
        "reasoning": {"prediction": "Expected outcome"},
        "plan": {"steps": ["step1", "step2"]},
    }
    report = pipeline.run(data)

    # Báo cáo phải chứa tất cả các phần chính
    required_keys = {
        "evaluation", "critique", "analysis", "metrics",
        "score", "improvement", "feedback", "report",
        "self_review", "validation"
    }
    assert required_keys.issubset(report.keys())
    assert report["evaluation"]["success"] is True
    assert 0.0 <= report["score"]["final_score"] <= 1.0
    assert report["validation"]["status"] in ["valid", "invalid"]

def test_pipeline_run_failed_execution():
    pipeline = ReflectionPipeline()
    data = {
        "execution_result": {"success": False, "error": "Runtime error"},
        "reasoning": {"prediction": "Expected outcome"},
        "plan": {"steps": ["step1"]},
    }
    report = pipeline.run(data)

    assert report["evaluation"]["success"] is False
    assert any("Execution failed" in w for w in report["critique"]["weaknesses"])
    assert report["score"]["final_score"] < 0.5
    assert report["validation"]["status"] == "invalid"

def test_pipeline_run_with_minimal_data():
    pipeline = ReflectionPipeline()
    data = {}
    report = pipeline.run(data)

    # Báo cáo vẫn phải có đủ key, nhưng có thể rỗng
    required_keys = {
        "evaluation", "critique", "analysis", "metrics",
        "score", "improvement", "feedback", "report",
        "self_review", "validation"
    }
    assert required_keys.issubset(report.keys())
    assert isinstance(report["report"]["summary"], str)
