"""
SciOS-NG Runtime Metrics Analysis

Tests for MetricTrendAnalyzer.

Contract coverage:
- construction
- identity
- runtime state
- configuration
- statistics
- trend algorithms
- registry
- lifecycle
- analysis
- batch analysis
- snapshot / restore
- clone / copy
- diagnostics
- hooks / events
- serialization
- Python protocols
"""

from __future__ import annotations

import json
import time

import pytest

from scios.runtime.observability.metrics.analysis import MetricTrendAnalyzer


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def analyzer() -> MetricTrendAnalyzer:
    return MetricTrendAnalyzer()


@pytest.fixture
def builtin_analyzer() -> MetricTrendAnalyzer:
    analyzer = MetricTrendAnalyzer(
        name="TestTrendAnalyzer",
        description="Trend analyzer test instance",
    )
    analyzer.register_builtin_algorithms()
    return analyzer


# ==============================================================================
# Part 1. Construction
# ==============================================================================


def test_default_construction() -> None:
    analyzer = MetricTrendAnalyzer()

    assert isinstance(analyzer, MetricTrendAnalyzer)
    assert analyzer.name == "MetricTrendAnalyzer"
    assert analyzer.description == ""
    assert analyzer.version == "0.2.0"


def test_custom_construction() -> None:
    analyzer = MetricTrendAnalyzer(
        name="Custom",
        description="Description",
    )

    assert analyzer.name == "Custom"
    assert analyzer.description == "Description"


def test_identity_is_unique() -> None:
    first = MetricTrendAnalyzer()
    second = MetricTrendAnalyzer()

    assert first.id != second.id
    assert isinstance(first.id, str)
    assert first.id


def test_metadata_timestamps_exist(
    analyzer: MetricTrendAnalyzer,
) -> None:
    assert analyzer.created_at is not None
    assert analyzer.updated_at is not None
    assert analyzer.updated_at >= analyzer.created_at


# ==============================================================================
# Part 2. Initial Runtime State
# ==============================================================================


def test_initial_runtime_state(
    analyzer: MetricTrendAnalyzer,
) -> None:
    assert analyzer.enabled is True
    assert analyzer.disabled is False
    assert analyzer.frozen is False
    assert analyzer.closed is False
    assert analyzer.running is False
    assert analyzer.active is True


def test_initial_statistics(
    analyzer: MetricTrendAnalyzer,
) -> None:
    assert analyzer.trend_count == 0
    assert analyzer.analysis_count == 0
    assert analyzer.error_count == 0
    assert analyzer.statistics is not None


def test_initial_configuration(
    analyzer: MetricTrendAnalyzer,
) -> None:
    assert analyzer.config == {
        "window": 5,
        "alpha": 0.30,
        "beta": 0.20,
        "season_length": 12,
        "min_samples": 3,
    }


def test_config_returns_copy(
    analyzer: MetricTrendAnalyzer,
) -> None:
    config = analyzer.config

    config["window"] = 999

    assert analyzer.config["window"] == 5


# ==============================================================================
# Part 3. Configuration
# ==============================================================================


def test_configure(
    analyzer: MetricTrendAnalyzer,
) -> None:
    result = analyzer.configure(
        window=7,
        alpha=0.5,
    )

    assert result is analyzer
    assert analyzer.config["window"] == 7
    assert analyzer.config["alpha"] == 0.5


def test_configure_preserves_existing_configuration(
    analyzer: MetricTrendAnalyzer,
) -> None:
    analyzer.configure(window=10)

    assert analyzer.config["window"] == 10
    assert analyzer.config["alpha"] == 0.30
    assert analyzer.config["beta"] == 0.20
    assert analyzer.config["season_length"] == 12
    assert analyzer.config["min_samples"] == 3


# ==============================================================================
# Part 4. Built-in Algorithms
# ==============================================================================


def test_initial_algorithm_registry_is_empty(
    analyzer: MetricTrendAnalyzer,
) -> None:
    assert analyzer.algorithms() == {}
    assert analyzer.algorithm_names() == []
    assert analyzer.algorithm_count == 0


def test_register_builtin_algorithms(
    analyzer: MetricTrendAnalyzer,
) -> None:
    result = analyzer.register_builtin_algorithms()

    assert result is analyzer
    assert analyzer.algorithm_count == 9


def test_builtin_algorithm_names(
    builtin_analyzer: MetricTrendAnalyzer,
) -> None:
    expected = {
        "linear",
        "slope",
        "momentum",
        "moving_average",
        "ema",
        "rolling",
        "seasonal",
        "cumulative",
        "custom",
    }

    assert set(builtin_analyzer.algorithm_names()) == expected


@pytest.mark.parametrize(
    "name",
    [
        "linear",
        "slope",
        "momentum",
        "moving_average",
        "ema",
        "rolling",
        "seasonal",
        "cumulative",
        "custom",
    ],
)
def test_builtin_algorithm_exists(
    builtin_analyzer: MetricTrendAnalyzer,
    name: str,
) -> None:
    assert builtin_analyzer.exists_algorithm(name)
    assert builtin_analyzer.contains_algorithm(name)
    assert builtin_analyzer.algorithm(name) is not None


def test_algorithm_returns_default(
    analyzer: MetricTrendAnalyzer,
) -> None:
    sentinel = object()

    assert analyzer.algorithm(
        "missing",
        default=sentinel,
    ) is sentinel


def test_algorithms_returns_copy(
    builtin_analyzer: MetricTrendAnalyzer,
) -> None:
    algorithms = builtin_analyzer.algorithms()

    algorithms.clear()

    assert builtin_analyzer.algorithm_count == 9


# ==============================================================================
# Part 5. Algorithm Registration
# ==============================================================================


