"""Tests for the Knowledge stores public API."""

import importlib


def test_stores_public_exports():
    stores = importlib.import_module(
        "scios.cognitive_core.knowledge.stores"
    )

    assert stores.__all__ == [
        "EntityStore",
        "RelationStore",
        "FactStore",
    ]


def test_stores_exports_are_importable():
    from scios.cognitive_core.knowledge.stores import (
        EntityStore,
        FactStore,
        RelationStore,
    )

    assert EntityStore is not None
    assert RelationStore is not None
    assert FactStore is not None


def test_stores_exports_are_correct_classes():
    from scios.cognitive_core.knowledge.stores import (
        EntityStore,
        FactStore,
        RelationStore,
    )
    from scios.cognitive_core.knowledge.stores.entity_store import (
        EntityStore as EntityStoreImpl,
    )
    from scios.cognitive_core.knowledge.stores.fact_store import (
        FactStore as FactStoreImpl,
    )
    from scios.cognitive_core.knowledge.stores.relation_store import (
        RelationStore as RelationStoreImpl,
    )

    assert EntityStore is EntityStoreImpl
    assert RelationStore is RelationStoreImpl
    assert FactStore is FactStoreImpl


def test_stores_do_not_export_private_names():
    stores = importlib.import_module(
        "scios.cognitive_core.knowledge.stores"
    )

    assert all(
        not name.startswith("_")
        for name in stores.__all__
    )
