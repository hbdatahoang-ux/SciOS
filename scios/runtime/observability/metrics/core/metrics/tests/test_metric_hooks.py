# ==========================================================
# Part 1. Imports
# ==========================================================

from __future__ import annotations

import copy
import inspect
import pickle
from typing import get_type_hints

import pytest

from scios.runtime.observability.metrics.core.metrics.core.metric_hooks import (
    MetricHooks,
)

# ==========================================================
# Test Callbacks
# ==========================================================

def before_collect_hook():
    return None


def before_collect_hook2():
    return None


def after_collect_hook():
    return None


def after_collect_hook2():
    return None


def before_export_hook():
    return None


def after_export_hook():
    return None
# ==========================================================
# Part 2. Fixtures
# ==========================================================

@pytest.fixture
def empty_hooks() -> MetricHooks:
    return MetricHooks()


@pytest.fixture
def custom_hooks() -> MetricHooks:
    hooks = MetricHooks()

    hooks.before_collect.append(before_collect_hook)
    hooks.after_collect.append(after_collect_hook)

    return hooks


@pytest.fixture
def full_hooks() -> MetricHooks:
    hooks = MetricHooks()

    hooks.before_collect.extend(
        [
            before_collect_hook,
            before_collect_hook2,
        ]
    )

    hooks.after_collect.extend(
        [
            after_collect_hook,
            after_collect_hook2,
        ]
    )

    hooks.before_export.append(before_export_hook)
    hooks.after_export.append(after_export_hook)

    return hooks

# ==========================================================
# Part 3. Construction
# ==========================================================

class TestConstruction:

    def test_create_default(self):
        hooks = MetricHooks()

        assert isinstance(hooks, MetricHooks)

    def test_create_custom(
        self,
        custom_hooks: MetricHooks,
    ):
        assert isinstance(custom_hooks, MetricHooks)

    def test_create_empty(
        self,
        empty_hooks: MetricHooks,
    ):
        assert isinstance(empty_hooks, MetricHooks)

    def test_create_full(
        self,
        full_hooks: MetricHooks,
    ):
        assert isinstance(full_hooks, MetricHooks)

# ==========================================================
# Part 4. Identity
# ==========================================================

class TestIdentity:

    def test_before_collect(
        self,
        custom_hooks: MetricHooks,
    ):
        assert isinstance(custom_hooks.before_collect, list)
        assert len(custom_hooks.before_collect) == 1

    def test_after_collect(
        self,
        custom_hooks: MetricHooks,
    ):
        assert isinstance(custom_hooks.after_collect, list)
        assert len(custom_hooks.after_collect) == 1

    def test_before_export(
        self,
        full_hooks: MetricHooks,
    ):
        assert isinstance(full_hooks.before_export, list)
        assert len(full_hooks.before_export) == 1

    def test_after_export(
        self,
        full_hooks: MetricHooks,
    ):
        assert isinstance(full_hooks.after_export, list)
        assert len(full_hooks.after_export) == 1

    def test_length(
        self,
        full_hooks: MetricHooks,
    ):
        expected = (
            len(full_hooks.before_collect)
            + len(full_hooks.after_collect)
            + len(full_hooks.before_export)
            + len(full_hooks.after_export)
        )

        assert len(full_hooks) == expected


# ==========================================================
# Part 5. Defaults
# ==========================================================

class TestDefaults:

    def test_default_empty(self):
        hooks = MetricHooks()

        assert hooks.before_collect == []
        assert hooks.after_collect == []
        assert hooks.before_export == []
        assert hooks.after_export == []

    def test_default_mutable_independent(self):
        h1 = MetricHooks()
        h2 = MetricHooks()

        h1.before_collect.append(lambda: None)

        assert len(h1.before_collect) == 1
        assert len(h2.before_collect) == 0

    def test_default_lists_independent(self):
        hooks = MetricHooks()

        hooks.before_collect.append(lambda: None)

        assert hooks.after_collect == []
        assert hooks.before_export == []
        assert hooks.after_export == []


# ==========================================================
# Part 6. Registration
# ==========================================================

class TestRegistration:

    def test_register_before_collect(
        self,
        empty_hooks: MetricHooks,
    ):
        fn = lambda: None

        empty_hooks.register_before_collect(fn)

        assert fn in empty_hooks.before_collect
        assert len(empty_hooks.before_collect) == 1

    def test_register_after_collect(
        self,
        empty_hooks: MetricHooks,
    ):
        fn = lambda: None

        empty_hooks.register_after_collect(fn)

        assert fn in empty_hooks.after_collect
        assert len(empty_hooks.after_collect) == 1

    def test_register_before_export(
        self,
        empty_hooks: MetricHooks,
    ):
        fn = lambda: None

        empty_hooks.register_before_export(fn)

        assert fn in empty_hooks.before_export
        assert len(empty_hooks.before_export) == 1

    def test_register_after_export(
        self,
        empty_hooks: MetricHooks,
    ):
        fn = lambda: None

        empty_hooks.register_after_export(fn)

        assert fn in empty_hooks.after_export
        assert len(empty_hooks.after_export) == 1

# ==========================================================
# Part 7. Execution
# ==========================================================

