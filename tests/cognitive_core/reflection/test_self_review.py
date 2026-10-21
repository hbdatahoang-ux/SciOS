# tests/test_self_review.py
import pytest
from scios.cognitive_core.reflection.self_review import SelfReview

def test_self_review_valid_report():
    reviewer = SelfReview()
    report = {
        "evaluation": {"success": True},
        "critique": {"weaknesses": [], "risks": []},
        "analysis": {"mismatches": []},
        "metrics": {"accuracy": 0.9, "confidence": 0.8, "latency": 0.5, "coverage": 1.0},
        "score": {"final_score": 0.85},
        "feedback": {"suggestions": ["Improve error handling"]},
    }
    result = reviewer.process({"report": report})

    assert result["status"] == "passed"
    assert not result["issues"]
    assert any("Score valid" in c for c in result["confirmations"])
    assert any("Feedback contains actionable suggestions" in c for c in result["confirmations"])

def test_self_review_missing_section():
    reviewer = SelfReview()
    report = {
        "evaluation": {"success": True},
        # critique section missing
        "analysis": {},
        "metrics": {},
        "score": {"final_score": 0.7},
        "feedback": {"suggestions": ["Add more tests"]},
    }
    result = reviewer.process({"report": report})

    assert result["status"] == "needs_revision"
    assert any("Missing section: critique" in i for i in result["issues"])

def test_self_review_invalid_score():
    reviewer = SelfReview()
    report = {
        "evaluation": {"success": True},
        "critique": {"weaknesses": [], "risks": []},
        "analysis": {},
        "metrics": {},
        "score": {"final_score": 1.5},  # invalid
        "feedback": {"suggestions": ["Refactor code"]},
    }
    result = reviewer.process({"report": report})

    assert result["status"] == "needs_revision"
    assert any("Score out of bounds" in i for i in result["issues"])

def test_self_review_no_feedback():
    reviewer = SelfReview()
    report = {
        "evaluation": {"success": True},
        "critique": {"weaknesses": [], "risks": []},
        "analysis": {},
        "metrics": {},
        "score": {"final_score": 0.9},
        "feedback": {},  # no suggestions
    }
    result = reviewer.process({"report": report})

    assert result["status"] == "needs_revision"
    assert any("No actionable feedback provided" in i for i in result["issues"])
