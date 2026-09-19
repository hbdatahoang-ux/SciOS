"""Core type definitions for the Knowledge subsystem."""

from __future__ import annotations

from enum import Enum


class EntityType(str, Enum):
    """Supported semantic entity categories."""

    CONCEPT = "concept"
    OBJECT = "object"
    PERSON = "person"
    PLACE = "place"
    EVENT = "event"
    ORGANIZATION = "organization"


class RelationType(str, Enum):
    """Supported semantic relation categories."""

    ASSOCIATED_WITH = "associated_with"
    PART_OF = "part_of"
    INSTANCE_OF = "instance_of"
    CAUSES = "causes"
    DEPENDS_ON = "depends_on"
    LOCATED_IN = "located_in"


class FactType(str, Enum):
    """Supported fact categories."""

    ASSERTION = "assertion"
    OBSERVATION = "observation"
    RULE = "rule"


__all__ = [
    "EntityType",
    "RelationType",
    "FactType",
]