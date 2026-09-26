# ==============================================================================
# Part 1. Imports
# ==============================================================================

import json

import pytest

from scios.runtime.observability.metrics.runtime.recorder import (
    RuntimeRecorder,
    DEFAULT_NAME,
    DEFAULT_ENABLED,
    DEFAULT_STARTED,
    DEFAULT_RECORD_LIMIT,
    DEFAULT_FLUSH_INTERVAL,
    DEFAULT_RECORDED,
    DEFAULT_DROPPED,
)


# ==============================================================================
# Part 2. Helpers
# ==============================================================================


def create_recorder() -> RuntimeRecorder:

    recorder = RuntimeRecorder(
        name="demo",
    )

    recorder.record(
        {
            "name": "cpu",
        }
    )

    recorder.record(
        {
            "name": "memory",
        }
    )

    recorder.record_success()

    recorder.record_drop()

    return recorder


# ==============================================================================
# Part 3. Constructor
# ==============================================================================


def test_default_constructor():

    recorder = RuntimeRecorder()

    assert recorder.name == DEFAULT_NAME
    assert recorder.enabled is DEFAULT_ENABLED
    assert recorder.started is DEFAULT_STARTED
    assert recorder.record_limit == DEFAULT_RECORD_LIMIT
    assert recorder.flush_interval == DEFAULT_FLUSH_INTERVAL
    assert recorder.recorded == DEFAULT_RECORDED
    assert recorder.dropped == DEFAULT_DROPPED
    assert len(recorder.records) == 0


def test_custom_constructor():

    recorder = RuntimeRecorder(
        name="recorder",
        enabled=False,
        record_limit=256,
        flush_interval=10.0,
    )

    assert recorder.name == "recorder"
    assert recorder.enabled is False
    assert recorder.record_limit == 256
    assert recorder.flush_interval == 10.0
    assert recorder.recorded == DEFAULT_RECORDED
    assert recorder.dropped == DEFAULT_DROPPED


def test_slots():

    assert hasattr(
        RuntimeRecorder,
        "__slots__",
    )


# ==============================================================================
# Part 4. Properties
# ==============================================================================


def test_properties():

    recorder = create_recorder()

    assert recorder.name == "demo"
    assert recorder.enabled is True
    assert recorder.started is False
    assert recorder.record_limit == DEFAULT_RECORD_LIMIT
    assert recorder.flush_interval == DEFAULT_FLUSH_INTERVAL
    assert recorder.recorded == 3
    assert recorder.dropped == 1
    assert recorder.size == 2


def test_name_property():

    recorder = RuntimeRecorder(
        name="metrics",
    )

    assert recorder.name == "metrics"


def test_enabled_property():

    recorder = RuntimeRecorder()

    assert recorder.enabled is True


def test_started_property():

    recorder = RuntimeRecorder()

    assert recorder.started is False

    recorder.start()

    assert recorder.started is True


def test_record_limit_property():

    recorder = RuntimeRecorder(
        record_limit=512,
    )

    assert recorder.record_limit == 512


def test_flush_interval_property():

    recorder = RuntimeRecorder(
        flush_interval=5.0,
    )

    assert recorder.flush_interval == 5.0


def test_records_property():

    recorder = create_recorder()

    assert isinstance(
        recorder.records,
        list,
    )

    assert len(
        recorder.records,
    ) == 2


def test_recorded_property():

    recorder = create_recorder()

    assert recorder.recorded == 3


def test_dropped_property():

    recorder = create_recorder()

    assert recorder.dropped == 1


def test_size_property():

    recorder = create_recorder()

    assert recorder.size == 2


def test_utilization_property():

    recorder = RuntimeRecorder(
        record_limit=10,
    )

    recorder.record(
        {
            "x": 1,
        }
    )

    recorder.record(
        {
            "y": 2,
        }
    )

    assert recorder.utilization == pytest.approx(
        0.2
    )


# ==============================================================================
# Part 5. Lifecycle
# ==============================================================================


def test_start():

    recorder = RuntimeRecorder()

    recorder.start()

    assert recorder.started is True


def test_stop():

    recorder = RuntimeRecorder()

    recorder.start()

    recorder.stop()

    assert recorder.started is False


def test_enable():

    recorder = RuntimeRecorder(
        enabled=False,
    )

    recorder.enable()

    assert recorder.enabled is True


def test_disable():

    recorder = RuntimeRecorder()

    recorder.disable()

    assert recorder.enabled is False


def test_clear():

    recorder = create_recorder()

    recorder.clear()

    assert len(
        recorder.records,
    ) == 0


def test_reset():

    recorder = create_recorder()

    recorder.start()

    recorder.reset()

    assert recorder.started is DEFAULT_STARTED
    assert recorder.enabled is DEFAULT_ENABLED
    assert recorder.recorded == DEFAULT_RECORDED
    assert recorder.dropped == DEFAULT_DROPPED
    assert len(
        recorder.records,
    ) == 0


def test_flush():

    recorder = create_recorder()

    flushed = recorder.flush()

    assert isinstance(
        flushed,
        list,
    )

    assert len(
        flushed,
    ) == 2

    assert len(
        recorder.records,
    ) == 0


def test_enable_disable():

    recorder = RuntimeRecorder()

    recorder.disable()

    assert recorder.enabled is False

    recorder.enable()

    assert recorder.enabled is True

# ==============================================================================
# Part 6. Record API
# ==============================================================================


def test_record():

    recorder = RuntimeRecorder()

    assert recorder.record({"a": 1}) is True
    assert recorder.size == 1


def test_append():

    recorder = RuntimeRecorder()

    recorder.append({"a": 1})

    assert recorder.size == 1


