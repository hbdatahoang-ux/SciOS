"""
SciOS Tool Sandbox
==================

Thực thi tool trong môi trường sandbox với:

- Bắt lỗi runtime.
- Giới hạn thời gian thực thi.
- Tương thích Windows và Unix-like systems.

Notes
-----
Trên Unix, timeout được thực hiện bằng ``SIGALRM``.

Trên Windows, ``SIGALRM`` không tồn tại nên sandbox sử dụng
``ThreadPoolExecutor`` để giới hạn thời gian chờ.
"""

from __future__ import annotations

import concurrent.futures
import signal
from typing import Any, Callable, Dict


# ============================================================================
# Exceptions
# ============================================================================


class TimeoutException(Exception):
    """Ngoại lệ khi tool vượt quá thời gian cho phép."""


# ============================================================================
# Unix timeout handler
# ============================================================================


def _timeout_handler(signum: int, frame: Any) -> None:
    """
    Signal handler dùng cho Unix ``SIGALRM``.
    """

    raise TimeoutException("Tool execution timed out")


# ============================================================================
# Sandbox
# ============================================================================


class ToolSandbox:
    """
    ToolSandbox thực thi tool với timeout và quản lý trạng thái.

    Parameters
    ----------
    timeout:
        Thời gian tối đa cho phép thực thi, tính bằng giây.
    """

    def __init__(self, timeout: int = 5) -> None:
        if timeout <= 0:
            raise ValueError("timeout must be greater than zero")

        self.timeout = timeout
        self.status = "idle"
        self.message: str | None = None
        self.result: Any = None

    # ========================================================================
    # Public execution API
    # ========================================================================

    def run(self, func: Callable[[], Any]) -> Any:
        """
        Thực thi tool trong sandbox.

        Returns
        -------
        Any
            Kết quả của tool khi thành công.

        dict
            Error response khi execution thất bại hoặc timeout.
        """

        if not callable(func):
            raise TypeError("func must be callable")

        self.status = "running"
        self.message = None
        self.result = None

        if hasattr(signal, "SIGALRM"):
            return self._run_with_signal(func)

        return self._run_with_thread(func)

    # ========================================================================
    # Unix implementation
    # ========================================================================

    def _run_with_signal(
        self,
        func: Callable[[], Any],
    ) -> Any:
        """
        Thực thi bằng ``SIGALRM`` trên Unix-like systems.
        """

        previous_handler = signal.getsignal(signal.SIGALRM)

        try:
            signal.signal(
                signal.SIGALRM,
                _timeout_handler,
            )

            signal.alarm(self.timeout)

            self.result = func()
            self.status = "success"

            return self.result

        except TimeoutException as exc:
            self.status = "error"
            self.message = str(exc)

            return self._error_response()

        except Exception as exc:
            self.status = "error"
            self.message = f"Sandbox error: {exc}"

            return self._error_response()

        finally:
            signal.alarm(0)
            signal.signal(
                signal.SIGALRM,
                previous_handler,
            )

    # ========================================================================
    # Windows / portable implementation
    # ========================================================================

    def _run_with_thread(
        self,
        func: Callable[[], Any],
    ) -> Any:
        """
        Thực thi bằng worker thread.

        ``future.result(timeout=...)`` giới hạn thời gian chờ của caller.
        Python không thể cưỡng chế terminate một thread đang chạy.
        """

        executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=1,
            thread_name_prefix="scios-sandbox",
        )

        future = executor.submit(func)

        try:
            self.result = future.result(
                timeout=self.timeout,
            )

            self.status = "success"

            return self.result

        except concurrent.futures.TimeoutError:
            self.status = "error"
            self.message = (
                f"Sandbox timeout after "
                f"{self.timeout} seconds"
            )

            future.cancel()

            return self._error_response()

        except Exception as exc:
            self.status = "error"
            self.message = f"Sandbox error: {exc}"

            return self._error_response()

        finally:
            executor.shutdown(
                wait=False,
                cancel_futures=True,
            )

    # ========================================================================
    # Error response
    # ========================================================================

    def _error_response(self) -> Dict[str, Any]:
        """
        Tạo error response ổn định cho caller.

        Schema
        ------
        {
            "status": "error",
            "message": "...",
        }
        """

        return {
            "status": "error",
            "message": self.message,
        }

    # ========================================================================
    # Lifecycle
    # ========================================================================

    def reset(self) -> None:
        """
        Đưa sandbox về trạng thái ban đầu.
        """

        self.status = "idle"
        self.message = None
        self.result = None

    # ========================================================================
    # Serialization
    # ========================================================================

    def to_dict(self) -> Dict[str, Any]:
        """
        Xuất trạng thái sandbox dưới dạng dictionary.
        """

        return {
            "status": self.status,
            "message": self.message,
            "result": self.result,
            "timeout": self.timeout,
        }

    # ========================================================================
    # Representation
    # ========================================================================

    def __repr__(self) -> str:
        return (
            f"<ToolSandbox "
            f"status={self.status} "
            f"timeout={self.timeout}>"
        )