"""
SciOS Cognitive Pipeline Dispatcher Tests

Author: Bui Dinh Hoang
License: Apache-2.0
"""

import pytest

from scios.cognitive_core.pipeline.dispatcher import PipelineDispatcher


# ============================================================
# Dummy Stage
# ============================================================

class DummyStage:
    """Simple stage used for dispatcher testing."""

    def __init__(self, name):
        self.name = name

    def execute(self, context):
        context["history"].append(self.name)
        return context


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def dispatcher():
    return PipelineDispatcher()


@pytest.fixture
def context():
    return {
        "history": []
    }


# ============================================================
# Initialization
# ============================================================

def test_dispatcher_initialization(dispatcher):
    assert dispatcher is not None


def test_dispatcher_has_dispatch_method(dispatcher):
    assert hasattr(dispatcher, "dispatch")


# ============================================================
# Sequential Dispatch
# ============================================================

def test_dispatch_single_stage(dispatcher, context):

    stage = DummyStage("stage1")

    result = dispatcher.dispatch(
        [stage],
        context
    )

    assert result["history"] == ["stage1"]


def test_dispatch_multiple_stages(dispatcher, context):

    stages = [
        DummyStage("A"),
        DummyStage("B"),
        DummyStage("C"),
    ]

    result = dispatcher.dispatch(
        stages,
        context
    )

    assert result["history"] == [
        "A",
        "B",
        "C",
    ]


# ============================================================
# Empty Dispatch
# ============================================================

def test_dispatch_empty_pipeline(dispatcher, context):

    result = dispatcher.dispatch(
        [],
        context
    )

    assert result == context


# ============================================================
# Error Handling
# ============================================================

class BrokenStage:

    def execute(self, context):
        raise RuntimeError("Stage failed")


def test_dispatch_stage_exception(dispatcher, context):

    with pytest.raises(RuntimeError):
        dispatcher.dispatch(
            [BrokenStage()],
            context
        )


# ============================================================
# Invalid Stage
# ============================================================

class InvalidStage:
    pass


def test_dispatch_invalid_stage(dispatcher, context):

    with pytest.raises(AttributeError):

        dispatcher.dispatch(
            [InvalidStage()],
            context
        )


# ============================================================
# Ordering
# ============================================================

def test_dispatch_preserves_order(dispatcher, context):

    names = [
        "perception",
        "memory",
        "reasoning",
        "planning",
        "tool_use",
        "reflection",
    ]

    stages = [
        DummyStage(name)
        for name in names
    ]

    result = dispatcher.dispatch(
        stages,
        context
    )

    assert result["history"] == names


# ============================================================
# Smoke Test
# ============================================================

def test_dispatcher_smoke(dispatcher):

    context = {
        "history": []
    }

    stages = [
        DummyStage("one"),
        DummyStage("two"),
    ]

    result = dispatcher.dispatch(
        stages,
        context
    )

    assert len(result["history"]) == 2
