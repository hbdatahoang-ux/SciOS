# ==============================================================================
# Part 1. Imports
# ==============================================================================

from __future__ import annotations

import copy
import json

import pytest

from scios.runtime.observability.metrics.runtime.collector import (
    RuntimeCollector,
)


# ==============================================================================
# Part 2. Helpers
# ==============================================================================


def create_collector() -> RuntimeCollector:

    collector = RuntimeCollector()

    collector.add(
        "cpu",
        20.0,
    )

    collector.add(
        "memory",
        40.0,
    )

    collector.start()

    return collector


# ==============================================================================
# Part 3. Constructor
# ==============================================================================


def test_default_constructor():

    collector = RuntimeCollector()

    assert collector.name == "runtime"

    assert collector.enabled is True

    assert collector.started is False

    assert collector.collect_limit == 1024

    assert collector.interval == 1.0

    assert collector.size == 0


def test_custom_constructor():

    collector = RuntimeCollector(
        name="system",
        enabled=False,
        started=True,
        collect_limit=10,
        interval=2.5,
    )

    assert collector.name == "system"

    assert collector.enabled is False

    assert collector.started is True

    assert collector.collect_limit == 10

    assert collector.interval == 2.5


def test_slots():

    collector = RuntimeCollector()

    assert hasattr(
        collector,
        "__slots__",
    )


# ==============================================================================
# Part 4. Properties
# ==============================================================================


def test_properties():

    collector = create_collector()

    assert collector.name == "runtime"

    assert collector.enabled is True

    assert collector.started is True

    assert collector.collect_limit == 1024

    assert collector.interval == 1.0

    assert collector.size == 2


def test_name_property():

    assert create_collector().name == "runtime"


def test_enabled_property():

    assert create_collector().enabled is True


def test_started_property():

    assert create_collector().started is True


def test_collect_limit_property():

    assert create_collector().collect_limit == 1024


def test_interval_property():

    assert create_collector().interval == 1.0


def test_samples_property():

    collector = create_collector()

    samples = collector.samples

    assert len(samples) == 2

    assert samples[0]["name"] == "cpu"

    assert samples[1]["name"] == "memory"


def test_collected_property():

    collector = create_collector()

    collector.record_success()

    assert collector.collected == 1


def test_failed_property():

    collector = create_collector()

    collector.record_failure()

    assert collector.failed == 1


def test_successes_property():

    collector = create_collector()

    collector.record_success()

    assert collector.successes == 1


def test_failures_property():

    collector = create_collector()

    collector.record_failure()

    assert collector.failures == 1


def test_created_at_property():

    assert create_collector().created_at > 0


def test_last_collect_property():

    collector = create_collector()

    assert collector.last_collect is None

    collector.collect()

    assert collector.last_collect is not None


def test_size_property():

    assert create_collector().size == 2


def test_utilization_property():

    collector = RuntimeCollector(
        collect_limit=4,
    )

    collector.add(
        "cpu",
        1,
    )

    collector.add(
        "memory",
        2,
    )

    assert collector.utilization == pytest.approx(
        0.5,
    )

# ==============================================================================
# Part 5. Lifecycle
# ==============================================================================


def test_start():

    collector = RuntimeCollector()

    collector.start()

    assert collector.started is True


def test_stop():

    collector = create_collector()

    collector.stop()

    assert collector.started is False


def test_enable():

    collector = RuntimeCollector(
        enabled=False,
    )

    collector.enable()

    assert collector.enabled is True


def test_disable():

    collector = create_collector()

    collector.disable()

    assert collector.enabled is False


def test_clear():

    collector = create_collector()

    collector.clear()

    assert collector.size == 0

    assert collector.collected == 0

    assert collector.failed == 0


def test_reset():

    collector = create_collector()

    collector.reset()

    assert collector.started is False

    assert collector.enabled is True

    assert collector.size == 0


def test_collect():

    collector = RuntimeCollector()

    assert collector.collect() is True

    assert collector.collected == 1


def test_collect_disabled():

    collector = RuntimeCollector(
        enabled=False,
    )

    assert collector.collect() is False

    assert collector.failed == 1


def test_start_stop():

    collector = RuntimeCollector()

    collector.start()

    collector.stop()

    assert collector.started is False


# ==============================================================================
# Part 6. Sample API
# ==============================================================================


def test_add():

    collector = RuntimeCollector()

    assert collector.add("cpu", 20.0)

    assert collector.size == 1


def test_add_many():

    collector = RuntimeCollector()

    count = collector.add_many(
        [
            {"name": "cpu", "value": 1},
            {"name": "memory", "value": 2},
        ]
    )

    assert count == 2


def test_append():

    collector = RuntimeCollector()

    collector.append("cpu", 1)

    assert collector.size == 1


def test_extend():

    collector = RuntimeCollector()

    collector.extend(
        [
            {"name": "a"},
            {"name": "b"},
        ]
    )

    assert collector.size == 2


def test_remove():

    collector = create_collector()

    sample = collector.first()

    assert collector.remove(sample)

    assert collector.size == 1


def test_pop():

    collector = create_collector()

    value = collector.pop()

    assert value is not None

    assert collector.size == 1


def test_latest():

    assert create_collector().latest()["name"] == "memory"


def test_first():

    assert create_collector().first()["name"] == "cpu"


def test_get():

    collector = create_collector()

    assert collector.get(0)["name"] == "cpu"

    assert collector.get(100) is None


def test_samples_list():

    collector = create_collector()

    samples = collector.samples_list()

    assert isinstance(samples, list)

    assert len(samples) == 2


def test_clear_samples():

    collector = create_collector()

    collector.clear_samples()

    assert collector.size == 0


def test_has_samples():

    assert create_collector().has_samples() is True

    assert RuntimeCollector().has_samples() is False


