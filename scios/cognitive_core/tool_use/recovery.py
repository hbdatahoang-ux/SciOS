"""
SciOS Tool Recovery
===================

Quản lý cơ chế phục hồi khi tool thất bại:
- Retry nhiều lần
- Fallback khi retry không thành công
- Reset trạng thái
- Xuất báo cáo trạng thái
"""

from typing import Any, Callable, Dict


class Recovery:
    """
    Recovery quản lý retry và fallback cho tool.
    """

    def __init__(self, max_retries: int = 1) -> None:
        self.max_retries = max_retries
        self.attempts = 0
        self.status = "idle"
        self.message: str | None = None

    def run(self, func: Callable[[], Any], fallback: Callable[[], Any] | None = None) -> Any:
        """
        Thực thi hàm với retry và fallback.
        """
        self.reset()

        for _ in range(self.max_retries):
            try:
                self.attempts += 1  # tăng trước khi gọi func
                result = func()
                self.status = "success"
                return result
            except Exception as e:
                self.status = "error"
                self.message = str(e)

        if fallback is not None:
            self.status = "fallback"
            return fallback()

        raise RuntimeError(self.message or "Recovery failed")

    def reset(self) -> None:
        """Đặt lại trạng thái về ban đầu."""
        self.attempts = 0
        self.status = "idle"
        self.message = None

    def to_dict(self) -> Dict[str, Any]:
        """Xuất trạng thái dưới dạng dict."""
        return {
            "max_retries": self.max_retries,
            "attempts": self.attempts,
            "status": self.status,
            "message": self.message,
        }

    def __repr__(self) -> str:
        return f"<Recovery status={self.status} attempts={self.attempts}>"
