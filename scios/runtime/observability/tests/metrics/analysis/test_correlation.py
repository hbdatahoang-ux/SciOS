# ==============================================================================
# SciOS Runtime Observability
# Metrics Analysis - Correlation
# ==============================================================================

from __future__ import annotations

import json
import math

import pytest

from scios.runtime.observability.metrics.analysis.correlation import (
    MetricCorrelationAnalyzer,
)


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def analyzer() -> MetricCorrelationAnalyzer:
    return MetricCorrelationAnalyzer(
        name="TestCorrelationAnalyzer",
    )


@pytest.fixture
def builtin_analyzer() -> MetricCorrelationAnalyzer:
    analyzer = MetricCorrelationAnalyzer(
        name="TestCorrelationAnalyzer",
    )
    analyzer.register_builtin_algorithms()
    return analyzer


# ==============================================================================
# Constructor / Representation
# ==============================================================================


def test_constructor(analyzer: MetricCorrelationAnalyzer) -> None:
    assert analyzer.name == "TestCorrelationAnalyzer"
    assert analyzer.enabled is True
    assert analyzer.frozen is False
    assert analyzer.closed is False


def test_repr(analyzer: MetricCorrelationAnalyzer) -> None:
    text = repr(analyzer)

    assert "MetricCorrelationAnalyzer" in text
    assert "enabled=True" in text


# ==============================================================================
# Initial State
# ==============================================================================


def test_initial_algorithms(
    analyzer: MetricCorrelationAnalyzer,
) -> None:
    assert analyzer.algorithms() == {}
    assert analyzer.algorithm_names() == []


def test_initial_status(
    analyzer: MetricCorrelationAnalyzer,
) -> None:
    result = analyzer.status()

    assert result["healthy"] is True
    assert result["status"] == "healthy"
    assert result["running"] is False
    assert result["errors"] == 0


def test_initial_summary(
    analyzer: MetricCorrelationAnalyzer,
) -> None:
    result = analyzer.summary()

    assert result["name"] == "TestCorrelationAnalyzer"
    assert result["version"] == "0.2.0"
    assert result["enabled"] is True
    assert result["frozen"] is False
    assert result["closed"] is False

    assert result["correlation_count"] == 0
    assert result["analysis_count"] == 0
    assert result["error_count"] == 0


# ==============================================================================
# Built-in Algorithms
# ==============================================================================


def test_register_builtin_algorithms(
    analyzer: MetricCorrelationAnalyzer,
) -> None:
    result = analyzer.register_builtin_algorithms()

    assert result is analyzer

    names = analyzer.algorithm_names()

    assert "pearson" in names
    assert "spearman" in names
    assert "kendall" in names
    assert "covariance" in names
    assert "cosine" in names
    assert "distance" in names
    assert "mutual_information" in names


def test_builtin_algorithms_are_callable(
    builtin_analyzer: MetricCorrelationAnalyzer,
) -> None:
    algorithms = builtin_analyzer.algorithms()

    for name in (
        "pearson",
        "spearman",
        "kendall",
        "covariance",
        "cosine",
        "distance",
        "mutual_information",
    ):
        assert name in algorithms
        assert callable(algorithms[name])


# ==============================================================================
# Basic Correlation
# ==============================================================================


def test_pearson(
    builtin_analyzer: MetricCorrelationAnalyzer,
) -> None:
    result = builtin_analyzer.pearson(
        [1, 2, 3, 4],
        [1, 2, 3, 4],
    )

    assert math.isclose(result, 1.0)


def test_pearson_negative(
    builtin_analyzer: MetricCorrelationAnalyzer,
) -> None:
    result = builtin_analyzer.pearson(
        [1, 2, 3, 4],
        [4, 3, 2, 1],
    )

    assert math.isclose(result, -1.0)


def test_covariance(
    builtin_analyzer: MetricCorrelationAnalyzer,
) -> None:
    result = builtin_analyzer.covariance(
        [1, 2, 3],
        [1, 2, 3],
    )

    assert math.isfinite(result)


def test_cosine(
    builtin_analyzer: MetricCorrelationAnalyzer,
) -> None:
    result = builtin_analyzer.cosine(
        [1, 0],
        [1, 0],
    )

    assert math.isclose(result, 1.0)


def test_distance(
    builtin_analyzer: MetricCorrelationAnalyzer,
) -> None:
    result = builtin_analyzer.distance(
        [0, 0],
        [3, 4],
    )

    assert math.isclose(result, 5.0)


# ==============================================================================
# Analysis API
# ==============================================================================


