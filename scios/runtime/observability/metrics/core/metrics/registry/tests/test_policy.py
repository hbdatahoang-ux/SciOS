"""
Tests for MetricPolicy.
"""

from __future__ import annotations

import inspect

from scios.runtime.observability.metrics.core.metrics.registry.policy import (
    MetricPolicy,
)

__all__: list[str] = []


# ==============================================================================
# Part 1. Constructor
# ==============================================================================


def test_default_constructor():

    policy = MetricPolicy()

    assert policy.name == ""
    assert policy.enabled is True
    assert isinstance(policy.rules, dict)
    assert isinstance(policy.state, dict)


def test_custom_constructor():

    policy = MetricPolicy(
        name="runtime",
        enabled=False,
    )

    assert policy.name == "runtime"
    assert policy.enabled is False


def test_slots():

    assert hasattr(
        MetricPolicy,
        "__slots__",
    )


def test_annotations():

    annotations = MetricPolicy.__annotations__

    assert "name" in annotations
    assert "enabled" in annotations
    assert "rules" in annotations
    assert "state" in annotations


def test_signature():

    sig = inspect.signature(
        MetricPolicy
    )

    assert "name" in sig.parameters


# ==============================================================================
# Part 2. Properties
# ==============================================================================


def test_name_property():

    policy = MetricPolicy(
        "cpu"
    )

    assert policy.name == "cpu"


def test_enabled_property():

    policy = MetricPolicy()

    assert policy.enabled is True


def test_rules_property():

    policy = MetricPolicy()

    assert isinstance(
        policy.rules,
        dict,
    )


def test_size_property():

    policy = MetricPolicy()

    assert policy.size == 0


def test_state_property():

    policy = MetricPolicy()

    assert isinstance(
        policy.state,
        dict,
    )


# ==============================================================================
# Part 3. Operations
# ==============================================================================


def test_add_rule():

    policy = MetricPolicy()

    policy.add_rule(
        "sample_rate",
        0.5,
    )

    assert policy.size == 1


def test_remove_rule():

    policy = MetricPolicy()

    policy.add_rule(
        "sample_rate",
        0.5,
    )

    policy.remove_rule(
        "sample_rate"
    )

    assert policy.size == 0


def test_get_rule():

    policy = MetricPolicy()

    policy.add_rule(
        "sample_rate",
        0.5,
    )

    assert (
        policy.get_rule(
            "sample_rate"
        )
        == 0.5
    )


def test_contains_rule():

    policy = MetricPolicy()

    policy.add_rule(
        "sample_rate",
        0.5,
    )

    assert policy.contains_rule(
        "sample_rate"
    )


def test_clear():

    policy = MetricPolicy()

    policy.add_rule(
        "sample_rate",
        0.5,
    )

    policy.clear()

    assert policy.size == 0


def test_list_rules():

    policy = MetricPolicy()

    policy.add_rule("a", 1)
    policy.add_rule("b", 2)

    rules = policy.list_rules()

    assert isinstance(
        rules,
        list,
    )

    assert len(rules) == 2


def test_normalize():

    policy = MetricPolicy(
        " Runtime "
    )

    policy.normalize()

    assert policy.name == "runtime"


# ==============================================================================
# Part 4. Serialization
# ==============================================================================


def test_to_dict():

    policy = MetricPolicy(
        "cpu"
    )

    data = policy.to_dict()

    assert data["name"] == "cpu"


def test_from_dict():

    policy = MetricPolicy.from_dict(
        {
            "name": "runtime",
            "enabled": False,
            "rules": {},
            "state": {},
        }
    )

    assert policy.name == "runtime"
    assert policy.enabled is False


def test_to_tuple():

    policy = MetricPolicy(
        "cpu"
    )

    value = policy.to_tuple()

    assert isinstance(
        value,
        tuple,
    )


def test_from_tuple():

    policy = MetricPolicy(
        "cpu"
    )

    restored = MetricPolicy.from_tuple(
        policy.to_tuple()
    )

    assert restored == policy


def test_snapshot():

    policy = MetricPolicy(
        "cpu"
    )

    snapshot = policy.snapshot()

    assert isinstance(
        snapshot,
        dict,
    )


def test_restore():

    policy = MetricPolicy()

    policy.restore(
        {
            "name": "runtime",
            "enabled": False,
            "rules": {},
            "state": {},
        }
    )

    assert policy.name == "runtime"
    assert policy.enabled is False


# ==============================================================================
# Part 5. Validation
# ==============================================================================


def test_validate_name():

    assert MetricPolicy.validate_name(
        "cpu"
    )


def test_validate_rules():

    assert MetricPolicy.validate_rules(
        {}
    )


def test_validate_policy():

    policy = MetricPolicy()

    assert MetricPolicy.validate_policy(
        policy
    )


def test_validate():

    policy = MetricPolicy()

    assert policy.validate()

# ==============================================================================
# Part 6. Utilities
# ==============================================================================


def test_clone():

    policy = MetricPolicy(
        "runtime"
    )

    cloned = policy.clone()

    assert cloned == policy
    assert cloned is not policy


def test_copy():

    policy = MetricPolicy(
        "runtime"
    )

    copied = policy.copy()

    assert copied == policy
    assert copied is not policy


def test_merge():

    a = MetricPolicy()

    b = MetricPolicy()

    b.add_rule(
        "sample_rate",
        0.5,
    )

    a.merge(b)

    assert a.size == 1
    assert (
        a.get_rule(
            "sample_rate"
        )
        == 0.5
    )


def test_update():

    a = MetricPolicy()

    b = MetricPolicy()

    b.add_rule(
        "export_interval",
        10,
    )

    a.update(b)

    assert a.size == 1
    assert (
        a.get_rule(
            "export_interval"
        )
        == 10
    )


def test_reset():

    policy = MetricPolicy()

    policy.add_rule(
        "sample_rate",
        0.5,
    )

    policy.reset()

    assert policy.size == 0
    assert policy.rules == {}


# ==============================================================================
# Part 7. Protocols
# ==============================================================================


def test_hash():

    policy = MetricPolicy()

    assert isinstance(
        hash(policy),
        int,
    )


def test_eq():

    a = MetricPolicy()

    b = MetricPolicy()

    assert a == b


def test_repr():

    policy = MetricPolicy()

    assert "MetricPolicy" in repr(
        policy
    )


def test_str():

    policy = MetricPolicy()

    assert isinstance(
        str(policy),
        str,
    )


def test_bool():

    policy = MetricPolicy()

    assert not policy

    policy.add_rule(
        "sample_rate",
        0.5,
    )

    assert policy


# ==============================================================================
# Part 8. Diagnostics
# ==============================================================================


def test_summary():

    policy = MetricPolicy()

    summary = policy.summary()

    assert isinstance(
        summary,
        dict,
    )


def test_diagnostics():

    policy = MetricPolicy()

    diagnostics = policy.diagnostics()

    assert diagnostics["valid"]


def test_policy_report():

    policy = MetricPolicy()

    report = policy.policy_report()

    assert isinstance(
        report,
        dict,
    )

    assert "summary" in report


def test_overall_status():

    policy = MetricPolicy()

    assert (
        policy.overall_status()
        == "healthy"
    )


# ==============================================================================
# Part 9. Public API
# ==============================================================================


def test_public_api():

    from scios.runtime.observability.metrics.core.metrics.registry.policy import (
        __all__,
    )

    assert "MetricPolicy" in __all__    