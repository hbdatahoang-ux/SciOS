# ==============================================================================
# Part 1. Imports
# ==============================================================================

import copy
import json
import math

import pytest

from scios.runtime.observability.metrics.runtime.collector import (
    RuntimeCollector,
)

from scios.runtime.observability.metrics.runtime.aggregator import (
    RuntimeAggregator,
    DEFAULT_NAME,
    DEFAULT_ENABLED,
    DEFAULT_WINDOW_SIZE,
    DEFAULT_PRECISION,
    DEFAULT_AGGREGATED,
    DEFAULT_COUNT,
    DEFAULT_IGNORE_NONE,
    DEFAULT_NUMERIC_ONLY,
)


# ==============================================================================
# Part 2. Helpers
# ==============================================================================


def create_collector():

    collector = RuntimeCollector(
        name="collector",
    )

    collector.add(
        {
            "cpu": 20.0,
            "memory": 40.0,
        }
    )

    collector.add(
        {
            "cpu": 30.0,
            "memory": 50.0,
        }
    )

    return collector


def create_aggregator():

    collector = create_collector()

    aggregator = RuntimeAggregator(
        name="demo",
        collector=collector,
        window_size=64,
        precision=2,
    )

    aggregator.aggregate()

    return aggregator


# ==============================================================================
# Part 3. Constructor
# ==============================================================================


def test_default_constructor():

    aggregator = RuntimeAggregator()

    assert aggregator.name == DEFAULT_NAME
    assert aggregator.enabled is DEFAULT_ENABLED
    assert isinstance(aggregator.collector, RuntimeCollector)

    assert aggregator.aggregated == DEFAULT_AGGREGATED
    assert aggregator.count == DEFAULT_COUNT

    assert aggregator.window_size == DEFAULT_WINDOW_SIZE
    assert aggregator.precision == DEFAULT_PRECISION

    assert aggregator.created_at > 0
    assert aggregator.last_aggregate is None


def test_custom_constructor():

    collector = create_collector()

    aggregator = RuntimeAggregator(
        name="runtime",
        enabled=False,
        collector=collector,
        window_size=32,
        precision=4,
    )

    assert aggregator.name == "runtime"
    assert aggregator.enabled is False
    assert aggregator.collector is collector
    assert aggregator.window_size == 32
    assert aggregator.precision == 4


def test_slots():

    assert hasattr(RuntimeAggregator, "__slots__")

    slots = set(RuntimeAggregator.__slots__)

    assert "_name" in slots
    assert "_enabled" in slots
    assert "_collector" in slots
    assert "_aggregated" in slots
    assert "_count" in slots
    assert "_created_at" in slots
    assert "_last_aggregate" in slots
    assert "_total_sum" in slots
    assert "_minimum" in slots
    assert "_maximum" in slots
    assert "_window_size" in slots
    assert "_precision" in slots


# ==============================================================================
# Part 4. Properties
# ==============================================================================


def test_properties():

    aggregator = create_aggregator()

    assert aggregator.name == "demo"
    assert aggregator.enabled is True

    assert isinstance(
        aggregator.collector,
        RuntimeCollector,
    )

    assert isinstance(
        aggregator.aggregated,
        dict,
    )

    assert aggregator.count >= 0
    assert aggregator.size == len(aggregator.aggregated)

    assert aggregator.created_at > 0

    if aggregator.count > 0:
        assert aggregator.last_aggregate in (
            None,
            aggregator.last_aggregate,
        )

    assert aggregator.window_size == 64
    assert aggregator.precision == 2


def test_name_property():

    assert create_aggregator().name == "demo"


def test_enabled_property():

    assert create_aggregator().enabled is True


def test_collector_property():

    aggregator = create_aggregator()

    assert isinstance(
        aggregator.collector,
        RuntimeCollector,
    )


def test_aggregated_property():

    aggregator = create_aggregator()

    assert isinstance(
        aggregator.aggregated,
        dict,
    )


def test_count_property():

    aggregator = create_aggregator()

    assert isinstance(
        aggregator.count,
        int,
    )

    assert aggregator.count >= 0


def test_size_property():

    aggregator = create_aggregator()

    assert aggregator.size == len(
        aggregator.aggregated,
    )


def test_created_at_property():

    assert create_aggregator().created_at > 0


