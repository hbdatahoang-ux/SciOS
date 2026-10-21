# ==============================================================================
# Part 1. Imports
# ==============================================================================


import copy

import json

import pytest


from scios.runtime.observability.metrics.runtime.scheduler import (
    RuntimeScheduler,
)



# ==============================================================================
# Part 2. Helpers
# ==============================================================================


def create_scheduler():

    scheduler = RuntimeScheduler()


    scheduler.add(
        {
            "name": "task1",
            "callback": lambda: None,
        }
    )


    scheduler.add(
        {
            "name": "task2",
            "callback": lambda: None,
        }
    )


    scheduler.start()


    return scheduler





# ==============================================================================
# Part 3. Constructor
# ==============================================================================


def test_default_constructor():


    scheduler = RuntimeScheduler()


    assert scheduler.name == "runtime"

    assert scheduler.enabled is True

    assert scheduler.running is False

    assert scheduler.interval > 0

    assert scheduler.max_ticks > 0

    assert scheduler.size == 0



def test_custom_constructor():


    scheduler = RuntimeScheduler(

        name="custom",

        enabled=False,

        running=True,

        interval=2.0,

        max_ticks=100,

    )


    assert scheduler.name == "custom"

    assert scheduler.enabled is False

    assert scheduler.running is True

    assert scheduler.interval == 2.0

    assert scheduler.max_ticks == 100



def test_slots():


    scheduler = RuntimeScheduler()


    assert hasattr(
        scheduler,
        "_name",
    )


    assert hasattr(
        scheduler,
        "_tasks",
    )


    assert hasattr(
        scheduler,
        "_thread",
    )





# ==============================================================================
# Part 4. Properties
# ==============================================================================


def test_properties():


    scheduler = create_scheduler()


    assert scheduler.name == "runtime"

    assert scheduler.enabled is True

    assert scheduler.running is True

    assert scheduler.interval > 0

    assert scheduler.max_ticks > 0

    assert scheduler.size == 2

    assert scheduler.ticks >= 0

    assert scheduler.executed >= 0

    assert scheduler.failed >= 0





def test_name_property():


    scheduler = RuntimeScheduler(
        name="abc"
    )


    assert scheduler.name == "abc"





def test_enabled_property():


    scheduler = RuntimeScheduler()


    assert scheduler.enabled is True


    scheduler.disable()


    assert scheduler.enabled is False





def test_running_property():


    scheduler = RuntimeScheduler()


    assert scheduler.running is False


    scheduler.start()


    assert scheduler.running is True





def test_interval_property():


    scheduler = RuntimeScheduler(
        interval=5.0
    )


    assert scheduler.interval == 5.0





def test_max_ticks_property():


    scheduler = RuntimeScheduler(
        max_ticks=50
    )


    assert scheduler.max_ticks == 50





def test_tasks_property():


    scheduler = create_scheduler()


    assert isinstance(
        scheduler.tasks,
        list,
    )


    assert len(
        scheduler.tasks
    ) == 2





def test_ticks_property():


    scheduler = RuntimeScheduler()


    assert scheduler.ticks == 0





def test_executed_property():


    scheduler = RuntimeScheduler()


    assert scheduler.executed == 0





def test_failed_property():


    scheduler = RuntimeScheduler()


    assert scheduler.failed == 0





def test_successes_property():


    scheduler = RuntimeScheduler()


    assert scheduler.successes == 0





def test_failures_property():


    scheduler = RuntimeScheduler()


    assert scheduler.failures == 0





def test_created_at_property():


    scheduler = RuntimeScheduler()


    assert scheduler.created_at > 0





def test_last_tick_property():


    scheduler = RuntimeScheduler()


    assert scheduler.last_tick is None





def test_size_property():


    scheduler = create_scheduler()


    assert scheduler.size == 2





def test_utilization_property():


    scheduler = RuntimeScheduler(
        max_ticks=10
    )


    scheduler.add(
        {
            "name": "task",
        }
    )


    assert scheduler.utilization >= 0

# ==============================================================================
# Part 5. Lifecycle
# ==============================================================================


def test_start():

    scheduler = RuntimeScheduler()

    result = scheduler.start()

    assert result is scheduler

    assert scheduler.running is True



def test_stop():

    scheduler = RuntimeScheduler()

    scheduler.start()

    result = scheduler.stop()

    assert result is scheduler

    assert scheduler.running is False



def test_enable():

    scheduler = RuntimeScheduler(
        enabled=False
    )

    result = scheduler.enable()

    assert result is scheduler

    assert scheduler.enabled is True



def test_disable():

    scheduler = RuntimeScheduler()

    result = scheduler.disable()

    assert result is scheduler

    assert scheduler.enabled is False



def test_clear():

    scheduler = create_scheduler()

    scheduler.clear()

    assert scheduler.size == 0

    assert scheduler.ticks == 0

    assert scheduler.executed == 0

    assert scheduler.failed == 0



