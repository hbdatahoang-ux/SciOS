"""Contract tests for PerceptorFactory."""

from __future__ import annotations

import pytest

from scios.cognitive_core.perception.core import (
    BasePerceptor,
    Modality,
    PerceptionResult,
    PerceptionStatus,
)
from scios.cognitive_core.perception.factory.factory import (
    PerceptorFactory,
)
from scios.cognitive_core.perception.registry import PerceptorRegistry


class TextPerceptor(BasePerceptor):
    """Minimal text perceptor for factory tests."""

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
    """Minimal image perceptor for factory tests."""

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


class TestPerceptorFactory:
    """Tests for the factory contract."""

    def test_constructor_requires_registry(self) -> None:
        registry = PerceptorRegistry()

        factory = PerceptorFactory(registry)

        assert factory.registry is registry

    def test_constructor_rejects_invalid_registry(self) -> None:
        with pytest.raises(TypeError, match="PerceptorRegistry"):
            PerceptorFactory(object())  # type: ignore[arg-type]

    def test_create_returns_registered_perceptor(self) -> None:
        registry = PerceptorRegistry()
        perceptor = TextPerceptor()

        registry.register(perceptor)

        factory = PerceptorFactory(registry)

        result = factory.create("text")

        assert result is perceptor

    def test_create_preserves_perceptor_identity(self) -> None:
        registry = PerceptorRegistry()
        perceptor = TextPerceptor()

        registry.register(perceptor)

        factory = PerceptorFactory(registry)

        assert factory.create("text") is factory.create("text")

    def test_create_supports_multiple_perceptors(self) -> None:
        registry = PerceptorRegistry()

        text = TextPerceptor()
        image = ImagePerceptor()

        registry.register(text)
        registry.register(image)

        factory = PerceptorFactory(registry)

        assert factory.create("text") is text
        assert factory.create("image") is image

    def test_create_missing_name_raises_key_error(self) -> None:
        registry = PerceptorRegistry()
        factory = PerceptorFactory(registry)

        with pytest.raises(KeyError, match="not registered"):
            factory.create("missing")

    def test_factory_does_not_register_automatically(self) -> None:
        registry = PerceptorRegistry()
        factory = PerceptorFactory(registry)

        assert len(registry) == 0

        with pytest.raises(KeyError):
            factory.create("text")

    def test_factory_returns_base_perceptor_contract(self) -> None:
        registry = PerceptorRegistry()
        registry.register(TextPerceptor())

        factory = PerceptorFactory(registry)

        result = factory.create("text")

        assert isinstance(result, BasePerceptor)


class TestPerceptorFactoryPublicAPI:
    """Tests for the factory module public API."""

    def test_all_is_exact(self) -> None:
        from scios.cognitive_core.perception.factory import factory

        assert factory.__all__ == ["PerceptorFactory"]

    def test_export_is_available(self) -> None:
        from scios.cognitive_core.perception.factory import factory

        assert factory.PerceptorFactory is PerceptorFactory
