# ==============================================================================
# SciOS Runtime Observability
# Metrics Analysis
# Tests: MetricStatistics
# ==============================================================================

from __future__ import annotations

from datetime import datetime
from math import isclose

import pytest

from scios.runtime.observability.metrics.analysis import MetricStatistics


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def statistics() -> MetricStatistics:
    return MetricStatistics([1, 2, 3, 4, 5])


@pytest.fixture
def repeated_statistics() -> MetricStatistics:
    return MetricStatistics([1, 2, 2, 3, 3, 3, 4])


# ==============================================================================
# Part 1. Construction Contract
# ==============================================================================


def test_construction_from_iterable() -> None:
    stats = MetricStatistics([1, 2, 3, 4, 5])

    assert stats.values() == [1.0, 2.0, 3.0, 4.0, 5.0]


def test_construction_from_tuple() -> None:
    stats = MetricStatistics((1, 2, 3))

    assert stats.values() == [1.0, 2.0, 3.0]


def test_construction_from_generator() -> None:
    stats = MetricStatistics(value for value in [1, 2, 3])

    assert stats.values() == [1.0, 2.0, 3.0]


def test_construction_preserves_input_order() -> None:
    stats = MetricStatistics([5, 1, 4, 2, 3])

    assert stats.values() == [5.0, 1.0, 4.0, 2.0, 3.0]


def test_empty_values_are_allowed() -> None:
    stats = MetricStatistics([])

    assert stats.values() == []


def test_invalid_values_are_rejected() -> None:
    with pytest.raises((ValueError, TypeError)):
        MetricStatistics(["invalid"])


# ==============================================================================
# Part 2. Basic Statistics
# ==============================================================================


def test_count(statistics: MetricStatistics) -> None:
    assert statistics.describe()["count"] == 5


def test_sum(statistics: MetricStatistics) -> None:
    assert statistics.describe()["sum"] == 15.0


def test_mean(statistics: MetricStatistics) -> None:
    assert statistics.describe()["mean"] == 3.0


def test_median(statistics: MetricStatistics) -> None:
    assert statistics.describe()["median"] == 3.0


def test_mode_with_repeated_values(
    repeated_statistics: MetricStatistics,
) -> None:
    assert repeated_statistics.describe()["mode"] == 3.0


def test_mode_for_unique_values(
    statistics: MetricStatistics,
) -> None:
    # Current implementation contract.
    assert statistics.describe()["mode"] == 1.0


def test_min(statistics: MetricStatistics) -> None:
    assert statistics.describe()["min"] == 1.0


def test_max(statistics: MetricStatistics) -> None:
    assert statistics.describe()["max"] == 5.0


def test_range(statistics: MetricStatistics) -> None:
    assert statistics.describe()["range"] == 4.0


# ==============================================================================
# Part 3. Dispersion Statistics
# ==============================================================================


def test_variance(statistics: MetricStatistics) -> None:
    assert isclose(
        statistics.describe()["variance"],
        2.5,
        rel_tol=1e-12,
        abs_tol=1e-12,
    )


def test_standard_deviation(statistics: MetricStatistics) -> None:
    assert isclose(
        statistics.describe()["std"],
        1.5811388300841898,
        rel_tol=1e-12,
        abs_tol=1e-12,
    )


# ==============================================================================
# Part 4. Quantiles
# ==============================================================================


def test_q25(statistics: MetricStatistics) -> None:
    assert statistics.describe()["q25"] == 2.0


def test_q50_equals_median(statistics: MetricStatistics) -> None:
    result = statistics.describe()

    assert result["q50"] == result["median"] == 3.0


def test_q75(statistics: MetricStatistics) -> None:
    assert statistics.describe()["q75"] == 4.0


def test_iqr(statistics: MetricStatistics) -> None:
    result = statistics.describe()

    assert result["iqr"] == result["q75"] - result["q25"]
    assert result["iqr"] == 2.0


# ==============================================================================
# Part 5. describe() Contract
# ==============================================================================


