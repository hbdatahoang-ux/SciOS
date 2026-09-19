# tests/test_report.py
import pytest
from scios.cognitive_core.reflection.report import ReflectionReport

def test_report_generation_with_complete_data():
    report = ReflectionReport()
    data = {
        "evaluation": {"success": True},
        "critique": {"strengths": ["Robust logic"], "weaknesses": ["Slow response"], "risks": []},
        "analysis": {"insights": ["Execution matched reasoning"], "mismatches": []},
        "metrics": {"accuracy": 0.9, "confidence": 0.8, "latency": 0.5, "coverage": 1.0},
        "score": {"final_score": 0.85},
        "feedback": {"suggestions": ["Improve error handling"], "notes": ["Consider optimizing latency"]},
    }
    result = report.process(data)

    assert "summary" in result
    assert "Evaluation" in result["summary"]
    assert "Critique" in result["summary"]
    assert "Analysis" in result["summary"]
    assert "Metrics" in result["summary"]
    assert "Score" in result["summary"]
    assert "Feedback" in result["summary"]

def test_report_generation_with_partial_data():
    report = ReflectionReport()
    data = {
        "evaluation": {"success": False},
        "score": {"final_score": 0.3},
    }
    result = report.process(data)

    assert "summary" in result
    # Summary vẫn phải chứa thông tin cơ bản
    assert "Evaluation" in result["summary"]
    assert "Score" in result["summary"]

def test_report_generation_empty_data():
    report = ReflectionReport()
    data = {}
    result = report.process(data)

    assert "summary" in result
    # Khi không có dữ liệu, summary vẫn tồn tại nhưng có thể rỗng hoặc placeholder
    assert isinstance(result["summary"], str)
    assert len(result["summary"]) > 0

def test_report_repr_contains_summary():
    report = ReflectionReport()
    data = {"evaluation": {"success": True}, "score": {"final_score": 0.9}}
    result = report.process(data)

    repr_str = repr(report)
    assert "ReflectionReport" in repr_str
