"""
SciOS Event System
==================

Định nghĩa EventBus và các loại KernelEventType.
Pipeline và Dispatcher chỉ publish event,
còn Logger, Reflection, Metrics, Tracer sẽ subscribe.
"""

from enum import Enum
from typing import Any, Callable, Dict, List


class KernelEventType(Enum):
    PIPELINE_STARTED = "pipeline_started"
    PIPELINE_COMPLETED = "pipeline_completed"
    PIPELINE_FAILED = "pipeline_failed"

    STAGE_STARTED = "stage_started"
    STAGE_COMPLETED = "stage_completed"
    STAGE_FAILED = "stage_failed"
    STAGE_ROLLBACK = "stage_rollback"


class KernelEvent:
    def __init__(self, event_type: KernelEventType, payload: Dict[str, Any]) -> None:
        self.type = event_type
        self.payload = payload

    def to_dict(self) -> Dict[str, Any]:
        return {"type": self.type.value, "payload": self.payload}

    def __repr__(self) -> str:
        return f"<KernelEvent type={self.type.value} payload={self.payload}>"


class EventBus:
    """
    EventBus quản lý publish/subscribe cho event.
    """

    def __init__(self) -> None:
        self._subscribers: Dict[KernelEventType, List[Callable[[KernelEvent], None]]] = {}

    def subscribe(self, event_type: KernelEventType, handler: Callable[[KernelEvent], None]) -> None:
        """Đăng ký handler cho một loại event."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: KernelEventType, handler: Callable[[KernelEvent], None]) -> None:
        """Hủy đăng ký handler."""
        if event_type in self._subscribers:
            self._subscribers[event_type] = [h for h in self._subscribers[event_type] if h != handler]

    def publish(self, event_type: KernelEventType, payload: Dict[str, Any]) -> None:
        """Phát event tới tất cả subscriber."""
        event = KernelEvent(event_type, payload)
        for handler in self._subscribers.get(event_type, []):
            handler(event)

    def clear(self) -> None:
        """Xóa toàn bộ subscriber."""
        self._subscribers.clear()

    def __repr__(self) -> str:
        return f"<EventBus subscribers={len(self._subscribers)}>"
