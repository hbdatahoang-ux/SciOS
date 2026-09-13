# tests/test_feedback.py
import pytest
from scios.cognitive_core.reflection.feedback import Feedback

def test_feedback_with_improvements():
    feedback = Feedback()
    improvements = {
        "execution": ["Review execution pipeline"],
        "planning": ["Refine planning strategy"],
        "reasoning": ["Add safeguards in reasoning"],
    }
    result = feedback.process(improvements)

    # Suggestions phải chứa các câu "Consider ..."
    assert any("Consider Review execution pipeline" in s for s in result["suggestions"])
    assert any("Consider Refine planning strategy" in s for s in result["suggestions"])
    assert any("Consider Add safeguards in reasoning" in s for s in result["suggestions"])

    # Notes phải chứa các câu "Improvement identified ..."
    assert any("Improvement identified in execution" in n for n in result["notes"])
    assert any("Improvement identified in planning" in n for n in result["notes"])
    assert any("Improvement identified in reasoning" in n for n in result["notes"])

def test_feedback_with_empty_improvements():
    feedback = Feedback()
    improvements = {
        "execution": [],
        "planning": [],
        "reasoning": [],
    }
    result = feedback.process(improvements)

    # Không có suggestions hoặc notes
    assert result["suggestions"] == []
    assert result["notes"] == []

def test_feedback_with_partial_improvements():
    feedback = Feedback()
    improvements = {
        "execution": ["Investigate low performance causes"],
        "planning": [],
    }
    result = feedback.process(improvements)

    # Có suggestion cho execution nhưng không cho planning
    assert any("Consider Investigate low performance causes" in s for s in result["suggestions"])
    assert any("Improvement identified in execution" in n for n in result["notes"])
    assert all("planning" not in n for n in result["notes"])
