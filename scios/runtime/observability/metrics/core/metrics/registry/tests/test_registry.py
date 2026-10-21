"""
MetricRegistry tests.

Python 3.11+
"""


from __future__ import annotations


import inspect


from ..registry import MetricRegistry
from ..index import MetricIndex
from ..key import MetricKey



# ==============================================================================
# Part 1. Constructor
# ==============================================================================


def test_default_constructor():

    registry = MetricRegistry()

    assert registry.name == ""

    assert registry.namespace == ""

    assert isinstance(
        registry.index,
        MetricIndex,
    )

    assert isinstance(
        registry.metrics,
        dict,
    )

    assert isinstance(
        registry.state,
        dict,
    )



def test_custom_constructor():

    index = MetricIndex(
        "cpu",
        "system",
    )

    registry = MetricRegistry(
        "runtime",
        "metrics",
        index,
    )

    assert registry.name == "runtime"

    assert registry.namespace == "metrics"

    assert registry.index == index



def test_slots():

    assert hasattr(
        MetricRegistry,
        "__slots__",
    )



def test_annotations():

    annotations = (
        MetricRegistry
        .__annotations__
    )

    assert "name" in annotations

    assert "namespace" in annotations

    assert "index" in annotations

    assert "metrics" in annotations

    assert "state" in annotations



def test_signature():

    signature = inspect.signature(
        MetricRegistry
    )

    params = list(
        signature.parameters
    )

    assert params == [

        "name",

        "namespace",

        "index",

        "metrics",

        "state",

    ]



# ==============================================================================
# Part 2. Properties
# ==============================================================================


def test_name_property():

    registry = MetricRegistry()

    assert registry.name == ""



def test_namespace_property():

    registry = MetricRegistry()

    assert registry.namespace == ""



def test_index_property():

    registry = MetricRegistry()

    assert isinstance(
        registry.index,
        MetricIndex,
    )



def test_metrics_property():

    registry = MetricRegistry()

    assert isinstance(
        registry.metrics,
        dict,
    )



def test_size_property():

    registry = MetricRegistry()

    assert registry.size == 0



def test_state_property():

    registry = MetricRegistry()

    assert isinstance(
        registry.state,
        dict,
    )



# ==============================================================================
# Part 3. Operations
# ==============================================================================


def test_register():

    registry = MetricRegistry()

    key = MetricKey(
        "cpu"
    )

    registry.register(
        key
    )

    assert registry.size == 1

    assert registry.contains(
        key
    )



def test_unregister():

    registry = MetricRegistry()

    key = MetricKey(
        "cpu"
    )

    registry.register(
        key
    )

    registry.unregister(
        key
    )

    assert registry.size == 0



def test_get():

    registry = MetricRegistry()

    key = MetricKey(
        "cpu"
    )

    registry.register(
        key
    )

    result = registry.get(
        key.fullname
    )

    assert result == key



def test_contains():

    registry = MetricRegistry()

    key = MetricKey(
        "cpu"
    )

    registry.register(
        key
    )

    assert registry.contains(
        key
    )



def test_clear():

    registry = MetricRegistry()

    registry.register(
        MetricKey(
            "cpu"
        )
    )

    registry.clear()

    assert registry.size == 0



def test_list():

    registry = MetricRegistry()

    key = MetricKey(
        "cpu"
    )

    registry.register(
        key
    )

    values = registry.list()

    assert isinstance(
        values,
        list,
    )

    assert values[0] == key



def test_normalize():

    registry = MetricRegistry(

        " CPU ",

        " SYSTEM ",

    )

    registry.normalize()

    assert registry.name == "cpu"

    assert registry.namespace == "system"



# ==============================================================================
# Part 4. Serialization
# ==============================================================================


def test_to_dict():

    registry = MetricRegistry(
        "cpu",
        "system",
    )

    data = registry.to_dict()

    assert data["name"] == "cpu"

    assert data["namespace"] == "system"

    assert "metrics" in data

    assert "index" in data



def test_from_dict():

    data = {

        "name":
            "cpu",

        "namespace":
            "system",

        "index":
            MetricIndex().to_dict(),

        "metrics":
            {},

        "state":
            {},

    }


    registry = MetricRegistry.from_dict(
        data
    )

    assert registry.name == "cpu"

    assert registry.namespace == "system"



def test_to_tuple():

    registry = MetricRegistry(
        "cpu"
    )

    value = registry.to_tuple()

    assert isinstance(
        value,
        tuple,
    )



