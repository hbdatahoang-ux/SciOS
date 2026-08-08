# ==============================================================================
# Part 1. Imports
# ==============================================================================

from __future__ import annotations

import pytest

from scios.runtime.observability.metrics.core.metric_hooks import (
    HookStage,
    MetricHooks,
)


# ==============================================================================
# Helpers
# ==============================================================================

def dummy_hook(*args, **kwargs):
    return ("ok", args, kwargs)


def another_hook(*args, **kwargs):
    return True


# ==============================================================================
# Part 2. Construction
# ==============================================================================

def test_default_hooks():
    hooks = MetricHooks()

    assert isinstance(hooks, MetricHooks)
    assert hooks.hooks == {}


def test_custom_hooks():
    hooks = MetricHooks(
        {
            HookStage.BEFORE_COLLECT: [dummy_hook],
            HookStage.AFTER_EXPORT: [another_hook],
        }
    )

    assert hooks.has(HookStage.BEFORE_COLLECT)
    assert hooks.has(HookStage.AFTER_EXPORT)
    assert hooks.count() == 2


# ==============================================================================
# Part 3. Defaults
# ==============================================================================

def test_empty_hooks():
    hooks = MetricHooks()

    assert hooks.empty is True
    assert hooks.count() == 0
    assert hooks.stages() == ()


# ==============================================================================
# Part 4. Validation
# ==============================================================================

def test_invalid_stage():
    with pytest.raises(ValueError):
        MetricHooks(
            {
                "invalid_stage": [dummy_hook],
            }
        )


def test_invalid_callback():
    with pytest.raises(TypeError):
        MetricHooks(
            {
                HookStage.BEFORE_COLLECT: [123],
            }
        )


# ==============================================================================
# Part 5. Properties
# ==============================================================================

def test_hooks():
    hooks = MetricHooks()

    hooks.register(
        HookStage.BEFORE_COLLECT,
        dummy_hook,
    )

    assert HookStage.BEFORE_COLLECT in hooks.mapping
    assert hooks.mapping[HookStage.BEFORE_COLLECT] == [
        dummy_hook,
    ]


def test_count():
    hooks = MetricHooks()

    hooks.register(
        HookStage.BEFORE_COLLECT,
        dummy_hook,
    )

    hooks.register(
        HookStage.AFTER_COLLECT,
        another_hook,
    )

    assert hooks.count() == 2
    assert hooks.size == 2


# ==============================================================================
# Part 6. Registration
# ==============================================================================

def test_register():
    hooks = MetricHooks()

    hooks.register(
        HookStage.BEFORE_COLLECT,
        dummy_hook,
    )

    assert hooks.has(HookStage.BEFORE_COLLECT)
    assert hooks.count() == 1

    # duplicate registration should be ignored
    hooks.register(
        HookStage.BEFORE_COLLECT,
        dummy_hook,
    )

    assert hooks.count() == 1


def test_unregister():
    hooks = MetricHooks()

    hooks.register(
        HookStage.BEFORE_COLLECT,
        dummy_hook,
    )

    hooks.unregister(
        HookStage.BEFORE_COLLECT,
        dummy_hook,
    )

    assert hooks.has(HookStage.BEFORE_COLLECT) is False
    assert hooks.count() == 0


def test_has():
    hooks = MetricHooks()

    assert hooks.has(HookStage.BEFORE_COLLECT) is False

    hooks.register(
        HookStage.BEFORE_COLLECT,
        dummy_hook,
    )

    assert hooks.has(HookStage.BEFORE_COLLECT) is True


def test_clear():
    hooks = MetricHooks()

    hooks.register(
        HookStage.BEFORE_COLLECT,
        dummy_hook,
    )

    hooks.register(
        HookStage.AFTER_EXPORT,
        another_hook,
    )

    hooks.clear(HookStage.BEFORE_COLLECT)

    assert hooks.has(HookStage.BEFORE_COLLECT) is False
    assert hooks.has(HookStage.AFTER_EXPORT) is True

    hooks.clear()

    assert hooks.count() == 0
    assert hooks.empty


def test_stages():
    hooks = MetricHooks()

    hooks.register(
        HookStage.BEFORE_COLLECT,
        dummy_hook,
    )

    hooks.register(
        HookStage.AFTER_EXPORT,
        another_hook,
    )

    stages = hooks.stages()

    assert HookStage.BEFORE_COLLECT in stages
    assert HookStage.AFTER_EXPORT in stages
    assert len(stages) == 2

# ==============================================================================
# Part 7. Execution
# ==============================================================================

def test_run():
    hooks = MetricHooks()

    hooks.register(
        HookStage.BEFORE_COLLECT,
        dummy_hook,
    )

    result = hooks.run(
        HookStage.BEFORE_COLLECT,
        1,
        key="value",
    )

    assert len(result) == 1
    assert result[0][0] == "ok"


def test_run_before_collect():
    hooks = MetricHooks()
    hooks.register(HookStage.BEFORE_COLLECT, dummy_hook)

    result = hooks.run_before_collect()

    assert len(result) == 1


