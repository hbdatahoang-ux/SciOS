"""Contract tests for the SciOS Cognitive Core BasePerceptor."""

from __future__ import annotations

from abc import ABC

import pytest

from scios.cognitive_core.perception.core.base import BasePerceptor
from scios.cognitive_core.perception.core.result import PerceptionResult
from scios.cognitive_core.perception.core.types import (
    Modality,
    PerceptionStatus,
)


class ConcretePerceptor(BasePerceptor):
    """Minimal concrete implementation for contract testing."""

    def __init__(self) -> None:
        super().__init__(
            name="test-perceptor",
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


class TestBasePerceptorContract:
    """Tests for the abstract base contract."""

    def test_is_abstract_base_class(self) -> None:
        assert issubclass(BasePerceptor, ABC)
        assert BasePerceptor.__abstractmethods__ == {"perceive"}

    def test_cannot_be_instantiated_directly(self) -> None:
        with pytest.raises(TypeError):
            BasePerceptor(
                name="test",
                modality=Modality.TEXT,
            )

    def test_concrete_perceptor_can_be_instantiated(self) -> None:
        perceptor = ConcretePerceptor()

        assert perceptor.name == "test-perceptor"
        assert perceptor.modality is Modality.TEXT

    def test_name_must_be_non_empty_string(self) -> None:
        with pytest.raises(ValueError, match="name"):
            ConcreteInvalidNamePerceptor()

    def test_modality_must_be_modality(self) -> None:
        with pytest.raises(TypeError, match="modality"):
            ConcreteInvalidModalityPerceptor()

    def test_perceive_returns_perception_result(self) -> None:
        perceptor = ConcretePerceptor()

        result = perceptor.perceive("hello")

        assert isinstance(result, PerceptionResult)
        assert result.status is PerceptionStatus.SUCCESS
        assert result.modality is Modality.TEXT
        assert result.content == "hello"

    def test_metadata_is_forwarded(self) -> None:
        perceptor = ConcretePerceptor()

        metadata = {"source": "test"}
        result = perceptor.perceive("hello", metadata)

        assert result.metadata == metadata


class ConcreteInvalidNamePerceptor(BasePerceptor):
    """Invalid-name implementation."""

    def __init__(self) -> None:
        super().__init__(
            name="",
            modality=Modality.TEXT,
        )

    def perceive(
        self,
        raw_input,
        metadata=None,
    ) -> PerceptionResult:
        raise NotImplementedError


class ConcreteInvalidModalityPerceptor(BasePerceptor):
    """Invalid-modality implementation."""

    def __init__(self) -> None:
        super().__init__(
            name="test",
            modality="text",
        )

    def perceive(
        self,
        raw_input,
        metadata=None,
    ) -> PerceptionResult:
        raise NotImplementedError


class TestBasePerceptorPublicAPI:
    """Tests for the public API surface."""

    def test_all_is_exact(self) -> None:
        from scios.cognitive_core.perception.core import base

        assert base.__all__ == ["BasePerceptor"]

    def test_export_is_available(self) -> None:
        from scios.cognitive_core.perception.core import base

        assert hasattr(base, "BasePerceptor")
