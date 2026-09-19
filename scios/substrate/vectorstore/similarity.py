"""
SciOS Vector Similarity
=======================

Similarity and distance metrics for the SciOS VectorStore.

Responsibilities
----------------
- Similarity computation
- Distance metrics
- Backend-independent implementations
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum

import numpy as np

from scios.substrate.tensor import SciOSTensor

__all__ = [
    "SimilarityMetric",
    "Similarity",
    "CosineSimilarity",
    "EuclideanDistance",
    "InnerProduct",
]


# ==========================================================
# Metrics
# ==========================================================

class SimilarityMetric(str, Enum):
    """
    Built-in similarity metrics.
    """

    COSINE = "cosine"

    EUCLIDEAN = "euclidean"

    INNER_PRODUCT = "inner_product"


# ==========================================================
# Abstract Base
# ==========================================================

class Similarity(ABC):
    """
    Abstract similarity metric.
    """

    metric: SimilarityMetric

    @abstractmethod
    def score(
        self,
        x: SciOSTensor,
        y: SciOSTensor,
    ) -> float:
        """
        Compute similarity or distance score.
        """
        raise NotImplementedError


# ==========================================================
# Cosine Similarity
# ==========================================================

class CosineSimilarity(Similarity):
    """
    Cosine similarity.

    Range:
        [-1, 1]

    Higher is better.
    """

    metric = SimilarityMetric.COSINE

    def score(
        self,
        x: SciOSTensor,
        y: SciOSTensor,
    ) -> float:

        a = x.numpy().ravel()
        b = y.numpy().ravel()

        denom = np.linalg.norm(a) * np.linalg.norm(b)

        if denom == 0.0:
            return 0.0

        return float(np.dot(a, b) / denom)


# ==========================================================
# Euclidean Distance
# ==========================================================

class EuclideanDistance(Similarity):
    """
    Euclidean (L2) distance.

    Lower is better.
    """

    metric = SimilarityMetric.EUCLIDEAN

    def score(
        self,
        x: SciOSTensor,
        y: SciOSTensor,
    ) -> float:

        a = x.numpy().ravel()
        b = y.numpy().ravel()

        return float(np.linalg.norm(a - b))


# ==========================================================
# Inner Product
# ==========================================================

class InnerProduct(Similarity):
    """
    Inner product.

    Higher is better.
    """

    metric = SimilarityMetric.INNER_PRODUCT

    def score(
        self,
        x: SciOSTensor,
        y: SciOSTensor,
    ) -> float:

        a = x.numpy().ravel()
        b = y.numpy().ravel()

        return float(np.dot(a, b))


# ==========================================================
# Factory
# ==========================================================

_METRICS: dict[SimilarityMetric, Similarity] = {
    SimilarityMetric.COSINE: CosineSimilarity(),
    SimilarityMetric.EUCLIDEAN: EuclideanDistance(),
    SimilarityMetric.INNER_PRODUCT: InnerProduct(),
}


def get_metric(
    metric: SimilarityMetric | str,
) -> Similarity:
    """
    Return a similarity metric instance.
    """

    if isinstance(metric, str):
        metric = SimilarityMetric(metric)

    return _METRICS[metric]
