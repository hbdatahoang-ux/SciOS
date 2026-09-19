from enum import Enum


class NodeKind(Enum):
    """Semantic kind of an ExecutionNode."""

    PRIMITIVE = "primitive"
    PROCESS = "process"