def test_register_custom_algorithm(
    analyzer: MetricTrendAnalyzer,
) -> None:
    def custom(values):
        return list(values)

    result = analyzer.register_algorithm(
        "custom_test",
        custom,
    )

    assert result is analyzer
    assert analyzer.exists_algorithm("custom_test")

    entry = analyzer.algorithm("custom_test")

    assert entry["name"] == "custom_test"
    assert entry["callable"] is custom
    assert entry["enabled"] is True
    assert entry["metadata"] == {}


def test_register_custom_algorithm_with_metadata(
    analyzer: MetricTrendAnalyzer,
) -> None:
    def custom(values):
        return list(values)

    analyzer.register_algorithm(
        "custom_test",
        custom,
        metadata={
            "description": "test",
            "version": "1.0",
        },
    )

    entry = analyzer.algorithm("custom_test")

    assert entry["metadata"] == {
        "description": "test",
        "version": "1.0",
    }


def test_register_disabled_algorithm(
    analyzer: MetricTrendAnalyzer,
) -> None:
    def custom(values):
        return list(values)

    analyzer.register_algorithm(
        "custom_test",
        custom,
        enabled=False,
    )

    assert analyzer.algorithm("custom_test")["enabled"] is False


def test_register_algorithm_requires_callable(
    analyzer: MetricTrendAnalyzer,
) -> None:
    with pytest.raises(TypeError):
        analyzer.register_algorithm(
            "invalid",
            "not_callable",
        )


def test_remove_algorithm(
    analyzer: MetricTrendAnalyzer,
) -> None:
    analyzer.register_algorithm(
        "test",
        lambda values: values,
    )

    result = analyzer.remove_algorithm("test")

    assert result is analyzer
    assert not analyzer.exists_algorithm("test")


def test_remove_missing_algorithm_is_noop(
    analyzer: MetricTrendAnalyzer,
) -> None:
    result = analyzer.remove_algorithm("missing")

    assert result is analyzer
    assert analyzer.algorithm_count == 0


def test_unregister_is_alias(
    analyzer: MetricTrendAnalyzer,
) -> None:
    analyzer.register_algorithm(
        "test",
        lambda values: values,
    )

    result = analyzer.unregister_algorithm("test")

    assert result is analyzer
    assert not analyzer.exists_algorithm("test")


def test_clear_algorithms(
    builtin_analyzer: MetricTrendAnalyzer,
) -> None:
    result = builtin_analyzer.clear_algorithms()

    assert result is builtin_analyzer
    assert builtin_analyzer.algorithm_names() == []
    assert builtin_analyzer.algorithm_count == 0


# ==============================================================================
# Part 6. Enable / Disable Algorithms
# ==============================================================================


def test_enable_algorithm(
    analyzer: MetricTrendAnalyzer,
) -> None:
    analyzer.register_algorithm(
        "test",
        lambda values: values,
        enabled=False,
    )

    result = analyzer.enable_algorithm("test")

    assert result is analyzer
    assert analyzer.algorithm("test")["enabled"] is True


def test_disable_algorithm(
    analyzer: MetricTrendAnalyzer,
) -> None:
    analyzer.register_algorithm(
        "test",
        lambda values: values,
    )

    result = analyzer.disable_algorithm("test")

    assert result is analyzer
    assert analyzer.algorithm("test")["enabled"] is False


def test_enable_missing_algorithm_is_noop(
    analyzer: MetricTrendAnalyzer,
) -> None:
    result = analyzer.enable_algorithm("missing")

    assert result is analyzer


def test_disable_missing_algorithm_is_noop(
    analyzer: MetricTrendAnalyzer,
) -> None:
    result = analyzer.disable_algorithm("missing")

    assert result is analyzer


# ==============================================================================
# Part 7. Linear Trend
# ==============================================================================


def test_linear_upward(
    analyzer: MetricTrendAnalyzer,
) -> None:
    result = analyzer.linear([1, 2, 3, 4, 5])

    assert result == {
        "algorithm": "linear",
        "trend": "upward",
        "slope": 1.0,
        "intercept": 1.0,
    }


def test_linear_downward(
    analyzer: MetricTrendAnalyzer,
) -> None:
    result = analyzer.linear([5, 4, 3, 2, 1])

    assert result["algorithm"] == "linear"
    assert result["trend"] == "downward"
    assert result["slope"] == -1.0
    assert result["intercept"] == 5.0


def test_linear_stable(
    analyzer: MetricTrendAnalyzer,
) -> None:
    result = analyzer.linear([3, 3, 3, 3])

    assert result["algorithm"] == "linear"
    assert result["trend"] == "stable"
    assert result["slope"] == 0.0
    assert result["intercept"] == 3.0


def test_linear_empty(
    analyzer: MetricTrendAnalyzer,
) -> None:
    result = analyzer.linear([])

    assert result == {
        "algorithm": "linear",
        "trend": "stable",
        "slope": 0.0,
        "intercept": 0.0,
    }


def test_linear_single_value(
    analyzer: MetricTrendAnalyzer,
) -> None:
    result = analyzer.linear([7])

    assert result == {
        "algorithm": "linear",
        "trend": "stable",
        "slope": 0.0,
        "intercept": 7,
    }


# ==============================================================================
# Part 8. Endpoint Slope
# ==============================================================================


def test_slope_upward(
    analyzer: MetricTrendAnalyzer,
) -> None:
    result = analyzer.slope([1, 3, 5])

    assert result["algorithm"] == "slope"
    assert result["trend"] == "upward"
    assert result["slope"] == 2.0


def test_slope_downward(
    analyzer: MetricTrendAnalyzer,
) -> None:
    result = analyzer.slope([5, 3, 1])

    assert result["trend"] == "downward"
    assert result["slope"] == -2.0


def test_slope_stable(
    analyzer: MetricTrendAnalyzer,
) -> None:
    result = analyzer.slope([4, 4, 4])

    assert result["trend"] == "stable"
    assert result["slope"] == 0.0