def test_describe_returns_dict(
    statistics: MetricStatistics,
) -> None:
    result = statistics.describe()

    assert isinstance(result, dict)


def test_describe_contains_complete_statistic_contract(
    statistics: MetricStatistics,
) -> None:
    result = statistics.describe()

    assert set(result) == {
        "count",
        "sum",
        "mean",
        "median",
        "mode",
        "min",
        "max",
        "range",
        "variance",
        "std",
        "q25",
        "q50",
        "q75",
        "iqr",
    }


def test_describe_values_are_numeric(
    statistics: MetricStatistics,
) -> None:
    result = statistics.describe()

    for value in result.values():
        assert isinstance(value, (int, float))


# ==============================================================================
# Part 6. Moving Average
# ==============================================================================


def test_moving_average_window_three(
    statistics: MetricStatistics,
) -> None:
    assert statistics.moving_average(3) == [
        2.0,
        3.0,
        4.0,
    ]


def test_moving_average_window_two(
    statistics: MetricStatistics,
) -> None:
    assert statistics.moving_average(2) == [
        1.5,
        2.5,
        3.5,
        4.5,
    ]


def test_moving_average_window_one(
    statistics: MetricStatistics,
) -> None:
    assert statistics.moving_average(1) == [
        1.0,
        2.0,
        3.0,
        4.0,
        5.0,
    ]


def test_moving_average_window_equal_to_length(
    statistics: MetricStatistics,
) -> None:
    assert statistics.moving_average(5) == [3.0]


def test_moving_average_invalid_zero_window(
    statistics: MetricStatistics,
) -> None:
    with pytest.raises((ValueError, TypeError)):
        statistics.moving_average(0)


def test_moving_average_invalid_negative_window(
    statistics: MetricStatistics,
) -> None:
    with pytest.raises((ValueError, TypeError)):
        statistics.moving_average(-1)


def test_moving_average_window_larger_than_values(
    statistics: MetricStatistics,
) -> None:
    assert statistics.moving_average(10) == []


# ==============================================================================
# Part 7. Rolling Standard Deviation
# ==============================================================================


def test_rolling_std_window_three(
    statistics: MetricStatistics,
) -> None:
    result = statistics.rolling_std(3)

    assert len(result) == 3

    for value in result:
        assert isclose(
            value,
            1.0,
            rel_tol=1e-12,
            abs_tol=1e-12,
        )


def test_rolling_std_window_two(
    statistics: MetricStatistics,
) -> None:
    result = statistics.rolling_std(2)

    assert len(result) == 4

    expected = 0.7071067811865476

    for value in result:
        assert isclose(
            value,
            expected,
            rel_tol=1e-12,
            abs_tol=1e-12,
        )


def test_rolling_std_window_one(
    statistics: MetricStatistics,
) -> None:
    assert statistics.rolling_std(1) == [
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
    ]


def test_rolling_std_invalid_zero_window(
    statistics: MetricStatistics,
) -> None:
    with pytest.raises((ValueError, TypeError)):
        statistics.rolling_std(0)


def test_rolling_std_invalid_negative_window(
    statistics: MetricStatistics,
) -> None:
    with pytest.raises((ValueError, TypeError)):
        statistics.rolling_std(-1)


def test_rolling_std_window_larger_than_values(
    statistics: MetricStatistics,
) -> None:
    assert statistics.rolling_std(10) == []


# ==============================================================================
# Part 8. Exponential Average
# ==============================================================================


def test_exponential_average_default_alpha(
    statistics: MetricStatistics,
) -> None:
    result = statistics.exponential_average()

    expected = [
        1.0,
        1.2,
        1.56,
        2.048,
        2.6384,
    ]

    assert len(result) == len(expected)

    for actual, wanted in zip(result, expected):
        assert isclose(
            actual,
            wanted,
            rel_tol=1e-12,
            abs_tol=1e-12,
        )


def test_exponential_average_alpha_one(
    statistics: MetricStatistics,
) -> None:
    result = statistics.exponential_average(alpha=1.0)

    assert result == statistics.values()


