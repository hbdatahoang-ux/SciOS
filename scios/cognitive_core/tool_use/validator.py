# scios/cognitive_core/tool_use/validator.py

"""
SciOS Tool Validator
====================

Kiểm tra request trước khi gọi tool:
- Đảm bảo có đủ field cần thiết
- Đúng kiểu dữ liệu
- Không chứa nội dung nguy hiểm
"""

from typing import Dict, Any


class ToolValidator:
    """
    ToolValidator kiểm tra request có hợp lệ không.
    """

    def __init__(self) -> None:
        pass

    def validate(self, request: Dict[str, Any]) -> bool:
        """
        Kiểm tra request:
        - Phải có key 'tool'
        - Phải có 'action' hoặc 'operation'
        - Không chứa ký tự nguy hiểm (ví dụ: __import__, os.system)
        """
        if not isinstance(request, dict):
            return False

        tool_name = request.get("tool")
        action = request.get("action") or request.get("operation")

        if not tool_name or not action:
            return False

        # Kiểm tra nội dung nguy hiểm
        expr = str(request)
        forbidden = ["__import__", "os.system", "subprocess", "eval", "exec"]
        if any(f in expr for f in forbidden):
            return False

        return True
