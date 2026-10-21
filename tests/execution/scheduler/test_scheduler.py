import pytest

from scios.execution.graph.edge import ExecutionEdge
from scios.execution.graph.graph import ExecutionGraph
from scios.execution.node.node import ExecutionNode
from scios.execution.node.status import NodeStatus
from scios.execution.scheduler.policy import SchedulingPolicy
from scios.execution.scheduler.scheduler import Scheduler


def make_graph(*nodes):
    graph = ExecutionGraph()
    for node in nodes:
        graph.add_node(node)
    return graph


def connect(graph, source, target):
    graph.add_edge(
        ExecutionEdge(
            source_id=source.node_id,
            target_id=target.node_id,
        )
    )


def test_root_node_is_ready_and_can_be_selected():
    node = ExecutionNode(status=NodeStatus.READY)
    graph = make_graph(node)

    scheduler = Scheduler(graph)

    selected = scheduler.next()

    assert selected is node
    assert node.status is NodeStatus.READY


def test_node_with_predecessor_is_waiting():
    source = ExecutionNode(status=NodeStatus.READY)
    target = ExecutionNode(status=NodeStatus.READY)

    graph = make_graph(source, target)
    connect(graph, source, target)

    scheduler = Scheduler(graph)

    assert source.status is NodeStatus.READY
    assert target.status is NodeStatus.WAITING
    assert scheduler.next() is source


def test_next_returns_none_when_predecessor_has_failed():
    source = ExecutionNode(status=NodeStatus.READY)
    target = ExecutionNode(status=NodeStatus.READY)

    graph = make_graph(source, target)
    connect(graph, source, target)

    scheduler = Scheduler(graph)

    assert scheduler.next() is source

    source.mark_failed()

    assert target.status is NodeStatus.WAITING
    assert scheduler.next() is None


def test_next_does_not_mark_node_running():
    node = ExecutionNode(status=NodeStatus.READY)
    graph = make_graph(node)

    scheduler = Scheduler(graph)

    selected = scheduler.next()

    assert selected is node
    assert node.status is NodeStatus.READY
    assert node.status is not NodeStatus.RUNNING


def test_selected_node_is_not_emitted_twice_before_completion():
    node = ExecutionNode(status=NodeStatus.READY)
    graph = make_graph(node)

    scheduler = Scheduler(graph)

    assert scheduler.next() is node
    assert scheduler.next() is None


def test_successful_completion_unlocks_successor():
    source = ExecutionNode(status=NodeStatus.READY)
    target = ExecutionNode(status=NodeStatus.READY)

    graph = make_graph(source, target)
    connect(graph, source, target)

    scheduler = Scheduler(graph)

    assert scheduler.next() is source
    assert target.status is NodeStatus.WAITING

    source.mark_success()
    scheduler.notify_completed(source)

    assert target.status is NodeStatus.READY
    assert scheduler.next() is target


def test_failed_predecessor_does_not_unlock_successor():
    source = ExecutionNode(status=NodeStatus.READY)
    target = ExecutionNode(status=NodeStatus.READY)

    graph = make_graph(source, target)
    connect(graph, source, target)

    scheduler = Scheduler(graph)

    assert scheduler.next() is source

    source.mark_failed()
    scheduler.notify_completed(source)

    assert target.status is NodeStatus.WAITING
    assert scheduler.next() is None


def test_all_predecessors_must_succeed():
    first = ExecutionNode(status=NodeStatus.READY)
    second = ExecutionNode(status=NodeStatus.READY)
    target = ExecutionNode(status=NodeStatus.READY)

    graph = make_graph(first, second, target)
    connect(graph, first, target)
    connect(graph, second, target)

    scheduler = Scheduler(graph)

    selected = scheduler.next()
    assert selected in (first, second)

    selected.mark_success()
    scheduler.notify_completed(selected)

    assert target.status is NodeStatus.WAITING

    other = second if selected is first else first
    other.mark_success()
    scheduler.notify_completed(other)

    assert target.status is NodeStatus.READY
    assert scheduler.next() is target


def test_policy_selects_from_ready_nodes():
    first = ExecutionNode(status=NodeStatus.READY)
    second = ExecutionNode(status=NodeStatus.READY)

    graph = make_graph(first, second)

    class SecondPolicy(SchedulingPolicy):
        def select(self, ready_nodes):
            assert first in ready_nodes
            assert second in ready_nodes
            return second

    scheduler = Scheduler(
        graph,
        policy=SecondPolicy(),
    )

    assert scheduler.next() is second


def test_scheduler_does_not_mutate_graph_topology():
    first = ExecutionNode(status=NodeStatus.READY)
    second = ExecutionNode(status=NodeStatus.READY)

    graph = make_graph(first, second)
    connect(graph, first, second)

    original_nodes = dict(graph.nodes)
    original_edges = list(graph.edges)

    scheduler = Scheduler(graph)

    scheduler.next()

    assert graph.nodes == original_nodes
    assert graph.edges == original_edges


def test_reset_restores_scheduler_state():
    source = ExecutionNode(status=NodeStatus.READY)
    target = ExecutionNode(status=NodeStatus.READY)

    graph = make_graph(source, target)
    connect(graph, source, target)

    scheduler = Scheduler(graph)

    assert scheduler.next() is source

    scheduler.reset()

    assert source.status is NodeStatus.READY
    assert target.status is NodeStatus.WAITING
    assert scheduler.next() is source


def test_scheduler_rejects_invalid_graph():
    with pytest.raises(TypeError):
        Scheduler(object())


def test_notify_completed_rejects_unknown_node():
    graph = ExecutionGraph()
    node = ExecutionNode(status=NodeStatus.READY)
    graph.add_node(node)

    scheduler = Scheduler(graph)

    unknown = ExecutionNode(status=NodeStatus.SUCCESS)

    with pytest.raises(ValueError):
        scheduler.notify_completed(unknown)


def test_notify_completed_accepts_failed_terminal_node():
    node = ExecutionNode(status=NodeStatus.READY)
    graph = make_graph(node)

    scheduler = Scheduler(graph)
    scheduler.next()

    node.mark_failed()

    scheduler.notify_completed(node)

    assert node.status is NodeStatus.FAILED