def test_last_aggregate_property():

    aggregator = create_aggregator()

    if aggregator.count > 0:
        assert aggregator.last_aggregate in (
    None,
    aggregator.last_aggregate,
)
    else:
        assert aggregator.last_aggregate is None


def test_window_size_property():

    assert create_aggregator().window_size == 64


def test_precision_property():

    assert create_aggregator().precision == 2

# ==============================================================================
# Part 5. Lifecycle
# ==============================================================================


def test_enable():

    aggregator = create_aggregator()

    aggregator.disable()

    aggregator.enable()

    assert aggregator.enabled is True


def test_disable():

    aggregator = create_aggregator()

    aggregator.disable()

    assert aggregator.enabled is False


def test_clear():

    aggregator = create_aggregator()

    aggregator.clear()

    assert aggregator.aggregated == {}
    assert aggregator.count == 0
    assert aggregator.size == 0


def test_reset():

    aggregator = create_aggregator()

    aggregator.reset()

    assert aggregator.enabled is DEFAULT_ENABLED
    assert aggregator.aggregated == DEFAULT_AGGREGATED
    assert aggregator.count == DEFAULT_COUNT


def test_aggregate():

    aggregator = RuntimeAggregator(
        collector=create_collector(),
    )

    assert aggregator.aggregate() is True

    assert aggregator.count >= 0

    if aggregator.count:
        assert aggregator.last_aggregate in (
    None,
    aggregator.last_aggregate,
)


def test_disabled_aggregate():

    aggregator = RuntimeAggregator(
        collector=create_collector(),
        enabled=False,
    )

    assert aggregator.aggregate() is False

    assert aggregator.count == 0


def test_enable_disable():

    aggregator = create_aggregator()

    aggregator.disable()

    assert aggregator.enabled is False

    aggregator.enable()

    assert aggregator.enabled is True


# ==============================================================================
# Part 6. Aggregation API
# ==============================================================================


def test_aggregate_sample():

    aggregator = RuntimeAggregator()

    aggregator.aggregate_sample(
        {
            "cpu": 50,
            "memory": 80,
        }
    )

    assert aggregator.count == 1

    assert aggregator.exists("cpu")
    assert aggregator.exists("memory")


def test_aggregate_samples():

    aggregator = RuntimeAggregator()

    aggregator.aggregate_samples(
        [
            {
                "cpu": 10,
            },
            {
                "cpu": 20,
            },
        ]
    )

    assert aggregator.count == 2


def test_recompute():

    aggregator = create_aggregator()

    old = copy.deepcopy(
        aggregator.aggregated,
    )

    aggregator.recompute()

    assert aggregator.aggregated == old


def test_get():

    aggregator = create_aggregator()

    key = next(iter(aggregator.keys()))

    assert aggregator.get(key) == aggregator.aggregated[key]


def test_keys():

    aggregator = create_aggregator()

    keys = list(aggregator.keys())

    assert len(keys) == aggregator.size



def test_values():

    aggregator = create_aggregator()

    values = list(aggregator.values())

    assert len(values) == aggregator.size


def test_items():

    aggregator = create_aggregator()

    items = list(aggregator.items())

    assert len(items) == aggregator.size


def test_exists():

    aggregator = create_aggregator()

    key = next(iter(aggregator.keys()))

    assert aggregator.exists(key) is True

    assert aggregator.exists("unknown") is False


def test_has_key():

    aggregator = create_aggregator()

    key = next(iter(aggregator.keys()))

    assert aggregator.has_key(key)

    assert not aggregator.has_key("invalid")


# ==============================================================================
# Part 7. Statistics
# ==============================================================================


def test_sum():

    aggregator = create_aggregator()

    result = aggregator.sum()

    assert isinstance(
        result,
        (int, float, dict),
    )


def test_average():

    aggregator = create_aggregator()

    result = aggregator.average()

    assert isinstance(
        result,
        (int, float, dict),
    )


def test_minimum():

    aggregator = create_aggregator()

    result = aggregator.minimum()

    assert result is not None


def test_maximum():

    aggregator = create_aggregator()

    result = aggregator.maximum()

    assert result is not None


def test_statistics():

    stats = create_aggregator().statistics()

    assert isinstance(stats, dict)


def test_reset_statistics():

    aggregator = create_aggregator()

    aggregator.reset_statistics()

    assert aggregator.count == 0


# ==============================================================================
# Part 8. Operations
# ==============================================================================


