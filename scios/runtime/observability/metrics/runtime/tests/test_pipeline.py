# ==============================================================================
# Part 1. Imports
# ==============================================================================


import copy

import json

import pytest


from scios.runtime.observability.metrics.runtime.pipeline import RuntimePipeline





# ==============================================================================
# Part 2. Helpers
# ==============================================================================


def create_pipeline():


    pipeline = RuntimePipeline()



    pipeline.add(

        {

            "name":

                "stage1",

        }

    )



    pipeline.add(

        {

            "name":

                "stage2",

        }

    )



    pipeline.start()



    return pipeline





# ==============================================================================
# Part 3. Constructor
# ==============================================================================


def test_default_constructor():


    pipeline = RuntimePipeline()



    assert pipeline.name == "runtime"

    assert pipeline.enabled is True

    assert pipeline.running is False

    assert pipeline.stages == []

    assert pipeline.executed == 0

    assert pipeline.failed == 0





def test_custom_constructor():


    pipeline = RuntimePipeline(

        name="custom",

        enabled=False,

        running=True,

    )


    assert pipeline.name == "custom"

    assert pipeline.enabled is False

    assert pipeline.running is True





def test_slots():


    pipeline = RuntimePipeline()



    with pytest.raises(
        AttributeError
    ):

        pipeline.extra = 1





# ==============================================================================
# Part 4. Properties
# ==============================================================================


def test_properties():


    pipeline = create_pipeline()



    assert pipeline.name == "runtime"

    assert pipeline.enabled is True

    assert pipeline.running is True

    assert len(pipeline.stages) == 2





def test_name_property():


    pipeline = RuntimePipeline()



    assert pipeline.name == "runtime"





def test_enabled_property():


    pipeline = RuntimePipeline()



    assert pipeline.enabled is True





def test_running_property():


    pipeline = RuntimePipeline()



    assert pipeline.running is False





def test_stages_property():


    pipeline = create_pipeline()



    stages = pipeline.stages



    assert isinstance(
        stages,
        list,
    )


    assert len(stages) == 2





def test_executed_property():


    pipeline = RuntimePipeline()



    assert pipeline.executed == 0





def test_failed_property():


    pipeline = RuntimePipeline()



    assert pipeline.failed == 0





def test_successes_property():


    pipeline = RuntimePipeline()



    assert pipeline.successes == 0





def test_failures_property():


    pipeline = RuntimePipeline()



    assert pipeline.failures == 0





def test_created_at_property():


    pipeline = RuntimePipeline()



    assert pipeline.created_at is not None





def test_last_run_property():


    pipeline = RuntimePipeline()



    assert pipeline.last_run is None





def test_size_property():


    pipeline = create_pipeline()



    assert pipeline.size == 2





def test_utilization_property():


    pipeline = create_pipeline()



    assert pipeline.utilization == 0.0

# ==============================================================================
# Part 5. Lifecycle
# ==============================================================================


def test_start():

    pipeline = RuntimePipeline()

    result = pipeline.start()

    assert result is pipeline

    assert pipeline.running is True



def test_stop():

    pipeline = create_pipeline()

    result = pipeline.stop()

    assert result is pipeline

    assert pipeline.running is False



def test_enable():

    pipeline = RuntimePipeline()

    pipeline.disable()

    result = pipeline.enable()

    assert result is pipeline

    assert pipeline.enabled is True



def test_disable():

    pipeline = RuntimePipeline()

    result = pipeline.disable()

    assert result is pipeline

    assert pipeline.enabled is False



def test_clear():

    pipeline = create_pipeline()

    pipeline.clear()

    assert pipeline.stage_count == 0

    assert pipeline.executed == 0

    assert pipeline.failed == 0



def test_reset():

    pipeline = create_pipeline()

    pipeline.execute({})

    pipeline.reset()

    assert pipeline.enabled is True

    assert pipeline.running is False

    assert pipeline.stage_count == 0



def test_run():

    pipeline = create_pipeline()

    result = pipeline.run(
        {"value": 1}
    )

    assert result is not None

    assert pipeline.executed >= 1



def test_run_stage():

    pipeline = RuntimePipeline()

    stage = {
        "name": "stage",
        "callback": lambda x: x + 1,
    }


    result = pipeline.run_stage(
        stage,
        1,
    )

    assert result == 2



