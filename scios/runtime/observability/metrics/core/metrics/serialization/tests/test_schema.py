"""
Schema tests.

Python 3.11+
"""

from __future__ import annotations


import copy
import inspect


from ..schema import (
    Schema,
    DEFAULT_SCHEMA_NAME,
    DEFAULT_VERSION,
    DEFAULT_STRICT,
    DEFAULT_ALLOW_EXTRA,
)



# ==============================================================================
# Part 1. Constructor
# ==============================================================================


def test_default_constructor():

    schema = Schema()

    assert schema.name == DEFAULT_SCHEMA_NAME
    assert schema.version == DEFAULT_VERSION
    assert schema.strict == DEFAULT_STRICT
    assert schema.allow_extra == DEFAULT_ALLOW_EXTRA
    assert schema.fields == {}



def test_custom_constructor():

    schema = Schema(
        name="metric",
        version="2.0",
        strict=False,
        allow_extra=True,
        fields={
            "value": {
                "type": int,
            }
        },
    )


    assert schema.name == "metric"
    assert schema.version == "2.0"
    assert schema.strict is False
    assert schema.allow_extra is True
    assert "value" in schema.fields



def test_slots():

    assert hasattr(
        Schema,
        "__slots__",
    )



def test_annotations():

    assert hasattr(
        Schema,
        "__annotations__",
    )



def test_signature():

    signature = inspect.signature(
        Schema
    )

    assert "name" in signature.parameters
    assert "version" in signature.parameters
    assert "strict" in signature.parameters
    assert "allow_extra" in signature.parameters
    assert "fields" in signature.parameters



# ==============================================================================
# Part 2. Properties
# ==============================================================================


def test_name_property():

    schema = Schema(
        name="test"
    )

    assert schema.name == "test"



def test_version_property():

    schema = Schema(
        version="3.0"
    )

    assert schema.version == "3.0"



def test_strict_property():

    schema = Schema(
        strict=False
    )

    assert schema.strict is False



def test_allow_extra_property():

    schema = Schema(
        allow_extra=True
    )

    assert schema.allow_extra is True



def test_fields_property():

    schema = Schema(
        fields={
            "x": {
                "type": int
            }
        }
    )

    fields = schema.fields

    assert "x" in fields
    assert fields["x"]["type"] is int



def test_size_property():

    schema = Schema(
        fields={
            "a": {
                "type": int
            },
            "b": {
                "type": str
            },
        }
    )

    assert schema.size == 2



# ==============================================================================
# Part 3. Field Management
# ==============================================================================


def test_add_field():

    schema = Schema()

    schema.add_field(
        "value",
        {
            "type": int
        },
    )

    assert "value" in schema



def test_remove_field():

    schema = Schema(
        fields={
            "value": {
                "type": int
            }
        }
    )

    schema.remove_field(
        "value"
    )

    assert "value" not in schema



def test_replace_field():

    schema = Schema()

    schema["value"] = {
        "type": int
    }

    schema["value"] = {
        "type": str
    }

    assert schema["value"]["type"] is str



def test_update():

    schema = Schema()

    schema.update(
        {
            "a": {
                "type": int
            }
        }
    )

    assert "a" in schema



def test_clear():

    schema = Schema(
        fields={
            "a": {
                "type": int
            }
        }
    )

    schema.clear()

    assert schema.size == 0



# ==============================================================================
# Part 4. Lookup
# ==============================================================================


def test_get():

    schema = Schema(
        fields={
            "value": {
                "type": int
            }
        }
    )

    assert schema.get("value") is not None



def test_require():

    schema = Schema(
        fields={
            "value": {
                "type": int
            }
        }
    )

    assert schema.require("value")["type"] is int



def test_contains():

    schema = Schema(
        fields={
            "value": {
                "type": int
            }
        }
    )

    assert "value" in schema



def test_exists():

    schema = Schema()

    assert schema.exists("missing") is False



def test_resolve():

    schema = Schema(
        fields={
            "value": {
                "type": int
            }
        }
    )

    assert schema.resolve("value")["type"] is int



# ==============================================================================
# Part 5. Validation
# ==============================================================================


def test_validate_name():

    schema = Schema()

    assert schema.validate_name(
        "test"
    )



def test_validate_field():

    schema = Schema()

    assert schema.validate_field(
        {
            "type": int
        }
    )



def test_validate_data():

    schema = Schema(
        fields={
            "value": {
                "type": int
            }
        }
    )


    result = schema.validate_data(
        {
            "value": 10
        }
    )

    assert result["valid"] is True



