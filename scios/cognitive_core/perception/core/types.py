"""Core types for the SciOS Cognitive Core Perception subsystem.

This module defines lightweight, dependency-free types shared across the
perception core, engine, registry, factory, and modality implementations.

The types in this module intentionally contain no perception logic and must
remain independent of external frameworks and modality-specific libraries.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any, TypeAlias


class Modality(StrEnum):
    """Supported perception input modalities."""

    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    SENSOR = "sensor"


class PerceptionStatus(StrEnum):
    """Outcome status of a perception operation."""

    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"


# ---------------------------------------------------------------------------
# Generic perception data types
# ---------------------------------------------------------------------------

RawInput: TypeAlias = Any
"""Raw input accepted by a perceptor."""

Metadata: TypeAlias = dict[str, Any]
"""Metadata associated with an input or perception result."""

Features: TypeAlias = dict[str, Any]
"""Structured features extracted during perception."""

Entity: TypeAlias = dict[str, Any]
"""A single extracted entity."""

Entities: TypeAlias = list[Entity]
"""Collection of extracted entities."""

Relation: TypeAlias = dict[str, Any]
"""A single relation between extracted entities."""

Relations: TypeAlias = list[Relation]
"""Collection of extracted relations."""

Embedding: TypeAlias = Any
"""Embedding representation produced by a perception component."""


__all__ = [
    "Embedding",
    "Entities",
    "Entity",
    "Features",
    "Metadata",
    "Modality",
    "PerceptionStatus",
    "RawInput",
    "Relation",
    "Relations",
]