def test_sample_count():

    assert create_collector().sample_count() == 2


# ==============================================================================
# Part 7. Statistics
# ==============================================================================


def test_record_success():

    collector = RuntimeCollector()

    collector.record_success()

    assert collector.successes == 1


def test_record_failure():

    collector = RuntimeCollector()

    collector.record_failure()

    assert collector.failures == 1


def test_success_rate():

    collector = RuntimeCollector()

    collector.record_success()

    collector.record_success()

    collector.record_failure()

    assert collector.success_rate() == pytest.approx(2 / 3)


def test_failure_rate():

    collector = RuntimeCollector()

    collector.record_success()

    collector.record_failure()

    collector.record_failure()

    assert collector.failure_rate() == pytest.approx(2 / 3)


def test_total_processed():

    collector = RuntimeCollector()

    collector.record_success()

    collector.record_failure()

    assert collector.total_processed() == 2


def test_statistics():

    collector = RuntimeCollector()

    collector.record_success()

    stats = collector.statistics()

    assert stats["successes"] == 1

    assert stats["size"] == 0


def test_reset_statistics():

    collector = RuntimeCollector()

    collector.record_success()

    collector.record_failure()

    collector.reset_statistics()

    assert collector.successes == 0

    assert collector.failures == 0


# ==============================================================================
# Part 8. Operations
# ==============================================================================


def test_clone():

    collector = create_collector()

    cloned = collector.clone()

    assert cloned == collector

    assert cloned is not collector


def test_copy():

    collector = create_collector()

    copied = collector.copy()

    assert copied == collector

    assert copied is not collector


def test_merge():

    left = RuntimeCollector()

    right = create_collector()

    left.merge(right)

    assert left.size == 2


def test_update():

    collector = RuntimeCollector()

    collector.update(
        {"name": "cpu", "value": 1}
    )

    collector.update(
        [
            {"name": "memory", "value": 2},
        ]
    )

    assert collector.size == 2


def test_snapshot():

    collector = create_collector()

    snapshot = collector.snapshot()

    assert isinstance(snapshot, dict)

    assert snapshot["name"] == "runtime"


def test_restore():

    collector = create_collector()

    snapshot = collector.snapshot()

    restored = RuntimeCollector()

    restored.restore(snapshot)

    assert restored == collector

# ==============================================================================
# Part 9. Validation
# ==============================================================================


def test_validate_name():

    collector = RuntimeCollector()

    assert collector.validate_name()

    assert collector.validate_name("metrics")

    assert collector.validate_name("") is False


def test_validate_samples():

    collector = RuntimeCollector()

    assert collector.validate_samples()

    assert collector.validate_samples([])

    assert collector.validate_samples({}) is False


def test_validate_limits():

    collector = RuntimeCollector()

    assert collector.validate_limits()


def test_validate():

    collector = RuntimeCollector()

    assert collector.validate()


def test_normalize():

    collector = RuntimeCollector()

    sample = collector.normalize(
        {"name": "cpu", "value": 10},
    )

    assert sample == {
        "name": "cpu",
        "value": 10,
    }


def test_validate_empty():

    collector = RuntimeCollector()

    collector.clear()

    assert collector.validate()


# ==============================================================================
# Part 10. Serialization
# ==============================================================================


def test_to_dict():

    collector = create_collector()

    data = collector.to_dict()

    assert isinstance(data, dict)

    assert data["name"] == "runtime"

    assert len(data["samples"]) == 2


def test_from_dict():

    collector = create_collector()

    restored = RuntimeCollector.from_dict(
        collector.to_dict(),
    )

    assert restored == collector


def test_to_tuple():

    collector = create_collector()

    value = collector.to_tuple()

    assert isinstance(value, tuple)

    assert value[0] == "runtime"


def test_from_tuple():

    collector = create_collector()

    restored = RuntimeCollector.from_tuple(
        collector.to_tuple(),
    )

    assert restored == collector


def test_to_json():

    collector = create_collector()

    payload = collector.to_json()

    assert isinstance(payload, str)

    assert json.loads(payload)["name"] == "runtime"


def test_from_json():

    collector = create_collector()

    restored = RuntimeCollector.from_json(
        collector.to_json(),
    )

    assert restored == collector


# ==============================================================================
# Part 11. Diagnostics
# ==============================================================================


def test_summary():

    collector = create_collector()

    summary = collector.summary()

    assert summary["name"] == "runtime"

    assert summary["size"] == 2


def test_diagnostics():

    collector = create_collector()

    diagnostics = collector.diagnostics()

    assert diagnostics["status"] == "started"

    assert diagnostics["enabled"] is True


def test_report():

    collector = create_collector()

    report = collector.report()

    assert "summary" in report

    assert "diagnostics" in report


def test_status():

    collector = RuntimeCollector()

    assert collector.status() == "ready"

    collector.start()

    assert collector.status() == "started"

    collector.disable()

    assert collector.status() == "disabled"


# ==============================================================================
# Part 12. Protocols
# ==============================================================================


def test_len():

    assert len(create_collector()) == 2


def test_contains():

    collector = create_collector()

    assert collector.first() in collector


def test_iter():

    collector = create_collector()

    assert len(list(iter(collector))) == 2


def test_hash():

    collector = RuntimeCollector()

    assert isinstance(hash(collector), int)


def test_eq():

    assert create_collector() == create_collector()


def test_repr():

    collector = create_collector()

    assert "RuntimeCollector" in repr(collector)


def test_str():

    collector = create_collector()

    assert str(collector).startswith("runtime")


def test_bool():

    assert bool(RuntimeCollector())

    invalid = RuntimeCollector(
        collect_limit=1,
    )
    invalid._collect_limit = 0

    assert bool(invalid) is False        