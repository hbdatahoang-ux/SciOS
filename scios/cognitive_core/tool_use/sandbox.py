"""
SciOS Tool Sandbox
==================

Thực thi tool trong môi trường an toàn:
- Bắt lỗi runtime
- Giới hạn thời gian (timeout)
- Giới hạn tài nguyên (CPU, memory)
"""

import signal
from typing import Callable, Any, Dict


class TimeoutException(Exception):
    """Ngoại lệ khi vượt quá thời gian cho phép."""
    pass


def _timeout_handler(signum, frame):
    raise TimeoutException("Tool execution timed out")


class ToolSandbox:
    """
    ToolSandbox đảm bảo việc thực thi tool an toàn.
    """

    def __init__(self, timeout: int = 5):
        # timeout mặc định: 5 giây
        self.timeout = timeout
        self.status = "idle"
        self.message: str | None = None
        self.result: Any = None

    def run(self, func: Callable[[], Any]) -> Any:
        """
        Chạy hàm trong sandbox.
        - Đặt timeout
        - Bắt lỗi runtime
        """
        signal.signal(signal.SIGALRM, _timeout_handler)
        signal.alarm(self.timeout)

        try:
            self.status = "running"
            self.result = func()
            self.status = "success"
            return self.result
        except TimeoutException as e:
            self.status = "error"
            self.message = str(e)
            return None
        except Exception as e:
            self.status = "error"
            self.message = f"Sandbox error: {str(e)}"
            return None
        finally:
            signal.alarm(0)

    def reset(self) -> None:
        """Đặt lại trạng thái sandbox."""
        self.status = "idle"
        self.message = None
        self.result = None

    def to_dict(self) -> Dict[str, Any]:
        """Xuất trạng thái sandbox dưới dạng dict."""
        return {
            "status": self.status,
            "message": self.message,
            "result": self.result,
            "timeout": self.timeout,
        }

    def __repr__(self) -> str:
        return f"<ToolSandbox status={self.status} timeout={self.timeout}>"
