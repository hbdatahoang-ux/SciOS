"""
SciOS Runtime Hook Tests
========================

Validate Hook, HookContext and HookHandle.

Tests
-----
- Hook execution
- Enable / disable lifecycle
- HookContext metadata
- HookHandle unregister
- Hook state management
"""

from __future__ import annotations

from scios.runtime.hook import (
    Hook,
    HookContext,
    HookHandle,
)


# ==========================================================
# Hook
# ==========================================================


def test_hook_execute() -> None:

    called = []

    def handler(value):
        called.append(value)

    hook = Hook(
        name="test",
        handler=handler,
    )

    hook("hello")

    assert called == [
        "hello"
    ]


def test_hook_disabled() -> None:

    called = []

    hook = Hook(
        name="test",
        handler=lambda: called.append(True),
    )

    hook.disable()

    hook()

    assert called == []


def test_hook_enable() -> None:

    called = []

    hook = Hook(
        name="test",
        handler=lambda: called.append(True),
    )

    hook.disable()

    hook.enable()

    hook()

    assert called == [True]


def test_hook_properties() -> None:

    hook = Hook(
        name="runtime.execute",
        handler=lambda: None,
        priority=10,
        once=True,
    )

    assert hook.name == "runtime.execute"

    assert hook.priority == 10

    assert hook.once is True

    assert hook.enabled is True

    assert hook.callable is True


def test_hook_repr() -> None:

    hook = Hook(
        name="test",
        handler=lambda: None,
    )

    text = repr(hook)

    assert "Hook" in text

    assert "test" in text


# ==========================================================
# HookContext
# ==========================================================


def test_hook_context_create() -> None:

    ctx = HookContext(
        name="runtime.after_execute",
    )

    assert (
        ctx.name
        ==
        "runtime.after_execute"
    )

    assert ctx.succeeded is True

    assert ctx.failed is False


def test_hook_context_metadata() -> None:

    ctx = HookContext(
        name="test",
    )

    ctx.set(
        "worker",
        "gpu",
    )

    assert (
        ctx.get("worker")
        ==
        "gpu"
    )


def test_hook_context_default() -> None:

    ctx = HookContext(
        name="test",
    )

    assert (
        ctx.get(
            "missing",
            "default",
        )
        ==
        "default"
    )


def test_hook_context_failure() -> None:

    error = ValueError(
        "boom"
    )

    ctx = HookContext(
        name="test",
        error=error,
    )

    assert ctx.failed is True

    assert ctx.succeeded is False


def test_hook_context_to_dict() -> None:

    ctx = HookContext(
        name="test",
        metadata={
            "a": 1
        },
    )

    data = ctx.to_dict()

    assert data["name"] == "test"

    assert data["metadata"] == {
        "a": 1
    }


# ==========================================================
# HookHandle
# ==========================================================


class DummyRegistry:

    def __init__(self):

        self.removed = []

    def unregister(
        self,
        name,
        handler,
    ):

        self.removed.append(
            name
        )


def test_hook_handle_unregister() -> None:

    registry = DummyRegistry()

    hook = Hook(
        name="test",
        handler=lambda: None,
    )

    handle = HookHandle(
        registry=registry,
        hook=hook,
    )

    handle.unregister()

    assert registry.removed == [
        "test"
    ]


def test_hook_handle_enable_disable() -> None:

    hook = Hook(
        name="test",
        handler=lambda: None,
    )

    handle = HookHandle(
        registry=None,
        hook=hook,
    )

    handle.disable()

    assert handle.enabled is False

    handle.enable()

    assert handle.enabled is True


def test_hook_handle_repr() -> None:

    hook = Hook(
        name="test",
        handler=lambda: None,
    )

    handle = HookHandle(
        registry=None,
        hook=hook,
    )

    text = repr(handle)

    assert "HookHandle" in text

    assert "test" in text