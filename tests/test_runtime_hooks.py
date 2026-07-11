"""
SciOS Runtime Hook Tests
========================

Validate the ExecutionEngine hook system.

The hook mechanism enables runtime extensibility without modifying
the Engine implementation.

Hooks
-----
- before_submit
- before_execute
- after_execute
- after_failure
"""

from __future__ import annotations

from scios.runtime import ExecutionEngine
from scios.runtime.result import ExecutionResult


# ==========================================================
# Success Hooks
# ==========================================================

def test_engine_hooks_success() -> None:

    events: list[tuple[str, object]] = []

    engine = ExecutionEngine()

    engine.register_hook(
        "before_submit",
        lambda ctx: events.append(
            ("before_submit", ctx.status)
        ),
    )

    engine.register_hook(
        "before_execute",
        lambda ctx: events.append(
            ("before_execute", ctx.status)
        ),
    )

    engine.register_hook(
        "after_execute",
        lambda ctx, result: events.append(
            ("after_execute", result.value)
        ),
    )

    engine.register_hook(
        "after_failure",
        lambda ctx, error: events.append(
            ("after_failure", str(error))
        ),
    )

    ctx = engine.run(
        lambda: "ok",
    )

    assert ctx.status == "completed"

    assert (
        "before_submit",
        "created",
    ) in events

    assert (
        "before_execute",
        "running",
    ) in events

    assert (
        "after_execute",
        "ok",
    ) in events

    assert not any(
        e[0] == "after_failure"
        for e in events
    )


# ==========================================================
# Failure Hooks
# ==========================================================

def test_engine_hooks_failure() -> None:

    events: list[tuple[str, object]] = []

    engine = ExecutionEngine()

    engine.register_hook(
        "after_failure",
        lambda ctx, err: events.append(
            (
                "after_failure",
                str(err),
            )
        ),
    )

    def failing() -> None:
        raise ValueError("boom")

    ctx = engine.run(
        failing,
    )

    assert ctx.status == "failed"

    assert any(
        e[0] == "after_failure"
        and "boom" in e[1]
        for e in events
    )


# ==========================================================
# Multiple Hooks
# ==========================================================

def test_multiple_hooks_same_stage() -> None:

    called: list[str] = []

    engine = ExecutionEngine()

    engine.register_hook(
        "before_execute",
        lambda ctx: called.append("A"),
    )

    engine.register_hook(
        "before_execute",
        lambda ctx: called.append("B"),
    )

    engine.run(
        lambda: None,
    )

    assert called == [
        "A",
        "B",
    ]


# ==========================================================
# Unknown Hook
# ==========================================================

def test_unknown_hook_name() -> None:

    engine = ExecutionEngine()

    try:

        engine.register_hook(
            "does_not_exist",
            lambda *_: None,
        )

    except ValueError:

        return

    raise AssertionError(
        "Unknown hook should raise ValueError."
    )


# ==========================================================
# Hook Failure Isolation
# ==========================================================

def test_hook_exception_isolated() -> None:

    engine = ExecutionEngine()

    def broken(ctx):

        raise RuntimeError(
            "hook failure"
        )

    engine.register_hook(
        "before_execute",
        broken,
    )

    ctx = engine.run(
        lambda: 42,
    )

    assert ctx.status == "completed"

    assert isinstance(
        ctx.result,
        ExecutionResult,
    )

    assert ctx.result.success


# ==========================================================
# Hook Ordering
# ==========================================================

def test_hook_execution_order() -> None:

    order: list[str] = []

    engine = ExecutionEngine()

    engine.register_hook(
        "before_submit",
        lambda ctx: order.append("submit"),
    )

    engine.register_hook(
        "before_execute",
        lambda ctx: order.append("execute"),
    )

    engine.register_hook(
        "after_execute",
        lambda ctx, result: order.append("after"),
    )

    engine.run(
        lambda: "done",
    )

    assert order == [
        "submit",
        "execute",
        "after",
    ]