def test_slope_single_value(
    analyzer: MetricTrendAnalyzer,
) -> None:
    result = analyzer.slope([10])

    assert result["trend"] == "stable"
    assert result["slope"] == 0.0


def test_slope_empty(
    analyzer: MetricTrendAnalyzer,
) -> None:
    result = analyzer.slope([])

    assert result["trend"] == "stable"
    assert result["slope"] == 0.0


# ==============================================================================
# Part 9. Momentum
# ==============================================================================


def test_momentum_upward(
    analyzer: MetricTrendAnalyzer,
) -> None:
    result = analyzer.momentum([1, 2, 5])

    assert result == {
        "algorithm": "momentum",
        "trend": "upward",
        "momentum": 3,
    }


def test_momentum_downward(
    analyzer: MetricTrendAnalyzer,
) -> None:
    result = analyzer.momentum([5, 3, 1])

    assert result["trend"] == "downward"
    assert result["momentum"] == -2


def test_momentum_stable(
    analyzer: MetricTrendAnalyzer,
) -> None:
    result = analyzer.momentum([5, 5])

    assert result["trend"] == "stable"
    assert result["momentum"] == 0


def test_momentum_single_value(
    analyzer: MetricTrendAnalyzer,
) -> None:
    result = analyzer.momentum([5])

    assert result["trend"] == "stable"
    assert result["momentum"] == 0.0


# ==============================================================================
# Part 10. Moving Average
# ==============================================================================


def test_moving_average_explicit_window(
    analyzer: MetricTrendAnalyzer,
) -> None:
    result = analyzer.moving_average(
        [1, 2, 3, 4, 5],
        window=3,
    )

    assert result == {
        "algorithm": "moving_average",
        "trend": "upward",
        "average": 4.0,
        "window": 3,
    }


def test_moving_average_default_window(
    analyzer: MetricTrendAnalyzer,
) -> None:
    result = analyzer.moving_average(
        [1, 2, 3, 4, 5, 6],
    )

    assert result["window"] == 5
    assert result["average"] == 4.0


def test_moving_average_window_larger_than_data(
    analyzer: MetricTrendAnalyzer,
) -> None:
    result = analyzer.moving_average(
        [1, 2, 3],
        window=100,
    )

    assert result["window"] == 3
    assert result["average"] == 2.0


def test_moving_average_empty(
    analyzer: MetricTrendAnalyzer,
) -> None:
    result = analyzer.moving_average(
        [],
        window=3,
    )

    assert result == {
        "algorithm": "moving_average",
        "trend": "stable",
        "average": 0.0,
    }


def test_moving_average_window_one(
    analyzer: MetricTrendAnalyzer,
) -> None:
    result = analyzer.moving_average(
        [1, 2, 3],
        window=1,
    )

    assert result["average"] == 3.0
    assert result["window"] == 1
    assert result["trend"] == "stable"


# ==============================================================================
# Part 11. EMA
# ==============================================================================


def test_ema_explicit_alpha(
    analyzer: MetricTrendAnalyzer,
) -> None:
    result = analyzer.ema(
        [1, 2, 3],
        alpha=0.5,
    )

    assert result["algorithm"] == "ema"
    assert result["alpha"] == 0.5
    assert result["ema"] == 2.25


def test_ema_default_alpha(
    analyzer: MetricTrendAnalyzer,
) -> None:
    result = analyzer.ema([1, 2, 3])

    assert result["alpha"] == 0.30


def test_ema_alpha_one(
    analyzer: MetricTrendAnalyzer,
) -> None:
    result = analyzer.ema(
        [1, 2, 3, 4],
        alpha=1.0,
    )

    assert result["ema"] == 4.0


def test_ema_empty(
    analyzer: MetricTrendAnalyzer,
) -> None:
    result = analyzer.ema([])

    assert result == {
        "algorithm": "ema",
        "trend": "stable",
        "ema": 0.0,
    }


# ==============================================================================
# Part 12. Rolling
# ==============================================================================


def test_rolling_with_window(
    analyzer: MetricTrendAnalyzer,
) -> None:
    result = analyzer.rolling(
        [1, 2, 3, 4, 5],
        window=3,
    )

    assert result["algorithm"] == "rolling"
    assert result["rolling"] == [
        2.0,
        3.0,
        4.0,
    ]
    assert result["trend"] == "upward"


def test_rolling_short_dataset_uses_moving_average(
    analyzer: MetricTrendAnalyzer,
) -> None:
    result = analyzer.rolling(
        [1, 2, 3],
        window=5,
    )

    assert result["algorithm"] == "moving_average"
    assert result["average"] == 2.0
    assert result["window"] == 3


def test_rolling_default_window(
    analyzer: MetricTrendAnalyzer,
) -> None:
    result = analyzer.rolling(
        [1, 2, 3, 4, 5, 6],
    )

    assert result["algorithm"] == "rolling"
    assert result["rolling"] == [
        3.0,
        4.0,
    ]


# ==============================================================================
# Part 13. Seasonal
# ==============================================================================


def test_seasonal_explicit_length(
    analyzer: MetricTrendAnalyzer,
) -> None:
    result = analyzer.seasonal(
        [1, 2, 3, 4, 5, 6],
        season_length=3,
    )

    assert result["algorithm"] == "seasonal"
    assert result["season_length"] == 3
    assert result["trend"] == "upward"
    assert result["slope"] == 1.0


def test_seasonal_short_dataset_falls_back_to_linear(
    analyzer: MetricTrendAnalyzer,
) -> None:
    result = analyzer.seasonal(
        [1, 2, 3],
        season_length=5,
    )

    assert result["algorithm"] == "linear"
    assert "season_length" not in result


def test_seasonal_default_length(
    analyzer: MetricTrendAnalyzer,
) -> None:
    result = analyzer.seasonal(
        list(range(15)),
    )

    assert result["algorithm"] == "seasonal"
    assert result["season_length"] == 12


