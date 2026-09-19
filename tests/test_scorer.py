# tests/test_scorer.py
import pytest
from scios.cognitive_core.reflection.scorer import Scorer

def test_scorer_high_quality_metrics():
    scorer = Scorer()
    metrics = {"accuracy": 0.95, "confidence": 0.9, "latency": 0.5}
    result = scorer.process(metrics)
    assert "final_score" in result
    assert 0.8 <= result["final_score"] <= 1.0

def test_scorer_low_quality_metrics():
    scorer = Scorer()
    metrics = {"accuracy": 0.2, "confidence": 0.3, "latency": 2.0}
    result = scorer.process(metrics)
    assert "final_score" in result
    assert result["final_score"] < 0.5

def test_scorer_missing_metrics_defaults():
    scorer = Scorer()
    metrics = {}  # no accuracy, confidence, latency
    result = scorer.process(metrics)
    # Should still return a final_score (defaults to 0.0 values)
    assert "final_score" in result
    assert 0.0 <= result["final_score"] <= 1.0

def test_scorer_boundary_values():
    scorer = Scorer()
    metrics = {"accuracy": 1.0, "confidence": 1.0, "latency": 0.0}
    result = scorer.process(metrics)
    assert result["final_score"] == pytest.approx(1.0, rel=1e-3)