def test_run_after_collect():
    hooks = MetricHooks()
    hooks.register(HookStage.AFTER_COLLECT, dummy_hook)

    result = hooks.run_after_collect()

    assert len(result) == 1


def test_run_before_export():
    hooks = MetricHooks()
    hooks.register(HookStage.BEFORE_EXPORT, dummy_hook)

    result = hooks.run_before_export()

    assert len(result) == 1


def test_run_after_export():
    hooks = MetricHooks()
    hooks.register(HookStage.AFTER_EXPORT, dummy_hook)

    result = hooks.run_after_export()

    assert len(result) == 1


def test_run_on_error():
    hooks = MetricHooks()
    hooks.register(HookStage.ON_ERROR, dummy_hook)

    result = hooks.run_on_error()

    assert len(result) == 1


def test_run_on_reset():
    hooks = MetricHooks()
    hooks.register(HookStage.ON_RESET, dummy_hook)

    result = hooks.run_on_reset()

    assert len(result) == 1


# ==============================================================================
# Part 8. Serialization
# ==============================================================================

def test_to_dict():
    hooks = MetricHooks()

    hooks.register(
        HookStage.BEFORE_COLLECT,
        dummy_hook,
    )

    data = hooks.to_dict()

    assert "hooks" in data
    assert data["hooks"]["before_collect"] == 1


def test_from_dict():
    hooks = MetricHooks.from_dict(
        {
            "hooks": {
                "before_collect": 2,
                "after_export": 1,
            }
        }
    )

    assert hooks.has(HookStage.BEFORE_COLLECT)
    assert hooks.has(HookStage.AFTER_EXPORT)
    assert hooks.count() == 3


def test_to_json():
    hooks = MetricHooks()

    hooks.register(
        HookStage.BEFORE_COLLECT,
        dummy_hook,
    )

    payload = hooks.to_json()

    assert isinstance(payload, str)
    assert "before_collect" in payload


def test_from_json():
    payload = (
        '{"hooks":{"before_collect":1}}'
    )

    hooks = MetricHooks.from_json(payload)

    assert hooks.has(HookStage.BEFORE_COLLECT)


# ==============================================================================
# Part 9. Copy
# ==============================================================================

def test_copy():
    hooks = MetricHooks()

    hooks.register(
        HookStage.BEFORE_COLLECT,
        dummy_hook,
    )

    copied = hooks.copy()

    assert copied == hooks
    assert copied is not hooks


def test_clone():
    hooks = MetricHooks()

    hooks.register(
        HookStage.BEFORE_COLLECT,
        dummy_hook,
    )

    cloned = hooks.clone()

    assert cloned == hooks
    assert cloned is not hooks


# ==============================================================================
# Part 10. Equality
# ==============================================================================

def test_eq():
    a = MetricHooks()
    b = MetricHooks()

    a.register(HookStage.BEFORE_COLLECT, dummy_hook)
    b.register(HookStage.BEFORE_COLLECT, dummy_hook)

    assert a == b


def test_hash():
    hooks = MetricHooks()

    hooks.register(
        HookStage.BEFORE_COLLECT,
        dummy_hook,
    )

    assert isinstance(hash(hooks), int)


# ==============================================================================
# Part 11. Representation
# ==============================================================================

def test_repr():
    hooks = MetricHooks()

    assert "MetricHooks" in repr(hooks)


def test_str():
    hooks = MetricHooks()

    assert "MetricHooks" in str(hooks)


# ==============================================================================
# Part 12. Public API
# ==============================================================================

def test_all():
    from scios.runtime.observability.metrics.core.metric_hooks import __all__

    assert "MetricHooks" in __all__
    assert "HookStage" in __all__


def test_version():
    from scios.runtime.observability.metrics.core.metric_hooks import (
        __version__,
    )

    assert isinstance(__version__, str)


# ==============================================================================
# Part 13. Regression
# ==============================================================================

def test_callbacks_are_copied():
    hooks = MetricHooks()

    hooks.register(
        HookStage.BEFORE_COLLECT,
        dummy_hook,
    )

    copied = hooks.copy()

    copied.register(
        HookStage.AFTER_EXPORT,
        another_hook,
    )

    assert hooks.has(HookStage.AFTER_EXPORT) is False
    assert copied.has(HookStage.AFTER_EXPORT) is True


def test_execution_order():
    order = []

    def first():
        order.append(1)

    def second():
        order.append(2)

    hooks = MetricHooks()

    hooks.register(
        HookStage.BEFORE_COLLECT,
        first,
    )

    hooks.register(
        HookStage.BEFORE_COLLECT,
        second,
    )

    hooks.run_before_collect()

    assert order == [1, 2]


def test_json_roundtrip():
    hooks = MetricHooks()

    hooks.register(
        HookStage.BEFORE_COLLECT,
        dummy_hook,
    )

    restored = MetricHooks.from_json(
        hooks.to_json(),
    )

    assert restored == hooks


def test_dict_roundtrip():
    hooks = MetricHooks()

    hooks.register(
        HookStage.BEFORE_COLLECT,
        dummy_hook,
    )

    restored = MetricHooks.from_dict(
        hooks.to_dict(),
    )

    assert restored == hooks    