# ==============================================================================
# Part 14. Cumulative
# ==============================================================================


def test_cumulative(
    analyzer: MetricTrendAnalyzer,
) -> None:
    result = analyzer.cumulative(
        [1, 2, 3, 4],
    )

    assert result["algorithm"] == "cumulative"
    assert result["cumulative"] == [
        1.0,
        3.0,
        6.0,
        10.0,
    ]
    assert result["trend"] == "upward"


def test_cumulative_empty(
    analyzer: MetricTrendAnalyzer,
) -> None:
    result = analyzer.cumulative([])

    assert result["algorithm"] == "cumulative"
    assert result["cumulative"] == []
    assert result["trend"] == "stable"


# ==============================================================================
# Part 15. Custom Analyzer
# ==============================================================================


def test_custom_analyzer(
    analyzer: MetricTrendAnalyzer,
) -> None:
    def custom(values, multiplier=1):
        return [
            value * multiplier
            for value in values
        ]

    result = analyzer.custom(
        [1, 2, 3],
        custom,
        multiplier=2,
    )

    assert result == [2, 4, 6]


def test_custom_analyzer_requires_callable(
    analyzer: MetricTrendAnalyzer,
) -> None:
    with pytest.raises(TypeError):
        analyzer.custom(
            [1, 2, 3],
            "invalid",
        )


# ==============================================================================
# Part 16. Analysis API
# ==============================================================================


def test_analyze_requires_registered_algorithm(
    analyzer: MetricTrendAnalyzer,
) -> None:
    with pytest.raises(KeyError):
        analyzer.analyze(
            [1, 2, 3],
            method="linear",
        )


def test_analyze(
    builtin_analyzer: MetricTrendAnalyzer,
) -> None:
    result = builtin_analyzer.analyze(
        [1, 2, 3, 4, 5],
        method="linear",
    )

    assert result["algorithm"] == "linear"
    assert result["trend"] == "upward"
    assert builtin_analyzer.analysis_count == 1
    assert builtin_analyzer.trend_count == 1
    assert builtin_analyzer.error_count == 0


def test_analyze_records_history(
    builtin_analyzer: MetricTrendAnalyzer,
) -> None:
    result = builtin_analyzer.analyze(
        [1, 2, 3],
        method="linear",
    )

    assert builtin_analyzer._history == [result]
    assert builtin_analyzer._last_result == result


def test_analyze_updates_latency(
    builtin_analyzer: MetricTrendAnalyzer,
) -> None:
    builtin_analyzer.analyze(
        [1, 2, 3],
        method="linear",
    )

    assert builtin_analyzer.latency >= 0.0


def test_analyze_resets_running_state(
    builtin_analyzer: MetricTrendAnalyzer,
) -> None:
    builtin_analyzer.analyze(
        [1, 2, 3],
        method="linear",
    )

    assert builtin_analyzer.running is False


def test_analyze_one(
    builtin_analyzer: MetricTrendAnalyzer,
) -> None:
    result = builtin_analyzer.analyze_one(
        [1, 2, 3],
        method="linear",
    )

    assert result["algorithm"] == "linear"


def test_run_alias(
    builtin_analyzer: MetricTrendAnalyzer,
) -> None:
    result = builtin_analyzer.run(
        [1, 2, 3],
        method="linear",
    )

    assert result["algorithm"] == "linear"


def test_execute_alias(
    builtin_analyzer: MetricTrendAnalyzer,
) -> None:
    result = builtin_analyzer.execute(
        [1, 2, 3],
        method="linear",
    )

    assert result["algorithm"] == "linear"


def test_process_alias(
    builtin_analyzer: MetricTrendAnalyzer,
) -> None:
    result = builtin_analyzer.process(
        [1, 2, 3],
        method="linear",
    )

    assert result["algorithm"] == "linear"


# ==============================================================================
# Part 17. Batch Analysis
# ==============================================================================


def test_analyze_many(
    builtin_analyzer: MetricTrendAnalyzer,
) -> None:
    datasets = [
        [1, 2, 3],
        [3, 2, 1],
        [4, 4, 4],
    ]

    results = builtin_analyzer.analyze_many(
        datasets,
        method="linear",
    )

    assert len(results) == 3
    assert results[0]["trend"] == "upward"
    assert results[1]["trend"] == "downward"
    assert results[2]["trend"] == "stable"
    assert builtin_analyzer.analysis_count == 3


def test_analyze_batch(
    builtin_analyzer: MetricTrendAnalyzer,
) -> None:
    batches = [
        [1, 2, 3],
        [3, 4, 5],
    ]

    results = builtin_analyzer.analyze_batch(
        batches,
        method="linear",
    )

    assert len(results) == 2
    assert builtin_analyzer.analysis_count == 2


# ==============================================================================
# Part 18. Unknown / Disabled Algorithms
# ==============================================================================


def test_execute_unknown_algorithm(
    builtin_analyzer: MetricTrendAnalyzer,
) -> None:
    with pytest.raises(KeyError):
        builtin_analyzer.execute_algorithm(
            "missing",
            [1, 2, 3],
        )


def test_execute_disabled_algorithm(
    builtin_analyzer: MetricTrendAnalyzer,
) -> None:
    builtin_analyzer.disable_algorithm("linear")

    with pytest.raises(RuntimeError):
        builtin_analyzer.execute_algorithm(
            "linear",
            [1, 2, 3],
        )


def test_analyze_disabled_algorithm(
    builtin_analyzer: MetricTrendAnalyzer,
) -> None:
    builtin_analyzer.disable_algorithm("linear")

    with pytest.raises(RuntimeError):
        builtin_analyzer.analyze(
            [1, 2, 3],
            method="linear",
        )


# ==============================================================================
# Part 19. Analyzer Lifecycle
# ==============================================================================


