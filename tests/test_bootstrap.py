"""
SciOS Bootstrap Tests
=====================

Unit tests for the SciOS kernel bootstrap.
Validate that default subsystems are initialized and registered.
"""

from __future__ import annotations

import pytest

from scios.kernel.bootstrap import Bootstrap


def test_bootstrap_initialization() -> None:
    """
    Bootstrap should initialize all kernel subsystems.
    """
    components = Bootstrap.init_kernel()

    # Kiểm tra các key cần có
    required = {
        "state",
        "lifecycle",
        "registry",
        "dispatcher",
        "runtime",
        "pipeline",
    }
    assert required.issubset(components.keys())

    # Kiểm tra các đối tượng không None
    for key in required:
        assert components[key] is not None


def test_bootstrap_pipeline_stages() -> None:
    """
    Default pipeline should contain Planner, Memory, Reasoner stages.
    """
    components = Bootstrap.init_kernel()
    pipeline = components["pipeline"]

    stage_names = [s.name for s in pipeline.stages]

    assert "planner" in stage_names
    assert "memory" in stage_names
    assert "reasoner" in stage_names


def test_bootstrap_registry_contains_pipeline() -> None:
    """
    Registry should contain pipeline reference.
    """
    components = Bootstrap.init_kernel()
    registry = components["registry"]

    pipeline = registry.get("pipeline")

    assert pipeline is not None
    assert hasattr(pipeline, "run")