def test_execute():

    pipeline = create_pipeline()

    result = pipeline.execute(
        {"value": 10}
    )

    assert result is not None

    assert pipeline.executed >= 1



def test_start_stop():

    pipeline = RuntimePipeline()

    pipeline.start()

    assert pipeline.running is True


    pipeline.stop()

    assert pipeline.running is False



# ==============================================================================
# Part 6. Stage API
# ==============================================================================


def test_add():

    pipeline = RuntimePipeline()

    result = pipeline.add(
        {
            "name": "stage1"
        }
    )

    assert result is pipeline

    assert pipeline.stage_count == 1



def test_add_many():

    pipeline = RuntimePipeline()

    pipeline.add_many(
        [
            {"name": "a"},
            {"name": "b"},
        ]
    )

    assert pipeline.stage_count == 2



def test_append():

    pipeline = RuntimePipeline()

    pipeline.append(
        {
            "name": "stage"
        }
    )

    assert pipeline.stage_count == 1



def test_extend():

    pipeline = RuntimePipeline()

    pipeline.extend(
        [
            {"name": "a"},
            {"name": "b"},
        ]
    )

    assert pipeline.stage_count == 2



def test_remove():

    pipeline = create_pipeline()

    pipeline.remove(0)

    assert pipeline.stage_count == 1



def test_pop():

    pipeline = create_pipeline()

    value = pipeline.pop()

    assert value is not None

    assert pipeline.stage_count == 1



def test_latest():

    pipeline = create_pipeline()

    value = pipeline.latest()

    assert value is not None



def test_first():

    pipeline = create_pipeline()

    value = pipeline.first()

    assert value is not None



def test_get():

    pipeline = create_pipeline()

    value = pipeline.get(0)

    assert value is not None



def test_stage_list():

    pipeline = create_pipeline()

    stages = pipeline.stage_list()

    assert isinstance(
        stages,
        list,
    )

    assert len(stages) == 2



def test_clear_stages():

    pipeline = create_pipeline()

    pipeline.clear_stages()

    assert pipeline.stage_count == 0



def test_has_stages():

    pipeline = create_pipeline()

    assert pipeline.has_stages() is True



def test_stage_count():

    pipeline = create_pipeline()

    assert pipeline.stage_count == 2



# ==============================================================================
# Part 7. Statistics
# ==============================================================================


def test_record_success():

    pipeline = RuntimePipeline()

    pipeline.record_success()

    assert pipeline.successes == 1



def test_record_failure():

    pipeline = RuntimePipeline()

    pipeline.record_failure()

    assert pipeline.failures == 1



def test_success_rate():

    pipeline = RuntimePipeline()

    pipeline.record_success()

    assert pipeline.success_rate() == 1



def test_failure_rate():

    pipeline = RuntimePipeline()

    pipeline.record_failure()

    assert pipeline.failure_rate() == 1



def test_total_processed():

    pipeline = RuntimePipeline()

    pipeline.record_success()

    pipeline.record_failure()

    assert pipeline.total_processed() == 2



def test_statistics():

    pipeline = RuntimePipeline()

    pipeline.record_success()

    stats = pipeline.statistics()

    assert stats["successes"] == 1



def test_reset_statistics():

    pipeline = RuntimePipeline()

    pipeline.record_success()

    pipeline.reset_statistics()

    assert pipeline.successes == 0

    assert pipeline.failures == 0



# ==============================================================================
# Part 8. Operations
# ==============================================================================


def test_clone():

    pipeline = create_pipeline()

    clone = pipeline.clone()

    assert clone is not pipeline

    assert clone == pipeline



def test_copy():

    pipeline = create_pipeline()

    copied = pipeline.copy()

    assert copied is not pipeline

    assert copied == pipeline



def test_merge():

    pipeline1 = create_pipeline()

    pipeline2 = RuntimePipeline()

    pipeline2.add(
        {
            "name": "stage3"
        }
    )


    result = pipeline1.merge(
        pipeline2
    )


    assert result is pipeline1

    assert pipeline1.stage_count == 3



def test_update():

    pipeline = RuntimePipeline()

    result = pipeline.update(
        {
            "name": "updated"
        }
    )

    assert result is pipeline

    assert pipeline.name == "updated"



def test_snapshot():

    pipeline = create_pipeline()

    snapshot = pipeline.snapshot()

    assert snapshot is not None

    assert isinstance(
        snapshot,
        dict,
    )



