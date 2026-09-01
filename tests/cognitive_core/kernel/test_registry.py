"""
Tests for scios.cognitive_core.kernel.registry.
"""

from __future__ import annotations

import pytest

from scios.cognitive_core.kernel.context import CognitiveContext
from scios.cognitive_core.kernel.request import CognitiveRequest
from scios.cognitive_core.kernel.stage import CognitiveStage
from scios.cognitive_core.kernel.registry import StageRegistry


class DemoStage(CognitiveStage):
    """Concrete stage used by registry tests."""

    def run(self, context: CognitiveContext):
        return "ok"


class AnotherStage(CognitiveStage):
    """Second concrete stage used for registry isolation tests."""

    def run(self, context: CognitiveContext):
        return "another"


@pytest.fixture
def registry() -> StageRegistry:
    return StageRegistry()


@pytest.fixture
def demo_stage() -> DemoStage:
    return DemoStage("demo")


@pytest.fixture
def another_stage() -> AnotherStage:
    return AnotherStage("another")


def test_registry_can_be_instantiated():
    registry = StageRegistry()

    assert isinstance(registry, StageRegistry)


def test_registry_starts_empty(registry: StageRegistry):
    assert len(registry) == 0


def test_registry_is_empty(registry: StageRegistry):
    assert registry.is_empty is True


def test_register_stage(registry: StageRegistry, demo_stage: DemoStage):
    result = registry.register(demo_stage)

    assert result is demo_stage
    assert len(registry) == 1


def test_register_stage_can_be_retrieved(
    registry: StageRegistry,
    demo_stage: DemoStage,
):
    registry.register(demo_stage)

    result = registry.get("demo")

    assert result is demo_stage


def test_contains_registered_stage(
    registry: StageRegistry,
    demo_stage: DemoStage,
):
    registry.register(demo_stage)

    assert "demo" in registry
    assert registry.contains("demo") is True


def test_unregistered_stage_is_not_contained(
    registry: StageRegistry,
):
    assert "missing" not in registry
    assert registry.contains("missing") is False


def test_get_missing_stage_returns_none(
    registry: StageRegistry,
):
    assert registry.get("missing") is None


def test_register_multiple_stages(
    registry: StageRegistry,
    demo_stage: DemoStage,
    another_stage: AnotherStage,
):
    registry.register(demo_stage)
    registry.register(another_stage)

    assert len(registry) == 2
    assert registry.get("demo") is demo_stage
    assert registry.get("another") is another_stage


def test_stage_names_are_used_as_registry_keys(
    registry: StageRegistry,
):
    stage = DemoStage("reasoning")

    registry.register(stage)

    assert registry.get("reasoning") is stage
    assert registry.get("demo") is None


def test_register_returns_registered_stage(
    registry: StageRegistry,
):
    stage = DemoStage("reasoning")

    result = registry.register(stage)

    assert result is stage


def test_duplicate_registration_is_rejected(
    registry: StageRegistry,
    demo_stage: DemoStage,
):
    registry.register(demo_stage)

    with pytest.raises((ValueError, KeyError)):
        registry.register(DemoStage("demo"))


def test_duplicate_registration_does_not_replace_original(
    registry: StageRegistry,
    demo_stage: DemoStage,
):
    registry.register(demo_stage)

    duplicate = DemoStage("demo")

    with pytest.raises((ValueError, KeyError)):
        registry.register(duplicate)

    assert registry.get("demo") is demo_stage


def test_unregister_existing_stage(
    registry: StageRegistry,
    demo_stage: DemoStage,
):
    registry.register(demo_stage)

    result = registry.unregister("demo")

    assert result is demo_stage
    assert registry.get("demo") is None
    assert len(registry) == 0


def test_unregister_missing_stage(
    registry: StageRegistry,
):
    result = registry.unregister("missing")

    assert result is None


def test_clear_removes_all_stages(
    registry: StageRegistry,
    demo_stage: DemoStage,
    another_stage: AnotherStage,
):
    registry.register(demo_stage)
    registry.register(another_stage)

    registry.clear()

    assert len(registry) == 0
    assert registry.is_empty is True
    assert registry.get("demo") is None
    assert registry.get("another") is None


def test_clear_on_empty_registry_is_safe(
    registry: StageRegistry,
):
    registry.clear()

    assert len(registry) == 0
    assert registry.is_empty is True


def test_names_returns_registered_names(
    registry: StageRegistry,
    demo_stage: DemoStage,
    another_stage: AnotherStage,
):
    registry.register(demo_stage)
    registry.register(another_stage)

    names = registry.names()

    assert set(names) == {"demo", "another"}


def test_names_preserve_registration_order(
    registry: StageRegistry,
):
    first = DemoStage("first")
    second = DemoStage("second")
    third = DemoStage("third")

    registry.register(first)
    registry.register(second)
    registry.register(third)

    assert registry.names() == [
        "first",
        "second",
        "third",
    ]


