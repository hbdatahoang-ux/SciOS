# tests/test_metrics.py
import pytest
from scios.cognitive_core.reflection.metrics import Metrics

def test_metrics_with_valid_data():
    metrics = Metrics()
    data = {
        "execution_result": {"success": True},
        "reasoning": {"prediction": "Expected outcome"},
        "plan": {"steps": ["step1", "step2"]},
    }
    result = metrics.process(data)

    # Kiểm tra các key tồn tại
    assert "accuracy" in result
    assert "confidence" in result
    assert "latency" in result
    assert "coverage" in result

    # Giá trị nằm trong khoảng hợp lệ
    assert 0.0 <= result["accuracy"] <= 1.0
    assert 0.0 <= result["confidence"] <= 1.0
    assert result["latency"] >= 0.0
    assert 0.0 <= result["coverage"] <= 1.0

def test_metrics_with_failure_execution():
    metrics = Metrics()
    data = {
        "execution_result": {"success": False},
        "reasoning": {"prediction": "Expected outcome"},
        "plan": {"steps": ["step1"]},
    }
    result = metrics.process(data)

    # Accuracy thấp khi thất bại
    assert result["accuracy"] < 0.5

def test_metrics_with_missing_data_defaults():
    metrics = Metrics()
    data = {}  # không có execution_result, reasoning, plan
    result = metrics.process(data)

    # Vẫn trả về đủ key với giá trị mặc định
    assert set(result.keys()) == {"accuracy", "confidence", "latency", "coverage"}
    assert 0.0 <= result["accuracy"] <= 1.0
    assert 0.0 <= result["confidence"] <= 1.0
    assert result["latency"] >= 0.0
    assert 0.0 <= result["coverage"] <= 1.0