def test_disable(
    analyzer: MetricTrendAnalyzer,
) -> None:
    result = analyzer.disable()

    assert result is analyzer
    assert analyzer.enabled is False
    assert analyzer.disabled is True
    assert analyzer.running is False
    assert analyzer.active is False


def test_enable(
    analyzer: MetricTrendAnalyzer,
) -> None:
    analyzer.disable()

    result = analyzer.enable()

    assert result is analyzer
    assert analyzer.enabled is True
    assert analyzer.disabled is False
    assert analyzer.active is True


def test_freeze(
    analyzer: MetricTrendAnalyzer,
) -> None:
    result = analyzer.freeze()

    assert result is analyzer
    assert analyzer.frozen is True
    assert analyzer.active is False


def test_unfreeze(
    analyzer: MetricTrendAnalyzer,
) -> None:
    analyzer.freeze()

    result = analyzer.unfreeze()

    assert result is analyzer
    assert analyzer.frozen is False
    assert analyzer.active is True


def test_close(
    analyzer: MetricTrendAnalyzer,
) -> None:
    result = analyzer.close()

    assert result is analyzer
    assert analyzer.closed is True
    assert analyzer.running is False
    assert analyzer.active is False


def test_reopen(
    analyzer: MetricTrendAnalyzer,
) -> None:
    analyzer.close()

    result = analyzer.reopen()

    assert result is analyzer
    assert analyzer.closed is False
    assert analyzer.active is True


def test_analyze_when_disabled(
    builtin_analyzer: MetricTrendAnalyzer,
) -> None:
    builtin_analyzer.disable()

    with pytest.raises(RuntimeError):
        builtin_analyzer.analyze(
            [1, 2, 3],
            method="linear",
        )


def test_analyze_when_frozen(
    builtin_analyzer: MetricTrendAnalyzer,
) -> None:
    builtin_analyzer.freeze()

    with pytest.raises(RuntimeError):
        builtin_analyzer.analyze(
            [1, 2, 3],
            method="linear",
        )


def test_analyze_when_closed(
    builtin_analyzer: MetricTrendAnalyzer,
) -> None:
    builtin_analyzer.close()

    with pytest.raises(RuntimeError):
        builtin_analyzer.analyze(
            [1, 2, 3],
            method="linear",
        )


# ==============================================================================
# Part 20. Reset / Clear
# ==============================================================================


def test_clear(
    builtin_analyzer: MetricTrendAnalyzer,
) -> None:
    builtin_analyzer.analyze(
        [1, 2, 3],
        method="linear",
    )

    assert builtin_analyzer._history

    result = builtin_analyzer.clear()

    assert result is builtin_analyzer
    assert builtin_analyzer._history == []
    assert builtin_analyzer._last_result is None


def test_clear_preserves_counters(
    builtin_analyzer: MetricTrendAnalyzer,
) -> None:
    builtin_analyzer.analyze(
        [1, 2, 3],
        method="linear",
    )

    builtin_analyzer.clear()

    assert builtin_analyzer.analysis_count == 1


def test_reset(
    builtin_analyzer: MetricTrendAnalyzer,
) -> None:
    builtin_analyzer.configure(
        window=10,
    )

    builtin_analyzer.analyze(
        [1, 2, 3],
        method="linear",
    )

    result = builtin_analyzer.reset()

    assert result is builtin_analyzer
    assert builtin_analyzer.trend_count == 0
    assert builtin_analyzer.analysis_count == 0
    assert builtin_analyzer.error_count == 0
    assert builtin_analyzer.latency == 0.0
    assert builtin_analyzer.running is False
    assert builtin_analyzer._last_result is None
    assert builtin_analyzer._history == []


def test_reset_preserves_configuration(
    builtin_analyzer: MetricTrendAnalyzer,
) -> None:
    builtin_analyzer.configure(
        window=10,
        alpha=0.5,
    )

    builtin_analyzer.reset()

    assert builtin_analyzer.config["window"] == 10
    assert builtin_analyzer.config["alpha"] == 0.5


def test_reset_preserves_algorithms(
    builtin_analyzer: MetricTrendAnalyzer,
) -> None:
    names = builtin_analyzer.algorithm_names()

    builtin_analyzer.reset()

    assert builtin_analyzer.algorithm_names() == names


# ==============================================================================
# Part 21. Snapshot / Restore
# ==============================================================================


def test_snapshot(
    builtin_analyzer: MetricTrendAnalyzer,
) -> None:
    builtin_analyzer.configure(window=10)

    builtin_analyzer.analyze(
        [1, 2, 3],
        method="linear",
    )

    snapshot = builtin_analyzer.snapshot()

    assert isinstance(snapshot, dict)

    assert set(snapshot) == {
        "config",
        "history",
        "last_result",
        "trend_count",
        "analysis_count",
        "error_count",
        "latency",
        "enabled",
        "frozen",
        "closed",
        "updated_at",
    }


def test_snapshot_contains_runtime_state(
    builtin_analyzer: MetricTrendAnalyzer,
) -> None:
    snapshot = builtin_analyzer.snapshot()

    assert snapshot["config"] == builtin_analyzer.config
    assert snapshot["history"] == []
    assert snapshot["last_result"] is None
    assert snapshot["trend_count"] == 0
    assert snapshot["analysis_count"] == 0
    assert snapshot["error_count"] == 0
    assert snapshot["latency"] == 0.0
    assert snapshot["enabled"] is True
    assert snapshot["frozen"] is False
    assert snapshot["closed"] is False


