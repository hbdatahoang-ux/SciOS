# tests/test_improvement.py
import pytest
from scios.cognitive_core.reflection.improvement import Improvement

def test_improvement_with_mismatches_and_weaknesses():
    improvement = Improvement()
    data = {
        "analysis": {"mismatches": ["Output mismatch"]},
        "critique": {"weaknesses": ["Poor error handling"], "risks": []},
        "score": {"final_score": 0.4},
    }
    result = improvement.process(data)

    # Có đề xuất cho mismatches và weaknesses
    assert any("Output mismatch" in s for s in result["execution"])
    assert any("Poor error handling" in s for s in result["execution"])
    # Score thấp → có đề xuất bổ sung
    assert any("Low score" in s for s in result["execution"])

def test_improvement_with_risks():
    improvement = Improvement()
    data = {
        "analysis": {"mismatches": []},
        "critique": {"weaknesses": [], "risks": ["Security vulnerability"]},
        "score": {"final_score": 0.8},
    }
    result = improvement.process(data)

    # Có đề xuất cho risk
    assert any("Security vulnerability" in s for s in result["execution"])

def test_improvement_with_high_score_and_no_issues():
    improvement = Improvement()
    data = {
        "analysis": {"mismatches": []},
        "critique": {"weaknesses": [], "risks": []},
        "score": {"final_score": 0.95},
    }
    result = improvement.process(data)

    # Không có đề xuất nào khi score cao và không có vấn đề
    assert result["execution"] == []
    assert result["planning"] == []
    assert result["reasoning"] == []

def test_improvement_partial_data_defaults():
    improvement = Improvement()
    data = {}  # thiếu toàn bộ keys
    result = improvement.process(data)

    # Vẫn trả về đủ keys với list rỗng
    assert set(result.keys()) == {"execution", "planning", "reasoning"}
    assert result["execution"] == []
    assert result["planning"] == []
    assert result["reasoning"] == []
