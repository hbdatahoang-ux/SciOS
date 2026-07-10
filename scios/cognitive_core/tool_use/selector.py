# scios/cognitive_core/tool_use/selector.py

"""
SciOS Tool Selector
===================

Chọn tool tối ưu từ danh sách tool khả dĩ dựa trên tiêu chí.
"""

from typing import Dict, Any, List, Optional
from scios.cognitive_core.tool_use.base import Tool


class ToolSelector:
    """
    ToolSelector chọn tool tối ưu từ danh sách tool khả dĩ.
    """

    def __init__(self) -> None:
        # Có thể mở rộng bằng cách nạp config từ metrics/permission
        pass

    def select(self, candidates: List[Tool], request: Dict[str, Any]) -> Optional[Tool]:
        """
        Chọn tool tối ưu từ danh sách candidates.
        Tiêu chí mặc định:
        - Nếu chỉ có 1 tool → chọn ngay.
        - Nếu nhiều tool → chọn tool có độ tin cậy cao nhất (dựa trên metrics).
        - Nếu bằng nhau → chọn tool đầu tiên.
        """
        if not candidates:
            return None

        if len(candidates) == 1:
            return candidates[0]

        # Nếu có nhiều tool, thử chọn theo metrics (giả định mỗi tool có attribute reliability_score)
        best_tool = max(candidates, key=lambda t: getattr(t, "reliability_score", 0.5))
        return best_tool