def test_from_tuple():

    registry = MetricRegistry(
        "cpu"
    )

    restored = MetricRegistry.from_tuple(
        registry.to_tuple()
    )

    assert restored == registry



def test_snapshot():

    registry = MetricRegistry(
        "cpu"
    )

    snap = registry.snapshot()

    assert isinstance(
        snap,
        dict,
    )



def test_restore():

    registry = MetricRegistry()

    registry.restore(

        {

            "name":
                "memory",

            "namespace":
                "runtime",

            "index":
                MetricIndex().to_dict(),

            "metrics":
                {},

            "state":
                {},

        }

    )


    assert registry.name == "memory"

    assert registry.namespace == "runtime"



# ==============================================================================
# Part 5. Validation
# ==============================================================================


def test_validate_name():

    assert MetricRegistry.validate_name(
        "cpu"
    )



def test_validate_namespace():

    assert MetricRegistry.validate_namespace(
        "system"
    )



def test_validate_index():

    assert MetricRegistry.validate_index(
        MetricIndex()
    )



def test_validate_metrics():

    assert MetricRegistry.validate_metrics(
        {}
    )



def test_validate_registry():

    registry = MetricRegistry(
        "cpu"
    )

    assert MetricRegistry.validate_registry(
        registry
    )



def test_validate():

    registry = MetricRegistry(
        "cpu"
    )

    assert registry.validate()

# ==============================================================================
# Part 6. Utilities
# ==============================================================================


def test_clone():

    registry = MetricRegistry(
        "cpu",
        "system",
    )

    registry.register(
        MetricKey("load")
    )

    clone = registry.clone()

    assert clone == registry

    assert clone is not registry



def test_copy():

    registry = MetricRegistry(
        "cpu"
    )

    copied = registry.copy()

    assert copied == registry

    assert copied is not registry



def test_merge():

    registry_a = MetricRegistry(
        "a"
    )

    registry_b = MetricRegistry(
        "b"
    )


    key = MetricKey(
        "cpu"
    )


    registry_b.register(
        key
    )


    registry_a.merge(
        registry_b
    )


    assert registry_a.contains(
        key
    )



def test_update():

    registry = MetricRegistry()


    registry.update(

        {

            "cpu":
                MetricKey(
                    "cpu"
                )

        }

    )


    assert registry.size == 1



def test_reset():

    registry = MetricRegistry()

    registry.register(
        MetricKey(
            "cpu"
        )
    )


    registry.state["x"] = 1


    registry.reset()


    assert registry.size == 0

    assert registry.state == {}



# ==============================================================================
# Part 7. Protocols
# ==============================================================================


def test_hash():

    registry = MetricRegistry(
        "cpu"
    )

    value = hash(
        registry
    )

    assert isinstance(
        value,
        int,
    )



def test_eq():

    a = MetricRegistry(
        "cpu",
        "system",
    )

    b = MetricRegistry(
        "cpu",
        "system",
    )


    assert a == b



def test_repr():

    registry = MetricRegistry(
        "cpu"
    )


    value = repr(
        registry
    )


    assert "MetricRegistry" in value



def test_str():

    registry = MetricRegistry(
        "cpu",
        "system",
    )


    value = str(
        registry
    )


    assert "cpu" in value

    assert "system" in value



def test_bool():

    empty = MetricRegistry()


    assert not bool(
        empty
    )


    filled = MetricRegistry()


    filled.register(
        MetricKey(
            "cpu"
        )
    )


    assert bool(
        filled
    )



# ==============================================================================
# Part 8. Diagnostics
# ==============================================================================


def test_summary():

    registry = MetricRegistry(
        "cpu"
    )


    result = registry.summary()


    assert isinstance(
        result,
        dict,
    )


    assert "name" in result

    assert "size" in result



def test_diagnostics():

    registry = MetricRegistry(
        "cpu"
    )


    result = registry.diagnostics()


    assert isinstance(
        result,
        dict,
    )


    assert "summary" in result

    assert "metrics" in result



def test_registry_report():

    registry = MetricRegistry(
        "cpu"
    )


    result = registry.registry_report()


    assert isinstance(
        result,
        dict,
    )


    assert "registry" in result

    assert "metric_count" in result



def test_overall_status():

    registry = MetricRegistry(
        "cpu"
    )


    status = registry.overall_status()


    assert status in (

        "healthy",

        "invalid",

    )



# ==============================================================================
# Part 9. Public API
# ==============================================================================


def test_public_api():

    from .. import registry


    assert hasattr(
        registry,
        "__all__",
    )


    assert (
        "MetricRegistry"
        in registry.__all__
    )    