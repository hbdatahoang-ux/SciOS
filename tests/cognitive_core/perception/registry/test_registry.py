"""Contract tests for PerceptorRegistry."""

from __future__ import annotations

import pytest

from scios.cognitive_core.perception.core import (
    BasePerceptor,
    Modality,
    PerceptionResult,
    PerceptionStatus,
)
from scios.cognitive_core.perception.registry.registry import (
    PerceptorRegistry,
)


class TextPerceptor(BasePerceptor):
    """Minimal text perceptor for registry tests."""

    def __init__(self, name: str = "text") -> None:
        super().__init__(
            name=name,
            modality=Modality.TEXT,
        )

    def perceive(
        self,
        raw_input,
        metadata=None,
    ) -> PerceptionResult:
        return PerceptionResult(
            status=PerceptionStatus.SUCCESS,
            modality=self.modality,
            content=raw_input,
            metadata=metadata or {},
        )


class ImagePerceptor(BasePerceptor):
    """Minimal image perceptor for registry tests."""

    def __init__(self, name: str = "image") -> None:
        super().__init__(
            name=name,
            modality=Modality.IMAGE,
        )

    def perceive(
        self,
        raw_input,
        metadata=None,
    ) -> PerceptionResult:
        return PerceptionResult(
            status=PerceptionStatus.SUCCESS,
            modality=self.modality,
            content=raw_input,
            metadata=metadata or {},
        )


class TestPerceptorRegistry:

    def test_initial_registry_is_empty(self) -> None:
        registry = PerceptorRegistry()

        assert len(registry) == 0
        assert registry.list() == []

    def test_register_returns_perceptor(self) -> None:
        registry = PerceptorRegistry()
        perceptor = TextPerceptor()

        result = registry.register(perceptor)

        assert result is perceptor

    def test_register_stores_perceptor_by_name(self) -> None:
        registry = PerceptorRegistry()
        perceptor = TextPerceptor()

        registry.register(perceptor)

        assert registry.get("text") is perceptor

    def test_register_increases_length(self) -> None:
        registry = PerceptorRegistry()

        registry.register(TextPerceptor())

        assert len(registry) == 1

    def test_register_rejects_non_perceptor(self) -> None:
        registry = PerceptorRegistry()

        with pytest.raises(TypeError, match="BasePerceptor"):
            registry.register(object())  # type: ignore[arg-type]

    def test_duplicate_name_is_rejected(self) -> None:
        registry = PerceptorRegistry()

        registry.register(TextPerceptor())

        with pytest.raises(ValueError, match="already registered"):
            registry.register(TextPerceptor())

    def test_get_returns_registered_perceptor(self) -> None:
        registry = PerceptorRegistry()
        perceptor = TextPerceptor()

        registry.register(perceptor)

        assert registry.get("text") is perceptor

    def test_get_missing_name_raises_key_error(self) -> None:
        registry = PerceptorRegistry()

        with pytest.raises(KeyError, match="not registered"):
            registry.get("missing")

    def test_has_returns_true_for_registered_name(self) -> None:
        registry = PerceptorRegistry()
        registry.register(TextPerceptor())

        assert registry.has("text") is True

    def test_has_returns_false_for_missing_name(self) -> None:
        registry = PerceptorRegistry()

        assert registry.has("missing") is False

    def test_contains_matches_has(self) -> None:
        registry = PerceptorRegistry()
        registry.register(TextPerceptor())

        assert "text" in registry
        assert "missing" not in registry

    def test_list_preserves_insertion_order(self) -> None:
        registry = PerceptorRegistry()

        registry.register(TextPerceptor("text"))
        registry.register(ImagePerceptor("image"))

        assert registry.list() == ["text", "image"]

    def test_unregister_returns_removed_perceptor(self) -> None:
        registry = PerceptorRegistry()
        perceptor = TextPerceptor()

        registry.register(perceptor)

        result = registry.unregister("text")

        assert result is perceptor
        assert len(registry) == 0

    def test_unregister_missing_name_raises_key_error(self) -> None:
        registry = PerceptorRegistry()

        with pytest.raises(KeyError, match="not registered"):
            registry.unregister("missing")

    def test_clear_removes_all_perceptors(self) -> None:
        registry = PerceptorRegistry()

        registry.register(TextPerceptor("text"))
        registry.register(ImagePerceptor("image"))

        registry.clear()

        assert len(registry) == 0
        assert registry.list() == []

    def test_iterates_over_names(self) -> None:
        registry = PerceptorRegistry()

        registry.register(TextPerceptor("text"))
        registry.register(ImagePerceptor("image"))

        assert list(registry) == ["text", "image"]


class TestPerceptorRegistryPublicAPI:

    def test_all_is_exact(self) -> None:
        from scios.cognitive_core.perception.registry import registry

        assert registry.__all__ == ["PerceptorRegistry"]

    def test_export_is_available(self) -> None:
        from scios.cognitive_core.perception.registry import registry

        assert registry.PerceptorRegistry is PerceptorRegistry
