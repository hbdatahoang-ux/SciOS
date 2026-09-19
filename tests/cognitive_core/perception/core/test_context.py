"""Contract tests for SciOS Cognitive Core Perception context."""

from __future__ import annotations

import pytest

from scios.cognitive_core.perception.core.context import PerceptionContext
from scios.cognitive_core.perception.core.result import PerceptionResult
from scios.cognitive_core.perception.core.types import (
    Modality,
    PerceptionStatus,
)


def make_result(
    *,
    modality: Modality = Modality.TEXT,
    status: PerceptionStatus = PerceptionStatus.SUCCESS,
    confidence: float = 0.8,
) -> PerceptionResult:
    return PerceptionResult(
        status=status,
        modality=modality,
        confidence=confidence,
    )


def make_context(**overrides) -> PerceptionContext:
    values = {
        "raw_input": "hello",
        "modality": Modality.TEXT,
        "result": make_result(),
    }
    values.update(overrides)
    return PerceptionContext(**values)


class TestPerceptionContextDefaults:
    """Tests for context defaults."""

    def test_required_fields(self) -> None:
        context = make_context()

        assert context.raw_input == "hello"
        assert context.modality is Modality.TEXT
        assert isinstance(context.result, PerceptionResult)

    def test_optional_fields(self) -> None:
        context = make_context()

        assert context.metadata == {}
        assert context.context_id is None

    def test_metadata_defaults_are_independent(self) -> None:
        first = make_context()
        second = make_context()

        first.metadata["source"] = "test"

        assert second.metadata == {}


class TestPerceptionContextProperties:
    """Tests for context convenience properties."""

    def test_successful(self) -> None:
        context = make_context(
            result=make_result(
                status=PerceptionStatus.SUCCESS,
                confidence=0.9,
            )
        )

        assert context.successful is True
        assert context.partial is False
        assert context.failed is False
        assert context.confidence == 0.9

    def test_partial(self) -> None:
        context = make_context(
            result=make_result(
                status=PerceptionStatus.PARTIAL,
                confidence=0.5,
            )
        )

        assert context.successful is False
        assert context.partial is True
        assert context.failed is False
        assert context.confidence == 0.5

    def test_failed(self) -> None:
        context = make_context(
            result=make_result(
                status=PerceptionStatus.FAILED,
                confidence=0.0,
            )
        )

        assert context.successful is False
        assert context.partial is False
        assert context.failed is True
        assert context.confidence == 0.0


class TestPerceptionContextValidation:
    """Tests for context validation."""

    def test_valid_context_passes(self) -> None:
        context = make_context()

        context.validate()

    def test_invalid_modality_type_raises(self) -> None:
        context = make_context(modality="text")

        with pytest.raises(TypeError, match="modality"):
            context.validate()

    def test_invalid_result_type_raises(self) -> None:
        context = make_context(result="invalid")

        with pytest.raises(TypeError, match="result"):
            context.validate()

    def test_mismatched_modality_raises(self) -> None:
        context = make_context(
            modality=Modality.IMAGE,
            result=make_result(modality=Modality.TEXT),
        )

        with pytest.raises(
            ValueError,
            match="context modality must match result modality",
        ):
            context.validate()

    def test_invalid_metadata_raises(self) -> None:
        context = make_context(metadata=[])

        with pytest.raises(TypeError, match="metadata"):
            context.validate()

    def test_result_validation_is_delegated(self) -> None:
        result = make_result()
        result.confidence = 2.0

        context = make_context(result=result)

        with pytest.raises(Exception):
            context.validate()


class TestPerceptionContextSerialization:
    """Tests for structural serialization."""

    def test_to_dict_contains_all_fields(self) -> None:
        result = make_result(confidence=0.75)

        context = make_context(
            result=result,
            metadata={"source": "test"},
            context_id="ctx-001",
        )

        data = context.to_dict()

        assert data == {
            "raw_input": "hello",
            "modality": "text",
            "result": result.to_dict(),
            "metadata": {"source": "test"},
            "context_id": "ctx-001",
        }

    def test_to_dict_preserves_raw_input(self) -> None:
        context = make_context(raw_input={"message": "hello"})

        assert context.to_dict()["raw_input"] == {"message": "hello"}


class TestPerceptionContextContract:
    """Tests for the public class contract."""

    def test_is_dataclass(self) -> None:
        from dataclasses import is_dataclass

        assert is_dataclass(PerceptionContext)

    def test_public_export(self) -> None:
        from scios.cognitive_core.perception.core import context

        assert context.__all__ == ["PerceptionContext"]
        assert hasattr(context, "PerceptionContext")
