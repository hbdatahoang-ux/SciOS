"""Public API for the SciOS Cognitive Core Perception core."""

from .base import BasePerceptor
from .context import PerceptionContext
from .errors import (
    PerceptionConfigurationError,
    PerceptionError,
    PerceptionInputError,
    PerceptionProcessingError,
    PerceptionValidationError,
)
from .result import PerceptionResult
from .types import (
    Embedding,
    Entities,
    Entity,
    Features,
    Metadata,
    Modality,
    PerceptionStatus,
    RawInput,
    Relation,
    Relations,
)

__all__ = [
    "BasePerceptor",
    "Embedding",
    "Entities",
    "Entity",
    "Features",
    "Metadata",
    "Modality",
    "PerceptionConfigurationError",
    "PerceptionContext",
    "PerceptionError",
    "PerceptionInputError",
    "PerceptionProcessingError",
    "PerceptionResult",
    "PerceptionStatus",
    "PerceptionValidationError",
    "RawInput",
    "Relation",
    "Relations",
]