def test_restore(
    builtin_analyzer: MetricTrendAnalyzer,
) -> None:
    builtin_analyzer.configure(window=10)

    builtin_analyzer.analyze(
        [1, 2, 3],
        method="linear",
    )

    snapshot = builtin_analyzer.snapshot()

    restored = MetricTrendAnalyzer(
        name="Restored",
    )

    result = restored.restore(snapshot)

    assert result is restored
    assert restored.config == snapshot["config"]
    assert restored._history == snapshot["history"]
    assert restored._last_result == snapshot["last_result"]
    assert restored.trend_count == snapshot["trend_count"]
    assert restored.analysis_count == snapshot["analysis_count"]
    assert restored.error_count == snapshot["error_count"]
    assert restored.latency == snapshot["latency"]
    assert restored.enabled == snapshot["enabled"]
    assert restored.frozen == snapshot["frozen"]
    assert restored.closed == snapshot["closed"]


def test_restore_none_is_noop(
    analyzer: MetricTrendAnalyzer,
) -> None:
    result = analyzer.restore()

    assert result is analyzer


# ==============================================================================
# Part 22. Clone / Copy
# ==============================================================================


def test_clone(
    builtin_analyzer: MetricTrendAnalyzer,
) -> None:
    builtin_analyzer.configure(
        window=10,
    )

    builtin_analyzer.analyze(
        [1, 2, 3],
        method="linear",
    )

    clone = builtin_analyzer.clone()

    assert isinstance(clone, MetricTrendAnalyzer)
    assert clone is not builtin_analyzer
    assert clone.id == builtin_analyzer.id
    assert clone.name == builtin_analyzer.name
    assert clone.description == builtin_analyzer.description
    assert clone.config == builtin_analyzer.config
    assert clone._history == builtin_analyzer._history
    assert clone.analysis_count == builtin_analyzer.analysis_count


def test_copy(
    builtin_analyzer: MetricTrendAnalyzer,
) -> None:
    copied = builtin_analyzer.copy()

    assert isinstance(copied, MetricTrendAnalyzer)
    assert copied is not builtin_analyzer
    assert copied.id == builtin_analyzer.id


def test_shallow_copy_protocol(
    builtin_analyzer: MetricTrendAnalyzer,
) -> None:
    copied = builtin_analyzer.__copy__()

    assert isinstance(copied, MetricTrendAnalyzer)
    assert copied is not builtin_analyzer


def test_deepcopy_protocol(
    builtin_analyzer: MetricTrendAnalyzer,
) -> None:
    copied = builtin_analyzer.__deepcopy__({})

    assert isinstance(copied, MetricTrendAnalyzer)
    assert copied is not builtin_analyzer


# ==============================================================================
# Part 23. Summary / Report / Health / Status
# ==============================================================================


def test_summary(
    builtin_analyzer: MetricTrendAnalyzer,
) -> None:
    summary = builtin_analyzer.summary()

    assert summary["id"] == builtin_analyzer.id
    assert summary["name"] == builtin_analyzer.name
    assert summary["version"] == builtin_analyzer.version
    assert summary["enabled"] is True
    assert summary["frozen"] is False
    assert summary["closed"] is False
    assert summary["running"] is False
    assert summary["algorithm_count"] == 9
    assert summary["history_size"] == 0
    assert summary["trend_count"] == 0
    assert summary["analysis_count"] == 0
    assert summary["error_count"] == 0
    assert summary["latency"] == 0.0
    assert summary["uptime"] >= 0.0


def test_report(
    builtin_analyzer: MetricTrendAnalyzer,
) -> None:
    report = builtin_analyzer.report()

    assert set(report) == {
        "summary",
        "algorithms",
        "configuration",
        "statistics",
        "last_result",
    }

    assert report["algorithms"] == builtin_analyzer.algorithm_names()
    assert report["configuration"] == builtin_analyzer.config


def test_report_statistics(
    builtin_analyzer: MetricTrendAnalyzer,
) -> None:
    statistics = builtin_analyzer.report()["statistics"]

    assert statistics == {
        "trend_count": 0,
        "analysis_count": 0,
        "error_count": 0,
        "history_size": 0,
    }


def test_health_initial(
    analyzer: MetricTrendAnalyzer,
) -> None:
    health = analyzer.health()

    assert health["healthy"] is True
    assert health["state"] == "idle"
    assert health["errors"] == 0
    assert health["latency"] == 0.0
    assert health["uptime"] >= 0.0


def test_health_disabled(
    analyzer: MetricTrendAnalyzer,
) -> None:
    analyzer.disable()

    health = analyzer.health()

    assert health["healthy"] is False
    assert health["state"] == "disabled"


def test_health_frozen(
    analyzer: MetricTrendAnalyzer,
) -> None:
    analyzer.freeze()

    health = analyzer.health()

    assert health["healthy"] is False
    assert health["state"] == "frozen"


def test_health_closed(
    analyzer: MetricTrendAnalyzer,
) -> None:
    analyzer.close()

    health = analyzer.health()

    assert health["healthy"] is False
    assert health["state"] == "closed"


def test_status_initial(
    analyzer: MetricTrendAnalyzer,
) -> None:
    status = analyzer.status()

    assert status == {
        "enabled": True,
        "disabled": False,
        "frozen": False,
        "closed": False,
        "running": False,
        "active": True,
    }


# ==============================================================================
# Part 24. Uptime
# ==============================================================================


def test_uptime_is_non_negative(
    analyzer: MetricTrendAnalyzer,
) -> None:
    assert analyzer.uptime >= 0.0


def test_uptime_increases(
    analyzer: MetricTrendAnalyzer,
) -> None:
    first = analyzer.uptime

    time.sleep(0.001)

    second = analyzer.uptime

    assert second >= first


# ==============================================================================
# Part 25. Hooks / Events
# ==============================================================================


def test_add_hook(
    analyzer: MetricTrendAnalyzer,
) -> None:
    calls = []

    def callback(instance, **payload):
        calls.append((instance, payload))

    result = analyzer.add_hook(
        "custom",
        callback,
    )

    assert result is analyzer

    analyzer.emit(
        "custom",
        value=42,
    )

    assert len(calls) == 1
    assert calls[0][0] is analyzer
    assert calls[0][1] == {"value": 42}


