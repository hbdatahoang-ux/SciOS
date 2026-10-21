"""Tests for the Knowledge core public API."""

import importlib


def test_core_public_exports():
    core = importlib.import_module(
        "scios.cognitive_core.knowledge.core"
    )

    expected = {
        "Entity",
        "EntityType",
        "Relation",
        "RelationType",
        "Fact",
        "FactType",
        "KnowledgeGraph",
        "KnowledgeComponent",
        "KnowledgeError",
        "EntityError",
        "RelationError",
        "FactError",
        "GraphError",
    }

    assert set(core.__all__) == expected


def test_core_exports_are_importable():
    from scios.cognitive_core.knowledge.core import (
        Entity,
        EntityError,
        EntityType,
        Fact,
        FactError,
        FactType,
        GraphError,
        KnowledgeComponent,
        KnowledgeError,
        KnowledgeGraph,
        Relation,
        RelationError,
        RelationType,
    )

    assert Entity is not None
    assert EntityType is not None
    assert Relation is not None
    assert RelationType is not None
    assert Fact is not None
    assert FactType is not None
    assert KnowledgeGraph is not None
    assert KnowledgeComponent is not None
    assert KnowledgeError is not None
    assert EntityError is not None
    assert RelationError is not None
    assert FactError is not None
    assert GraphError is not None


def test_core_does_not_export_private_names():
    core = importlib.import_module(
        "scios.cognitive_core.knowledge.core"
    )

    assert all(not name.startswith("_") for name in core.__all__)

def test_package_public_export():
    from scios.cognitive_core.knowledge import (
        KnowledgeManager,
        KnowledgeSerializer,
    )

    assert KnowledgeManager is not None
    assert KnowledgeSerializer is not None


def test_package_all():
    import scios.cognitive_core.knowledge as knowledge

    assert knowledge.__all__ == [
        "KnowledgeManager",
        "KnowledgeSerializer",
    ]
