"""
SciOS VectorStore
=================

Public interface for the SciOS Vector Storage subsystem.

The VectorStore provides backend-independent vector indexing,
storage, embedding, metadata management, and similarity search.

Architecture
------------
VectorStore
├── Embedding Provider
├── Storage Backend
├── Vector Index
├── Similarity Engine
├── Metadata Manager
└── Search Engine

Public API
----------
EmbeddingProvider
    Abstract interface for embedding generation.

VectorStorage
    Persistent storage backend.

VectorIndex
    Vector indexing engine.

SimilarityMetric
    Built-in similarity metrics.

Metadata
    Metadata associated with vectors.

VectorSearch
    High-level search interface.
"""

from .embedding import EmbeddingProvider
from .index import VectorIndex
from .metadata import Metadata
from .search import VectorSearch
from .similarity import SimilarityMetric
from .storage import VectorStorage

__all__ = [
    "EmbeddingProvider",
    "VectorIndex",
    "Metadata",
    "VectorSearch",
    "SimilarityMetric",
    "VectorStorage",
]
