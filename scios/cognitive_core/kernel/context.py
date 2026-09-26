"""
SciOS Cognitive Context
=======================

CognitiveContext là bộ nhớ tạm xuyên suốt pipeline.
Mọi stage đều đọc/ghi dữ liệu vào đây.
"""

from __future__ import annotations

from typing import Any, Dict, List

from .request import CognitiveRequest


__all__ = [
    "CognitiveContext",
]


class CognitiveContext:
    """
    CognitiveContext lưu trữ trạng thái của toàn bộ pipeline.

    Attributes
    ----------
    request:
        CognitiveRequest hiện tại.
    state:
        Dữ liệu được tạo ra trong quá trình pipeline thực thi.
    metadata:
        Metadata bổ sung cho execution.
    trace:
        Lịch sử các thay đổi state theo thứ tự thực thi.
    """

    def __init__(
        self,
        request: CognitiveRequest,
    ) -> None:
        self.request = request
        self.state: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = {}
        self.trace: List[Dict[str, Any]] = []

    # =========================================================
    # State management
    # =========================================================

    def set(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Ghi kết quả của một stage vào context.

        Mỗi lần ghi state sẽ tạo một trace entry tương ứng.
        """
        self.state[key] = value
        self.trace.append({key: value})

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Đọc dữ liệu từ context.

        Parameters
        ----------
        key:
            Tên state cần lấy.
        default:
            Giá trị trả về nếu key không tồn tại.
        """
        return self.state.get(key, default)

    # =========================================================
    # Metadata
    # =========================================================

    def set_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Ghi một metadata entry.
        """
        self.metadata[key] = value

    def get_metadata(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Đọc metadata.

        Parameters
        ----------
        key:
            Tên metadata.
        default:
            Giá trị mặc định nếu key không tồn tại.
        """
        return self.metadata.get(key, default)

    # =========================================================
    # Serialization
    # =========================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:
        """
        Chuyển context thành dictionary.

        Schema
        ------
        {
            "request": ...,
            "state": ...,
            "metadata": ...,
            "trace": ...
        }
        """
        return {
            "request": self.request.to_dict(),
            "state": dict(self.state),
            "metadata": dict(self.metadata),
            "trace": list(self.trace),
        }

    # =========================================================
    # Utility
    # =========================================================

    def clear(
        self,
    ) -> None:
        """
        Xóa state, metadata và trace.

        Request hiện tại được giữ nguyên.
        """
        self.state.clear()
        self.metadata.clear()
        self.trace.clear()

    # =========================================================
    # Representation
    # =========================================================

    def __repr__(
        self,
    ) -> str:
        return (
            "<CognitiveContext "
            f"state_keys={list(self.state.keys())}>"
        )