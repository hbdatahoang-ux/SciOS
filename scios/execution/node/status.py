from enum import Enum

class NodeStatus(Enum):
    """
    NodeStatus = Lifecycle state of an ExecutionNode.
    """

    # Initial states
    CREATED = "created"       # Node vừa được tạo
    READY = "ready"           # Đủ điều kiện để chạy
    WAITING = "waiting"       # Đang chờ dependency hoặc resource

    # Active states
    RUNNING = "running"       # Đang thực thi
    REFLECTING = "reflecting" # Đang được Reflection xử lý

    # Terminal states
    SUCCESS = "success"       # Hoàn thành thành công
    FAILED = "failed"         # Thất bại
    SKIPPED = "skipped"       # Bỏ qua
    CANCELLED = "cancelled"   # Hủy bỏ

    # Recovery states
    RETRYING = "retrying"     # Đang retry sau Reflection hoặc Failure


# =========================================================
# Lifecycle utility functions
# =========================================================

def is_terminal(status: NodeStatus) -> bool:
    return status in {
        NodeStatus.SUCCESS,
        NodeStatus.FAILED,
        NodeStatus.SKIPPED,
        NodeStatus.CANCELLED,
    }

def is_active(status: NodeStatus) -> bool:
    return status in {
        NodeStatus.RUNNING,
        NodeStatus.REFLECTING,
        NodeStatus.RETRYING,
    }

def is_pending(status: NodeStatus) -> bool:
    return status in {
        NodeStatus.CREATED,
        NodeStatus.READY,
        NodeStatus.WAITING,
    }

def can_retry(status: NodeStatus) -> bool:
    return status in {
        NodeStatus.FAILED,
        NodeStatus.CANCELLED,
    }