def test_reset():

    scheduler = create_scheduler()

    scheduler.tick()

    scheduler.reset()

    assert scheduler.enabled is True

    assert scheduler.running is False

    assert scheduler.size == 0

    assert scheduler.ticks == 0



def test_tick():

    scheduler = create_scheduler()

    result = scheduler.tick()

    assert result is True

    assert scheduler.ticks == 1



def test_run_once():

    scheduler = create_scheduler()

    result = scheduler.run_once()

    assert result is not None

    assert scheduler.ticks >= 1



def test_run_forever():

    scheduler = RuntimeScheduler(
        interval=0.001,
        max_ticks=2,
    )


    scheduler.add(
        {
            "name": "task",
            "callback": lambda: None,
        }
    )


    scheduler.run_forever()


    assert scheduler.ticks >= 0



def test_disabled_tick():

    scheduler = RuntimeScheduler()

    scheduler.disable()

    result = scheduler.tick()

    assert result is False



def test_start_stop():

    scheduler = RuntimeScheduler()


    scheduler.start()

    assert scheduler.running is True


    scheduler.stop()

    assert scheduler.running is False





# ==============================================================================
# Part 6. Task API
# ==============================================================================


def test_add():

    scheduler = RuntimeScheduler()

    result = scheduler.add(
        {
            "name": "task1"
        }
    )


    assert result is True

    assert scheduler.size == 1



def test_add_many():

    scheduler = RuntimeScheduler()


    result = scheduler.add_many(
        [
            {
                "name": "a"
            },
            {
                "name": "b"
            },
        ]
    )


    assert result is True

    assert scheduler.size == 2



def test_append():

    scheduler = RuntimeScheduler()


    assert scheduler.append(
        {
            "name": "task"
        }
    )


    assert scheduler.size == 1



def test_extend():

    scheduler = RuntimeScheduler()


    scheduler.extend(
        [
            {
                "name": "a"
            },
            {
                "name": "b"
            },
        ]
    )


    assert scheduler.size == 2



def test_remove():

    scheduler = create_scheduler()


    item = scheduler.first()


    result = scheduler.remove(item)


    assert result is True

    assert scheduler.size == 1



def test_pop():

    scheduler = create_scheduler()


    item = scheduler.pop()


    assert item is not None

    assert scheduler.size == 1



def test_latest():

    scheduler = create_scheduler()


    assert scheduler.latest() is not None



def test_first():

    scheduler = create_scheduler()


    assert scheduler.first() is not None



def test_get():

    scheduler = create_scheduler()


    result = scheduler.get(0)


    assert result is not None



def test_task_list():

    scheduler = create_scheduler()


    tasks = scheduler.task_list()


    assert isinstance(
        tasks,
        list,
    )


    assert len(tasks) == 2



def test_clear_tasks():

    scheduler = create_scheduler()


    scheduler.clear_tasks()


    assert scheduler.size == 0



def test_has_tasks():

    scheduler = create_scheduler()


    assert scheduler.has_tasks() is True



def test_task_count():

    scheduler = create_scheduler()


    assert scheduler.task_count() == 2





# ==============================================================================
# Part 7. Statistics
# ==============================================================================


def test_record_success():

    scheduler = RuntimeScheduler()


    scheduler.record_success()


    assert scheduler.executed == 1

    assert scheduler.successes == 1



def test_record_failure():

    scheduler = RuntimeScheduler()


    scheduler.record_failure()


    assert scheduler.failed == 1

    assert scheduler.failures == 1



def test_success_rate():

    scheduler = RuntimeScheduler()


    scheduler.record_success()

    scheduler.record_failure()


    assert scheduler.success_rate() == 0.5



def test_failure_rate():

    scheduler = RuntimeScheduler()


    scheduler.record_success()

    scheduler.record_failure()


    assert scheduler.failure_rate() == 0.5



def test_total_processed():

    scheduler = RuntimeScheduler()


    scheduler.record_success()

    scheduler.record_failure()


    assert scheduler.total_processed() == 2



def test_statistics():

    scheduler = RuntimeScheduler()


    scheduler.record_success()


    stats = scheduler.statistics()


    assert stats["executed"] == 1

    assert stats["failed"] == 0



def test_reset_statistics():

    scheduler = RuntimeScheduler()


    scheduler.record_success()

    scheduler.record_failure()


    scheduler.reset_statistics()


    assert scheduler.executed == 0

    assert scheduler.failed == 0





# ==============================================================================
# Part 8. Operations
# ==============================================================================


def test_clone():

    scheduler = create_scheduler()


    cloned = scheduler.clone()


    assert cloned == scheduler

    assert cloned is not scheduler



def test_copy():

    scheduler = create_scheduler()


    copied = scheduler.copy()


    assert copied == scheduler

    assert copied is not scheduler



def test_merge():

    a = RuntimeScheduler()

    b = RuntimeScheduler()


    a.add(
        {
            "name": "a"
        }
    )

    b.add(
        {
            "name": "b"
        }
    )


    a.merge(b)


    assert a.size == 2