def test_add_hook_requires_callable(
    analyzer: MetricTrendAnalyzer,
) -> None:
    with pytest.raises(TypeError):
        analyzer.add_hook(
            "custom",
            "invalid",
        )


def test_remove_hook(
    analyzer: MetricTrendAnalyzer,
) -> None:
    calls = []

    def callback(instance, **payload):
        calls.append(payload)

    analyzer.add_hook(
        "custom",
        callback,
    )

    analyzer.remove_hook(
        "custom",
        callback,
    )

    analyzer.emit(
        "custom",
        value=1,
    )

    assert calls == []


def test_remove_all_hooks(
    analyzer: MetricTrendAnalyzer,
) -> None:
    calls = []

    def callback(instance, **payload):
        calls.append(payload)

    analyzer.add_hook(
        "custom",
        callback,
    )

    analyzer.remove_hook("custom")

    analyzer.emit(
        "custom",
        value=1,
    )

    assert calls == []


def test_subscribe_alias(
    analyzer: MetricTrendAnalyzer,
) -> None:
    calls = []

    def callback(instance, **payload):
        calls.append(payload)

    result = analyzer.subscribe(
        "custom",
        callback,
    )

    assert result is analyzer

    analyzer.emit(
        "custom",
        value=42,
    )

    assert calls == [{"value": 42}]


def test_emit_records_event(
    analyzer: MetricTrendAnalyzer,
) -> None:
    analyzer.emit(
        "custom",
        value=42,
    )

    assert len(analyzer._events) == 1

    event = analyzer._events[-1]

    assert event["event"] == "custom"
    assert event["payload"] == {"value": 42}
    assert event["timestamp"] is not None


def test_before_analyze_hook(
    analyzer: MetricTrendAnalyzer,
) -> None:
    calls = []

    def callback(instance, **payload):
        calls.append(payload)

    analyzer.add_hook(
        "before_analyze",
        callback,
    )

    result = analyzer.before_analyze(
        [1, 2, 3],
        "linear",
        example=True,
    )

    assert result is analyzer
    assert calls == [
        {
            "values": [1, 2, 3],
            "method": "linear",
            "kwargs": {
                "example": True,
            },
        }
    ]


def test_after_analyze_hook(
    analyzer: MetricTrendAnalyzer,
) -> None:
    calls = []

    def callback(instance, **payload):
        calls.append(payload)

    analyzer.add_hook(
        "after_analyze",
        callback,
    )

    result = analyzer.after_analyze(
        {"trend": "upward"},
        "linear",
    )

    assert result is analyzer
    assert calls == [
        {
            "result": {"trend": "upward"},
            "method": "linear",
        }
    ]


def test_before_algorithm_hook(
    analyzer: MetricTrendAnalyzer,
) -> None:
    calls = []

    def callback(instance, **payload):
        calls.append(payload)

    analyzer.add_hook(
        "before_algorithm",
        callback,
    )

    result = analyzer.before_algorithm("linear")

    assert result is analyzer
    assert calls == [
        {
            "algorithm": "linear",
        }
    ]


def test_after_algorithm_hook(
    analyzer: MetricTrendAnalyzer,
) -> None:
    calls = []

    def callback(instance, **payload):
        calls.append(payload)

    analyzer.add_hook(
        "after_algorithm",
        callback,
    )

    result = analyzer.after_algorithm(
        "linear",
        {"trend": "upward"},
    )

    assert result is analyzer
    assert calls == [
        {
            "algorithm": "linear",
            "result": {
                "trend": "upward",
            },
        }
    ]


# ==============================================================================
# Part 26. Serialization
# ==============================================================================


def test_to_dict(
    builtin_analyzer: MetricTrendAnalyzer,
) -> None:
    data = builtin_analyzer.to_dict()

    assert set(data) == {
        "id",
        "name",
        "description",
        "version",
        "enabled",
        "frozen",
        "closed",
        "config",
        "trend_count",
        "analysis_count",
        "error_count",
        "latency",
        "created_at",
        "updated_at",
        "algorithm_names",
        "history",
        "last_result",
    }


def test_to_dict_identity(
    analyzer: MetricTrendAnalyzer,
) -> None:
    data = analyzer.to_dict()

    assert data["id"] == analyzer.id
    assert data["name"] == analyzer.name
    assert data["description"] == analyzer.description
    assert data["version"] == analyzer.version


def test_to_dict_initial_runtime_state(
    analyzer: MetricTrendAnalyzer,
) -> None:
    data = analyzer.to_dict()

    assert data["enabled"] is True
    assert data["frozen"] is False
    assert data["closed"] is False
    assert data["trend_count"] == 0
    assert data["analysis_count"] == 0
    assert data["error_count"] == 0
    assert data["latency"] == 0.0
    assert data["history"] == []
    assert data["last_result"] is None


def test_to_dict_after_analysis(
    builtin_analyzer: MetricTrendAnalyzer,
) -> None:
    result = builtin_analyzer.analyze(
        [1, 2, 3],
        method="linear",
    )

    data = builtin_analyzer.to_dict()

    assert data["history"] == [result]
    assert data["last_result"] == result
    assert data["analysis_count"] == 1
    assert data["trend_count"] == 1


def test_from_dict(
    builtin_analyzer: MetricTrendAnalyzer,
) -> None:
    builtin_analyzer.configure(
        window=10,
    )

    builtin_analyzer.analyze(
        [1, 2, 3],
        method="linear",
    )

    data = builtin_analyzer.to_dict()

    restored = MetricTrendAnalyzer.from_dict(data)

    assert isinstance(restored, MetricTrendAnalyzer)
    assert restored.id == builtin_analyzer.id
    assert restored.name == builtin_analyzer.name
    assert restored.description == builtin_analyzer.description
    assert restored.version == builtin_analyzer.version
    assert restored.config == builtin_analyzer.config
    assert restored.trend_count == builtin_analyzer.trend_count
    assert restored.analysis_count == builtin_analyzer.analysis_count
    assert restored.error_count == builtin_analyzer.error_count
    assert restored.latency == builtin_analyzer.latency
    assert restored._history == builtin_analyzer._history
    assert restored._last_result == builtin_analyzer._last_result


