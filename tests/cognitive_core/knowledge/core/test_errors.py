"""Tests for Knowledge core exception hierarchy."""

from scios.cognitive_core.knowledge.core.errors import (
    EntityError,
    FactError,
    GraphError,
    KnowledgeError,
    RelationError,
)


def test_knowledge_error_inherits_exception():
    assert issubclass(KnowledgeError, Exception)


def test_entity_error_inherits_knowledge_error():
    assert issubclass(EntityError, KnowledgeError)


def test_relation_error_inherits_knowledge_error():
    assert issubclass(RelationError, KnowledgeError)


def test_fact_error_inherits_knowledge_error():
    assert issubclass(FactError, KnowledgeError)


def test_graph_error_inherits_knowledge_error():
    assert issubclass(GraphError, KnowledgeError)


def test_all_subclasses_are_knowledge_errors():
    error_types = (
        EntityError,
        RelationError,
        FactError,
        GraphError,
    )

    assert all(issubclass(error_type, KnowledgeError) for error_type in error_types)


def test_knowledge_error_can_be_raised_and_caught():
    try:
        raise KnowledgeError("knowledge failure")
    except KnowledgeError as exc:
        assert str(exc) == "knowledge failure"


def test_entity_error_can_be_raised_and_caught_as_knowledge_error():
    try:
        raise EntityError("invalid entity")
    except KnowledgeError as exc:
        assert str(exc) == "invalid entity"


def test_relation_error_can_be_raised_and_caught_as_knowledge_error():
    try:
        raise RelationError("invalid relation")
    except KnowledgeError as exc:
        assert str(exc) == "invalid relation"


def test_fact_error_can_be_raised_and_caught_as_knowledge_error():
    try:
        raise FactError("invalid fact")
    except KnowledgeError as exc:
        assert str(exc) == "invalid fact"


def test_graph_error_can_be_raised_and_caught_as_knowledge_error():
    try:
        raise GraphError("invalid graph")
    except KnowledgeError as exc:
        assert str(exc) == "invalid graph"


def test_public_exports():
    from scios.cognitive_core.knowledge.core import errors

    assert errors.__all__ == [
        "KnowledgeError",
        "EntityError",
        "RelationError",
        "FactError",
        "GraphError",
    ]