def test_values_returns_registered_stages(
    registry: StageRegistry,
    demo_stage: DemoStage,
    another_stage: AnotherStage,
):
    registry.register(demo_stage)
    registry.register(another_stage)

    values = registry.values()

    assert list(values) == [
        demo_stage,
        another_stage,
    ]


def test_items_returns_name_stage_pairs(
    registry: StageRegistry,
    demo_stage: DemoStage,
    another_stage: AnotherStage,
):
    registry.register(demo_stage)
    registry.register(another_stage)

    items = registry.items()

    assert items == [
        ("demo", demo_stage),
        ("another", another_stage),
    ]


def test_iteration_returns_stage_names(
    registry: StageRegistry,
):
    registry.register(DemoStage("first"))
    registry.register(DemoStage("second"))

    assert list(registry) == [
        "first",
        "second",
    ]


def test_registry_does_not_share_state_between_instances():
    first = StageRegistry()
    second = StageRegistry()

    first.register(DemoStage("demo"))

    assert len(first) == 1
    assert len(second) == 0
    assert second.get("demo") is None


def test_register_rejects_non_stage(
    registry: StageRegistry,
):
    with pytest.raises((TypeError, ValueError)):
        registry.register(object())


def test_register_rejects_invalid_name(
    registry: StageRegistry,
):
    stage = DemoStage("")

    with pytest.raises((ValueError, KeyError)):
        registry.register(stage)


def test_get_returns_exact_object(
    registry: StageRegistry,
):
    stage = DemoStage("exact")

    registry.register(stage)

    assert registry.get("exact") is stage


def test_registry_supports_bracket_lookup(
    registry: StageRegistry,
):
    stage = DemoStage("demo")

    registry.register(stage)

    assert registry["demo"] is stage


def test_bracket_lookup_missing_name_raises_key_error(
    registry: StageRegistry,
):
    with pytest.raises(KeyError):
        registry["missing"]


def test_registry_length_tracks_registration(
    registry: StageRegistry,
):
    assert len(registry) == 0

    registry.register(DemoStage("one"))
    assert len(registry) == 1

    registry.register(DemoStage("two"))
    assert len(registry) == 2

    registry.unregister("one")
    assert len(registry) == 1


def test_repr_contains_registry_name():
    registry = StageRegistry()

    result = repr(registry)

    assert "StageRegistry" in result


def test_repr_contains_registered_count(
    registry: StageRegistry,
):
    registry.register(DemoStage("demo"))

    result = repr(registry)

    assert "1" in result


def test_registry_can_store_same_stage_instance_only_once(
    registry: StageRegistry,
):
    stage = DemoStage("demo")

    registry.register(stage)

    with pytest.raises((ValueError, KeyError)):
        registry.register(stage)

    assert len(registry) == 1


def test_unregister_then_register_again(
    registry: StageRegistry,
):
    first = DemoStage("demo")

    registry.register(first)
    removed = registry.unregister("demo")

    assert removed is first

    second = DemoStage("demo")
    registry.register(second)

    assert registry.get("demo") is second
    assert len(registry) == 1


def test_registry_preserves_stage_object_state(
    registry: StageRegistry,
):
    stage = DemoStage("demo")

    stage.status = "ready"
    stage.message = "prepared"

    registry.register(stage)

    result = registry.get("demo")

    assert result is stage
    assert result.status == "ready"
    assert result.message == "prepared"


def test_registry_registration_does_not_execute_stage(
    registry: StageRegistry,
):
    stage = DemoStage("demo")

    registry.register(stage)

    assert stage.executions == 0


def test_registry_registration_does_not_initialize_stage(
    registry: StageRegistry,
):
    stage = DemoStage("demo")

    registry.register(stage)

    assert stage.status == "idle"


def test_registry_contains_only_registered_names(
    registry: StageRegistry,
):
    registry.register(DemoStage("demo"))

    assert set(registry.names()) == {"demo"}


def test_registry_clear_allows_fresh_registration(
    registry: StageRegistry,
):
    registry.register(DemoStage("first"))
    registry.register(DemoStage("second"))

    registry.clear()

    stage = DemoStage("third")
    registry.register(stage)

    assert len(registry) == 1
    assert registry.get("third") is stage


def test_registry_items_are_independent_from_internal_mapping(
    registry: StageRegistry,
):
    registry.register(DemoStage("demo"))

    items = registry.items()

    assert items == [("demo", registry.get("demo"))]


def test_registry_values_are_independent_from_internal_mapping(
    registry: StageRegistry,
):
    stage = DemoStage("demo")
    registry.register(stage)

    values = registry.values()

    assert list(values) == [stage]


def test_registry_names_are_independent_from_internal_mapping(
    registry: StageRegistry,
):
    registry.register(DemoStage("demo"))

    names = registry.names()

    assert names == ["demo"]