def test_analyze(
    builtin_analyzer: MetricCorrelationAnalyzer,
) -> None:
    result = builtin_analyzer.analyze(
        [1, 2, 3, 4],
        [1, 2, 3, 4],
    )

    assert result is not None


def test_analyze_one(
    builtin_analyzer: MetricCorrelationAnalyzer,
) -> None:
    result = builtin_analyzer.analyze_one(
        [1, 2, 3],
        [1, 2, 3],
    )

    assert result is not None


def test_run(
    builtin_analyzer: MetricCorrelationAnalyzer,
) -> None:
    result = builtin_analyzer.run(
        [1, 2, 3],
        [1, 2, 3],
    )

    assert result is not None


# ==============================================================================
# Algorithm Registry
# ==============================================================================


def test_register_custom_algorithm(
    analyzer: MetricCorrelationAnalyzer,
) -> None:

    def custom(x, y):
        return 42.0

    result = analyzer.register_algorithm(
        "custom",
        custom,
    )

    assert result is analyzer
    assert analyzer.contains_algorithm("custom")
    assert analyzer.exists_algorithm("custom")
    assert analyzer.algorithm("custom") is custom


def test_unregister_custom_algorithm(
    analyzer: MetricCorrelationAnalyzer,
) -> None:

    def custom(x, y):
        return 42.0

    analyzer.register_algorithm("custom", custom)

    result = analyzer.unregister_algorithm("custom")

    assert result is analyzer
    assert not analyzer.contains_algorithm("custom")


# ==============================================================================
# Lifecycle
# ==============================================================================


def test_disable(
    analyzer: MetricCorrelationAnalyzer,
) -> None:
    result = analyzer.disable()

    assert result is analyzer
    assert analyzer.enabled is False


def test_enable(
    analyzer: MetricCorrelationAnalyzer,
) -> None:
    analyzer.disable()

    result = analyzer.enable()

    assert result is analyzer
    assert analyzer.enabled is True


def test_freeze(
    analyzer: MetricCorrelationAnalyzer,
) -> None:
    result = analyzer.freeze()

    assert result is analyzer
    assert analyzer.frozen is True


def test_unfreeze(
    analyzer: MetricCorrelationAnalyzer,
) -> None:
    analyzer.freeze()

    result = analyzer.unfreeze()

    assert result is analyzer
    assert analyzer.frozen is False


def test_close(
    analyzer: MetricCorrelationAnalyzer,
) -> None:
    result = analyzer.close()

    assert result is analyzer
    assert analyzer.closed is True


def test_reopen(
    analyzer: MetricCorrelationAnalyzer,
) -> None:
    analyzer.close()

    result = analyzer.reopen()

    assert result is analyzer
    assert analyzer.closed is False


# ==============================================================================
# Copy Protocol
# ==============================================================================


def test_clone(
    builtin_analyzer: MetricCorrelationAnalyzer,
) -> None:
    clone = builtin_analyzer.clone()

    assert clone is not builtin_analyzer
    assert clone.name == builtin_analyzer.name
    assert clone.algorithm_names() == builtin_analyzer.algorithm_names()


def test_copy(
    builtin_analyzer: MetricCorrelationAnalyzer,
) -> None:
    copied = builtin_analyzer.copy()

    assert copied is not builtin_analyzer
    assert copied.algorithm_names() == builtin_analyzer.algorithm_names()


# ==============================================================================
# Serialization
# ==============================================================================


def test_serialize(
    analyzer: MetricCorrelationAnalyzer,
) -> None:
    result = analyzer.serialize()

    assert isinstance(result, dict)
    assert result["name"] == "TestCorrelationAnalyzer"
    assert result["version"] == "0.2.0"


def test_to_dict(
    analyzer: MetricCorrelationAnalyzer,
) -> None:
    result = analyzer.to_dict()

    assert isinstance(result, dict)
    assert result["name"] == "TestCorrelationAnalyzer"


def test_json_roundtrip(
    analyzer: MetricCorrelationAnalyzer,
) -> None:
    text = analyzer.to_json()

    assert isinstance(text, str)

    data = json.loads(text)

    assert data["name"] == "TestCorrelationAnalyzer"


# ==============================================================================
# Health / Report
# ==============================================================================


def test_health(
    analyzer: MetricCorrelationAnalyzer,
) -> None:
    result = analyzer.health()

    assert result["healthy"] is True
    assert result["status"] == "healthy"


def test_report(
    analyzer: MetricCorrelationAnalyzer,
) -> None:
    result = analyzer.report()

    assert "summary" in result
    assert "configuration" in result
    assert "algorithms" in result