def test_restore():

    pipeline = create_pipeline()

    snapshot = pipeline.snapshot()


    pipeline.clear()


    pipeline.restore(
        snapshot
    )


    assert pipeline.stage_count == 2

# ==============================================================================
# Part 9. Validation
# ==============================================================================


def test_validate_name():

    pipeline = RuntimePipeline()

    assert pipeline.validate_name() is True

    assert pipeline.validate_name(
        ""
    ) is False



def test_validate_stages():

    pipeline = RuntimePipeline()

    assert pipeline.validate_stages() is True


    pipeline._stages = "invalid"


    assert pipeline.validate_stages() is False



def test_validate():

    pipeline = create_pipeline()

    assert pipeline.validate() is True



def test_normalize():

    pipeline = RuntimePipeline()


    result = pipeline.normalize(
        {
            "name": "stage"
        }
    )


    assert result == {
        "name": "stage"
    }


    result = pipeline.normalize(
        lambda: None
    )


    assert "callback" in result





# ==============================================================================
# Part 10. Serialization
# ==============================================================================


def test_to_dict():

    pipeline = create_pipeline()


    value = pipeline.to_dict()


    assert isinstance(
        value,
        dict,
    )


    assert value["name"] == "runtime"

    assert len(value["stages"]) == 2




def test_from_dict():

    pipeline = create_pipeline()


    data = pipeline.to_dict()


    restored = RuntimePipeline.from_dict(
        data
    )


    assert restored.name == pipeline.name

    assert restored.stage_count == 2




def test_to_tuple():

    pipeline = create_pipeline()


    value = pipeline.to_tuple()


    assert isinstance(
        value,
        tuple,
    )


    assert value[0] == "runtime"




def test_from_tuple():

    pipeline = create_pipeline()


    data = pipeline.to_tuple()


    restored = RuntimePipeline.from_tuple(
        data
    )


    assert restored.name == pipeline.name

    assert restored.stage_count == 2




def test_to_json():

    pipeline = create_pipeline()


    value = pipeline.to_json()


    assert isinstance(
        value,
        str,
    )


    data = json.loads(value)


    assert data["name"] == "runtime"




def test_from_json():

    pipeline = create_pipeline()


    value = pipeline.to_json()


    restored = RuntimePipeline.from_json(
        value
    )


    assert restored.name == pipeline.name

    assert restored.stage_count == 2





# ==============================================================================
# Part 11. Diagnostics
# ==============================================================================


def test_summary():

    pipeline = create_pipeline()


    value = pipeline.summary()


    assert isinstance(
        value,
        dict,
    )


    assert value["name"] == "runtime"




def test_diagnostics():

    pipeline = create_pipeline()


    value = pipeline.diagnostics()


    assert isinstance(
        value,
        dict,
    )


    assert "summary" in value




def test_report():

    pipeline = create_pipeline()


    value = pipeline.report()


    assert isinstance(
        value,
        dict,
    )


    assert "pipeline" in value




def test_status():

    pipeline = RuntimePipeline()


    assert pipeline.status() in (

        "idle",

        "ready",

        "running",

        "disabled",

    )





# ==============================================================================
# Part 12. Protocols
# ==============================================================================


def test_len():

    pipeline = create_pipeline()


    assert len(pipeline) == 2




def test_contains():

    pipeline = create_pipeline()


    stage = pipeline.first()


    assert stage in pipeline




def test_iter():

    pipeline = create_pipeline()


    values = list(
        iter(pipeline)
    )


    assert len(values) == 2




def test_hash():

    pipeline = RuntimePipeline()


    value = hash(
        pipeline
    )


    assert isinstance(
        value,
        int,
    )




def test_eq():

    pipeline1 = RuntimePipeline()

    pipeline2 = RuntimePipeline()


    assert pipeline1 == pipeline2




def test_repr():

    pipeline = RuntimePipeline()


    value = repr(
        pipeline
    )


    assert "RuntimePipeline" in value




def test_str():

    pipeline = RuntimePipeline()


    value = str(
        pipeline
    )


    assert isinstance(
        value,
        str,
    )




def test_bool():

    pipeline = RuntimePipeline()


    assert bool(
        pipeline
    ) is True


    pipeline._enabled = False


    assert bool(
        pipeline
    ) is False        