# ============================================================
# Part 1 – Fixtures
# ============================================================

import pytest

from scios.runtime.observability.tracing.baggage import (
    Baggage,
)


@pytest.fixture
def baggage() -> Baggage:
    """
    Empty baggage container.
    """

    return Baggage()


@pytest.fixture
def populated_baggage() -> Baggage:
    """
    Baggage container populated with common values.
    """

    bag = Baggage()

    bag.set(
        "service",
        "scios",
    )

    bag.set(
        "version",
        "0.3",
    )

    bag.set(
        "trace_id",
        "trace-001",
    )

    bag.set(
        "user_id",
        "user-123",
    )

    bag.set(
        "environment",
        "test",
    )

    return bag
# ============================================================
# Creation
# ============================================================


def test_baggage_creation(
    baggage,
):

    assert baggage is not None



def test_default_empty(
    baggage,
):

    assert len(
        baggage
    ) == 0
# ============================================================
# Set / Get
# ============================================================


def test_set_item(
    baggage,
):

    baggage.set(
        "user.id",
        "12345",
    )


    assert (
        baggage.get(
            "user.id"
        )
        ==
        "12345"
    )



def test_get_item(
    populated_baggage,
):

    assert (
        populated_baggage.get(
            "service.name"
        )
        ==
        "SciOS"
    )



def test_get_missing(
    baggage,
):

    assert (
        baggage.get(
            "missing"
        )
        is None
    )



def test_default_value(
    baggage,
):

    assert (
        baggage.get(
            "missing",
            "default",
        )
        ==
        "default"
    )



def test_overwrite_item(
    baggage,
):

    baggage.set(
        "trace.id",
        "old",
    )


    baggage.set(
        "trace.id",
        "new",
    )


    assert (
        baggage.get(
            "trace.id"
        )
        ==
        "new"
    )
# ============================================================
# Bulk Operations
# ============================================================


def test_update(
    baggage,
):

    baggage.update(
        {
            "user.id": "1001",
            "tenant.id": "tenant-a",
        }
    )


    assert (
        baggage.get(
            "user.id"
        )
        ==
        "1001"
    )


    assert (
        baggage.get(
            "tenant.id"
        )
        ==
        "tenant-a"
    )



def test_merge(
    baggage,
):

    baggage.set(
        "service.name",
        "SciOS",
    )


    baggage.merge(
        {
            "service.version": "0.3",
        }
    )


    assert (
        baggage.get(
            "service.name"
        )
        ==
        "SciOS"
    )


    assert (
        baggage.get(
            "service.version"
        )
        ==
        "0.3"
    )



def test_remove(
    populated_baggage,
):

    populated_baggage.remove(
        "service.name"
    )


    assert (
        populated_baggage.get(
            "service.name"
        )
        is None
    )



def test_clear(
    populated_baggage,
):

    populated_baggage.clear()


    assert (
        len(
            populated_baggage
        )
        ==
        0
    )



def test_count(
    populated_baggage,
):

    assert (
        populated_baggage.count()
        ==
        3
    )
# ============================================================
# Validation
# ============================================================


def test_invalid_key(
    baggage,
):

    with pytest.raises(
        Exception,
    ):

        baggage.set(
            "",
            "value",
        )



def test_invalid_none_key(
    baggage,
):

    with pytest.raises(
        Exception,
    ):

        baggage.set(
            None,
            "value",
        )



def test_validate(
    populated_baggage,
):

    assert (
        populated_baggage.validate()
        is True
    )
# ============================================================
# Serialization
# ============================================================


def test_to_dict(
    populated_baggage,
):

    data = (
        populated_baggage
        .to_dict()
    )


    assert isinstance(
        data,
        dict,
    )


    assert (
        data["service.name"]
        ==
        "SciOS"
    )



def test_from_dict(
    populated_baggage,
):

    data = (
        populated_baggage
        .to_dict()
    )


    restored = (
        Baggage
        .from_dict(data)
    )


    assert (
        restored.get(
            "service.name"
        )
        ==
        "SciOS"
    )



def test_to_json(
    populated_baggage,
):

    value = (
        populated_baggage
        .to_json()
    )


    assert isinstance(
        value,
        str,
    )


    data = json.loads(
        value
    )


    assert (
        data["service.version"]
        ==
        "0.3"
    )