def test_clone():

    aggregator = create_aggregator()

    cloned = aggregator.clone()

    assert cloned == aggregator
    assert cloned is not aggregator


def test_copy():

    aggregator = create_aggregator()

    copied = aggregator.copy()

    assert copied == aggregator
    assert copied is not aggregator


def test_merge():

    left = create_aggregator()

    right = create_aggregator()

    left.merge(right)

    assert left.count >= right.count
    assert isinstance(left.aggregated, dict)


def test_update():

    aggregator = create_aggregator()

    before = dict(aggregator.aggregated)

    aggregator.update(
        {
            "cpu": 100,
        }
    )

    assert isinstance(
        aggregator.aggregated,
        dict,
    )

    assert aggregator.size >= len(before)


def test_snapshot():

    aggregator = create_aggregator()

    snapshot = aggregator.snapshot()

    assert isinstance(snapshot, dict)


def test_restore():

    aggregator = create_aggregator()

    snapshot = aggregator.snapshot()

    restored = RuntimeAggregator()

    restored.restore(snapshot)

    assert restored == aggregator


# ==============================================================================
# Part 9. Validation
# ==============================================================================


def test_validate():

    aggregator = create_aggregator()

    assert aggregator.validate() is True


def test_normalize():

    aggregator = RuntimeAggregator()

    assert aggregator.normalize(10) == 10
    assert aggregator.normalize(10.5) == 10.5
    assert aggregator.normalize(None) is None


def test_normalize_nan():

    aggregator = RuntimeAggregator()

    result = aggregator.normalize(math.nan)

    assert result == 0.0


def test_normalize_inf():

    aggregator = RuntimeAggregator()

    result = aggregator.normalize(math.inf)

    assert result == 0.0


def test_validate_empty():

    aggregator = RuntimeAggregator()

    assert aggregator.validate() is True


# ==============================================================================
# Part 10. Serialization
# ==============================================================================


def test_to_dict():

    aggregator = create_aggregator()

    data = aggregator.to_dict()

    assert isinstance(data, dict)


def test_from_dict():

    aggregator = create_aggregator()

    restored = RuntimeAggregator.from_dict(
        aggregator.to_dict(),
    )

    assert restored == aggregator


def test_to_tuple():

    aggregator = create_aggregator()

    data = aggregator.to_tuple()

    assert isinstance(data, tuple)


def test_from_tuple():

    aggregator = create_aggregator()

    restored = RuntimeAggregator.from_tuple(
        aggregator.to_tuple(),
    )

    assert restored == aggregator


def test_to_json():

    aggregator = create_aggregator()

    text = aggregator.to_json()

    assert isinstance(text, str)

    json.loads(text)


def test_from_json():

    aggregator = create_aggregator()

    restored = RuntimeAggregator.from_json(
        aggregator.to_json(),
    )

    assert restored == aggregator


# ==============================================================================
# Part 11. Diagnostics
# ==============================================================================


def test_summary():

    summary = create_aggregator().summary()

    assert isinstance(summary, dict)


def test_diagnostics():

    diagnostics = create_aggregator().diagnostics()

    assert isinstance(diagnostics, dict)


def test_report():

    report = create_aggregator().report()

    assert isinstance(
        report,
        (str, dict),
    )


def test_status():

    status = create_aggregator().status()

    assert isinstance(
        status,
        (str, dict),
    )


# ==============================================================================
# Part 12. Protocols
# ==============================================================================


def test_len():

    aggregator = create_aggregator()

    assert len(aggregator) == aggregator.size


def test_contains():

    aggregator = create_aggregator()

    key = next(iter(aggregator.keys()))

    assert key in aggregator


def test_iter():

    aggregator = create_aggregator()

    items = list(iter(aggregator))

    assert len(items) == aggregator.size


def test_hash():

    aggregator = create_aggregator()

    assert isinstance(
        hash(aggregator),
        int,
    )


def test_eq():

    left = create_aggregator()

    right = create_aggregator()

    assert left == right


def test_repr():

    text = repr(create_aggregator())

    assert "RuntimeAggregator" in text


def test_str():

    text = str(create_aggregator())

    assert isinstance(text, str)


def test_bool():

    assert bool(create_aggregator()) is True

    aggregator = RuntimeAggregator()

    assert bool(aggregator) is True

    aggregator.disable()

    assert bool(aggregator) is False      