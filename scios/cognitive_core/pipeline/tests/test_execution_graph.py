"""
SciOS Cognitive Pipeline Execution Graph Tests

Author: Bui Dinh Hoang
License: Apache-2.0
"""

import pytest

from scios.cognitive_core.pipeline.execution_graph import ExecutionGraph


# ============================================================
# Dummy Stage
# ============================================================

class DummyStage:
    """Simple pipeline stage used for graph testing."""

    def __init__(self, name):
        self.name = name

    def execute(self, context):
        context["history"].append(self.name)
        return context


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def graph():
    return ExecutionGraph()


@pytest.fixture
def context():
    return {
        "history": []
    }


# ============================================================
# Initialization
# ============================================================

def test_graph_initialization(graph):

    assert graph is not None


def test_graph_starts_empty(graph):

    assert len(graph.nodes()) == 0


# ============================================================
# Node Registration
# ============================================================

def test_add_node(graph):

    graph.add_stage(DummyStage("memory"))

    assert graph.has_stage("memory")


def test_add_multiple_nodes(graph):

    graph.add_stage(DummyStage("perception"))
    graph.add_stage(DummyStage("memory"))
    graph.add_stage(DummyStage("reasoning"))

    assert len(graph.nodes()) == 3


def test_duplicate_stage_raises(graph):

    graph.add_stage(DummyStage("memory"))

    with pytest.raises(ValueError):
        graph.add_stage(DummyStage("memory"))


# ============================================================
# Edge Registration
# ============================================================

def test_add_edge(graph):

    graph.add_stage(DummyStage("memory"))
    graph.add_stage(DummyStage("reasoning"))

    graph.connect("memory", "reasoning")

    assert graph.has_edge("memory", "reasoning")


def test_connect_unknown_stage(graph):

    graph.add_stage(DummyStage("memory"))

    with pytest.raises(KeyError):
        graph.connect("memory", "planning")


# ============================================================
# Execution
# ============================================================

def test_linear_execution(graph, context):

    graph.add_stage(DummyStage("perception"))
    graph.add_stage(DummyStage("memory"))
    graph.add_stage(DummyStage("reasoning"))

    graph.connect("perception", "memory")
    graph.connect("memory", "reasoning")

    graph.execute(context)

    assert context["history"] == [
        "perception",
        "memory",
        "reasoning",
    ]


def test_execute_empty_graph(graph, context):

    graph.execute(context)

    assert context["history"] == []


# ============================================================
# Topological Ordering
# ============================================================

def test_topological_order(graph):

    graph.add_stage(DummyStage("A"))
    graph.add_stage(DummyStage("B"))
    graph.add_stage(DummyStage("C"))

    graph.connect("A", "B")
    graph.connect("B", "C")

    order = graph.topological_sort()

    assert order == ["A", "B", "C"]


# ============================================================
# Cycle Detection
# ============================================================

def test_cycle_detection(graph):

    graph.add_stage(DummyStage("A"))
    graph.add_stage(DummyStage("B"))

    graph.connect("A", "B")
    graph.connect("B", "A")

    with pytest.raises(ValueError):
        graph.validate()


# ============================================================
# Validation
# ============================================================

def test_validate_linear_graph(graph):

    graph.add_stage(DummyStage("perception"))
    graph.add_stage(DummyStage("memory"))

    graph.connect("perception", "memory")

    assert graph.validate() is True


def test_validate_empty_graph(graph):

    assert graph.validate() is True


# ============================================================
# Stage Lookup
# ============================================================

def test_get_stage(graph):

    stage = DummyStage("memory")

    graph.add_stage(stage)

    assert graph.get_stage("memory") is stage


def test_unknown_stage(graph):

    with pytest.raises(KeyError):
        graph.get_stage("reasoning")


# ============================================================
# Remove Stage
# ============================================================

def test_remove_stage(graph):

    graph.add_stage(DummyStage("planning"))

    graph.remove_stage("planning")

    assert not graph.has_stage("planning")


# ============================================================
# Clear
# ============================================================

def test_clear_graph(graph):

    graph.add_stage(DummyStage("A"))
    graph.add_stage(DummyStage("B"))

    graph.clear()

    assert len(graph.nodes()) == 0


# ============================================================
# Smoke Test
# ============================================================

def test_execution_graph_smoke():

    graph = ExecutionGraph()

    graph.add_stage(DummyStage("perception"))
    graph.add_stage(DummyStage("memory"))
    graph.add_stage(DummyStage("reasoning"))

    graph.connect("perception", "memory")
    graph.connect("memory", "reasoning")

    context = {"history": []}

    graph.execute(context)

    assert context["history"] == [
        "perception",
        "memory",
        "reasoning",
    ]