def test_exponential_average_rejects_zero_alpha(
    statistics: MetricStatistics,
) -> None:
    with pytest.raises(ValueError):
        statistics.exponential_average(alpha=0.0)


@pytest.mark.parametrize(
    "alpha",
    [-1.0, 1.1, 2.0],
)
def test_exponential_average_rejects_invalid_alpha(
    statistics: MetricStatistics,
    alpha: float,
) -> None:
    with pytest.raises((ValueError, TypeError)):
        statistics.exponential_average(alpha=alpha)


def test_exponential_average_rejects_non_numeric_alpha(
    statistics: MetricStatistics,
) -> None:
    with pytest.raises((ValueError, TypeError)):
        statistics.exponential_average(alpha="invalid")


# ==============================================================================
# Part 9. Serialization Contract
# ==============================================================================


def test_to_dict_returns_dict(
    statistics: MetricStatistics,
) -> None:
    result = statistics.to_dict()

    assert isinstance(result, dict)


def test_to_dict_contains_required_top_level_keys(
    statistics: MetricStatistics,
) -> None:
    result = statistics.to_dict()

    assert set(result) == {
        "id",
        "name",
        "description",
        "values",
        "statistics",
        "enabled",
        "closed",
        "created_at",
        "updated_at",
        "version",
    }


def test_to_dict_values_match(
    statistics: MetricStatistics,
) -> None:
    result = statistics.to_dict()

    assert result["values"] == statistics.values()


def test_to_dict_statistics_match(
    statistics: MetricStatistics,
) -> None:
    result = statistics.to_dict()

    assert result["statistics"] == statistics.describe()


def test_to_dict_name(
    statistics: MetricStatistics,
) -> None:
    result = statistics.to_dict()

    assert result["name"] == "MetricStatistics"


def test_to_dict_default_description(
    statistics: MetricStatistics,
) -> None:
    result = statistics.to_dict()

    assert result["description"] == ""


def test_to_dict_enabled_by_default(
    statistics: MetricStatistics,
) -> None:
    result = statistics.to_dict()

    assert result["enabled"] is True


def test_to_dict_closed_by_default(
    statistics: MetricStatistics,
) -> None:
    result = statistics.to_dict()

    assert result["closed"] is False


def test_to_dict_version(
    statistics: MetricStatistics,
) -> None:
    result = statistics.to_dict()

    assert result["version"] == "0.3"


def test_to_dict_id_is_string(
    statistics: MetricStatistics,
) -> None:
    result = statistics.to_dict()

    assert isinstance(result["id"], str)
    assert result["id"]


def test_to_dict_created_at_is_iso_datetime(
    statistics: MetricStatistics,
) -> None:
    result = statistics.to_dict()

    created_at = datetime.fromisoformat(
        result["created_at"]
    )

    assert created_at.tzinfo is not None


def test_to_dict_updated_at_is_iso_datetime(
    statistics: MetricStatistics,
) -> None:
    result = statistics.to_dict()

    updated_at = datetime.fromisoformat(
        result["updated_at"]
    )

    assert updated_at.tzinfo is not None


# ==============================================================================
# Part 10. Metadata Stability
# ==============================================================================


def test_statistics_id_is_stable(
    statistics: MetricStatistics,
) -> None:
    first = statistics.to_dict()["id"]
    second = statistics.to_dict()["id"]

    assert first == second


def test_analysis_does_not_mutate_values(
    statistics: MetricStatistics,
) -> None:
    original = statistics.values()

    statistics.describe()
    statistics.moving_average(3)
    statistics.rolling_std(3)
    statistics.exponential_average()

    assert statistics.values() == original


# ==============================================================================
# Part 11. Numerical Contract
# ==============================================================================


def test_all_values_are_floats(
    statistics: MetricStatistics,
) -> None:
    assert all(
        isinstance(value, float)
        for value in statistics.values()
    )


def test_statistics_are_reproducible() -> None:
    first = MetricStatistics([1, 2, 3, 4, 5]).describe()
    second = MetricStatistics([1, 2, 3, 4, 5]).describe()

    assert first == second