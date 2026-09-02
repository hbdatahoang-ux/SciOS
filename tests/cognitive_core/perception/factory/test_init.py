"""Contract tests for perception.factory public API."""

from __future__ import annotations

from scios.cognitive_core.perception import factory


def test_factory_all_is_exact() -> None:
    assert factory.__all__ == ["PerceptorFactory"]


def test_perceptor_factory_is_exported() -> None:
    from scios.cognitive_core.perception.factory import PerceptorFactory

    assert factory.PerceptorFactory is PerceptorFactory
