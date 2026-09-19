from scios.execution.node.status import NodeStatus


# =========================================================
# Lifecycle utility functions
# =========================================================

def is_terminal(status: NodeStatus) -> bool:
    """
    Check if node has reached a terminal state.
    """
    return status in {
        NodeStatus.SUCCESS,
        NodeStatus.FAILED,
        NodeStatus.SKIPPED,
        NodeStatus.CANCELLED,
    }


def is_active(status: NodeStatus) -> bool:
    """
    Check if node is currently active.
    """
    return status in {
        NodeStatus.RUNNING,
        NodeStatus.REFLECTING,
        NodeStatus.RETRYING,
    }


def is_pending(status: NodeStatus) -> bool:
    """
    Check if node is pending execution.
    """
    return status in {
        NodeStatus.CREATED,
        NodeStatus.READY,
        NodeStatus.WAITING,
    }


def can_retry(status: NodeStatus) -> bool:
    """
    Check if node can be retried after failure or cancellation.
    """
    return status in {
        NodeStatus.FAILED,
        NodeStatus.CANCELLED,
    }
