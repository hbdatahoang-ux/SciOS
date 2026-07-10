from enum import Enum

class NodeKind(Enum):
    """
    NodeKind = Type of ExecutionNode.
    """

    # Primitive node = atomic operation (e.g. function call, instruction)
    PRIMITIVE = "primitive"

    # Process node = composed of multiple primitives
    PROCESS = "process"

    # Reflection node = handles error recovery, retry, or reasoning
    REFLECTION = "reflection"

    # Snapshot node = captures context state
    SNAPSHOT = "snapshot"

    # Resource node = manages external resource allocation
    RESOURCE = "resource"

    # Knowledge node = manages knowledge base updates
    KNOWLEDGE = "knowledge"
