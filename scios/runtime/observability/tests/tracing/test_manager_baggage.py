"""
Tests for TraceManager baggage API.

Coverage
--------
- add_baggage()
- get_baggage()
- has_baggage()
- remove_baggage()
- clear_baggage()
- baggage snapshot
- overwrite values
- error paths
"""

from __future__ import annotations

import pytest

from scios.runtime.observability.tracing.manager import TraceManager


# ==========================================================
# Helpers
# ==========================================================


def create_manager():

    manager = TraceManager()

    manager.start_trace("runtime")

    return manager


# ==========================================================
# Add
# ==========================================================


def test_add_baggage():

    manager = create_manager()

    manager.add_baggage("user", "alice")

    assert manager.get_baggage("user") == "alice"


def test_add_multiple_baggage():

    manager = create_manager()

    manager.add_baggage("user", "alice")

    manager.add_baggage("job", "planner")

    manager.add_baggage("node", "gpu0")

    assert manager.get_baggage("user") == "alice"

    assert manager.get_baggage("job") == "planner"

    assert manager.get_baggage("node") == "gpu0"


def test_overwrite_baggage():

    manager = create_manager()

    manager.add_baggage("user", "alice")

    manager.add_baggage("user", "bob")

    assert manager.get_baggage("user") == "bob"


# ==========================================================
# Query
# ==========================================================


def test_get_default():

    manager = create_manager()

    assert manager.get_baggage(

        "missing",

        "default",

    ) == "default"


def test_has_baggage_true():

    manager = create_manager()

    manager.add_baggage("user", "alice")

    assert manager.has_baggage("user")


def test_has_baggage_false():

    manager = create_manager()

    assert not manager.has_baggage("missing")


# ==========================================================
# Snapshot
# ==========================================================


def test_baggage_snapshot():

    manager = create_manager()

    manager.add_baggage("a", 1)

    manager.add_baggage("b", 2)

    snapshot = manager.baggage

    assert snapshot == {

        "a": 1,

        "b": 2,

    }


def test_snapshot_is_copy():

    manager = create_manager()

    manager.add_baggage("user", "alice")

    snapshot = manager.baggage

    snapshot["user"] = "changed"

    assert manager.get_baggage("user") == "alice"


# ==========================================================
# Remove
# ==========================================================


def test_remove_existing_baggage():

    manager = create_manager()

    manager.add_baggage("user", "alice")

    assert manager.remove_baggage("user")

    assert not manager.has_baggage("user")


def test_remove_missing_baggage():

    manager = create_manager()

    assert manager.remove_baggage("missing") is False


# ==========================================================
# Clear
# ==========================================================


def test_clear_baggage():

    manager = create_manager()

    manager.add_baggage("a", 1)

    manager.add_baggage("b", 2)

    removed = manager.clear_baggage()

    assert removed == 2

    assert manager.baggage == {}


def test_clear_empty_baggage():

    manager = create_manager()

    removed = manager.clear_baggage()

    assert removed == 0

    assert manager.baggage == {}


# ==========================================================
# Error Paths
# ==========================================================


def test_add_without_trace():

    manager = TraceManager()

    with pytest.raises(RuntimeError):

        manager.add_baggage(

            "user",

            "alice",

        )


def test_remove_without_trace():

    manager = TraceManager()

    with pytest.raises(RuntimeError):

        manager.remove_baggage("user")


def test_clear_without_trace():

    manager = TraceManager()

    with pytest.raises(RuntimeError):

        manager.clear_baggage()


def test_has_without_trace():

    manager = TraceManager()

    with pytest.raises(RuntimeError):

        manager.has_baggage("user")


# ==========================================================
# Regression
# ==========================================================


def test_finish_trace_preserves_baggage_snapshot():

    manager = create_manager()

    manager.add_baggage("user", "alice")

    snapshot = manager.baggage

    manager.finish_trace()

    assert snapshot["user"] == "alice"


def test_reset_clears_baggage():

    manager = create_manager()

    manager.add_baggage("user", "alice")

    manager.reset()

    assert manager.baggage == {}


def test_many_baggage_items():

    manager = create_manager()

    for i in range(100):

        manager.add_baggage(

            f"k{i}",

            i,

        )

    assert len(manager.baggage) == 100


def test_unicode_baggage():

    manager = create_manager()

    manager.add_baggage(

        "người_dùng",

        "Hoàng",

    )

    assert (

        manager.get_baggage(

            "người_dùng"

        )

        == "Hoàng"

    )