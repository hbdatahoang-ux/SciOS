"""Contract tests for perception.engine public API."""

from __future__ import annotations

from scios.cognitive_core.perception import engine


def test_engine_all_is_exact() -> None:
    assert engine.__all__ == [
        "PerceptionEngine",
        "PerceptionPipeline",
    ]


def test_engine_exports_are_available() -> None:
    from scios.cognitive_core.perception.engine import (
        PerceptionEngine,
        PerceptionPipeline,
    )

    assert engine.PerceptionEngine is PerceptionEngine
    assert engine.PerceptionPipeline is PerceptionPipeline
