# tests/test_analyzer.py
import pytest
from scios.cognitive_core.reflection.analyzer import Analyzer

def test_analyzer_success_with_plan_and_reasoning():
    analyzer = Analyzer()
    data = {
        "reasoning": {"prediction": "Expected outcome"},
        "plan": {"steps": ["step1", "step2"]},
        "execution_result": {"success": True, "output": "Expected outcome"},
    }
    result = analyzer.process(data)
    assert "insights" in result
    assert "Execution matched reasoning prediction" in result["insights"]
    assert "Plan executed successfully" in result["insights"]
    assert result["mismatches"] == []

def test_analyzer_mismatch_reasoning():
    analyzer = Analyzer()
    data = {
        "reasoning": {"prediction": "Expected outcome"},
        "execution_result": {"success": True, "output": "Different outcome"},
    }
    result = analyzer.process(data)
    assert "mismatches" in result
    assert "Execution output did not match reasoning prediction" in result["mismatches"]

def test_analyzer_plan_failed():
    analyzer = Analyzer()
    data = {
        "plan": {"steps": ["step1"]},
        "execution_result": {"success": False},
    }
    result = analyzer.process(data)
    assert "mismatches" in result
    assert "Plan execution failed" in result["mismatches"]

def test_analyzer_missing_data_defaults():
    analyzer = Analyzer()
    data = {}  # no reasoning, plan, execution_result
    result = analyzer.process(data)
    # Should still return keys with empty lists
    assert "insights" in result
    assert "mismatches" in result
    assert result["insights"] == []
    assert result["mismatches"] == []