def test_update():

    scheduler = RuntimeScheduler()


    scheduler.update(
        {
            "name": "task"
        }
    )


    assert scheduler.size == 1



def test_snapshot():

    scheduler = create_scheduler()


    snapshot = scheduler.snapshot()


    assert isinstance(
        snapshot,
        dict,
    )


    assert snapshot["name"] == scheduler.name



def test_restore():

    scheduler = create_scheduler()


    snapshot = scheduler.snapshot()


    restored = RuntimeScheduler()

    restored.restore(snapshot)


    assert restored == scheduler

# ==============================================================================
# Part 9. Validation
# ==============================================================================


def test_validate_name():

    scheduler = RuntimeScheduler(
        name="runtime"
    )


    assert scheduler.validate_name() is True


    assert scheduler.validate_name(
        ""
    ) is False



def test_validate_tasks():

    scheduler = RuntimeScheduler()


    assert scheduler.validate_tasks() is True


    scheduler._tasks = "invalid"


    assert scheduler.validate_tasks() is False



def test_validate_limits():

    scheduler = RuntimeScheduler(
        interval=1.0,
        max_ticks=10,
    )


    assert scheduler.validate_limits() is True



def test_validate():

    scheduler = create_scheduler()


    assert scheduler.validate() is True



def test_normalize():

    scheduler = RuntimeScheduler()


    value = scheduler.normalize(
        {
            "name": "task"
        }
    )


    assert isinstance(
        value,
        dict,
    )


    assert value["name"] == "task"



def test_validate_empty():

    scheduler = RuntimeScheduler()


    assert scheduler.validate() is True





# ==============================================================================
# Part 10. Serialization
# ==============================================================================


def test_to_dict():

    scheduler = create_scheduler()


    data = scheduler.to_dict()


    assert isinstance(
        data,
        dict,
    )


    assert data["name"] == scheduler.name


    assert "tasks" in data



def test_from_dict():

    scheduler = create_scheduler()


    data = scheduler.to_dict()


    restored = RuntimeScheduler.from_dict(
        data
    )


    assert restored == scheduler



def test_to_tuple():

    scheduler = create_scheduler()


    value = scheduler.to_tuple()


    assert isinstance(
        value,
        tuple,
    )


    assert value[0] == scheduler.name



def test_from_tuple():

    scheduler = create_scheduler()


    value = scheduler.to_tuple()


    restored = RuntimeScheduler.from_tuple(
        value
    )


    assert restored == scheduler



def test_to_json():

    scheduler = create_scheduler()


    value = scheduler.to_json()


    assert isinstance(
        value,
        str,
    )


    data = json.loads(
        value
    )


    assert data["name"] == scheduler.name



def test_from_json():

    scheduler = create_scheduler()


    value = scheduler.to_json()


    restored = RuntimeScheduler.from_json(
        value
    )


    assert restored == scheduler





# ==============================================================================
# Part 11. Diagnostics
# ==============================================================================


def test_summary():

    scheduler = create_scheduler()


    result = scheduler.summary()


    assert isinstance(
        result,
        dict,
    )


    assert result["name"] == scheduler.name



def test_diagnostics():

    scheduler = create_scheduler()


    result = scheduler.diagnostics()


    assert isinstance(
        result,
        dict,
    )


    assert "status" in result



def test_report():

    scheduler = create_scheduler()


    result = scheduler.report()


    assert isinstance(
        result,
        dict,
    )


    assert "summary" in result

    assert "diagnostics" in result



def test_status():

    scheduler = RuntimeScheduler()


    assert scheduler.status() == "enabled"


    scheduler.disable()


    assert scheduler.status() == "disabled"


    scheduler.enable()

    scheduler.start()


    assert scheduler.status() == "running"





# ==============================================================================
# Part 12. Protocols
# ==============================================================================


def test_len():

    scheduler = create_scheduler()


    assert len(
        scheduler
    ) == 2



def test_contains():

    scheduler = create_scheduler()


    task = scheduler.first()


    assert task in scheduler



def test_iter():

    scheduler = create_scheduler()


    items = list(
        iter(scheduler)
    )


    assert len(items) == 2



def test_hash():

    scheduler = RuntimeScheduler()


    value = hash(
        scheduler
    )


    assert isinstance(
        value,
        int,
    )



def test_eq():

    a = RuntimeScheduler()

    b = RuntimeScheduler()


    assert a == b



def test_repr():

    scheduler = RuntimeScheduler()


    value = repr(
        scheduler
    )


    assert "RuntimeScheduler" in value



def test_str():

    scheduler = RuntimeScheduler()


    value = str(
        scheduler
    )


    assert scheduler.name in value



def test_bool():

    scheduler = RuntimeScheduler()


    assert bool(
        scheduler
    ) is True


    scheduler._max_ticks = 0


    assert bool(
        scheduler
    ) is False        