def test_to_json(
    analyzer: MetricTrendAnalyzer,
) -> None:
    text = analyzer.to_json()

    assert isinstance(text, str)

    data = json.loads(text)

    assert data["id"] == analyzer.id
    assert data["name"] == analyzer.name


def test_to_json_accepts_kwargs(
    analyzer: MetricTrendAnalyzer,
) -> None:
    text = analyzer.to_json(
        sort_keys=True,
    )

    data = json.loads(text)

    assert data["id"] == analyzer.id


def test_from_json(
    analyzer: MetricTrendAnalyzer,
) -> None:
    text = analyzer.to_json()

    restored = MetricTrendAnalyzer.from_json(text)

    assert isinstance(restored, MetricTrendAnalyzer)
    assert restored.id == analyzer.id
    assert restored.name == analyzer.name


def test_serialize_alias(
    analyzer: MetricTrendAnalyzer,
) -> None:
    assert analyzer.serialize() == analyzer.to_dict()


def test_deserialize_dict(
    analyzer: MetricTrendAnalyzer,
) -> None:
    restored = MetricTrendAnalyzer.deserialize(
        analyzer.to_dict(),
    )

    assert isinstance(restored, MetricTrendAnalyzer)
    assert restored.id == analyzer.id


def test_deserialize_json(
    analyzer: MetricTrendAnalyzer,
) -> None:
    restored = MetricTrendAnalyzer.deserialize(
        analyzer.to_json(),
    )

    assert isinstance(restored, MetricTrendAnalyzer)
    assert restored.id == analyzer.id


# ==============================================================================
# Part 27. Python Protocols
# ==============================================================================


def test_repr(
    builtin_analyzer: MetricTrendAnalyzer,
) -> None:
    text = repr(builtin_analyzer)

    assert "MetricTrendAnalyzer" in text
    assert builtin_analyzer.name in text
    assert "enabled=True" in text
    assert "running=False" in text
    assert "algorithms=9" in text
    assert "analyses=0" in text


def test_str(
    builtin_analyzer: MetricTrendAnalyzer,
) -> None:
    text = str(builtin_analyzer)

    assert builtin_analyzer.name in text
    assert "enabled=True" in text
    assert "running=False" in text
    assert "algorithms=9" in text


def test_len(
    builtin_analyzer: MetricTrendAnalyzer,
) -> None:
    assert len(builtin_analyzer) == 9


def test_iter(
    builtin_analyzer: MetricTrendAnalyzer,
) -> None:
    assert list(builtin_analyzer) == (
        builtin_analyzer.algorithm_names()
    )


def test_contains(
    builtin_analyzer: MetricTrendAnalyzer,
) -> None:
    assert "linear" in builtin_analyzer
    assert "slope" in builtin_analyzer
    assert "missing" not in builtin_analyzer


def test_call(
    builtin_analyzer: MetricTrendAnalyzer,
) -> None:
    result = builtin_analyzer(
        [1, 2, 3],
        method="linear",
    )

    assert result["algorithm"] == "linear"


# ==============================================================================
# Part 28. Error Accounting
# ==============================================================================


def test_failed_analysis_increments_error_count(
    builtin_analyzer: MetricTrendAnalyzer,
) -> None:
    before = builtin_analyzer.error_count

    with pytest.raises(KeyError):
        builtin_analyzer.analyze(
            [1, 2, 3],
            method="missing",
        )

    # Unknown algorithm is rejected before the try/except block.
    assert builtin_analyzer.error_count == before


def test_algorithm_failure_increments_error_count(
    analyzer: MetricTrendAnalyzer,
) -> None:
    def failing(values):
        raise ValueError("boom")

    analyzer.register_algorithm(
        "failing",
        failing,
    )

    with pytest.raises(ValueError, match="boom"):
        analyzer.analyze(
            [1, 2, 3],
            method="failing",
        )

    assert analyzer.error_count == 1
    assert analyzer.analysis_count == 0
    assert analyzer.running is False


# ==============================================================================
# Part 29. Updated Timestamp
# ==============================================================================


def test_configure_updates_timestamp(
    analyzer: MetricTrendAnalyzer,
) -> None:
    before = analyzer.updated_at

    time.sleep(0.001)

    analyzer.configure(window=10)

    assert analyzer.updated_at >= before


def test_algorithm_registration_updates_timestamp(
    analyzer: MetricTrendAnalyzer,
) -> None:
    before = analyzer.updated_at

    time.sleep(0.001)

    analyzer.register_algorithm(
        "test",
        lambda values: values,
    )

    assert analyzer.updated_at >= before


# ==============================================================================
# Part 30. Input Iterable Compatibility
# ==============================================================================


def test_linear_accepts_tuple(
    analyzer: MetricTrendAnalyzer,
) -> None:
    result = analyzer.linear((1, 2, 3))

    assert result["trend"] == "upward"


def test_linear_accepts_generator(
    analyzer: MetricTrendAnalyzer,
) -> None:
    result = analyzer.linear(
        value for value in [1, 2, 3]
    )

    assert result["trend"] == "upward"


def test_moving_average_accepts_generator(
    analyzer: MetricTrendAnalyzer,
) -> None:
    result = analyzer.moving_average(
        (value for value in [1, 2, 3]),
        window=2,
    )

    assert result["average"] == 2.5


def test_cumulative_accepts_generator(
    analyzer: MetricTrendAnalyzer,
) -> None:
    result = analyzer.cumulative(
        value for value in [1, 2, 3]
    )

    assert result["cumulative"] == [
        1.0,
        3.0,
        6.0,
    ]