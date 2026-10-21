"""Exception hierarchy for the Knowledge subsystem."""

from __future__ import annotations


class KnowledgeError(Exception):
    """Base exception for all Knowledge subsystem errors."""


class EntityError(KnowledgeError):
    """Raised when an entity operation is invalid."""


class RelationError(KnowledgeError):
    """Raised when a relation operation is invalid."""


class FactError(KnowledgeError):
    """Raised when a fact operation is invalid."""


class GraphError(KnowledgeError):
    """Raised when a graph operation is invalid."""


__all__ = [
    "KnowledgeError",
    "EntityError",
    "RelationError",
    "FactError",
    "GraphError",
]
