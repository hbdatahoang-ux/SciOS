"""
SciOS Runtime HookRegistry Tests
================================

Validate the Runtime HookRegistry.

Responsibilities
----------------
- Register hooks
- Unregister hooks
- Emit hooks
- Preserve FIFO order
- Isolate hook failures
- Prevent duplicate registration
- Provide registry statistics
"""

from __future__ import annotations

from scios.runtime.hook_registry import HookRegistry


# ==========================================================
# Registration
# ==========================================================


def test_register_and_emit() -> None:

    registry = HookRegistry()

    called: list[str] = []

    registry.register(
        "stage",
        lambda: called.append("ok"),
    )

    registry.emit("stage")

    assert called == ["ok"]


def test_unregister() -> None:

    registry = HookRegistry()

    called: list[str] = []

    def handler() -> None:
        called.append("called")

    registry.register(
        "stage",
        handler,
    )

    registry.unregister(
        "stage",
        handler,
    )

    registry.emit("stage")

    assert called == []

    assert not registry.registered("stage")


def test_duplicate_handler() -> None:
    """
    Duplicate registration should be ignored.
    """

    registry = HookRegistry()

    def handler() -> None:
        pass

    registry.register(
        "stage",
        handler,
    )

    registry.register(
        "stage",
        handler,
    )

    assert registry.count("stage") == 1


# ==========================================================
# Emit
# ==========================================================


def test_emit_unknown_hook() -> None:

    registry = HookRegistry()

    registry.emit("does_not_exist")

    assert len(registry) == 0


def test_fifo_order() -> None:

    registry = HookRegistry()

    order: list[int] = []

    registry.register(
        "stage",
        lambda: order.append(1),
    )

    registry.register(
        "stage",
        lambda: order.append(2),
    )

    registry.register(
        "stage",
        lambda: order.append(3),
    )

    registry.emit("stage")

    assert order == [1, 2, 3]


def test_exception_isolation() -> None:

    registry = HookRegistry()

    called = []

    def broken() -> None:
        raise RuntimeError("boom")

    def healthy() -> None:
        called.append(True)

    registry.register(
        "stage",
        broken,
    )

    registry.register(
        "stage",
        healthy,
    )

    registry.emit("stage")

    assert called == [True]


# ==========================================================
# Queries
# ==========================================================


def test_registered() -> None:

    registry = HookRegistry()

    assert not registry.registered("stage")

    registry.register(
        "stage",
        lambda: None,
    )

    assert registry.registered("stage")


def test_handlers() -> None:

    registry = HookRegistry()

    def handler() -> None:
        pass

    registry.register(
        "stage",
        handler,
    )

    handlers = registry.handlers("stage")

    assert isinstance(
        handlers,
        tuple,
    )

    assert len(handlers) == 1

    assert handlers[0] is handler


def test_count() -> None:

    registry = HookRegistry()

    registry.register(
        "a",
        lambda: None,
    )

    registry.register(
        "a",
        lambda: None,
    )

    registry.register(
        "b",
        lambda: None,
    )

    assert registry.count("a") == 2

    assert registry.count("b") == 1

    assert registry.count("c") == 0


# ==========================================================
# Maintenance
# ==========================================================


def test_clear() -> None:

    registry = HookRegistry()

    registry.register(
        "a",
        lambda: None,
    )

    registry.register(
        "b",
        lambda: None,
    )

    registry.clear()

    assert len(registry) == 0

    assert not registry


# ==========================================================
# Python Protocols
# ==========================================================


def test_len() -> None:

    registry = HookRegistry()

    registry.register(
        "a",
        lambda: None,
    )

    registry.register(
        "b",
        lambda: None,
    )

    registry.register(
        "b",
        lambda: None,
    )

    assert len(registry) == 3


def test_contains() -> None:

    registry = HookRegistry()

    assert "stage" not in registry

    registry.register(
        "stage",
        lambda: None,
    )

    assert "stage" in registry


def test_bool() -> None:

    registry = HookRegistry()

    assert not registry

    registry.register(
        "stage",
        lambda: None,
    )

    assert registry


def test_status() -> None:

    registry = HookRegistry()

    registry.register(
        "alpha",
        lambda: None,
    )

    registry.register(
        "beta",
        lambda: None,
    )

    registry.register(
        "beta",
        lambda: None,
    )

    status = registry.status()

    assert status == {
        "alpha": 1,
        "beta": 2,
    }


def test_repr() -> None:

    registry = HookRegistry()

    registry.register(
        "stage",
        lambda: None,
    )

    text = repr(registry)

    assert "HookRegistry" in text

    assert "hooks=1" in text

    assert "handlers=1" in text