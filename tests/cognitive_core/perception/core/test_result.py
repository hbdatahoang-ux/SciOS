"""Contract tests for SciOS Cognitive Core Perception results."""

from __future__ import annotations

import pytest

from scios.cognitive_core.perception.core.errors import (
    PerceptionValidationError,
)
from scios.cognitive_core.perception.core.result import PerceptionResult
from scios.cognitive_core.perception.core.types import (
    Modality,
    PerceptionStatus,
)


def make_result(**overrides) -> PerceptionResult:
    values = {
        "status": PerceptionStatus.SUCCESS,
        "modality": Modality.TEXT,
    }
    values.update(overrides)
    return PerceptionResult(**values)


class TestPerceptionResultDefaults:
    """Tests for default result state."""

    def test_required_fields(self) -> None:
        result = make_result()

        assert result.status is PerceptionStatus.SUCCESS
        assert result.modality is Modality.TEXT

    def test_optional_fields_have_expected_defaults(self) -> None:
        result = make_result()

        assert result.content is None
        assert result.features == {}
        assert result.entities == []
        assert result.relations == []
        assert result.embedding is None
        assert result.confidence == 0.0
        assert result.metadata == {}

    def test_mutable_defaults_are_independent(self) -> None:
        first = make_result()
        second = make_result()

        first.features["x"] = 1
        first.entities.append({"name": "x"})
        first.relations.append({"type": "test"})
        first.metadata["source"] = "test"

        assert second.features == {}
        assert second.entities == []
        assert second.relations == []
        assert second.metadata == {}


class TestPerceptionResultValidation:
    """Tests for result validation."""

    def test_valid_result_passes(self) -> None:
        result = make_result(confidence=0.75)
        result.validate()

    @pytest.mark.parametrize("confidence", [0.0, 0.5, 1.0])
    def test_valid_confidence_range(self, confidence: float) -> None:
        result = make_result(confidence=confidence)
        result.validate()

    @pytest.mark.parametrize("confidence", [-0.01, 1.01, 2.0, -1.0])
    def test_invalid_confidence_raises(
        self,
        confidence: float,
    ) -> None:
        result = make_result(confidence=confidence)

        with pytest.raises(PerceptionValidationError):
            result.validate()

    def test_invalid_status_raises(self) -> None:
        result = make_result(status="success")

        with pytest.raises(PerceptionValidationError):
            result.validate()

    def test_invalid_modality_raises(self) -> None:
        result = make_result(modality="text")

        with pytest.raises(PerceptionValidationError):
            result.validate()

    def test_invalid_features_raises(self) -> None:
        result = make_result(features=[])

        with pytest.raises(PerceptionValidationError):
            result.validate()

    def test_invalid_entities_raises(self) -> None:
        result = make_result(entities={})

        with pytest.raises(PerceptionValidationError):
            result.validate()

    def test_invalid_relations_raises(self) -> None:
        result = make_result(relations={})

        with pytest.raises(PerceptionValidationError):
            result.validate()

    def test_invalid_metadata_raises(self) -> None:
        result = make_result(metadata=[])

        with pytest.raises(PerceptionValidationError):
            result.validate()


class TestPerceptionResultStatusProperties:
    """Tests for status convenience properties."""

    def test_successful(self) -> None:
        result = make_result(status=PerceptionStatus.SUCCESS)

        assert result.successful is True
        assert result.partial is False
        assert result.failed is False

    def test_partial(self) -> None:
        result = make_result(status=PerceptionStatus.PARTIAL)

        assert result.successful is False
        assert result.partial is True
        assert result.failed is False

    def test_failed(self) -> None:
        result = make_result(status=PerceptionStatus.FAILED)

        assert result.successful is False
        assert result.partial is False
        assert result.failed is True


class TestPerceptionResultSerialization:
    """Tests for structural serialization."""

    def test_to_dict_contains_all_fields(self) -> None:
        result = make_result(
            content="hello",
            features={"length": 5},
            entities=[{"type": "word"}],
            relations=[{"type": "contains"}],
            embedding=[0.1, 0.2],
            confidence=0.9,
            metadata={"source": "test"},
        )

        data = result.to_dict()

        assert data == {
            "status": "success",
            "modality": "text",
            "content": "hello",
            "features": {"length": 5},
            "entities": [{"type": "word"}],
            "relations": [{"type": "contains"}],
            "embedding": [0.1, 0.2],
            "confidence": 0.9,
            "metadata": {"source": "test"},
        }

    def test_to_dict_does_not_mutate_result(self) -> None:
        result = make_result(content="hello")
        data = result.to_dict()

        assert result.content == "hello"
        assert data["content"] == "hello"


class TestPerceptionResultContract:
    """Tests for the public class contract."""

    def test_is_dataclass(self) -> None:
        from dataclasses import is_dataclass

        assert is_dataclass(PerceptionResult)

    def test_public_export(self) -> None:
        from scios.cognitive_core.perception.core import result

        assert result.__all__ == ["PerceptionResult"]
        assert hasattr(result, "PerceptionResult")
