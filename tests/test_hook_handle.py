"""
SciOS Runtime HookHandle Tests
==============================

Validate HookHandle lifecycle.

Tests
-----
- unregister()
- enable()
- disable()
- enabled property
- repr()
"""

from __future__ import annotations

from scios.runtime.hook import Hook, HookHandle
from scios.runtime.hook_registry import HookRegistry


# ==========================================================
# unregister
# ==========================================================


def test_unregister() -> None:

    registry = HookRegistry()

    called = []

    def handler():

        called.append(True)

    handle = registry.register(
        "runtime.test",
        handler,
    )

    registry.emit("runtime.test")

    assert called == [True]

    handle.unregister()

    called.clear()

    registry.emit("runtime.test")

    assert called == []


# ==========================================================
# disable
# ==========================================================


def test_disable() -> None:

    registry = HookRegistry()

    called = []

    def handler():

        called.append(True)

    handle = registry.register(
        "runtime.test",
        handler,
    )

    handle.disable()

    registry.emit("runtime.test")

    assert called == []

    assert handle.enabled is False


# ==========================================================
# enable
# ==========================================================


def test_enable() -> None:

    registry = HookRegistry()

    called = []

    def handler():

        called.append(True)

    handle = registry.register(
        "runtime.test",
        handler,
    )

    handle.disable()

    handle.enable()

    registry.emit("runtime.test")

    assert called == [True]

    assert handle.enabled is True


# ==========================================================
# once
# ==========================================================


def test_once_hook() -> None:

    registry = HookRegistry()

    counter = []

    registry.register(
        "runtime.test",
        lambda: counter.append(1),
        once=True,
    )

    registry.emit("runtime.test")

    registry.emit("runtime.test")

    registry.emit("runtime.test")

    assert counter == [1]


# ==========================================================
# priority
# ==========================================================


def test_priority_order() -> None:

    registry = HookRegistry()

    order = []

    registry.register(
        "runtime.test",
        lambda: order.append(2),
        priority=20,
    )

    registry.register(
        "runtime.test",
        lambda: order.append(1),
        priority=10,
    )

    registry.register(
        "runtime.test",
        lambda: order.append(3),
        priority=30,
    )

    registry.emit("runtime.test")

    assert order == [
        1,
        2,
        3,
    ]


# ==========================================================
# handle properties
# ==========================================================


def test_handle_properties() -> None:

    registry = HookRegistry()

    handle = registry.register(
        "runtime.test",
        lambda: None,
    )

    assert isinstance(
        handle.hook,
        Hook,
    )

    assert handle.hook.name == "runtime.test"

    assert handle.enabled is True


# ==========================================================
# repr
# ==========================================================


def test_repr() -> None:

    registry = HookRegistry()

    handle = registry.register(
        "runtime.test",
        lambda: None,
    )

    text = repr(handle)

    assert "HookHandle" in text

    assert "runtime.test" in text


# ==========================================================
# multiple unregister
# ==========================================================


def test_unregister_twice() -> None:

    registry = HookRegistry()

    handle = registry.register(
        "runtime.test",
        lambda: None,
    )

    handle.unregister()

    handle.unregister()

    assert True


# ==========================================================
# empty registry after unregister
# ==========================================================


def test_registry_empty_after_unregister() -> None:

    registry = HookRegistry()

    handle = registry.register(
        "runtime.test",
        lambda: None,
    )

    handle.unregister()

    assert registry.count(
        "runtime.test",
    ) == 0