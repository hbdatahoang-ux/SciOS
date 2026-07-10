# scios/cognitive_core/tool_use/monitor.py

"""
SciOS Runtime Monitor
=====================

Theo dõi quá trình thực thi tool trong thời gian thực:
- Bắt đầu/kết thúc thực thi
- Thời gian chạy
- Trạng thái (success/error)
- Ghi log runtime
"""

import time
from typing import Dict, Any


class Monitor:
    """
    Monitor giám sát việc thực thi tool.
    """

    def __init__(self) -> None:
        self.logs: list[Dict[str, Any]] = []

    def start(self, tool_name: str, request: Dict[str, Any]) -> float:
        """
        Đánh dấu thời điểm bắt đầu thực thi tool.
        Trả về timestamp để tính thời gian chạy.
        """
        start_time = time.time()
        self.logs.append({
            "event": "start",
            "tool": tool_name,
            "request": request,
            "timestamp": start_time,
        })
        return start_time

    def end(self, tool_name: str, response: Dict[str, Any], start_time: float) -> None:
        """
        Đánh dấu thời điểm kết thúc thực thi tool.
        Tính thời gian chạy và ghi log.
        """
        end_time = time.time()
        duration = end_time - start_time

        status = response.get("status", "unknown")

        self.logs.append({
            "event": "end",
            "tool": tool_name,
            "response": response,
            "status": status,
            "duration": duration,
            "timestamp": end_time,
        })

    def get_logs(self) -> list[Dict[str, Any]]:
        """Lấy toàn bộ log runtime."""
        return self.logs

    def clear(self) -> None:
        """Xóa toàn bộ log runtime."""
        self.logs.clear()

    def to_dict(self) -> Dict[str, Any]:
        """Xuất log dưới dạng dict."""
        return {"entries": self.logs}

    def __repr__(self) -> str:
        return f"<Monitor entries={len(self.logs)}>"
