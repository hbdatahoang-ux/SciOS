"""
Runtime Metrics Public API Tests
================================

Tests public exports and constants.

Python 3.11+
"""


# ==============================================================================
# Part 1. Imports
# ==============================================================================


import pytest


from scios.runtime.observability.metrics.runtime import (
    RuntimeScheduler,
    RuntimePipeline,

    DEFAULT_NAME,
    DEFAULT_ENABLED,
    DEFAULT_RUNNING,
    DEFAULT_INTERVAL,
    DEFAULT_MAX_TICKS,

    __version__,
    __all__,
)


# ==============================================================================
# Part 2. Package Export
# ==============================================================================


def test_runtime_package_import():

    assert RuntimeScheduler is not None

    assert RuntimePipeline is not None



def test_scheduler_export():

    assert "RuntimeScheduler" in __all__



def test_pipeline_export():

    assert "RuntimePipeline" in __all__



def test_all_defined():

    assert isinstance(
        __all__,
        list,
    )

    assert len(__all__) > 0



# ==============================================================================
# Part 3. Constants API
# ==============================================================================


def test_default_name():

    assert DEFAULT_NAME is not None

    assert isinstance(
        DEFAULT_NAME,
        str,
    )



def test_default_enabled():

    assert isinstance(
        DEFAULT_ENABLED,
        bool,
    )



def test_default_running():

    assert isinstance(
        DEFAULT_RUNNING,
        bool,
    )



def test_default_interval():

    assert isinstance(
        DEFAULT_INTERVAL,
        (int, float),
    )



    assert DEFAULT_INTERVAL > 0



def test_default_max_ticks():

    assert isinstance(
        DEFAULT_MAX_TICKS,
        int,
    )



    assert DEFAULT_MAX_TICKS > 0



def test_constants_types():

    assert isinstance(
        DEFAULT_NAME,
        str,
    )


    assert isinstance(
        DEFAULT_ENABLED,
        bool,
    )


    assert isinstance(
        DEFAULT_RUNNING,
        bool,
    )


    assert isinstance(
        DEFAULT_INTERVAL,
        (int, float),
    )


    assert isinstance(
        DEFAULT_MAX_TICKS,
        int,
    )

# ==============================================================================
# Part 4. Scheduler Public API
# ==============================================================================


def test_scheduler_constructible():

    scheduler = RuntimeScheduler()

    assert isinstance(
        scheduler,
        RuntimeScheduler,
    )



def test_scheduler_methods():

    scheduler = RuntimeScheduler()


    required_methods = [

        "start",

        "stop",

        "enable",

        "disable",

        "tick",

        "run_once",

        "run_forever",

        "add",

        "add_many",

        "append",

        "extend",

        "remove",

        "pop",

        "clear",

        "reset",

        "snapshot",

        "restore",

        "to_dict",

        "from_dict",

        "to_tuple",

        "from_tuple",

        "to_json",

        "from_json",

    ]


    for method in required_methods:

        assert hasattr(
            scheduler,
            method,
        )

        assert callable(
            getattr(
                scheduler,
                method,
            )
        )



def test_scheduler_properties():

    scheduler = RuntimeScheduler()


    required_properties = [

        "name",

        "enabled",

        "running",

        "interval",

        "max_ticks",

        "tasks",

        "ticks",

        "executed",

        "failed",

        "successes",

        "failures",

        "created_at",

        "last_tick",

        "size",

        "utilization",

    ]


    for prop in required_properties:

        assert hasattr(
            scheduler,
            prop,
        )



def test_scheduler_serialization():

    scheduler = RuntimeScheduler()


    data = scheduler.to_dict()


    assert isinstance(
        data,
        dict,
    )


    restored = RuntimeScheduler.from_dict(
        data
    )


    assert isinstance(
        restored,
        RuntimeScheduler,
    )


    assert restored.name == scheduler.name



# ==============================================================================
# Part 5. Pipeline Public API
# ==============================================================================


def test_pipeline_constructible():

    pipeline = RuntimePipeline()

    assert isinstance(
        pipeline,
        RuntimePipeline,
    )



def test_pipeline_methods():

    pipeline = RuntimePipeline()


    required_methods = [

        "start",

        "stop",

        "enable",

        "disable",

        "run",

        "run_stage",

        "execute",

        "add",

        "add_many",

        "append",

        "extend",

        "remove",

        "pop",

        "clear",

        "reset",

        "snapshot",

        "restore",

        "to_dict",

        "from_dict",

        "to_tuple",

        "from_tuple",

        "to_json",

        "from_json",

    ]


    for method in required_methods:

        assert hasattr(
            pipeline,
            method,
        )

        assert callable(
            getattr(
                pipeline,
                method,
            )
        )



def test_pipeline_properties():

    pipeline = RuntimePipeline()


    required_properties = [

        "name",

        "enabled",

        "running",

        "stages",

        "executed",

        "failed",

        "successes",

        "failures",

        "created_at",

        "last_run",

        "size",

        "utilization",

    ]


    for prop in required_properties:

        assert hasattr(
            pipeline,
            prop,
        )



def test_pipeline_serialization():

    pipeline = RuntimePipeline()


    data = pipeline.to_dict()


    assert isinstance(
        data,
        dict,
    )


    restored = RuntimePipeline.from_dict(
        data
    )


    assert isinstance(
        restored,
        RuntimePipeline,
    )


    assert restored.name == pipeline.name



# ==============================================================================
# Part 6. Cross Runtime Compatibility
# ==============================================================================


def test_scheduler_pipeline_independent():

    scheduler = RuntimeScheduler()

    pipeline = RuntimePipeline()


    assert scheduler is not pipeline

    assert type(scheduler) is not type(pipeline)



def test_scheduler_pipeline_hashable():

    scheduler = RuntimeScheduler()

    pipeline = RuntimePipeline()


    assert isinstance(
        hash(scheduler),
        int,
    )


    assert isinstance(
        hash(pipeline),
        int,
    )



def test_scheduler_pipeline_repr():

    scheduler = RuntimeScheduler()

    pipeline = RuntimePipeline()


    scheduler_repr = repr(
        scheduler
    )

    pipeline_repr = repr(
        pipeline
    )


    assert "RuntimeScheduler" in scheduler_repr

    assert "RuntimePipeline" in pipeline_repr



# ==============================================================================
# Part 7. Version/API Stability
# ==============================================================================


def test_version_exists():

    assert isinstance(
        __version__,
        str,
    )

    assert len(
        __version__
    ) > 0



def test_public_symbols_stable():

    required_symbols = [

        "RuntimeScheduler",

        "RuntimePipeline",

        "DEFAULT_NAME",

        "DEFAULT_ENABLED",

        "DEFAULT_RUNNING",

        "DEFAULT_INTERVAL",

        "DEFAULT_MAX_TICKS",

    ]


    for symbol in required_symbols:

        assert symbol in __all__    