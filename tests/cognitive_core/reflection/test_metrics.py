from pytest import approx

from scios.cognitive_core.reflection.metrics import Metrics


def test_metrics_initialization():
    metrics = Metrics()

    assert metrics.name == "Metrics"


def test_metrics_compute_successful_execution():
    metrics = Metrics()

    result = metrics.compute(
        {
            "success": True,
            "metrics": {
                "quality": 0.8,
                "latency": 0.25,
            },
        },
        {
            "insights": ["matched reasoning"],
            "mismatches": [],
        },
    )

    assert result["accuracy"] == 1.0
    assert result["confidence"] == approx(0.8)
    assert result["latency"] == approx(0.25)
    assert result["coverage"] == 1


def test_metrics_compute_failed_execution():
    metrics = Metrics()

    result = metrics.compute(
        {
            "success": False,
            "metrics": {
                "quality": 0.2,
                "latency": 1.5,
            },
        },
        {
            "insights": [],
            "mismatches": ["execution failed"],
        },
    )

    assert result["accuracy"] == 0.0
    assert result["confidence"] == approx(0.2)
    assert result["latency"] == approx(1.5)
    assert result["coverage"] == 1


def test_metrics_missing_data_defaults():
    metrics = Metrics()

    result = metrics.compute({}, {})

    assert result == {
        "accuracy": 0.0,
        "confidence": 0.0,
        "latency": 1.0,
        "coverage": 0,
    }


def test_metrics_process():
    metrics = Metrics()

    result = metrics.process(
        {
            "execution_result": {
                "success": True,
                "metrics": {
                    "quality": 0.9,
                    "latency": 0.1,
                },
            },
            "analysis": {
                "insights": ["a", "b"],
                "mismatches": ["c"],
            },
        }
    )

    assert result["accuracy"] == 1.0
    assert result["confidence"] == approx(0.9)
    assert result["coverage"] == 3
