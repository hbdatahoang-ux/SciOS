from scios.cognitive_core.memory.stores import (
    EpisodicMemory,
    SemanticMemory,
    WorkingMemory,
)


def test_working_memory_export() -> None:
    assert WorkingMemory.__name__ == "WorkingMemory"


def test_episodic_memory_export() -> None:
    assert EpisodicMemory.__name__ == "EpisodicMemory"


def test_semantic_memory_export() -> None:
    assert SemanticMemory.__name__ == "SemanticMemory"


def test_public_exports() -> None:
    from scios.cognitive_core.memory import stores

    assert stores.__all__ == [
        "WorkingMemory",
        "EpisodicMemory",
        "SemanticMemory",
    ]