def test_validate():

    schema = Schema(
        fields={
            "value": {
                "type": int
            }
        }
    )

    assert schema.validate(
        {
            "value": 10
        }
    )



def test_is_empty():

    assert Schema().is_empty()



# ==============================================================================
# Part 6. Snapshot
# ==============================================================================


def test_snapshot():

    schema = Schema(
        fields={
            "value": {
                "type": int
            }
        }
    )

    snapshot = schema.snapshot()

    assert snapshot["name"] == DEFAULT_SCHEMA_NAME



def test_restore():

    schema = Schema(
        fields={
            "value": {
                "type": int
            }
        }
    )

    snapshot = schema.snapshot()

    restored = Schema()

    restored.restore(
        snapshot
    )

    assert restored == schema



def test_copy():

    schema = Schema()

    cloned = schema.copy()

    assert cloned == schema



def test_deepcopy():

    schema = Schema(
        fields={
            "value": {
                "type": int
            }
        }
    )

    cloned = copy.deepcopy(
        schema
    )

    assert cloned == schema



def test_clone():

    schema = Schema()

    cloned = schema.clone()

    assert cloned == schema
    assert cloned is not schema

# ==============================================================================
# Part 7. Protocols
# ==============================================================================


def test_contains_protocol():

    schema = Schema(
        fields={
            "value": {
                "type": int
            }
        }
    )

    assert "value" in schema
    assert "missing" not in schema



def test_getitem():

    schema = Schema(
        fields={
            "value": {
                "type": int
            }
        }
    )

    assert schema["value"]["type"] is int



def test_setitem():

    schema = Schema()

    schema["value"] = {
        "type": int
    }

    assert schema["value"]["type"] is int



def test_delitem():

    schema = Schema(
        fields={
            "value": {
                "type": int
            }
        }
    )

    del schema["value"]

    assert "value" not in schema



def test_iter():

    schema = Schema(
        fields={
            "a": {
                "type": int
            },
            "b": {
                "type": str
            },
        }
    )

    keys = list(schema)

    assert "a" in keys
    assert "b" in keys



def test_len():

    schema = Schema(
        fields={
            "a": {
                "type": int
            },
            "b": {
                "type": str
            },
        }
    )

    assert len(schema) == 2



def test_bool():

    assert bool(
        Schema()
    ) is False


    assert bool(
        Schema(
            fields={
                "a": {
                    "type": int
                }
            }
        )
    ) is True



def test_repr():

    schema = Schema()

    value = repr(schema)

    assert "Schema" in value



def test_str():

    schema = Schema()

    value = str(schema)

    assert "Schema" in value



def test_eq():

    schema1 = Schema(
        fields={
            "value": {
                "type": int
            }
        }
    )

    schema2 = Schema(
        fields={
            "value": {
                "type": int
            }
        }
    )

    assert schema1 == schema2



def test_hash():

    schema = Schema()

    value = hash(schema)

    assert isinstance(
        value,
        int,
    )



def test_pickle():

    import pickle


    schema = Schema(
        fields={
            "value": {
                "type": int
            }
        }
    )


    data = pickle.dumps(
        schema
    )

    restored = pickle.loads(
        data
    )


    assert restored == schema



# ==============================================================================
# Part 8. Diagnostics
# ==============================================================================


def test_summary():

    schema = Schema()

    result = schema.summary()


    assert isinstance(
        result,
        dict,
    )

    assert result["name"] == DEFAULT_SCHEMA_NAME



def test_diagnostics():

    schema = Schema()

    result = schema.diagnostics()


    assert isinstance(
        result,
        dict,
    )

    assert "status" in result



def test_schema_report():

    schema = Schema()

    result = schema.schema_report()


    assert isinstance(
        result,
        dict,
    )

    assert "schema" in result



def test_overall_status():

    schema = Schema()

    result = schema.overall_status()


    assert isinstance(
        result,
        str,
    )



# ==============================================================================
# Part 9. Public API
# ==============================================================================


def test_public_api():

    from .. import schema as module


    assert "Schema" in module.__all__

    assert (
        "DEFAULT_SCHEMA_NAME"
        in module.__all__
    )

    assert (
        "DEFAULT_VERSION"
        in module.__all__
    )

    assert (
        "DEFAULT_STRICT"
        in module.__all__
    )

    assert (
        "DEFAULT_ALLOW_EXTRA"
        in module.__all__
    )    