def test_from_json(
    populated_baggage,
):

    value = (
        populated_baggage
        .to_json()
    )


    restored = (
        Baggage
        .from_json(value)
    )


    assert (
        restored.get(
            "service.version"
        )
        ==
        "0.3"
    )



def test_snapshot(
    populated_baggage,
):

    snapshot = (
        populated_baggage
        .snapshot()
    )


    assert isinstance(
        snapshot,
        dict,
    )


    assert (
        snapshot["service.name"]
        ==
        "SciOS"
    )



def test_restore(
    populated_baggage,
):

    snapshot = (
        populated_baggage
        .snapshot()
    )


    restored = (
        Baggage
        .restore(snapshot)
    )


    assert (
        restored.get(
            "service.name"
        )
        ==
        "SciOS"
    )
# ============================================================
# Part 7 - Clone / Copy
# ============================================================


def test_clone(
    populated_baggage,
):

    cloned = (
        populated_baggage
        .clone()
    )

    assert cloned is not populated_baggage

    assert (
        cloned.to_dict()
        ==
        populated_baggage.to_dict()
    )


def test_copy(
    populated_baggage,
):

    copied = (
        populated_baggage
        .copy()
    )

    assert copied is not populated_baggage

    assert (
        copied.to_dict()
        ==
        populated_baggage.to_dict()
    )


def test_python_copy(
    populated_baggage,
):

    copied = copy.copy(
        populated_baggage
    )

    assert copied is not populated_baggage

    assert (
        copied.to_dict()
        ==
        populated_baggage.to_dict()
    )


def test_python_deepcopy(
    populated_baggage,
):

    copied = copy.deepcopy(
        populated_baggage
    )

    assert copied is not populated_baggage

    assert (
        copied.to_dict()
        ==
        populated_baggage.to_dict()
    )
# ============================================================
# Part 8 - Diagnostics
# ============================================================


def test_diagnostics(
    populated_baggage,
):

    result = (
        populated_baggage
        .diagnostics()
    )

    assert isinstance(
        result,
        dict,
    )

    assert (
        result["valid"]
        is True
    )

    assert (
        result["count"]
        ==
        populated_baggage.count()
    )

    assert (
        result["empty"]
        is False
    )

    assert "keys" in result

    assert "types" in result


def test_summary(
    populated_baggage,
):

    result = (
        populated_baggage
        .summary()
    )

    assert isinstance(
        result,
        dict,
    )

    assert (
        result["count"]
        ==
        populated_baggage.count()
    )

    assert (
        result["empty"]
        is False
    )

    assert (
        result["valid"]
        is True
    )

    assert (
        "keys"
        in result
    )
# ============================================================
# Part 9 - Python Protocols
# ============================================================


def test_repr(
    baggage,
):

    result = repr(
        baggage
    )

    assert isinstance(
        result,
        str,
    )

    assert (
        "Baggage"
        in result
    )


def test_str(
    baggage,
):

    result = str(
        baggage
    )

    assert isinstance(
        result,
        str,
    )


def test_len(
    populated_baggage,
):

    assert (
        len(
            populated_baggage
        )
        ==
        populated_baggage.count()
    )


def test_contains(
    populated_baggage,
):

    assert (
        "service"
        in populated_baggage
    )


def test_getitem(
    populated_baggage,
):

    assert (
        populated_baggage["service"]
        ==
        "scios"
    )


def test_setitem(
    baggage,
):

    baggage["runtime"] = (
        "engine"
    )

    assert (
        baggage["runtime"]
        ==
        "engine"
    )


def test_delitem(
    baggage,
):

    baggage["temp"] = 123

    del baggage["temp"]

    assert (
        "temp"
        not in baggage
    )


def test_iter(
    populated_baggage,
):

    keys = list(
        iter(
            populated_baggage
        )
    )

    assert (
        "service"
        in keys
    )

    assert (
        "version"
        in keys
    )


def test_bool(
    baggage,
    populated_baggage,
):

    assert (
        bool(
            baggage
        )
        is False
    )

    assert (
        bool(
            populated_baggage
        )
        is True
    )


def test_equality():

    first = Baggage()

    first.set(
        "a",
        1,
    )

    second = Baggage()

    second.set(
        "a",
        1,
    )

    assert (
        first
        ==
        second
    )


def test_hash(
    baggage,
):

    value = hash(
        baggage
    )

    assert isinstance(
        value,
        int,
    )                                