def test_extend():

    recorder = RuntimeRecorder()

    recorder.extend(
        [
            {"a": 1},
            {"b": 2},
        ]
    )

    assert recorder.size == 2


def test_remove():

    recorder = create_recorder()

    record = recorder.first()

    recorder.remove(record)

    assert recorder.size == 1


def test_pop():

    recorder = create_recorder()

    record = recorder.pop()

    assert record["name"] == "memory"
    assert recorder.size == 1


def test_latest():

    recorder = create_recorder()

    assert recorder.latest()["name"] == "memory"


def test_first():

    recorder = create_recorder()

    assert recorder.first()["name"] == "cpu"


def test_records_list():

    recorder = create_recorder()

    records = recorder.records_list()

    assert isinstance(records, list)
    assert len(records) == 2


def test_clear_records():

    recorder = create_recorder()

    recorder.clear_records()

    assert recorder.size == 0


def test_has_records():

    recorder = create_recorder()

    assert recorder.has_records() is True

    recorder.clear_records()

    assert recorder.has_records() is False


# ==============================================================================
# Part 7. Statistics
# ==============================================================================


def test_record_success():

    recorder = RuntimeRecorder()

    recorder.record_success()

    assert recorder.recorded == 1


def test_record_drop():

    recorder = RuntimeRecorder()

    recorder.record_drop()

    assert recorder.dropped == 1


def test_success_rate():

    recorder = RuntimeRecorder()

    recorder.record_success()
    recorder.record_success()
    recorder.record_drop()

    assert recorder.success_rate == pytest.approx(
        2 / 3
    )


def test_drop_rate():

    recorder = RuntimeRecorder()

    recorder.record_success()
    recorder.record_drop()

    assert recorder.drop_rate == pytest.approx(
        0.5
    )


def test_stats():

    recorder = create_recorder()

    stats = recorder.stats()

    assert stats["recorded"] == recorder.recorded
    assert stats["dropped"] == recorder.dropped


def test_reset_stats():

    recorder = create_recorder()

    recorder.reset_stats()

    assert recorder.recorded == 0
    assert recorder.dropped == 0


# ==============================================================================
# Part 8. Operations
# ==============================================================================


def test_clone():

    recorder = create_recorder()

    clone = recorder.clone()

    assert clone == recorder
    assert clone is not recorder


def test_copy():

    recorder = create_recorder()

    copy = recorder.copy()

    assert copy == recorder
    assert copy is not recorder


def test_merge():

    a = RuntimeRecorder()

    b = create_recorder()

    a.merge(b)

    assert a.size == b.size
    assert a.recorded == b.recorded


def test_update():

    recorder = RuntimeRecorder()

    recorder.update(
        [
            {"a": 1},
            {"b": 2},
        ]
    )

    assert recorder.size == 2


def test_snapshot():

    recorder = create_recorder()

    state = recorder.snapshot()

    assert isinstance(state, dict)


def test_restore():

    recorder = RuntimeRecorder()

    recorder.restore(
        create_recorder().snapshot()
    )

    assert recorder.size == 2
    assert recorder.first()["name"] == "cpu"


# ==============================================================================
# Part 9. Validation
# ==============================================================================


def test_validate_name():

    assert create_recorder().validate_name()


def test_validate_records():

    assert create_recorder().validate_records()


def test_validate_limits():

    assert create_recorder().validate_limits()


def test_validate():

    assert create_recorder().validate()


def test_normalize():

    recorder = RuntimeRecorder(
        name=" recorder "
    )

    recorder.normalize()

    assert recorder.name == "recorder"


# ==============================================================================
# Part 10. Serialization
# ==============================================================================


def test_to_dict():

    data = create_recorder().to_dict()

    assert isinstance(data, dict)


def test_from_dict():

    recorder = RuntimeRecorder.from_dict(
        create_recorder().to_dict()
    )

    assert recorder.size == 2


def test_to_tuple():

    data = create_recorder().to_tuple()

    assert isinstance(data, tuple)


def test_from_tuple():

    recorder = RuntimeRecorder.from_tuple(
        create_recorder().to_tuple()
    )

    assert recorder.size == 2


def test_to_json():

    text = create_recorder().to_json()

    assert isinstance(text, str)

    json.loads(text)


def test_from_json():

    recorder = RuntimeRecorder.from_json(
        create_recorder().to_json()
    )

    assert recorder.size == 2


# ==============================================================================
# Part 11. Diagnostics
# ==============================================================================


def test_summary():

    summary = create_recorder().summary()

    assert summary["name"] == "demo"


def test_diagnostics():

    diagnostics = create_recorder().diagnostics()

    assert diagnostics["valid"] is True


def test_report():

    report = create_recorder().report()

    assert isinstance(report, dict)


def test_status():

    recorder = RuntimeRecorder()

    assert recorder.status() == "idle"

    recorder.start()

    assert recorder.status() == "running"

    recorder.disable()

    assert recorder.status() == "disabled"


# ==============================================================================
# Part 12. Protocols
# ==============================================================================


def test_len():

    assert len(create_recorder()) == 2


def test_contains():

    recorder = create_recorder()

    assert recorder.first() in recorder


def test_iter():

    recorder = create_recorder()

    assert len(list(recorder)) == 2


def test_hash():

    assert isinstance(
        hash(create_recorder()),
        int,
    )


def test_eq():

    assert (
        create_recorder()
        ==
        create_recorder()
    )


def test_repr():

    assert "RuntimeRecorder" in repr(
        create_recorder()
    )


def test_str():

    assert str(create_recorder()) == "demo"


def test_bool():

    assert bool(create_recorder()) is True    