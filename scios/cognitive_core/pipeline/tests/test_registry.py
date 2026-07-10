"""
SciOS Cognitive Pipeline Registry Tests

Author: Bui Dinh Hoang
License: Apache-2.0
"""

import pytest

from scios.cognitive_core.pipeline.registry import StageRegistry


# ============================================================
# Dummy Stage
# ============================================================

class DummyStage:
    """Simple stage used for registry testing."""

    def __init__(self, name):
        self.name = name

    def execute(self, context):
        return context


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def registry():
    return StageRegistry()


@pytest.fixture
def stage():
    return DummyStage("memory")


# ============================================================
# Initialization
# ============================================================

def test_registry_initialization(registry):
    assert registry is not None


def test_registry_starts_empty(registry):
    assert len(registry.list()) == 0


# ============================================================
# Registration
# ============================================================

def test_register_stage(registry, stage):

    registry.register(stage)

    assert registry.exists("memory")


def test_get_registered_stage(registry, stage):

    registry.register(stage)

    result = registry.get("memory")

    assert result is stage


def test_register_multiple_stages(registry):

    registry.register(DummyStage("perception"))
    registry.register(DummyStage("memory"))
    registry.register(DummyStage("reasoning"))

    assert registry.exists("perception")
    assert registry.exists("memory")
    assert registry.exists("reasoning")


# ============================================================
# Duplicate Registration
# ============================================================

def test_duplicate_registration_raises(registry):

    registry.register(DummyStage("memory"))

    with pytest.raises(ValueError):
        registry.register(DummyStage("memory"))


# ============================================================
# Removal
# ============================================================

def test_unregister_stage(registry):

    registry.register(DummyStage("planning"))

    registry.unregister("planning")

    assert not registry.exists("planning")


def test_unregister_unknown_stage(registry):

    with pytest.raises(KeyError):
        registry.unregister("unknown")


# ============================================================
# Lookup
# ============================================================

def test_get_unknown_stage(registry):

    with pytest.raises(KeyError):
        registry.get("reflection")


def test_exists_unknown_stage(registry):

    assert registry.exists("tool_use") is False


# ============================================================
# Listing
# ============================================================

def test_list_registered_stages(registry):

    registry.register(DummyStage("perception"))
    registry.register(DummyStage("memory"))
    registry.register(DummyStage("reasoning"))

    stages = registry.list()

    assert len(stages) == 3


def test_list_contains_stage_names(registry):

    registry.register(DummyStage("planning"))

    names = registry.names()

    assert "planning" in names


# ============================================================
# Clear
# ============================================================

def test_clear_registry(registry):

    registry.register(DummyStage("memory"))
    registry.register(DummyStage("reasoning"))

    registry.clear()

    assert len(registry.list()) == 0


# ============================================================
# Validation
# ============================================================

def test_register_none(registry):

    with pytest.raises(TypeError):
        registry.register(None)


class InvalidStage:
    pass


def test_register_invalid_stage(registry):

    with pytest.raises(AttributeError):
        registry.register(InvalidStage())


# ============================================================
# Smoke Test
# ============================================================

def test_registry_smoke():

    registry = StageRegistry()

    registry.register(DummyStage("memory"))
    registry.register(DummyStage("planning"))

    assert registry.exists("memory")
    assert registry.exists("planning")

    registry.clear()

    assert len(registry.list()) == 0