class TestExecution:

    def test_execute_before_collect(
        self,
        empty_hooks: MetricHooks,
    ):
        called = []

        def fn():
            called.append(True)

        empty_hooks.register_before_collect(fn)

        empty_hooks.run_before_collect()

        assert called == [True]

    def test_execute_after_collect(
        self,
        empty_hooks: MetricHooks,
    ):
        called = []

        def fn():
            called.append(True)

        empty_hooks.register_after_collect(fn)

        empty_hooks.run_after_collect()

        assert called == [True]

    def test_execute_before_export(
        self,
        empty_hooks: MetricHooks,
    ):
        called = []

        def fn():
            called.append(True)

        empty_hooks.register_before_export(fn)

        empty_hooks.run_before_export()

        assert called == [True]

    def test_execute_after_export(
        self,
        empty_hooks: MetricHooks,
    ):
        called = []

        def fn():
            called.append(True)

        empty_hooks.register_after_export(fn)

        empty_hooks.run_after_export()

        assert called == [True]


# ==========================================================
# Part 8. Validation
# ==========================================================

class TestValidation:

    def test_validate(
        self,
        full_hooks: MetricHooks,
    ):
        full_hooks.validate()

        assert full_hooks.is_valid() is True

    def test_validate_invalid_callback(self):
        hooks = MetricHooks()

        hooks.before_collect.append(123)  # type: ignore[arg-type]

        with pytest.raises(Exception):
            hooks.validate()

    def test_validate_invalid_collection(self):
        hooks = MetricHooks()

        hooks.before_collect = None  # type: ignore[assignment]

        with pytest.raises(Exception):
            hooks.validate()

    def test_is_valid(self):
        hooks = MetricHooks()

        assert hooks.is_valid() is True


# ==========================================================
# Part 9. Comparison
# ==========================================================

class TestComparison:

    def test_equals(
        self,
        empty_hooks: MetricHooks,
    ):
        other = empty_hooks.copy()

        assert empty_hooks == other

    def test_not_equals(
        self,
        empty_hooks: MetricHooks,
        custom_hooks: MetricHooks,
    ):
        assert empty_hooks != custom_hooks

    def test_hash(
        self,
        empty_hooks: MetricHooks,
    ):
        assert isinstance(hash(empty_hooks), int)

    def test_copy_equality(
        self,
        full_hooks: MetricHooks,
    ):
        copied = full_hooks.copy()

        assert copied == full_hooks
        assert copied is not full_hooks

# ==========================================================
# Part 10. Snapshot
# ==========================================================

class TestSnapshot:

    def test_copy(
        self,
        full_hooks: MetricHooks,
    ):
        copied = full_hooks.copy()

        assert copied == full_hooks
        assert copied is not full_hooks

    def test_deepcopy(
        self,
        full_hooks: MetricHooks,
    ):
        copied = copy.deepcopy(full_hooks)

        assert copied == full_hooks
        assert copied is not full_hooks

    def test_clone(
        self,
        full_hooks: MetricHooks,
    ):
        cloned = full_hooks.clone()

        assert cloned == full_hooks
        assert cloned is not full_hooks

    def test_replace(
        self,
        full_hooks: MetricHooks,
    ):
        replaced = full_hooks.replace()

        assert replaced == full_hooks
        assert replaced is not full_hooks


# ==========================================================
# Part 11. Python Protocols
# ==========================================================

class TestPythonProtocols:

    def test_repr(
        self,
        full_hooks: MetricHooks,
    ):
        assert isinstance(repr(full_hooks), str)

    def test_str(
        self,
        full_hooks: MetricHooks,
    ):
        assert isinstance(str(full_hooks), str)

    def test_bool(
        self,
        empty_hooks: MetricHooks,
        full_hooks: MetricHooks,
    ):
        assert bool(empty_hooks) is False
        assert bool(full_hooks) is True

    def test_len(
        self,
        full_hooks: MetricHooks,
    ):
        assert len(full_hooks) >= 0

    def test_iter(
        self,
        full_hooks: MetricHooks,
    ):
        assert list(iter(full_hooks)) == list(full_hooks.items())

    def test_contains(
        self,
        full_hooks: MetricHooks,
    ):
        item = next(iter(full_hooks.items()))
        assert item in full_hooks

    def test_getitem(
        self,
        full_hooks: MetricHooks,
    ):
        key = next(iter(full_hooks.keys()))
        assert full_hooks[key] == getattr(full_hooks, key)

    def test_setitem(
        self,
        empty_hooks: MetricHooks,
    ):
        callback = lambda: None

        empty_hooks["before_collect"] = [callback]

        assert callback in empty_hooks.before_collect

    def test_delitem(
        self,
        full_hooks: MetricHooks,
    ):
        full_hooks["before_collect"] = []

        del full_hooks["before_collect"]

        assert full_hooks.before_collect == []

    def test_hash_protocol(
        self,
        full_hooks: MetricHooks,
    ):
        assert isinstance(hash(full_hooks), int)


# ==========================================================
# Part 12. API Freeze
# ==========================================================

class TestAPIFreeze:

    def test_public_api(self):
        expected = {
            "copy",
            "clone",
            "deepcopy",
            "replace",
            "validate",
            "is_valid",
            "register_before_collect",
            "register_after_collect",
            "register_before_export",
            "register_after_export",
            "run_before_collect",
            "run_after_collect",
            "run_before_export",
            "run_after_export",
        }

        public = {
            name
            for name in dir(MetricHooks)
            if not name.startswith("_")
        }

        assert expected <= public

    def test_annotations(self):
        hints = get_type_hints(MetricHooks)

        assert isinstance(hints, dict)

    def test_slots(self):
        assert hasattr(MetricHooks, "__slots__")

    def test_signature(self):
        signature = inspect.signature(MetricHooks)

        assert signature is not None

    def test_pickle(
        self,
        full_hooks: MetricHooks,
    ):
        restored = pickle.loads(
            pickle.dumps(full_hooks),
        )

        assert restored == full_hooks                        