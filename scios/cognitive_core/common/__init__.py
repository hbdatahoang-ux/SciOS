"""
SciOS Cognitive Core - Common
=============================

Foundational components shared across the Cognitive Core:
- interfaces: Abstract base classes and protocols
- context: CognitiveContext for passing state
- result: CognitiveResult for standardized outputs
- errors: Common exception hierarchy
"""

from scios.cognitive_core.common.interfaces import (
    PlannerInterface,
    MemoryInterface,
    ReasonerInterface,
    ToolInterface,
)
from scios.cognitive_core.common.context import CognitiveContext
from scios.cognitive_core.common.result import CognitiveResult

from scios.cognitive_core.common.errors import (
    CognitiveError,
    PlannerError,
    ReasoningError,
    MemoryError,
    ToolError,
    PipelineError,
)
__all__ = [
    "PlannerInterface",
    "MemoryInterface",
    "ReasonerInterface",
    "ToolInterface",
    "CognitiveContext",
    "CognitiveResult",
    "CognitiveError",
    "PlannerError",
    "ReasoningError",
    "MemoryError",
    "ToolError",
    "PipelineError",
]
