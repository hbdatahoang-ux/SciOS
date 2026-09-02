"""Contract tests for perception.registry public API."""

from __future__ import annotations

from scios.cognitive_core.perception import registry


def test_registry_all_is_exact() -> None:
    assert registry.__all__ == ["PerceptorRegistry"]


def test_perceptor_registry_is_exported() -> None:
    from scios.cognitive_core.perception.registry import PerceptorRegistry

    assert registry.PerceptorRegistry is PerceptorRegistry
