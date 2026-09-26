"""Tests for Knowledge retrieval public API."""

import scios.cognitive_core.knowledge.retrieval as retrieval


def test_public_exports():
    assert retrieval.__all__ == [
        "RetrievalStrategy",
        "EntityRetrieval",
        "RelationRetrieval",
        "FactRetrieval",
    ]


def test_retrieval_strategy_export():
    from scios.cognitive_core.knowledge.retrieval import RetrievalStrategy

    assert RetrievalStrategy is retrieval.RetrievalStrategy


def test_entity_retrieval_export():
    from scios.cognitive_core.knowledge.retrieval import EntityRetrieval

    assert EntityRetrieval is retrieval.EntityRetrieval


def test_relation_retrieval_export():
    from scios.cognitive_core.knowledge.retrieval import RelationRetrieval

    assert RelationRetrieval is retrieval.RelationRetrieval


def test_fact_retrieval_export():
    from scios.cognitive_core.knowledge.retrieval import FactRetrieval

    assert FactRetrieval is retrieval.FactRetrieval
