import pytest

from scios.execution.node.node import ExecutionNode
from scios.execution.node.status import NodeStatus
from scios.execution.scheduler.policy import SchedulingPolicy


def test_select_returns_one_ready_node():
    policy = SchedulingPolicy()

    first = ExecutionNode(status=NodeStatus.READY)
    second = ExecutionNode(status=NodeStatus.READY)

    selected = policy.select([first, second])

    assert selected is first
    assert selected in [first, second]


def test_select_only_selects_from_ready_nodes():
    policy = SchedulingPolicy()

    ready = ExecutionNode(status=NodeStatus.READY)
    waiting = ExecutionNode(status=NodeStatus.WAITING)

    selected = policy.select([ready])

    assert selected is ready
    assert selected is not waiting


def test_select_preserves_fifo_order():
    policy = SchedulingPolicy()

    first = ExecutionNode(status=NodeStatus.READY)
    second = ExecutionNode(status=NodeStatus.READY)
    third = ExecutionNode(status=NodeStatus.READY)

    assert policy.select([first, second, third]) is first


def test_select_rejects_empty_ready_set():
    policy = SchedulingPolicy()

    with pytest.raises(ValueError):
        policy.select([])


def test_select_does_not_change_node_status():
    policy = SchedulingPolicy()

    node = ExecutionNode(status=NodeStatus.READY)

    selected = policy.select([node])

    assert selected is node
    assert node.status is NodeStatus.READY
