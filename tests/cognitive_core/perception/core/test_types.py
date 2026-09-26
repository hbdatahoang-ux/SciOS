"""Contract tests for SciOS Cognitive Core Perception core types."""

from __future__ import annotations

from typing import get_args, get_origin

from typing import Any, get_args, get_origin

from scios.cognitive_core.perception.core.types import (
    Embedding,
    Entities,
    Entity,
    Features,
    Metadata,
    Modality,
    PerceptionStatus,
    RawInput,
    Relation,
    Relations,
)


class TestModality:
    """Tests for the Modality enum contract."""

    def test_members_are_exact(self) -> None:
        assert list(Modality) == [
            Modality.TEXT,
            Modality.IMAGE,
            Modality.AUDIO,
            Modality.VIDEO,
            Modality.DOCUMENT,
            Modality.SENSOR,
        ]

    def test_values_are_exact(self) -> None:
        assert [member.value for member in Modality] == [
            "text",
            "image",
            "audio",
            "video",
            "document",
            "sensor",
        ]

    def test_is_string_compatible(self) -> None:
        assert isinstance(Modality.TEXT, str)
        assert Modality.TEXT == "text"

    def test_names_are_exact(self) -> None:
        assert [member.name for member in Modality] == [
            "TEXT",
            "IMAGE",
            "AUDIO",
            "VIDEO",
            "DOCUMENT",
            "SENSOR",
        ]

    def test_lookup_by_value(self) -> None:
        assert Modality("text") is Modality.TEXT
        assert Modality("image") is Modality.IMAGE
        assert Modality("audio") is Modality.AUDIO
        assert Modality("video") is Modality.VIDEO
        assert Modality("document") is Modality.DOCUMENT
        assert Modality("sensor") is Modality.SENSOR


class TestPerceptionStatus:
    """Tests for the PerceptionStatus enum contract."""

    def test_members_are_exact(self) -> None:
        assert list(PerceptionStatus) == [
            PerceptionStatus.SUCCESS,
            PerceptionStatus.PARTIAL,
            PerceptionStatus.FAILED,
        ]

    def test_values_are_exact(self) -> None:
        assert [member.value for member in PerceptionStatus] == [
            "success",
            "partial",
            "failed",
        ]

    def test_is_string_compatible(self) -> None:
        assert isinstance(PerceptionStatus.SUCCESS, str)
        assert PerceptionStatus.SUCCESS == "success"

    def test_names_are_exact(self) -> None:
        assert [member.name for member in PerceptionStatus] == [
            "SUCCESS",
            "PARTIAL",
            "FAILED",
        ]

    def test_lookup_by_value(self) -> None:
        assert PerceptionStatus("success") is PerceptionStatus.SUCCESS
        assert PerceptionStatus("partial") is PerceptionStatus.PARTIAL
        assert PerceptionStatus("failed") is PerceptionStatus.FAILED


class TestTypeAliases:
    """Tests for the public type-alias contract."""

    def test_entity_is_dict_of_string_to_any(self) -> None:
        assert get_origin(Entity) is dict

    def test_relation_is_dict_of_string_to_any(self) -> None:
        assert get_origin(Relation) is dict

    def test_entities_is_list_of_entity(self) -> None:
        assert get_origin(Entities) is list
        assert get_args(Entities) == (Entity,)

    def test_relations_is_list_of_relation(self) -> None:
        assert get_origin(Relations) is list
        assert get_args(Relations) == (Relation,)

    def test_metadata_is_dict_of_string_to_any(self) -> None:
        assert get_origin(Metadata) is dict

        args = get_args(Metadata)
        assert args[0] is str
        assert args[1] is Any


    def test_features_is_dict_of_string_to_any(self) -> None:
        assert get_origin(Features) is dict

        args = get_args(Features)
        assert args[0] is str
        assert args[1] is Any

    def test_raw_input_exists(self) -> None:
        assert RawInput is not None

    def test_embedding_exists(self) -> None:
        assert Embedding is not None


class TestPublicExports:
    """Tests for the module's explicit public API."""

    def test_all_is_exact(self) -> None:
        from scios.cognitive_core.perception.core import types

        assert types.__all__ == [
            "Embedding",
            "Entities",
            "Entity",
            "Features",
            "Metadata",
            "Modality",
            "PerceptionStatus",
            "RawInput",
            "Relation",
            "Relations",
        ]

    def test_all_exports_are_available(self) -> None:
        from scios.cognitive_core.perception.core import types

        for name in types.__all__:
            assert hasattr(types, name)