"""
SciOS Runtime Metrics Processors
================================

Public API for the Runtime Metrics Processing subsystem.

Architecture
------------
MetricProcessor
    ├── FilterProcessor
    ├── SamplingProcessor
    ├── NormalizerProcessor
    ├── ValidatorProcessor
    ├── EnrichmentProcessor
    ├── BatchingProcessor
    └── CompressionProcessor

Python 3.11+
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, TypeAlias


# ======================================================================
# Base Processor
# ======================================================================

from .processor import (
    MetricProcessor,
)


# ======================================================================
# Built-in Processors
# ======================================================================

from .filter import (
    FilterProcessor,
)

from .sampler import (
    SamplingProcessor,
)

from .normalizer import (
    NormalizerProcessor,
)

from .validator import (
    ValidatorProcessor,
)

from .enrichment import (
    EnrichmentProcessor,
)

from .batching import (
    BatchingProcessor,
)

from .compression import (
    CompressionProcessor,
)


# ======================================================================
# Public Type Aliases
# ======================================================================

ProcessorClass: TypeAlias = type[MetricProcessor]


# ======================================================================
# Compatibility Aliases
# ======================================================================

Processor = MetricProcessor

SamplerProcessor = SamplingProcessor


# ======================================================================
# Processor Registry
# ======================================================================

PROCESSORS: dict[str, ProcessorClass] = {
    "processor": MetricProcessor,
    "filter": FilterProcessor,
    "sampler": SamplingProcessor,
    "sampling": SamplingProcessor,
    "normalizer": NormalizerProcessor,
    "validator": ValidatorProcessor,
    "enrichment": EnrichmentProcessor,
    "batching": BatchingProcessor,
    "compression": CompressionProcessor,
}


# ======================================================================
# Factory Helpers
# ======================================================================

def available_processors() -> tuple[str, ...]:
    """
    Return all registered processor names.

    The returned tuple is sorted and does not expose the internal
    registry object.
    """

    return tuple(
        sorted(
            PROCESSORS
        )
    )


def get_processor_class(
    processor: str,
) -> ProcessorClass:
    """
    Resolve a processor name to its implementation class.

    Parameters
    ----------
    processor:
        Registered processor name.

    Raises
    ------
    TypeError
        If ``processor`` is not a string.

    ValueError
        If the processor name is unknown.
    """

    if not isinstance(
        processor,
        str,
    ):
        raise TypeError(
            "processor must be a string"
        )

    name = processor.strip().lower()

    if not name:
        raise ValueError(
            "processor name cannot be empty"
        )

    try:
        return PROCESSORS[name]
    except KeyError as exc:
        raise ValueError(
            f"Unknown processor: {processor}"
        ) from exc


def create_processor(
    processor: str,
    **kwargs: Any,
) -> MetricProcessor:
    """
    Create a Runtime Metrics processor.

    Examples
    --------
    ``create_processor("filter")``

    ``create_processor("sampler", rate=0.5)``

    ``create_processor("compression", level=9)``
    """

    processor_class = get_processor_class(
        processor
    )

    return processor_class(
        **kwargs
    )


def build_pipeline(
    processors: Sequence[str],
) -> list[MetricProcessor]:
    """
    Build a processor pipeline from registered names.

    Parameters
    ----------
    processors:
        Ordered sequence of processor names.

    Returns
    -------
    list[MetricProcessor]
        Newly constructed processor instances.

    Notes
    -----
    Each invocation creates fresh processor instances.
    """

    if isinstance(
        processors,
        str,
    ):
        raise TypeError(
            "processors must be a sequence of names, "
            "not a single string"
        )

    return [
        create_processor(
            name
        )
        for name in processors
    ]


# ======================================================================
# Public Namespace
# ======================================================================

__all__ = [
    # Base
    "MetricProcessor",
    "Processor",

    # Processors
    "FilterProcessor",
    "SamplingProcessor",
    "SamplerProcessor",
    "NormalizerProcessor",
    "ValidatorProcessor",
    "EnrichmentProcessor",
    "BatchingProcessor",
    "CompressionProcessor",

    # Registry
    "PROCESSORS",
    "ProcessorClass",

    # Factory
    "available_processors",
    "get_processor_class",
    "create_processor",
    "build_pipeline",
]