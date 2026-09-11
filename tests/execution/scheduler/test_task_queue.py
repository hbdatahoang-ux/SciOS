from scios.execution.node.node import ExecutionNode
from scios.execution.node.status import NodeStatus
from scios.execution.scheduler.queue import TaskQueue


def test_enqueue_and_dequeue_ready_node():
    queue = TaskQueue()
    node = ExecutionNode(status=NodeStatus.READY)

    queue.enqueue(node)

    assert queue.size() == 1
    assert queue.has_tasks()
    assert queue.dequeue() is node
    assert queue.size() == 0
    assert not queue.has_tasks()


def test_peek_does_not_remove_node():
    queue = TaskQueue()
    node = ExecutionNode(status=NodeStatus.READY)

    queue.enqueue(node)

    assert queue.peek() is node
    assert queue.size() == 1


def test_dequeue_empty_returns_none():
    queue = TaskQueue()

    assert queue.dequeue() is None


def test_peek_empty_returns_none():
    queue = TaskQueue()

    assert queue.peek() is None


def test_reset_clears_queue():
    queue = TaskQueue()
    node = ExecutionNode(status=NodeStatus.READY)

    queue.enqueue(node)
    queue.reset()

    assert queue.size() == 0
    assert not queue.has_tasks()
    assert queue.peek() is None
    assert queue.dequeue() is None


def test_only_ready_nodes_can_be_enqueued():
    queue = TaskQueue()

    node = ExecutionNode(status=NodeStatus.WAITING)

    try:
        queue.enqueue(node)
    except ValueError:
        pass
    else:
        raise AssertionError("WAITING node must not be enqueued")


def test_enqueue_rejects_non_execution_node():
    queue = TaskQueue()

    try:
        queue.enqueue(object())
    except TypeError:
        pass
    else:
        raise AssertionError("non-ExecutionNode must be rejected")


def test_fifo_order_is_preserved():
    queue = TaskQueue()

    first = ExecutionNode(status=NodeStatus.READY)
    second = ExecutionNode(status=NodeStatus.READY)
    third = ExecutionNode(status=NodeStatus.READY)

    queue.enqueue(first)
    queue.enqueue(second)
    queue.enqueue(third)

    assert queue.dequeue() is first
    assert queue.dequeue() is second
    assert queue.dequeue() is third
