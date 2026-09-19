"""Contract tests for Knowledge core types."""

from enum import Enum

from scios.cognitive_core.knowledge.core.types import (
    EntityType,
    FactType,
    RelationType,
)


class TestEntityType:
    def test_is_string_enum(self):
        assert issubclass(EntityType, str)
        assert issubclass(EntityType, Enum)

    def test_values(self):
        assert EntityType.CONCEPT.value == "concept"
        assert EntityType.OBJECT.value == "object"
        assert EntityType.PERSON.value == "person"
        assert EntityType.PLACE.value == "place"
        assert EntityType.EVENT.value == "event"
        assert EntityType.ORGANIZATION.value == "organization"

    def test_members_are_stable(self):
        assert list(EntityType) == [
            EntityType.CONCEPT,
            EntityType.OBJECT,
            EntityType.PERSON,
            EntityType.PLACE,
            EntityType.EVENT,
            EntityType.ORGANIZATION,
        ]


class TestRelationType:
    def test_is_string_enum(self):
        assert issubclass(RelationType, str)
        assert issubclass(RelationType, Enum)

    def test_values(self):
        assert RelationType.ASSOCIATED_WITH.value == "associated_with"
        assert RelationType.PART_OF.value == "part_of"
        assert RelationType.INSTANCE_OF.value == "instance_of"
        assert RelationType.CAUSES.value == "causes"
        assert RelationType.DEPENDS_ON.value == "depends_on"
        assert RelationType.LOCATED_IN.value == "located_in"

    def test_members_are_stable(self):
        assert list(RelationType) == [
            RelationType.ASSOCIATED_WITH,
            RelationType.PART_OF,
            RelationType.INSTANCE_OF,
            RelationType.CAUSES,
            RelationType.DEPENDS_ON,
            RelationType.LOCATED_IN,
        ]


class TestFactType:
    def test_is_string_enum(self):
        assert issubclass(FactType, str)
        assert issubclass(FactType, Enum)

    def test_values(self):
        assert FactType.ASSERTION.value == "assertion"
        assert FactType.OBSERVATION.value == "observation"
        assert FactType.RULE.value == "rule"

    def test_members_are_stable(self):
        assert list(FactType) == [
            FactType.ASSERTION,
            FactType.OBSERVATION,
            FactType.RULE,
        ]


class TestPublicExports:
    def test_all_exports(self):
        from scios.cognitive_core.knowledge.core import types

        assert types.__all__ == [
            "EntityType",
            "RelationType",
            "FactType",
        ]

    def test_imports_are_available(self):
        from scios.cognitive_core.knowledge.core.types import (
            EntityType,
            FactType,
            RelationType,
        )

        assert EntityType is not None
        assert RelationType is not None
        assert FactType is not None
